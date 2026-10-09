"""Compare same-cycle exported Canary chart facts without credentials or writes."""

import argparse
import json
import pathlib
import re
import sys

from verify_commit import VerificationError, require


def views(payload, view):
    if not isinstance(payload, dict):
        raise VerificationError("Expected a report_read_block envelope, not an unlabelled view array")
    if view == "published":
        result = payload.get("published_result")
        require(isinstance(result, dict), "Missing explicit published_result")
        require(result.get("status") == "ok" and not result.get("error"), "Published block has an error")
        value = result.get("data")
    else:
        result = payload.get("result")
        require(isinstance(result, dict), "Missing effective result cache")
        require(result.get("status") == "ok" and not result.get("error"), "Effective block has an error")
        value = result.get("payload")
    require(isinstance(value, list), "Result has no view array")
    return value


def walk(value):
    if isinstance(value, list):
        for item in value:
            yield from walk(item)
    elif isinstance(value, dict):
        yield value
        if value.get("kind") == "aligned":
            yield from walk(value.get("item"))
        elif value.get("kind") == "layout":
            yield from walk(value.get("items", []))


def markdown(data):
    return "\n".join(item["markdown"] for item in walk(data)
                     if item.get("kind") == "markdown" and isinstance(item.get("markdown"), str))


def cycle(data):
    matches = set(re.findall(r"(?:Published|Candidate) cycle (\d{4}-\d{2}-\d{2}T00:00:00\.000Z)",
                             markdown(data)))
    require(len(matches) == 1, "Cannot establish exactly one snapshot cycle")
    return matches.pop()


def semantic_marks(plot):
    result = {}
    require(isinstance(plot.get("marks"), list), "Plot marks must be an array")
    require(all(isinstance(mark, dict) for mark in plot["marks"]), "Malformed plot mark")
    for mark in plot["marks"]:
        tooltip = mark.get("tooltip")
        if tooltip is not None:
            require(isinstance(tooltip, dict) and isinstance(tooltip.get("rows", []), list),
                    "Malformed mark tooltip")
            require(all(isinstance(row, dict) for row in tooltip.get("rows", [])),
                    "Malformed tooltip row")
    comparison_plot = any(
        mark.get("prim") == "dot" and any(row.get("label") == "cadence"
                                        for row in (mark.get("tooltip") or {}).get("rows", []))
        for mark in plot.get("marks", [])
    )
    for mark in plot.get("marks", []):
        require(isinstance(mark, dict), "Malformed plot mark")
        if mark.get("prim") == "dot":
            tooltip = mark.get("tooltip")
            require(isinstance(tooltip, dict) and isinstance(tooltip.get("rows"), list),
                    "Median mark is missing tooltip evidence")
            labels = {row["label"]: row.get("values") for row in tooltip["rows"]}
            if "cadence" in labels:
                relevant = ("model_name", "case_name", "cadence", "current_median", "baseline_median",
                            "ciLow", "ciHigh", "tolLow", "tolHigh", "n_current", "n_baseline",
                            "delta_tokens", "delta_pct", "ci_95_lo", "ci_95_hi", "ci_95_width",
                            "relative_ci_95_width", "spread_ratio", "verdict", "verdict_reason",
                            "provisional", "freshness_hours")
                require(all(field in labels for field in relevant), "Comparison tooltip contract incomplete")
                require("comparison" not in result, "Duplicate comparison median mark")
                result["comparison"] = {field: labels[field] for field in relevant}
            elif all(field in labels for field in ("Samples", "Median", "P25", "P75", "Run")):
                require("history" not in result, "Duplicate history median mark")
                channels = mark.get("channels", {})
                require("x" in channels and "y" in channels, "History median channels missing")
                result["history"] = {
                    "tooltip": {field: labels[field] for field in ("Samples", "Median", "P25", "P75", "Run")},
                    "x": channels["x"], "y": channels["y"],
                }
        if not comparison_plot and mark.get("prim") == "rule" and all(
            field in mark.get("channels", {}) for field in ("x", "y0", "y1")
        ):
            require("quartiles" not in result, "Duplicate history percentile whisker mark")
            result["quartiles"] = {field: mark["channels"][field] for field in ("x", "y0", "y1")}
        if not comparison_plot and mark.get("prim") == "line" and all(
            field in mark.get("channels", {}) for field in ("x", "y")
        ):
            # Comparison hatching is decorative, not a history distribution.
            if not mark.get("decoration"):
                require("line" not in result, "Duplicate history connecting line")
                result["line"] = {field: mark["channels"][field] for field in ("x", "y")}
    return result


