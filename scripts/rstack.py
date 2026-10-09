#!/usr/bin/env python3
"""Offline evidence checks. No dispatch, writes, network, or permission grants."""
import argparse
import json
import math
from pathlib import Path, PurePosixPath
import subprocess
import sys
from datetime import datetime, timezone


class InvalidRecord(ValueError):
    pass


def instant(value):
    if not isinstance(value, str):
        raise InvalidRecord("timestamp must be an ISO 8601 string with timezone")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise InvalidRecord("timestamp must include timezone")
    return result.astimezone(timezone.utc)


def checkpoint(previous, current, last_progress, interval=15):
    if not isinstance(interval, (int, float)) or not math.isfinite(interval) or interval <= 0:
        raise InvalidRecord("interval must be positive and finite")
    prior, now, progress = map(instant, (previous, current, last_progress))
    if prior > now or progress > now:
        raise InvalidRecord("checkpoint or progress timestamp is in the future")
    elapsed = (now - prior).total_seconds() / 60
    age = (now - progress).total_seconds() / 60
    return {"previous_at": previous, "current_at": current,
            "elapsed_minutes": round(elapsed, 3), "progress_age_minutes": round(age, 3),
            "due": elapsed >= interval, "stale": age >= interval,
            "next_step": "inspect_changed_evidence" if age >= interval else "continue_current_unit"}


def path_parts(value):
    if not isinstance(value, str) or not value or "\\" in value:
        raise InvalidRecord("scope paths must be nonempty POSIX relative paths")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise InvalidRecord("scope paths must be relative and cannot escape the repository")
    return path.parts


def contains(parent, child):
    p, c = path_parts(parent), path_parts(child)
    return c[:len(p)] == p


def require(obj, fields, label):
    if not isinstance(obj, dict):
        raise InvalidRecord(label + " must be an object")
    for field, kind in fields.items():
        if field not in obj or type(obj[field]) is not kind:
            raise InvalidRecord(label + "." + field + " must be " + kind.__name__)


def reference(value):
    return isinstance(value, str) and bool(value.strip())


