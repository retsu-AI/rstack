import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from record_v2 import upgrade_fixture


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts/rstack.py"


class PublicCLI(unittest.TestCase):
    def command(self, *args):
        p = subprocess.run([sys.executable, "-B", str(CLI), *map(str, args)], capture_output=True, text=True)
        self.assertEqual(p.stderr, "")
        return p.returncode, json.loads(p.stdout)

    def record(self, value, now="2026-01-01T12:05:00Z"):
        value = upgrade_fixture(value)
        with tempfile.TemporaryDirectory(prefix="rstack-record-") as d:
            path = Path(d) / "record.json"
            path.write_text(json.dumps(value))
            return self.command("validate", path, "--now", now)

    def example(self):
        return json.loads((ROOT / "templates/outcome.example.json").read_text())

    def test_delivered_accepted_outcome(self):
        code, result = self.record(self.example())
        self.assertEqual(code, 0)
        self.assertEqual(result["decision"], "record_consistent")
        self.assertEqual(result["completion_supported"], True)

    def test_observed_failure_classes(self):
        for case in json.loads((ROOT / "tests/fixtures/cases.json").read_text()):
            with self.subTest(case=case["name"]):
                code, result = self.record(case["record"], case["now"])
                self.assertEqual(code, 1)
                self.assertIn(case["expected_code"], [e["code"] for e in result["errors"]])
                self.assertEqual(result["completion_supported"], False)

    def test_absent_effect_allows_bounded_retry_but_found_effect_does_not(self):
        record = self.example()
        record["next_action"] = {"kind": "retry", "paths": []}
        record["operation"] = {"id": "fixture:upload", "status": "uncertain", "attempts": 1,
                               "max_attempts": 2, "retry_authorized": True,
                               "readback_receipt": "fixture:destination-read", "readback_result": "absent"}
        code, result = self.record(record)
        self.assertEqual((code, result["decision"]), (0, "record_consistent"))
        record["operation"]["readback_result"] = "present"
        code, result = self.record(record)
        self.assertEqual(code, 1)
        self.assertIn("RETRY_FORBIDDEN", [e["code"] for e in result["errors"]])

    def test_denial_does_not_block_independent_inspection(self):
        record = self.example()
        record["next_action"] = {"kind": "inspect", "paths": []}
        record["operation"] = {"id": "fixture:denied", "status": "denied", "attempts": 1, "max_attempts": 1}
        code, result = self.record(record)
        self.assertEqual((code, result["decision"]), (0, "record_consistent"))

    def test_unknown_percentage_is_not_zero(self):
        record = self.example()
        record["metrics"][0].update(numerator=None, denominator=None, percentage=None)
        code, result = self.record(record)
        self.assertEqual((code, result["decision"]), (0, "record_consistent"))

    def test_disjoint_writer_paths_are_accepted(self):
        record = self.example()
        record["writers"] = [{"owner": "worker", "paths": ["src/parser"]}, {"owner": "helper", "paths": ["tests/parser"]}]
        code, result = self.record(record)
        self.assertEqual((code, result["decision"]), (0, "record_consistent"))

    def test_checkpoint_boundary_timezone_and_future(self):
        code, result = self.command("checkpoint", "--previous", "2026-01-01T07:00:00-05:00", "--current", "2026-01-01T12:15:00Z", "--last-progress", "2026-01-01T12:01:00Z")
        self.assertEqual(code, 0)
        self.assertEqual((result["elapsed_minutes"], result["progress_age_minutes"], result["due"], result["stale"]), (15, 14, True, False))
        code, result = self.command("checkpoint", "--previous", "2026-01-01T12:00:00Z", "--current", "2026-01-01T12:15:00Z", "--last-progress", "2026-01-01T12:00:00Z")
        self.assertEqual((result["stale"], result["next_step"]), (True, "inspect_changed_evidence"))
        for prior in ("2026-01-01T12:16:00Z", "2026-01-01T12:00:00"):
            code, result = self.command("checkpoint", "--previous", prior, "--current", "2026-01-01T12:15:00Z", "--last-progress", "2026-01-01T12:00:00Z")
            self.assertEqual((code, result["errors"][0]["code"]), (2, "INVALID_INPUT"))

    def test_invalid_schema_path_and_future_observation(self):
        for update in ({"schema_version": 8}, {"acceptance": []}, {"next_action": {"kind": "edit", "paths": ["../escape"]}}, {"owner": ""}):
            record = self.example()
            record.update(update)
            code, result = self.record(record)
            self.assertEqual((code, result["errors"][0]["code"]), (2, "INVALID_INPUT"))
        code, result = self.record(self.example(), "2026-01-01T12:00:00Z")
        self.assertEqual((code, result["errors"][0]["code"]), (2, "INVALID_INPUT"))

    def test_string_authority_is_not_a_boolean_grant(self):
        record = self.example()
        record["next_action"] = {"kind": "retry", "paths": []}
        record["operation"] = {"id": "fixture:op", "status": "failed", "attempts": 0,
                               "max_attempts": 1, "retry_authorized": "false"}
        code, result = self.record(record)
        self.assertEqual((code, result["errors"][0]["code"]), (2, "INVALID_INPUT"))

    def test_changed_manifest_invalidates_review_even_with_same_revision_label(self):
        record = self.example()
        record["evidence"][1]["manifest"]["diagram"] = "f" * 64
        code, result = self.record(record)
        self.assertEqual(code, 1)
        self.assertIn("CHANGED_REVISION_REVIEW", [e["code"] for e in result["errors"]])

    def test_missing_acceptance_evidence_and_false_test_claim(self):
        for change in ("missing", "failed"):
            record = self.example()
            if change == "missing":
                record["acceptance"][0]["evidence_ids"] = ["nonexistent"]
            else:
                record["evidence"][0]["status"] = "failed"
            code, result = self.record(record)
            self.assertEqual(code, 1)
            self.assertIn("ACCEPTANCE_UNSUPPORTED", [e["code"] for e in result["errors"]])

    def test_real_git_reconciliation_and_preservation(self):
        with tempfile.TemporaryDirectory(prefix="rstack-git-") as d:
            root = Path(d)
            def git(*args):
                return subprocess.check_output(["git", "-C", d, *args], stderr=subprocess.STDOUT).decode().strip()
            git("init", "-b", "main")
            git("config", "user.name", "Synthetic Fixture")
            git("config", "user.email", "fixture@example.invalid")
            (root / "feature.txt").write_text("base\n")
            git("add", "feature.txt")
            git("-c", "core.hooksPath=/dev/null", "commit", "-m", "base")
            base = git("rev-parse", "HEAD")
            git("checkout", "-b", "feature")
            (root / "feature.txt").write_text("base\nuseful feature\n")
            git("add", "feature.txt")
            git("-c", "core.hooksPath=/dev/null", "commit", "-m", "feature")
            candidate = git("rev-parse", "HEAD")
            git("checkout", "-b", "existing-pr", base)
            (root / "unrelated.txt").write_text("independent\n")
            git("add", "unrelated.txt")
            git("-c", "core.hooksPath=/dev/null", "commit", "-m", "independent")
            git("-c", "core.hooksPath=/dev/null", "cherry-pick", candidate)
            target = git("rev-parse", "HEAD")
            self.assertNotEqual(candidate, target)
            (root / "preserve.txt").write_text("owned unfinished work\n")
            before = git("status", "--porcelain=v1")
            code, result = self.command("reconcile", "--repo", d, "--candidate", candidate, "--target", target, "--paths", "feature.txt")
            self.assertEqual(code, 0)
            self.assertEqual(result["decision"], "same_selected_files")
            self.assertEqual(result["ancestor"], False)
            self.assertEqual(result["patch_matches"], [target])
            self.assertEqual(git("status", "--porcelain=v1"), before)
            self.assertEqual((root / "preserve.txt").read_text(), "owned unfinished work\n")
            (root / "feature.txt").write_text("base\nuseful feature\nnewer change\n")
            git("add", "feature.txt")
            git("-c", "core.hooksPath=/dev/null", "commit", "-m", "later modification")
            code, result = self.command("reconcile", "--repo", d, "--candidate", candidate, "--target", "HEAD", "--paths", "feature.txt")
            self.assertEqual((code, result["decision"]), (0, "equivalent_patch"))
            self.assertEqual(result["selected_files_equal"], False)
            code, result = self.command("reconcile", "--repo", d, "--candidate", base, "--target", "HEAD", "--paths", "feature.txt")
            self.assertEqual((code, result["decision"]), (0, "already_ancestor"))
            code, result = self.command("reconcile", "--repo", d, "--candidate", candidate, "--target", base, "--paths", "feature.txt")
            self.assertEqual((code, result["decision"]), (0, "delta_review_required"))
            code, result = self.command("reconcile", "--repo", d, "--candidate", candidate, "--target", target, "--paths", "missing.txt")
            self.assertEqual((code, result["errors"][0]["code"]), (2, "INVALID_INPUT"))


if __name__ == "__main__":
    unittest.main()