def summaries(data):
    result = {}
    statuses = {}
    for card in walk(data):
        if card.get("kind") != "layout" or not card.get("items"):
            continue
        first = card["items"][0]
        if not isinstance(first, dict) or first.get("kind") != "markdown":
            continue
        match = re.search(r'class="canary-model-heading"\s+data-verdict="([^"]+)">([^<]+)',
                          first.get("markdown", ""))
        if not match:
            continue
        status, model = match.groups()
        require(model not in statuses, "Duplicate model card")
        statuses[model] = status
        history_index = 0
        for plot in walk(card):
            if plot.get("kind") != "plot":
                continue
            marks = semantic_marks(plot)
            if "comparison" in marks:
                facts = marks["comparison"]
                require(all(isinstance(facts[field], list) and len(facts[field]) == 1
                            for field in ("model_name", "case_name", "cadence")), "Invalid comparison identity")
                require(facts["model_name"][0] == model, "Comparison placed in wrong model card")
                key = (model, facts["case_name"][0], facts["cadence"][0])
                facts = {"comparison": facts}
            else:
                require(all(part in marks for part in ("history", "quartiles", "line")),
                        "History is missing median, percentile whisker, or connecting line")
                key = (model, "history", history_index)
                history_index += 1
                facts = marks
            require(key not in result, f"Duplicate chart identity: {key}")
            require(isinstance(plot.get("scales"), list)
                    and all(isinstance(scale, dict) for scale in plot["scales"]), "Malformed plot scales")
            axes = {scale["id"]: {field: scale.get(field) for field in ("type", "domain")}
                    for scale in plot["scales"] if scale.get("id") in ("x", "y")}
            require(set(axes) == {"x", "y"} and all(scale["domain"] is not None for scale in axes.values()),
                    "Missing actual x/y scale domains")
            result[key] = {"facts": facts, "axes": axes}
    require(bool(result) and bool(statuses), "No Canary charts/model cards found")
    return statuses, result


def compare(baseline, candidate, view="published"):
    old_data = views(baseline, "published")
    new_data = views(candidate, view)
    require(cycle(old_data) == cycle(new_data), "Cross-cycle comparison is not presentation-only")
    require(not any(item.get("kind") == "error" for item in walk(old_data + new_data)),
            "Inline output error in snapshot")
    old_status, old = summaries(old_data)
    new_status, new = summaries(new_data)
    require(old_status == new_status, "Model status/card membership changed")
    require(old.keys() == new.keys(), "Comparison or populated-history membership changed")
    for key in old:
        require(old[key] == new[key], f"Business values, channels, or scale domain changed: {key}")
    return {"status": "ok", "view": view, "cycle": cycle(new_data), "models": len(new_status),
            "comparisons": sum(key[1] != "history" for key in new),
            "populated_histories": sum(key[1] == "history" for key in new),
            "scope": "same-cycle business values, statuses, and scale domains; not UI geometry or export health"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=pathlib.Path, required=True)
    parser.add_argument("--candidate", type=pathlib.Path, required=True)
    parser.add_argument("--view", choices=("published", "effective"), default="published")
    args = parser.parse_args()
    try:
        result = compare(json.loads(args.baseline.read_text()), json.loads(args.candidate.read_text()), args.view)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"status": "error", "error": str(error)}), file=sys.stderr)
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