def shape(r):
    require(r, {"schema_version": int, "outcome_id": str, "original_request": dict,
                "approval": dict, "register": dict, "owner": str, "scope": dict,
                "acceptance": list, "stop_conditions": list, "subject": dict,
                "execution": dict, "checkpoint": dict, "evidence": list,
                "delivery": dict, "next_action": dict, "claim_status": str}, "record")
    if r["schema_version"] != 2:
        raise InvalidRecord("unsupported schema_version; version 2 requires approved obligations, native goal and handoff records")
    require(r, {"completion_contract": dict, "outcome_results": list, "native_goal": dict, "handoff_receipts": dict}, "record v2")
    for key, fields in {
        "original_request": {"ref": str, "summary": str},
        "approval": {"ref": str, "allowed_actions": list, "denied_actions": list, "stop": bool},
        "register": {"ref": str, "writer": str},
        "scope": {"write_paths": list},
        "subject": {"revision": str, "manifest": dict, "authors": list, "review_required": bool},
        "execution": {"state": str, "task_id": str, "admission_receipt": str,
                      "action_receipt": str, "last_progress_at": str},
        "checkpoint": {"previous_at": str, "current_at": str, "next_action": str, "progress_ref": str},
        "delivery": {"status": str}, "next_action": {"kind": str, "paths": list},
    }.items():
        require(r[key], fields, key)
    if r["execution"]["state"] not in {"admitted", "running", "completed", "interrupted", "cancelled", "held", "waiting"}:
        raise InvalidRecord("unknown execution state")
    if r["delivery"]["status"] not in {"not_delivered", "delivered", "uncertain"}:
        raise InvalidRecord("unknown delivery status")
    if r["delivery"]["status"] == "delivered":
        require(r["delivery"], {"receipt": str, "artifact_ref": str, "revision": str, "manifest": dict}, "delivery")
        if not all(reference(r["delivery"][key]) for key in ("receipt", "artifact_ref", "revision")):
            raise InvalidRecord("delivered records need nonempty string receipt, artifact and revision references")
    if r["claim_status"] not in {"admitted", "running", "waiting", "delivered", "complete"}:
        raise InvalidRecord("unknown claim status")
    if not r["acceptance"] or not r["stop_conditions"] or not r["subject"]["manifest"]:
        raise InvalidRecord("acceptance, stop_conditions and subject manifest cannot be empty")
    for a in r["acceptance"]:
        require(a, {"id": str, "description": str, "status": str, "evidence_ids": list}, "acceptance")
        if a["status"] not in {"pending", "passed", "failed", "unverified"}:
            raise InvalidRecord("unknown acceptance status")
    for e in r["evidence"]:
        require(e, {"id": str, "kind": str, "ref": str, "status": str,
                    "revision": str, "manifest": dict}, "evidence")
        if e["status"] not in {"passed", "failed", "inconclusive", "not_run"}:
            raise InvalidRecord("unknown evidence status")
    for p in r["scope"]["write_paths"] + r["next_action"]["paths"]:
        path_parts(p)
    for label, items in (("allowed_actions", r["approval"]["allowed_actions"]),
                         ("denied_actions", r["approval"]["denied_actions"]),
                         ("authors", r["subject"]["authors"]),
                         ("stop_conditions", r["stop_conditions"])):
        if any(not isinstance(item, str) or not item.strip() for item in items):
            raise InvalidRecord(label + " requires nonempty strings")
    if not r["subject"]["authors"]:
        raise InvalidRecord("subject authors cannot be empty")
    for a in r["acceptance"]:
        if not a["id"].strip() or not a["description"].strip() or any(not isinstance(i, str) or not i for i in a["evidence_ids"]):
            raise InvalidRecord("acceptance needs named criteria and string evidence IDs")
    for e in r["evidence"]:
        if not e["id"].strip() or not e["kind"].strip():
            raise InvalidRecord("evidence identity and kind cannot be empty")
        if e["status"] == "passed" and not e["ref"].strip():
            raise InvalidRecord("passing evidence needs a receipt reference")
        if e["kind"] == "review" and e["status"] == "passed":
            require(e, {"reviewer": str, "independence_receipt": str}, "review")
    for label in ("operation", "recovery", "reconciliation"):
        if label in r and not isinstance(r[label], dict):
            raise InvalidRecord(label + " must be an object")
    for label in ("metrics", "writers"):
        if label in r and not isinstance(r[label], list):
            raise InvalidRecord(label + " must be a list")
    if r.get("recovery"):
        require(r["recovery"], {"resume_approval_ref": str, "state_readback": str}, "recovery")
    for key in ("outcome_id", "owner"):
        if not r[key].strip():
            raise InvalidRecord(key + " cannot be empty")
    for obj, key in ((r["original_request"], "ref"), (r["original_request"], "summary"),
                     (r["approval"], "ref"), (r["register"], "ref"), (r["register"], "writer"),
                     (r["subject"], "revision"), (r["checkpoint"], "next_action")):
        if not obj[key].strip():
            raise InvalidRecord(key + " cannot be empty")
    for name, digest in r["subject"]["manifest"].items():
        if not name or not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise InvalidRecord("manifest requires named SHA-256 digests")


