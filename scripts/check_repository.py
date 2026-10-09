#!/usr/bin/env python3
"""Check repository packaging without installing dependencies or calling services."""
import json
import hashlib
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    errors = []
    skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
    names = []
    for path in skills:
        content = path.read_text()
        match = re.match(r"\A---\nname: ([a-z0-9-]+)\ndescription: ([^\n]+)\n---\n", content)
        if not match:
            errors.append(f"Invalid frontmatter: {path.relative_to(ROOT)}")
            continue
        name, description = match.groups()
        if name != path.parent.name or len(name) >= 64 or not description.strip():
            errors.append(f"Invalid discovery fields: {name}")
        names.append(name)
        if not (ROOT / ".agents/skills" / name).resolve() == path.parent.resolve():
            errors.append(f"Missing discovery link: {name}")
    if not skills or len(names) != len(set(names)):
        errors.append("Missing skills or duplicate skill names")
    link_count = 0
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue
        content = path.read_text()
        if "[TODO:" in content:
            errors.append(f"Unfinished scaffold: {path.relative_to(ROOT)}")
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", content):
            target = target.strip("<>").split("#")[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            link_count += 1
            resolved = (path.parent / target).resolve()
            if not resolved.is_relative_to(ROOT) or not resolved.exists():
                errors.append(f"Missing or nonportable link: {path.relative_to(ROOT)} -> {target}")
    expected = {"admitted_not_running", "stale_checkpoint", "completed_undelivered", "scope_creep",
                "duplicate_cherrypick", "uncertain_external_send", "changed_revision_review",
                "missing_denominator", "permission_denial"}
    cases = json.loads((ROOT / "tests/fixtures/cases.json").read_text())
    missing = expected - {case["name"] for case in cases}
    if missing:
        errors.append("Missing required behavioral fixtures: " + ", ".join(sorted(missing)))
    contract_cases = json.loads((ROOT / "tests/fixtures/completion-contract/cases.json").read_text())
    required_contract_cases = {"goal_capability_unavailable", "report_substitutes_delivery", "multipart_missing_usage",
                               "recipient_receipt_missing", "incorporation_ack_only", "complete_local_delivery"}
    if required_contract_cases != {case["name"] for case in contract_cases}:
        errors.append("Completion-contract behavioral fixture population differs from the declared set")
    manifest_path = ROOT / "review/SUBJECT.json"
    if manifest_path.exists():
        subject = json.loads(manifest_path.read_text())
        entries = subject["files"]
        recorded = {e["path"] for e in entries}
        actual = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*")
                  if ".git" not in p.relative_to(ROOT).parts and p != manifest_path
                  and (p.is_symlink() or p.is_file())}
        if recorded != actual or len(recorded) != len(entries):
            errors.append("Subject manifest file population differs from the checkout")
        for entry in entries:
            path = ROOT / entry["path"]
            if not path.resolve().is_relative_to(ROOT) or not path.exists():
                errors.append("Invalid subject path: " + entry["path"])
                continue
            data = str(path.readlink()).encode() if path.is_symlink() else path.read_bytes()
            kind = "symlink" if path.is_symlink() else "file"
            if hashlib.sha256(data).hexdigest() != entry["sha256"] or kind != entry["kind"]:
                errors.append("Subject bytes changed: " + entry["path"])
    print(json.dumps({"ok": not errors, "skills": len(skills), "local_links": link_count,
                      "behavioral_fixtures": len(cases), "contract_fixtures": len(contract_cases), "errors": errors}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
