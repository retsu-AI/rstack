import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from record_v2 import upgrade_fixture


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/independent-review"


class IndependentReviewRegressions(unittest.TestCase):
    def record(self, record):
        record = upgrade_fixture(record)
        with tempfile.TemporaryDirectory(prefix="rstack-review-case-") as directory:
            path = Path(directory) / "record.json"
            path.write_text(json.dumps(record))
            run = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/rstack.py"),
                                  "validate", str(path), "--now", "2026-01-01T12:05:00Z"],
                                 capture_output=True, text=True)
            self.assertEqual(run.stderr, "")
            return run.returncode, json.loads(run.stdout)

    def fixture(self, name="valid_neighbor"):
        return json.loads((FIXTURES / (name + ".json")).read_text())

    def rejected(self, record):
        code, result = self.record(record)
        self.assertNotEqual(code, 0, result)
        self.assertEqual(result["ok"], False)
        self.assertEqual(result.get("completion_supported", False), False)

    def accepted(self, record):
        code, result = self.record(record)
        self.assertEqual((code, result["decision"]), (0, "record_consistent"))
        return result

    def test_preserved_independent_inputs_with_explicit_v2_context(self):
        for case in json.loads((FIXTURES / "index.json").read_text()):
            with self.subTest(case=case["file"]):
                record = json.loads((FIXTURES / case["file"]).read_text())
                self.accepted(record) if case["expected_ok"] else self.rejected(record)

    def test_retry_requires_operation_and_each_required_field(self):
        record = self.fixture("retry_missing_operation")
        self.rejected(record)
        for value in ({}, None, [], True):
            with self.subTest(operation=value):
                record = self.fixture("retry_missing_operation")
                record["operation"] = value
                self.rejected(record)
        for field in ("id", "status", "attempts", "max_attempts", "retry_authorized"):
            with self.subTest(missing=field):
                record = self.fixture("cancelled_retry_valid_neighbor")
                del record["operation"][field]
                self.rejected(record)
        record = self.fixture("cancelled_retry_valid_neighbor")
        record["operation"]["id"] = "  "
        self.rejected(record)
        self.accepted(self.fixture("cancelled_retry_valid_neighbor"))

    def test_delivery_requires_nonempty_string_references(self):
        for field in ("receipt", "artifact_ref"):
            for value in (False, True, "", " \t\n", None, 1, [], {}):
                with self.subTest(field=field, value=value):
                    record = self.fixture()
                    record["delivery"][field] = value
                    self.rejected(record)
            record = self.fixture()
            del record["delivery"][field]
            self.rejected(record)
        self.accepted(self.fixture())

    def test_uncertain_and_cancelled_retry_readback_types_and_results(self):
        for status in ("uncertain", "cancelled"):
            for value in (False, True, "", " \t\n", None, 1, [], {}):
                with self.subTest(status=status, receipt=value):
                    record = self.fixture("cancelled_retry_valid_neighbor")
                    record["operation"].update(status=status, readback_receipt=value)
                    self.rejected(record)
            for value in (False, True, "", "missing", "absent ", "unknown", "present", None):
                with self.subTest(status=status, readback_result=value):
                    record = self.fixture("cancelled_retry_valid_neighbor")
                    record["operation"].update(status=status, readback_result=value)
                    self.rejected(record)
            for field in ("readback_receipt", "readback_result"):
                record = self.fixture("cancelled_retry_valid_neighbor")
                record["operation"]["status"] = status
                del record["operation"][field]
                self.rejected(record)
            record = self.fixture("cancelled_retry_valid_neighbor")
            record["operation"]["status"] = status
            self.accepted(record)

    def test_downstream_claims_require_first_action_and_consistent_stage(self):
        for state in ("admitted", "running", "completed"):
            for claim in ("running", "delivered", "complete"):
                for receipt in ("", " \t\n"):
                    with self.subTest(state=state, claim=claim, receipt=receipt):
                        record = self.fixture()
                        record["execution"].update(state=state, action_receipt=receipt)
                        record["claim_status"] = claim
                        self.rejected(record)
        record = self.fixture()
        record["execution"]["state"] = "admitted"
        self.rejected(record)
        record = self.fixture()
        record["execution"]["action_receipt"] = ""
        record["claim_status"] = "waiting"
        self.rejected(record)

    def test_waiting_and_partial_delivery_remain_distinct(self):
        record = self.fixture()
        record["execution"].update(state="waiting", action_receipt="")
        record["claim_status"] = "waiting"
        record["delivery"] = {"status": "not_delivered"}
        record["acceptance"][1].update(status="pending", evidence_ids=[])
        self.assertEqual(self.accepted(record)["completion_supported"], False)
        record = self.fixture()
        record["execution"]["state"] = "running"
        record["claim_status"] = "delivered"
        record["acceptance"][1].update(status="pending", evidence_ids=[])
        self.assertEqual(self.accepted(record)["completion_supported"], False)

    def test_inspection_has_no_writes_even_without_stop(self):
        for stopped in (False, True):
            record = self.fixture("stopped_inspect_with_write_paths")
            record["approval"]["stop"] = stopped
            self.rejected(record)
            record["next_action"]["paths"] = []
            self.accepted(record)

    def test_scoped_report_and_preserve_remain_available_during_stop(self):
        for kind in ("report", "preserve"):
            record = self.fixture("stopped_inspect_valid_neighbor")
            record["next_action"] = {"kind": kind, "paths": ["docs/parser.md"]}
            self.accepted(record)
            record["next_action"]["paths"] = ["outside/approval.md"]
            self.rejected(record)


if __name__ == "__main__":
    unittest.main()