def completion_contract(r, evidence, accepted, delivered, reviewed, reject):
    c = r['completion_contract']
    require(c, {'approval_ref': str, 'request_ref': str, 'outcome_kind': str,
                'native_goal_required': bool, 'obligations': list, 'handoff': dict}, 'completion_contract')
    if c['approval_ref'] != r['approval']['ref'] or c['request_ref'] != r['original_request']['ref']:
        reject('CONTRACT_BINDING', 'The obligation inventory must bind the original request and current approval.')
    if c['outcome_kind'] not in {'support', 'delivery'} or 'parent_outcome_id' not in c:
        raise InvalidRecord('contract needs a known outcome kind and explicit parent_outcome_id')
    parent = c['parent_outcome_id']
    if parent is not None and (not reference(parent) or parent == r['outcome_id']):
        raise InvalidRecord('parent must be a distinct outcome reference or null')
    if c['outcome_kind'] == 'support' and parent is None:
        reject('PARENT_OUTCOME', 'A supporting outcome must identify the delivery outcome it assists.')
    if not c['obligations']:
        raise InvalidRecord('approved obligation inventory cannot be empty')
    obligations, required, mapped = {}, {}, set()
    acceptance = {a['id']: a for a in r['acceptance']}
    for o in c['obligations']:
        require(o, {'id': str, 'description': str, 'source_ref': str, 'kind': str,
                    'part_ids': list, 'acceptance_ids': list}, 'obligation')
        if any(not reference(o[k]) for k in ('id', 'description', 'source_ref')) or o['kind'] not in {'support', 'delivery'}:
            raise InvalidRecord('obligation needs identity, source, description and known kind')
        if o['id'] in obligations:
            raise InvalidRecord('duplicate obligation identity')
        obligations[o['id']] = o
        if c['outcome_kind'] == 'support' and o['kind'] == 'delivery':
            reject('OUTCOME_SUBSTITUTION', 'Supporting work cannot close a delivery obligation.')
        for key in ('part_ids', 'acceptance_ids'):
            values = o[key]
            if not values or any(not reference(v) for v in values) or len(values) != len(set(values)):
                raise InvalidRecord('obligation ' + key + ' needs unique nonempty references')
        mapped.update(o['acceptance_ids'])
        for part in o['part_ids']:
            required[(o['id'], part)] = o
    if mapped != set(acceptance):
        reject('OBLIGATION_COVERAGE', 'Every approved acceptance ID must map to retained obligations, with no unknown IDs.')
    def proof(ids):
        if not isinstance(ids, list) or any(not reference(i) for i in ids):
            raise InvalidRecord('outcome evidence_ids must be string references')
        return bool(ids) and all(i in evidence and evidence[i]['status'] == 'passed'
                    and reference(evidence[i]['ref']) and evidence[i]['revision'] == r['subject']['revision']
                    and evidence[i]['manifest'] == r['subject']['manifest'] for i in ids)
    results, parts_complete = {}, True
    for result in r['outcome_results']:
        require(result, {'obligation_id': str, 'part_id': str, 'kind': str,
                         'status': str, 'evidence_ids': list}, 'outcome_result')
        if result['status'] not in {'pending', 'blocked', 'complete'} or result['kind'] not in {'support', 'delivery'}:
            raise InvalidRecord('unknown outcome result state or kind')
        key = (result['obligation_id'], result['part_id'])
        if key in results or key not in required:
            reject('OBLIGATION_COVERAGE', 'Each result must name one unique approved obligation part.')
        results[key] = result
        if key in required and result['kind'] != required[key]['kind']:
            reject('OUTCOME_SUBSTITUTION', 'A report/support result cannot substitute for the approved delivery kind.')
        valid = proof(result['evidence_ids'])
        if result['status'] == 'complete' and not valid:
            reject('OUTCOME_EVIDENCE', 'A completed part needs evidence bound to the current subject.')
        parts_complete = parts_complete and result['status'] == 'complete' and valid
    if set(results) != set(required):
        reject('OBLIGATION_COVERAGE', 'Retain each original part, including blocked or pending parts.')
        parts_complete = False

    h = c['handoff']
    require(h, {'destination': str, 'recipient': str, 'artifact_ref': str, 'required_stages': list}, 'handoff contract')
    stages = {'persistence', 'attachment', 'recipient_readback', 'incorporation'}
    required_stages = h['required_stages']
    if any(not reference(h[k]) for k in ('destination', 'recipient', 'artifact_ref')):
        raise InvalidRecord('handoff contract requires expected destination, recipient and artifact')
    if (not required_stages or any(not isinstance(s, str) or s not in stages for s in required_stages)
            or len(required_stages) != len(set(required_stages))):
        raise InvalidRecord('handoff requires distinct known stages selected by the approved contract')
    if delivered and r['delivery']['artifact_ref'] != h['artifact_ref']:
        reject('HANDOFF_BINDING', 'The delivered artifact differs from the selected contract.')
    confirmed, receipt_refs = set(), set()
    for stage, receipt in r['handoff_receipts'].items():
        if stage not in stages:
            raise InvalidRecord('unknown handoff receipt stage')
        require(receipt, {'status': str}, 'handoff receipt')
        if receipt['status'] not in {'pending', 'uncertain', 'confirmed'}:
            raise InvalidRecord('unknown handoff receipt status')
        if receipt['status'] != 'confirmed':
            continue
        require(receipt, {'ref': str, 'artifact_ref': str, 'revision': str, 'manifest': dict,
                          'destination': str, 'recipient': str}, 'confirmed handoff')
        valid = all(reference(receipt[k]) for k in ('ref', 'artifact_ref', 'revision', 'destination', 'recipient'))
        valid = valid and all(receipt[k] == h[k] for k in ('artifact_ref', 'destination', 'recipient'))
        valid = valid and receipt['revision'] == r['subject']['revision'] and receipt['manifest'] == r['subject']['manifest']
        if stage == 'incorporation':
            require(receipt, {'register_ref': str, 'writer': str, 'disposition': str,
                              'readback_ref': str, 'detail': str}, 'incorporation')
            valid = valid and receipt['register_ref'] == r['register']['ref'] and receipt['writer'] == r['register']['writer']
            valid = valid and receipt['disposition'] in {'incorporated', 'retained'}
            valid = valid and reference(receipt['readback_ref']) and reference(receipt['detail'])
        if not valid:
            reject('HANDOFF_RECEIPT', 'Confirmed stages need exact subject/destination binding; incorporation needs canonical readback or explicit retained disposition.')
        elif receipt['ref'] in receipt_refs:
            reject('HANDOFF_RECEIPT_REUSE', 'Persistence, attachment, readback and incorporation require distinct event references.')
        else:
            receipt_refs.add(receipt['ref'])
            confirmed.add(stage)
    transport_complete = (set(required_stages) - {'incorporation'}) <= confirmed
    handoff_complete = set(required_stages) <= confirmed
    if r['claim_status'] in {'delivered', 'complete'} and not transport_complete:
        reject('HANDOFF_OPEN', 'The selected persistence/attachment/recipient stages are not all confirmed.')
    if r['claim_status'] == 'complete' and (not parts_complete or not handoff_complete):
        reject('COMPLETION_CONTRACT_OPEN', 'Required outcome parts or canonical handoff remain open.')

    goal = r['native_goal']
    require(goal, {'state': str}, 'native_goal')
    state, action = goal['state'], r['next_action']['kind']
    if state not in {'not_selected', 'retained', 'created', 'unavailable', 'conflict', 'absent'}:
        raise InvalidRecord('unknown native goal binding state')
    if state == 'not_selected' and c['native_goal_required']:
        reject('GOAL_NOT_BOUND', 'A selected native goal cannot be omitted; record its actual binding or lifecycle dependency.')
    goal_complete = state == 'not_selected' and not c['native_goal_required']
    goal_finished = False
    if state in {'unavailable', 'conflict', 'absent'}:
        require(goal.get('dependency'), {'action': str, 'owner': str, 'resume_when': str, 'observation_ref': str}, 'goal dependency')
        if not all(reference(v) for v in goal['dependency'].values()):
            raise InvalidRecord('goal dependency must name action, owner, observation and resumption trigger')
    if state in {'retained', 'created'}:
        require(goal, {'id': str, 'outcome_id': str, 'prior_readback': dict, 'current_readback': dict}, 'bound goal')
        if not reference(goal['id']) or goal['outcome_id'] != r['outcome_id']:
            reject('GOAL_BINDING', 'The native goal must bind this outcome, not its parent or a different objective.')
        prior, current = goal['prior_readback'], goal['current_readback']
        require(prior, {'ref': str, 'state': str}, 'prior goal readback')
        require(current, {'ref': str, 'goal_id': str, 'outcome_id': str, 'status': str, 'native_status': str}, 'current goal readback')
        if not all(reference(current[k]) for k in current) or not reference(prior['ref']):
            raise InvalidRecord('goal readbacks require nonempty string references/statuses')
        if current['status'] not in {'unfinished', 'complete'}:
            raise InvalidRecord('unknown normalized goal status; retain actual native status separately')
        if current['goal_id'] != goal['id'] or current['outcome_id'] != r['outcome_id']:
            reject('GOAL_BINDING', 'Current readback must identify the bound goal and outcome.')
        if state == 'retained':
            require(prior, {'goal_id': str, 'outcome_id': str}, 'retained goal readback')
            if prior['state'] != 'same_unfinished' or prior['goal_id'] != goal['id'] or prior['outcome_id'] != r['outcome_id']:
                reject('GOAL_REPLACEMENT', 'Retain the compatible unfinished goal; do not replace another goal.')
        else:
            require(goal, {'creation_approval_ref': str, 'creation_receipt': str}, 'created goal')
            if (prior['state'] != 'none_unfinished' or not reference(goal['creation_receipt'])
                    or goal['creation_approval_ref'] != c['approval_ref']
                    or 'create_goal' not in r['approval']['allowed_actions']
                    or 'create_goal' in r['approval']['denied_actions'] or r['approval']['stop']):
                reject('GOAL_CREATE_AUTHORITY', 'Creation requires actual no-unfinished-goal readback, scoped authority and a creation receipt.')
        goal_finished = current['status'] == 'complete'
        goal_complete = goal_finished
    if action == 'create_goal':
        prior = goal.get('prior_readback', {})
        if state != 'absent' or prior.get('state') != 'none_unfinished' or not reference(prior.get('ref')):
            reject('GOAL_CREATE_AUTHORITY', 'Proposed creation needs supported absence readback; unavailable/conflicting is not absent.')
    if action == 'complete_goal' and state not in {'retained', 'created'}:
        reject('GOAL_NOT_BOUND', 'Completion requires an actual compatible native goal binding.')
    ready = accepted and delivered and reviewed and parts_complete and handoff_complete
    if (goal_finished or action == 'complete_goal') and not ready:
        reject('GOAL_PREMATURE_COMPLETION', 'All original Done checks and selected delivery stages must pass before goal completion.')
    if r['claim_status'] == 'complete' and not goal_complete:
        reject('GOAL_NOT_BOUND', 'Required native goal completion/readback is missing; preserve the lifecycle dependency.')
    return parts_complete and handoff_complete and goal_complete


