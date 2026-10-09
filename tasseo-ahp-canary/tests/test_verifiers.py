import copy
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from verify_commit import VerificationError, committed_snapshot  # noqa: E402
from verify_snapshot import compare  # noqa: E402

FIXTURE = json.loads((ROOT / "evals/fixtures/synthetic.json").read_text())


def frames(label):
    contract, cycle = FIXTURE["contract"], FIXTURE["cycles"][label]
    result = []
    for model in contract["models"]:
        for case in contract["scenarios"]:
            for cadence in contract["cadences"]:
                identity = f"{label}-{model}-{case}-{cadence}"
                result.append({
                    "measure": "synthetic.frames", "observationId": identity, "contentHash": f"hash-{identity}",
                    "effectiveAt": contract["gauge_address"], "recordedAt": cycle["frame_written"],
                    "series": {"harness": contract["harness"], "model_name": model, "case_name": case,
                               "cadence": cadence, "view_kind": "current",
                               "comparison_basis": contract["comparison_basis"],
                               "clock_methodology": contract["clock_methodology"]},
                    "values": {"cycle_id": f"execution-{cycle['end'][:10]}-UTC",
                               "cycle_end": cycle["end"], "computed_at": cycle["point"]},
                })
    return result


def receipt(label, report_id="synthetic-reader"):
    contract, cycle = FIXTURE["contract"], FIXTURE["cycles"][label]
    return {
        "measure": "synthetic.receipts", "observationId": f"receipt-{label}-{report_id}",
        "contentHash": f"receipt-hash-{label}", "effectiveAt": contract["gauge_address"],
        "recordedAt": cycle["receipt_written"],
        "series": {"report_id": report_id, "comparison_basis": contract["comparison_basis"],
                   "clock_methodology": contract["clock_methodology"]},
        "values": {"publication_status": "published", "cycle_end": cycle["end"],
                   "active_cycle": f"execution-{cycle['end'][:10]}-UTC", "computed_at": cycle["point"],
                   "comparison_count": contract["expected_frames"],
                   "daily_count": contract["expected_history_slots"]},
    }


def channel(values):
    return {"kind": "column", "values": values}


def comparison(model, case, cadence):
    facts = {
        "model_name": model, "case_name": case, "cadence": cadence,
        "current_median": 12, "baseline_median": 10, "ciLow": 11, "ciHigh": 13,
        "tolLow": 9, "tolHigh": 11, "n_current": 60, "n_baseline": 720,
        "delta_tokens": 2, "delta_pct": 20, "ci_95_lo": 1, "ci_95_hi": 3,
        "ci_95_width": 2, "relative_ci_95_width": 20, "spread_ratio": 1,
        "verdict": "watch", "verdict_reason": "synthetic", "provisional": False,
        "freshness_hours": 1, "observation_id": "synthetic-current-id", "content_hash": "synthetic-hash",
    }
    return {"kind": "plot", "height": 38,
            "scales": [{"id": "x", "type": "linear", "domain": [0, 1]},
                       {"id": "y", "type": "linear", "domain": [0, 2]}],
            "marks": [
                {"prim": "rule", "channels": {"x": channel([0.2]), "y0": channel([0]), "y1": channel([2])}},
                {"prim": "rule", "channels": {"x": channel([0.8]), "y0": channel([0]), "y1": channel([2])}},
                {"prim": "dot", "channels": {"x": channel([0.6]), "y": channel([1])},
                 "tooltip": {"rows": [{"label": key, "values": [value]} for key, value in facts.items()]}},
            ]}


def history():
    xs = channel(["01-01", "01-02"])
    ys = channel([10, 12])
    return {
        "kind": "plot", "height": 125,
        "scales": [{"id": "x", "type": "band", "domain": ["01-01", "01-02"]},
                   {"id": "y", "type": "linear", "domain": [7, 16]}],
        "marks": [
            {"prim": "rule", "channels": {"x": xs, "y0": channel([8, 9]), "y1": channel([14, 15])}},
            {"prim": "line", "channels": {"x": xs, "y": ys}},
            {"prim": "dot", "channels": {"x": xs, "y": ys}, "tooltip": {"rows": [
                {"label": "Samples", "values": [60, 60]}, {"label": "Median", "values": [10, 12]},
                {"label": "P25", "values": [8, 9]}, {"label": "P75", "values": [14, 15]},
                {"label": "Run", "values": ["synthetic-run-1", "synthetic-run-2"]},
            ]}},
        ],
    }


