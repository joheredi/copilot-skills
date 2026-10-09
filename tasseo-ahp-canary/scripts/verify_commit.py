"""Credential-free oracle for exported native Canary commitment evidence."""

import argparse
import datetime as dt
import json
import pathlib
import re
import sys


class VerificationError(ValueError):
    """The supplied evidence cannot establish a complete committed snapshot."""


def instant(value):
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z", value
    ):
        raise VerificationError(f"Invalid UTC timestamp: {value!r}")
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise VerificationError(f"Invalid UTC calendar timestamp: {value!r}") from error


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def rows(payload):
    if isinstance(payload, list):
        result = payload
    elif isinstance(payload, dict) and isinstance(payload.get("rows"), list):
        require(not payload.get("nextCursor"), "Incomplete observation page: follow nextCursor")
        result = payload["rows"]
    else:
        raise VerificationError("Expected an observation array or complete {rows, nextCursor} export")
    require(all(isinstance(row, dict) for row in result), "Observation rows must be objects")
    return result


def flatten(row):
    if "values" not in row:
        return dict(row)
    require(isinstance(row["values"], dict) and isinstance(row.get("series"), dict),
            "Native observation requires series and values objects")
    return {
        **row["series"], **row["values"],
        "measure": row.get("measure"),
        "observation_id": row.get("observationId"),
        "content_hash": row.get("contentHash"),
        "effective_at": row.get("effectiveAt"),
        "recorded_at": row.get("recordedAt"),
    }


def same_measure(value, binding):
    return value in (binding["id"], binding["slug"])


def identity(row):
    require(isinstance(row.get("observation_id"), str) and bool(row["observation_id"]),
            "Missing native observation identity")
    require(isinstance(row.get("content_hash"), str) and bool(row["content_hash"]),
            "Missing native observation content hash")


def committed_snapshot(frame_payload, receipt_payload, bindings):
    contract = bindings["contract"]
    report_id = bindings["report"]["id"]
    receipts = [
        flatten(row) for row in rows(receipt_payload)
        if same_measure(row.get("measure"), bindings["measures"]["publication_status"])
    ]
    receipts = [row for row in receipts
                if row.get("report_id") == report_id and row.get("publication_status") == "published"]
    require(bool(receipts), "No successful receipt for the target reader")
    for receipt in receipts:
        identity(receipt)
        require(receipt.get("comparison_basis") == contract["comparison_basis"],
                "Receipt comparison basis mismatch")
        require(receipt.get("clock_methodology") == contract["clock_methodology"],
                "Receipt clock methodology mismatch")
        require(receipt.get("effective_at") == contract["gauge_address"],
                "Receipt gauge address mismatch")
        instant(receipt.get("computed_at"))
        instant(receipt.get("recorded_at"))
        cycle = instant(receipt.get("cycle_end"))
        require(cycle.hour == cycle.minute == cycle.second == cycle.microsecond == 0,
                "Receipt cycle end is not UTC midnight")
        require(receipt.get("active_cycle") == f"execution-{cycle.date().isoformat()}-UTC",
                "Receipt cycle identity mismatch")
        require(receipt.get("comparison_count") == contract["expected_frames"],
                "Receipt comparison count mismatch")
        require(receipt.get("daily_count") == contract["expected_history_slots"],
                "Receipt history-slot count mismatch")
    receipts.sort(key=lambda row: (instant(row["cycle_end"]), instant(row["recorded_at"])),
                  reverse=True)
    receipt = receipts[0]
    ties = [row for row in receipts
            if row["cycle_end"] == receipt["cycle_end"] and row["recorded_at"] == receipt["recorded_at"]]
    require(len(ties) == 1, "Ambiguous successful publication receipt")
    cutoff = instant(receipt["recorded_at"])
    selected, revisions = {}, {}
    for source in rows(frame_payload):
        frame = flatten(source)
        if not same_measure(frame.get("measure"), bindings["measures"]["frames"]):
            continue
        if (frame.get("cycle_id"), frame.get("cycle_end"), frame.get("computed_at")) != (
            receipt["active_cycle"], receipt["cycle_end"], receipt["computed_at"]
        ):
            continue
        recorded = instant(frame.get("recorded_at"))
        if recorded > cutoff:
            continue
        identity(frame)
        require(frame.get("harness") == contract["harness"], "Frame harness mismatch")
        require(frame.get("view_kind") == "current", "Frame is not a retained current revision")
        require(frame.get("comparison_basis") == contract["comparison_basis"],
                "Frame comparison basis mismatch")
        require(frame.get("clock_methodology") == contract["clock_methodology"],
                "Frame clock methodology mismatch")
        require(frame.get("effective_at") == contract["gauge_address"], "Frame gauge address mismatch")
        cell = frame.get("model_name"), frame.get("case_name"), frame.get("cadence")
        revision = cell, recorded
        fingerprint = frame["observation_id"], frame["content_hash"]
        require(revision not in revisions or revisions[revision] == fingerprint,
                f"Ambiguous same-time Frame revision: {cell}")
        revisions[revision] = fingerprint
        if cell not in selected or recorded > instant(selected[cell]["recorded_at"]):
            selected[cell] = frame
    expected = {(model, case, cadence) for model in contract["models"]
                for case in contract["scenarios"] for cadence in contract["cadences"]}
    require(len(expected) == contract["expected_frames"], "Bindings contain an inconsistent cell grid")
    require(set(selected) == expected,
            f"Committed grid mismatch: {len(expected - set(selected))} missing, "
            f"{len(set(selected) - expected)} unexpected cells")
    require(len({row["observation_id"] for row in selected.values()}) == len(expected),
            "Native observation identity reused across cells")
    return receipt, [selected[key] for key in sorted(selected)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frames", type=pathlib.Path, required=True)
    parser.add_argument("--receipts", type=pathlib.Path, required=True)
    parser.add_argument("--bindings", type=pathlib.Path,
                        default=pathlib.Path(__file__).resolve().parents[1] / "references/resource-map.json")
    args = parser.parse_args()
    try:
        receipt, selected = committed_snapshot(
            json.loads(args.frames.read_text()), json.loads(args.receipts.read_text()),
            json.loads(args.bindings.read_text()),
        )
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"status": "error", "error": str(error)}), file=sys.stderr)
        return 1
    print(json.dumps({
        "status": "ok", "scope": "commit identity and membership, not statistics or publication health",
        "cycle_end": receipt["cycle_end"], "computed_at": receipt["computed_at"],
        "committed_at": receipt["recorded_at"], "frames": len(selected),
        "observation_ids": [row["observation_id"] for row in selected],
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