def evaluate(r, now):
    shape(r)
    errors = []
    def reject(code, detail):
        if not any(e["code"] == code for e in errors):
            errors.append({"code": code, "detail": detail})
    subject, execution, approval, action = (r[k] for k in ("subject", "execution", "approval", "next_action"))
    current = instant(now)
    check = checkpoint(r["checkpoint"]["previous_at"], r["checkpoint"]["current_at"], execution["last_progress_at"])
    age = (current - instant(r["checkpoint"]["current_at"])).total_seconds() / 60
    if age < 0:
        raise InvalidRecord("checkpoint is later than observation time")
    if age >= 15:
        reject("STALE_CHECKPOINT", "Refresh facts and compare previous/current times before answering status.")
    if not r["checkpoint"]["progress_ref"]:
        reject("PROGRESS_UNVERIFIED", "A timestamp without a concrete progress receipt is not progress.")
    downstream_claim = r["claim_status"] in {"running", "delivered", "complete"} or r["delivery"]["status"] == "delivered"
    if execution["state"] in {"running", "completed"} or downstream_claim:
        if not reference(execution["action_receipt"]):
            reject("ADMITTED_NOT_RUNNING", "Execution, delivery and completion claims require a first-action receipt.")
    if execution["state"] == "admitted" and downstream_claim:
        reject("EXECUTION_STAGE", "An admission-only execution state cannot support a running, delivered or complete claim.")
    if action["kind"] not in approval["allowed_actions"] or action["kind"] in approval["denied_actions"]:
        reject("PERMISSION_DENIED", "The proposed action is outside current scoped approval or explicitly denied.")
    if approval["stop"] and action["kind"] not in {"inspect", "report", "preserve"}:
        reject("STOP_GATE", "Preserve work and report; explicit stop prevents new execution.")
    if action["kind"] == "inspect" and action["paths"]:
        reject("READ_ONLY_WRITES", "Inspection cannot include proposed write paths.")
    if execution["state"] in {"held", "cancelled", "interrupted"} and action["kind"] not in {"inspect", "report", "preserve"}:
        if not r.get("recovery", {}).get("resume_approval_ref") or not r.get("recovery", {}).get("state_readback"):
            reject("RECOVERY_UNVERIFIED", "Read back effects and bind current resume authority before continuing.")
    if any(not any(contains(p, v) for p in r["scope"]["write_paths"]) for v in action["paths"]):
        reject("SCOPE_CREEP", "A proposed write lies outside the approved path set.")
    leases = r.get("writers", [{"owner": r["owner"], "paths": r["scope"]["write_paths"]}])
    for i, one in enumerate(leases):
        require(one, {"owner": str, "paths": list}, "writer")
        for two in leases[i+1:]:
            require(two, {"owner": str, "paths": list}, "writer")
            if one["owner"] != two["owner"] and any(contains(a, b) or contains(b, a) for a in one["paths"] for b in two["paths"]):
                reject("WRITER_COLLISION", "Different writers claim overlapping paths.")
    op = r.get("operation")
    if action["kind"] == "retry":
        require(op, {"retry_authorized": bool}, "retry operation")
    if op is not None:
        require(op, {"id": str, "status": str, "attempts": int, "max_attempts": int}, "operation")
        if not reference(op["id"]) or op["status"] not in {"not_attempted", "failed", "uncertain", "cancelled", "succeeded", "denied"}:
            raise InvalidRecord("operation needs an identity and known status")
        if op["attempts"] < 0 or op["max_attempts"] < 0:
            raise InvalidRecord("operation attempt counts cannot be negative")
        if "retry_authorized" in op and type(op["retry_authorized"]) is not bool:
            raise InvalidRecord("retry_authorized must be boolean")
        if "readback_receipt" in op and not reference(op["readback_receipt"]):
            raise InvalidRecord("readback_receipt must be a nonempty string reference")
        if "readback_result" in op and (not isinstance(op["readback_result"], str) or op["readback_result"] not in {"absent", "present", "unknown"}):
            raise InvalidRecord("readback_result must be absent, present or unknown")
        if action["kind"] == "retry":
            if op["status"] in {"uncertain", "cancelled"} and (not reference(op.get("readback_receipt")) or op.get("readback_result") != "absent"):
                reject("UNCERTAIN_EXTERNAL_SEND", "Inspect the original destination/effect before considering a retry.")
            if op["status"] in {"succeeded", "denied"} or op.get("readback_result") == "present":
                reject("RETRY_FORBIDDEN", "Success, a found effect, or a denial cannot be treated as a retryable failure.")
            if not op.get("retry_authorized") or op["attempts"] >= op["max_attempts"]:
                reject("RETRY_BUDGET", "Retry needs scoped authority and an unspent finite attempt budget.")
    ids = [e["id"] for e in r["evidence"]]
    if len(ids) != len(set(ids)):
        reject("DUPLICATE_EVIDENCE", "Evidence IDs must be unique.")
    a_ids = [a["id"] for a in r["acceptance"]]
    if len(a_ids) != len(set(a_ids)):
        reject("DUPLICATE_ACCEPTANCE", "Acceptance IDs must identify distinct obligations.")
    evidence = {e["id"]: e for e in r["evidence"]}
    reviews = []
    for e in evidence.values():
        bound = e["revision"] == subject["revision"] and e["manifest"] == subject["manifest"]
        if e["status"] == "passed" and not bound:
            reject("CHANGED_REVISION_REVIEW" if e["kind"] == "review" else "SOURCE_BINDING", "Passing evidence refers to a different revision or source manifest.")
        if e["kind"] == "review" and e["status"] == "passed":
            independent = e.get("reviewer") and e["reviewer"] not in subject["authors"] and e["reviewer"] != r["owner"] and e.get("independence_receipt")
            if not independent:
                reject("SELF_REVIEW", "A renamed role or an author's own check is not independent acceptance.")
            if bound and independent:
                reviews.append(e)
        if e["kind"] == "tests" and e["status"] == "passed":
            counts = [e.get(k) for k in ("executed", "failed", "skipped")]
            if any(type(n) is not int or n < 0 for n in counts) or counts[0] == 0 or counts[1] != 0 or counts[2] != 0:
                reject("TEST_COVERAGE", "Passing required tests need nonzero executed, zero failed and zero skipped checks.")
    accepted = True
    for a in r["acceptance"]:
        proof = a["evidence_ids"]
        valid = a["status"] == "passed" and proof and all(i in evidence and evidence[i]["status"] == "passed" and evidence[i]["ref"] and evidence[i]["revision"] == subject["revision"] and evidence[i]["manifest"] == subject["manifest"] for i in proof)
        if not valid:
            accepted = False
            if a["status"] == "passed":
                reject("ACCEPTANCE_UNSUPPORTED", "A passed criterion has missing, failing, or stale evidence.")
    delivery = r["delivery"]
    delivered = delivery["status"] == "delivered" and delivery["revision"] == subject["revision"] and delivery["manifest"] == subject["manifest"]
    if delivery["status"] == "delivered" and not delivered:
        reject("DELIVERY_BINDING", "Delivery needs a receipt and artifact bound to the current subject.")
    if execution["state"] == "completed" and not delivered:
        reject("COMPLETED_UNDELIVERED", "The worker ended without the promised delivery receipt.")
    if r["claim_status"] in {"delivered", "complete"} and not delivered:
        reject("COMPLETED_UNDELIVERED", "Do not claim delivery from an ended task or a prepared artifact.")
    if r["claim_status"] == "complete":
        if not accepted:
            reject("ACCEPTANCE_OPEN", "One or more original acceptance criteria remain unmet.")
        if subject["review_required"] and not reviews:
            reject("INDEPENDENT_REVIEW_MISSING", "The current subject lacks an authentic independent verdict.")
    for metric in r.get("metrics", []):
        require(metric, {"population": str, "revision": str, "observed_at": str}, "metric")
        instant(metric["observed_at"])
        n, d, percent = (metric.get(k) for k in ("numerator", "denominator", "percentage"))
        if percent is None:
            continue
        numbers = all(type(v) in {int, float} and math.isfinite(v) for v in (n, d, percent))
        if not numbers or d <= 0 or n < 0 or n > d or not metric["population"].strip() or not metric["revision"].strip():
            reject("MISSING_DENOMINATOR", "Percentages need a stable named population, revision and valid numerator/denominator.")
        elif abs(percent - n / d * 100) > 0.051:
            reject("PERCENTAGE_MISMATCH", "Reported percentage disagrees with its numerator and denominator.")
    reconciliation = r.get("reconciliation", {})
    if action["kind"] == "cherry_pick" and reconciliation.get("decision") in {"already_ancestor", "same_tree", "same_selected_files", "equivalent_patch"}:
        reject("DUPLICATE_CHERRYPICK", "Existing incorporation evidence requires a delta decision before another cherry-pick.")
    contract_complete = completion_contract(r, evidence, accepted, delivered, bool(reviews) or not subject["review_required"], reject)
    return {"ok": not errors, "outcome_id": r["outcome_id"], "decision": "hold_claim_or_action" if errors else "record_consistent",
            "errors": errors, "checkpoint": check, "checkpoint_age_minutes": round(age, 3),
            "completion_supported": bool(not errors and accepted and delivered and contract_complete and (reviews or not subject["review_required"])),
            "completion_scope": r["outcome_id"], "parent_completion_supported": False,
            "authority": "This checks supplied evidence. It grants no permission and authenticates no receipt."}


