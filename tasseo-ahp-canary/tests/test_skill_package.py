import json
import pathlib
import re
import unittest
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
CASES = json.loads((ROOT / "evals/cases.json").read_text())
BINDINGS = json.loads((ROOT / "references/resource-map.json").read_text())
SCENARIOS = json.loads((ROOT / "evals/fixtures/native-alerts.json").read_text())["scenarios"]


class PackageTests(unittest.TestCase):
    def test_relative_markdown_links_resolve(self):
        for path in ROOT.rglob("*.md"):
            for target in re.findall(r"\[[^\]]+\]\(([^)\s]+)\)", path.read_text()):
                if target.startswith(("https://", "http://", "#")):
                    continue
                with self.subTest(path=path.relative_to(ROOT), target=target):
                    self.assertTrue((path.parent / target.split("#", 1)[0]).exists())

    def test_resource_grid_is_consistent(self):
        contract = BINDINGS["contract"]
        cells = len(contract["models"]) * len(contract["scenarios"])
        self.assertEqual(contract["expected_frames"], cells * len(contract["cadences"]))
        self.assertEqual(contract["expected_history_slots"], cells * contract["history_days"])
        self.assertEqual(len(contract["models"]), len(set(contract["models"])))

    def test_policy_bindings_and_source_labels_are_distinct(self):
        policies = BINDINGS["policies"]
        self.assertNotEqual(policies["dated_comparisons"]["id"], policies["retired_signal"]["id"])
        self.assertIn("Retired", policies["retired_signal"]["role"])
        labels = BINDINGS["source_labels"]
        self.assertNotEqual(labels["current_frames"], labels["dated_policy_frames"])

    def test_cases_have_unique_ids_and_explicit_criteria(self):
        ids = [case["id"] for case in CASES["cases"]]
        self.assertEqual(len(ids), len(set(ids)))
        for case in CASES["cases"]:
            with self.subTest(case=case["id"]):
                for key in ("prompt", "setup", "must", "must_not"):
                    self.assertTrue(case[key])

    def test_all_scenarios_have_case_locators(self):
        covered = set()
        for case in CASES["cases"]:
            locator = case.get("fixture")
            if locator is None:
                continue
            path = ROOT / "evals" / locator["path"]
            scenarios = json.loads(path.read_text())["scenarios"]
            self.assertIn(locator["scenario"], scenarios)
            covered.add(locator["scenario"])
        self.assertEqual(covered, set(SCENARIOS))

    def test_release_blockers_cover_native_alert_authority(self):
        self.assertIn("fabricated_alert_identity", CASES["release_blockers"])
        self.assertIn("unauthorized_issue_delivery", CASES["release_blockers"])


class NativeFixtureTests(unittest.TestCase):
    def test_backfill_and_live_contexts_are_distinct(self):
        historical = SCENARIOS["historical-backfill"]
        live = SCENARIOS["newer-detector-evidence"]
        self.assertEqual(historical["publication_origin"], "backfill")
        self.assertEqual(historical["evaluation"]["state"], "violating")
        self.assertEqual(historical["live_occurrences"], [])
        self.assertEqual(live["publication_origin"], "live")
        self.assertTrue(live["live_occurrence"]["id"])
        self.assertLess(live["reader"]["cycle_end"], live["dated_frame"]["cycle_end"])
        self.assertIsNone(live["candidate_publication"]["artifact"])

    def test_source_context_has_equal_facts_with_different_technical_views(self):
        current, dated = SCENARIOS["source-label-contamination"]["acquisitions"]
        self.assertNotEqual(current["label"], dated["label"])
        left, right = current["rows"][0], dated["rows"][0]
        self.assertEqual(left["values"], right["values"])
        self.assertEqual(left["computation_id"], right["computation_id"])
        self.assertNotEqual(left["view_kind"], right["view_kind"])
        self.assertNotEqual(left["observation_id"], right["observation_id"])
        self.assertNotEqual(left["effective_at"], right["effective_at"])

    def test_mismatch_context_differs_in_business_facts(self):
        mismatch = SCENARIOS["business-field-mismatch"]
        self.assertEqual(mismatch["current"]["computation_id"], mismatch["dated"]["computation_id"])
        self.assertNotEqual(mismatch["current"]["values"], mismatch["dated"]["values"])

    def test_retry_context_keeps_one_occurrence_and_an_uncertain_external_outcome(self):
        retry = SCENARIOS["continuous-violation-retry"]
        occurrences = {row["occurrence_id"] for row in retry["evaluations"]}
        self.assertEqual(len(occurrences), 1)
        self.assertEqual(retry["delivery"]["external_creation_outcome"], "unknown after timeout")
        self.assertIsNone(retry["delivery"]["persisted_issue_url"])
        self.assertIn(retry["delivery"]["candidate_issue_marker"], occurrences)
        self.assertIn(".invalid/", retry["delivery"]["candidate_issue_url"])

    def test_closure_context_discriminates_effective_from_recorded_time(self):
        closure = SCENARIOS["closure-realert"]

        def timestamp(value):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))

        closed_at = timestamp(closure["old_occurrence"]["github_closed_at"])
        self.assertLess(timestamp(closure["old_evidence"]["effective_at"]), closed_at)
        self.assertGreater(timestamp(closure["old_evidence"]["recorded_at"]), closed_at)
        self.assertGreater(timestamp(closure["new_evidence"]["effective_at"]), closed_at)
        self.assertFalse(closure["policy"]["autoRecover"])

    def test_grouping_context_does_not_establish_shared_cause_or_authority(self):
        grouping = SCENARIOS["grouping-request"]
        self.assertNotEqual(grouping["occurrences"][0]["series"], grouping["occurrences"][1]["series"])
        self.assertEqual(grouping["shared_root_cause"], "unknown")
        self.assertFalse(grouping["approved_native_group_lifecycle"])

    def test_trace_export_context_has_no_completion_callback(self):
        integration = SCENARIOS["trace-export-only"]
        self.assertTrue(integration["producer"]["otel_tasseo_enabled"])
        self.assertIsNone(integration["producer"]["tasseo_automation_url"])
        self.assertNotIn("runIds", integration["receiver"]["accepted_inputs"])
        self.assertEqual(integration["possible_callback_mode"]["completion_unit"], "one evaluation issue")

    def test_compiler_context_does_not_authorize_platform_writes(self):
        compiler = SCENARIOS["temporal-compiler"]
        self.assertIn("@measure/runtime", compiler["diagnostic"])
        self.assertFalse(compiler["minimal_constant_policy_reads_temporal_field"])
        self.assertTrue(compiler["minimal_constant_policy_has_same_diagnostic"])
        self.assertFalse(compiler["platform_change_authorized"])


if __name__ == "__main__":
    unittest.main()