def snapshot():
    cards = []
    for model in FIXTURE["contract"]["models"]:
        items = [{"kind": "markdown", "markdown":
                  f'<h2 class="canary-model-heading" data-verdict="WATCH">{model}</h2>'}]
        items.extend(comparison(model, case, cadence) for case in FIXTURE["contract"]["scenarios"]
                     for cadence in FIXTURE["contract"]["cadences"])
        items.extend([history(), history()])
        cards.append({"kind": "layout", "items": items})
    data = [{"kind": "markdown", "markdown": "**Published cycle 2030-01-01T00:00:00.000Z**"}, *cards]
    return {"published_result": {"status": "ok", "data": data},
            "result": {"status": "ok", "payload": copy.deepcopy(data)}}


class CommitTests(unittest.TestCase):
    def test_failed_rollover_retains_old_commit(self):
        failed = receipt("next", "synthetic-reader:failure")
        failed["values"]["publication_status"] = "failed"
        commit, selected = committed_snapshot(frames("old") + frames("next"),
                                             [receipt("old"), failed], FIXTURE)
        self.assertEqual(commit["cycle_end"], FIXTURE["cycles"]["old"]["end"])
        self.assertEqual({row["observation_id"] for row in selected},
                         {row["observationId"] for row in frames("old")})

    def test_next_success_advances_commit(self):
        commit, selected = committed_snapshot(frames("old") + frames("next"),
                                             [receipt("old"), receipt("next")], FIXTURE)
        self.assertEqual(commit["cycle_end"], FIXTURE["cycles"]["next"]["end"])
        self.assertEqual(len(selected), 8)

    def test_other_report_cannot_select_cycle(self):
        commit, _ = committed_snapshot(frames("old") + frames("next"),
                                      [receipt("old"), receipt("next", "other-report")], FIXTURE)
        self.assertEqual(commit["cycle_end"], FIXTURE["cycles"]["old"]["end"])

    def test_later_same_point_revisions_excluded(self):
        later = frames("old")
        later[0]["recordedAt"] = "2030-01-01T22:00:00.000Z"
        later[0]["observationId"] = "later-id"
        _, selected = committed_snapshot(frames("old") + later[:1], [receipt("old")], FIXTURE)
        self.assertNotIn("later-id", {row["observation_id"] for row in selected})

    def test_latest_revision_before_commit_selected(self):
        revision = frames("old")[0]
        revision["recordedAt"] = "2030-01-01T21:05:00.000Z"
        revision["observationId"] = "before-commit"
        _, selected = committed_snapshot(frames("old") + [revision], [receipt("old")], FIXTURE)
        self.assertIn("before-commit", {row["observation_id"] for row in selected})

    def test_incomplete_grid_rejected(self):
        with self.assertRaisesRegex(VerificationError, "grid mismatch"):
            committed_snapshot(frames("old")[1:], [receipt("old")], FIXTURE)

    def test_extra_cell_rejected(self):
        unexpected = frames("old")[0]
        unexpected["series"]["model_name"] = "unexpected-model"
        with self.assertRaisesRegex(VerificationError, "grid mismatch"):
            committed_snapshot(frames("old") + [unexpected], [receipt("old")], FIXTURE)

    def test_conflicting_revision_rejected(self):
        conflict = frames("old")[0]
        conflict["contentHash"] = "conflicting-hash"
        with self.assertRaisesRegex(VerificationError, "Ambiguous same-time"):
            committed_snapshot(frames("old") + [conflict], [receipt("old")], FIXTURE)

    def test_ambiguous_receipt_rejected(self):
        with self.assertRaisesRegex(VerificationError, "Ambiguous successful"):
            committed_snapshot(frames("old"), [receipt("old"), receipt("old")], FIXTURE)

    def test_missing_success_rejected(self):
        with self.assertRaisesRegex(VerificationError, "No successful"):
            committed_snapshot(frames("old"), [receipt("next", "other-report")], FIXTURE)

    def test_cursor_rejected(self):
        with self.assertRaisesRegex(VerificationError, "Incomplete observation page"):
            committed_snapshot({"rows": frames("old"), "nextCursor": "next"}, [receipt("old")], FIXTURE)

    def test_bad_calendar_timestamp_rejected(self):
        invalid = receipt("old")
        invalid["recordedAt"] = "2030-02-30T00:00:00.000Z"
        with self.assertRaisesRegex(VerificationError, "calendar timestamp"):
            committed_snapshot(frames("old"), [invalid], FIXTURE)

    def test_bad_frame_identity_rejected(self):
        invalid = frames("old")
        invalid[0]["contentHash"] = None
        with self.assertRaisesRegex(VerificationError, "content hash"):
            committed_snapshot(invalid, [receipt("old")], FIXTURE)

    def test_wrong_method_rejected(self):
        invalid = frames("old")
        invalid[0]["series"]["clock_methodology"] = "wrong"
        with self.assertRaisesRegex(VerificationError, "methodology mismatch"):
            committed_snapshot(invalid, [receipt("old")], FIXTURE)

    def test_cli_runs_from_other_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            base = pathlib.Path(folder)
            for name, data in (("frames", frames("old")), ("receipts", [receipt("old")]), ("bindings", FIXTURE)):
                (base / f"{name}.json").write_text(json.dumps(data))
            completed = subprocess.run(
                [sys.executable, str(ROOT / "scripts/verify_commit.py"),
                 "--frames", str(base / "frames.json"), "--receipts", str(base / "receipts.json"),
                 "--bindings", str(base / "bindings.json")],
                cwd=base, capture_output=True, text=True, check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(json.loads(completed.stdout)["frames"], 8)


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.baseline = snapshot()
        self.candidate = copy.deepcopy(self.baseline)

    def test_same_snapshot(self):
        self.assertEqual(compare(self.baseline, self.candidate)["comparisons"], 8)

    def test_visual_changes_allowed(self):
        for card in self.candidate["published_result"]["data"][1:]:
            for plot in card["items"][1:]:
                plot["height"] += 10
                plot["marks"][0]["channels"]["strokeOpacity"] = {"kind": "const", "value": 0.8}
        self.assertEqual(compare(self.baseline, self.candidate)["populated_histories"], 4)

    def test_observation_identity_difference_allowed(self):
        rows = self.candidate["published_result"]["data"][1]["items"][1]["marks"][2]["tooltip"]["rows"]
        next(row for row in rows if row["label"] == "observation_id")["values"] = ["dated-view-id"]
        self.assertEqual(compare(self.baseline, self.candidate)["status"], "ok")

    def test_statistical_change_rejected(self):
        rows = self.candidate["published_result"]["data"][1]["items"][1]["marks"][2]["tooltip"]["rows"]
        next(row for row in rows if row["label"] == "current_median")["values"] = [999]
        with self.assertRaisesRegex(VerificationError, "Business values"):
            compare(self.baseline, self.candidate)

    def test_domain_change_rejected(self):
        self.candidate["published_result"]["data"][1]["items"][-1]["scales"][1]["domain"] = [0, 100]
        with self.assertRaisesRegex(VerificationError, "scale domain"):
            compare(self.baseline, self.candidate)

    def test_percentile_change_rejected(self):
        self.candidate["published_result"]["data"][1]["items"][-1]["marks"][0]["channels"]["y1"] = channel([20, 21])
        with self.assertRaisesRegex(VerificationError, "Business values"):
            compare(self.baseline, self.candidate)

    def test_history_line_removed_rejected(self):
        self.candidate["published_result"]["data"][1]["items"][-1]["marks"].pop(1)
        with self.assertRaisesRegex(VerificationError, "connecting line"):
            compare(self.baseline, self.candidate)

    def test_status_change_rejected(self):
        self.candidate["published_result"]["data"][1]["items"][0]["markdown"] = (
            '<h2 class="canary-model-heading" data-verdict="OK">synthetic-model-a</h2>')
        with self.assertRaisesRegex(VerificationError, "status/card"):
            compare(self.baseline, self.candidate)

    def test_cross_cycle_rejected(self):
        self.candidate["published_result"]["data"][0]["markdown"] = (
            "**Published cycle 2030-01-02T00:00:00.000Z**")
        with self.assertRaisesRegex(VerificationError, "Cross-cycle"):
            compare(self.baseline, self.candidate)

    def test_inline_error_rejected(self):
        self.candidate["published_result"]["data"].append({"kind": "error", "message": "output error"})
        with self.assertRaisesRegex(VerificationError, "Inline output error"):
            compare(self.baseline, self.candidate)

    def test_preview_is_explicit(self):
        del self.candidate["published_result"]
        with self.assertRaisesRegex(VerificationError, "published_result"):
            compare(self.baseline, self.candidate)
        self.assertEqual(compare(self.baseline, self.candidate, "effective")["view"], "effective")

    def test_failed_publication_rejected(self):
        self.candidate["published_result"]["status"] = "error"
        with self.assertRaisesRegex(VerificationError, "Published block"):
            compare(self.baseline, self.candidate)

    def test_malformed_mark_rejected(self):
        self.candidate["published_result"]["data"][1]["items"][1]["marks"].append(None)
        with self.assertRaisesRegex(VerificationError, "Malformed plot mark"):
            compare(self.baseline, self.candidate)

    def test_snapshot_cli_runs_from_other_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            base = pathlib.Path(folder)
            (base / "baseline.json").write_text(json.dumps(self.baseline))
            (base / "candidate.json").write_text(json.dumps(self.candidate))
            completed = subprocess.run(
                [sys.executable, str(ROOT / "scripts/verify_snapshot.py"),
                 "--baseline", str(base / "baseline.json"), "--candidate", str(base / "candidate.json")],
                cwd=base, capture_output=True, text=True, check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(json.loads(completed.stdout)["view"], "published")


if __name__ == "__main__":
    unittest.main()