def git(repo, *args, input_bytes=None, allow_one=False):
    p = subprocess.run(["git", "--no-optional-locks", "-C", str(repo), *args], input=input_bytes, capture_output=True)
    if p.returncode and not (allow_one and p.returncode == 1):
        raise InvalidRecord(p.stderr.decode().strip() or "git command failed")
    return p


def reconcile(repo, candidate, target, paths):
    if not paths:
        raise InvalidRecord("name the files whose incorporation matters")
    for path in paths:
        path_parts(path)
    def resolve(ref):
        return git(repo, "rev-parse", "--verify", "--end-of-options", ref + "^{commit}").stdout.decode().strip()
    c, t = resolve(candidate), resolve(target)
    ancestor = git(repo, "merge-base", "--is-ancestor", c, t, allow_one=True).returncode == 0
    trees = [git(repo, "rev-parse", v + "^{tree}").stdout.decode().strip() for v in (c, t)]
    same_files = git(repo, "diff", "--quiet", "--no-ext-diff", "--no-textconv", c, t, "--", *paths, allow_one=True).returncode == 0
    for path in paths:
        if not any(git(repo, "ls-tree", "-r", v, "--", path).stdout for v in (c, t)):
            raise InvalidRecord("selected path absent from both revisions: " + path)
    patch = git(repo, "show", "--format=", "--no-ext-diff", "--no-textconv", c, "--", *paths).stdout
    patch_id = git(repo, "patch-id", "--stable", input_bytes=patch).stdout.decode().split()
    history = git(repo, "log", "--format=commit %H", "-p", "--no-ext-diff", "--no-textconv", t, "--", *paths).stdout
    target_patches = git(repo, "patch-id", "--stable", input_bytes=history).stdout.decode().splitlines()
    matches = [line.split()[1] for line in target_patches if patch_id and line.split()[0] == patch_id[0]]
    decision = "already_ancestor" if ancestor else "same_tree" if trees[0] == trees[1] else "same_selected_files" if same_files else "equivalent_patch" if matches else "delta_review_required"
    status = git(repo, "status", "--porcelain=v1", "--untracked-files=normal").stdout.decode().splitlines()
    return {"candidate": c, "target": t, "paths": paths, "candidate_tree": trees[0], "target_tree": trees[1],
            "ancestor": ancestor, "selected_files_equal": same_files, "patch_matches": matches,
            "decision": decision, "dirty_entries": status,
            "limit": "Committed revisions only. Patch equality is supporting evidence, not semantic acceptance or publication proof. Working-tree edits require separate preservation and comparison."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("record", type=Path)
    validate.add_argument("--now", required=True)
    cp = sub.add_parser("checkpoint")
    for flag in ("previous", "current", "last-progress"):
        cp.add_argument("--" + flag, required=True)
    rec = sub.add_parser("reconcile")
    rec.add_argument("--repo", required=True, type=Path)
    rec.add_argument("--candidate", required=True)
    rec.add_argument("--target", required=True)
    rec.add_argument("--paths", nargs="+", required=True)
    args = parser.parse_args()
    try:
        if args.command == "validate":
            result = evaluate(json.loads(args.record.read_text()), args.now)
        elif args.command == "checkpoint":
            result = checkpoint(args.previous, args.current, args.last_progress)
        else:
            result = reconcile(args.repo, args.candidate, args.target, args.paths)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1 if result.get("ok") is False else 0
    except (InvalidRecord, ValueError, TypeError, KeyError, OSError) as exc:
        print(json.dumps({"ok": False, "completion_supported": False, "errors": [{"code": "INVALID_INPUT", "detail": str(exc)}]}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
