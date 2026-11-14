#!/usr/bin/env python3
"""
Reusable Harness Onboarding CLI for the Tasseo Daily Evaluation Report Pipeline.

Usage:
  1. Qualify & capture 32-day Kusto history + infer repeat expectations + register in harnesses.json:
     python3 onboard-harness.py --client CCA --agent "GitHub Copilot Cloud Agent" \
       --display-name "GitHub Copilot Cloud Agent" --team copilot-cca-evals --stage=qualify

  2. Prepare daily & 32-day cohort Measure batches (execute via execute_pinned_baseline_native):
     python3 onboard-harness.py --client CCA --stage=prepare-daily
     # -> execute_pinned_baseline_native(runDailyNov10_12) + execute_pinned_baseline_native(readDailyNov10_12)
     python3 onboard-harness.py --client CCA --stage=prepare-cohort
     # -> execute_pinned_baseline_native(runCohortNov10_12) + execute_pinned_baseline_native(readCohortNov10_12)
     python3 onboard-harness.py --client CCA --stage=prepare-comparisons
     # -> execute_pinned_baseline_native(runComparisonsNov10_12) + execute_pinned_baseline_native(readComparisonsNov10_12)
     python3 onboard-harness.py --client CCA --stage=prepare-assessments
     # -> execute_pinned_baseline_native(runAssessmentsNov10_12) + execute_pinned_baseline_native(readAssessmentsNov10_12)
"""

import argparse
import base64
import collections
import datetime as dt
import hashlib
import json
import math
import re
import subprocess
import sys
import uuid
from pathlib import Path

root = Path(__file__).resolve().parent
ext_path = root.parent.parent / "extensions" / "baseline-native-transport" / "extension.mjs"

sha = lambda data: hashlib.sha256(data).hexdigest()
canon = lambda value: re.sub(r"^.+?\.eval\.[^.]+\.(.+?)(?::[^:]+)?$", r"\1", value).lower()
read = lambda name: json.loads((root / name).read_text())


def update_extension_hash(manifest_hex):
    text = ext_path.read_text()
    updated = re.sub(
        r'const manifestHash = "[0-9a-f]{64}";',
        f'const manifestHash = "{manifest_hex}";',
        text,
        count=1,
    )
    ext_path.write_text(updated)


def run_kusto(stem, query):
    kql_file = root / f"{stem}.kql"
    json_file = root / f"{stem}.json"
    if json_file.exists():
        json_file.unlink()
    kql_file.write_text(query)
    proc = subprocess.run(
        [sys.executable, str(root / "baseline-source-query.py"), kql_file.name, json_file.name],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Kusto query {stem} failed: {proc.stderr.strip() or proc.stdout.strip()}")
    return json.loads(json_file.read_text())["rows"]


def recognized_mode(benchmark, raw):
    value = re.sub(r"[\s_-]", "", (raw or "").strip().lower())
    if value not in {"default", "autopilot", "plan", "planwithautopilot"}:
        return ""
    return "task-configured" if benchmark.startswith("copilotclibench") and value == "default" else value


def quantile(vals, p):
    if not vals:
        return None
    s = sorted(vals)
    at = (len(s) - 1) * p
    lo = int(math.floor(at))
    hi = int(math.ceil(at))
    return s[lo] + (s[hi] - s[lo]) * (at - lo)


def round1(v):
    return math.floor(v * 10 + 0.5) / 10 if v >= 0 else -math.floor(-v * 10 + 0.5) / 10


def make_sketch(vals, scale_digits=None):
    clean = [round(float(v), scale_digits) if scale_digits is not None else int(v) for v in vals if v is not None]
    clean.sort()
    n = len(clean)
    if n == 0:
        return {"n": 0, "sum": 0, "pts": []}, None
    idxs = sorted({
        int(math.floor((n - 1) * q)) for q in (0.5, 0.9, 0.95)
    } | {
        int(math.ceil((n - 1) * q)) for q in (0.5, 0.9, 0.95)
    })
    pts = [[idx, clean[idx]] for idx in idxs]
    total = round(sum(clean), scale_digits) if scale_digits is not None else int(sum(clean))
    at = (n - 1) * 0.5
    lo, hi = int(math.floor(at)), int(math.ceil(at))
    p50 = clean[lo] + (clean[hi] - clean[lo]) * (at - lo)
    return {"n": n, "sum": total, "pts": pts}, p50


def make_prior_center(vals, scale_digits=None):
    clean = [round(float(v), scale_digits) if scale_digits is not None else int(v) for v in vals if v is not None]
    clean.sort()
    n = len(clean)
    if n == 0:
        return None
    lo = max(0, (n - 1) // 2 - 1)
    hi = min(n, (n - 1) // 2 + 3)
    return {
        "totalCount": n,
        "belowCount": lo,
        "center": clean[lo:hi],
        "aboveCount": n - hi,
    }


def delta_encode_int(vals):
    s = sorted(int(round(v)) for v in vals)
    if not s:
        return []
    return [s[0]] + [s[i] - s[i - 1] for i in range(1, len(s))]


def stage_qualify(client, agent, display_name, owning_team, window_start, cutoff):
    disc_q = f"""let Cutoff=datetime({cutoff});
let Candidates=materialize(CESBenchmarkMetadataTable
| where EventTime >= datetime({window_start}) and EventTime <= Cutoff
| where Agent == "{agent}"
| where tostring(UserTags["run"])=="workflow-scheduled" and tostring(UserTags["branch"])=="main"
| distinct RunId);
let Visible=CESBenchmarkMetadataV2View
| where RunId in (Candidates)
| distinct RunId
| extend SourceViewEligible=true;
CESBenchmarkMetadataTable
| where RunId in (Candidates) and EventTime <= Cutoff
| project EventTime,RunId,Agent,Model,UserTags,SourceUserEligible=User startswith "76d3a380"
| summarize FirstMetadata=min(EventTime),arg_max(EventTime,Agent,Model,UserTags,SourceUserEligible) by RunId
| join kind=leftouter Visible on RunId
| where FirstMetadata >= datetime({window_start}) and FirstMetadata <= Cutoff
| extend RunBin=tostring(UserTags["run-bin"])
| extend SourceDay=iff(isnotempty(RunBin),substring(RunBin,0,10),format_datetime(FirstMetadata,"yyyy-MM-dd"))
| project RunId,Agent,Model,FirstMetadata,LatestMetadata=EventTime,SourceUserEligible,
    SourceViewEligible=coalesce(SourceViewEligible,false),
    RunTag=tostring(UserTags["run"]),Branch=tostring(UserTags["branch"]),
    Benchmark=tostring(UserTags["benchmark"]),RawTrack=tostring(UserTags["track"]),
    RawMode=tostring(UserTags["agent-mode"]),LegacyMode=tostring(UserTags["mode"]),
    Suite=tostring(UserTags["suite"]),Replica=tostring(UserTags["replica"]),
    RunBin,SourceDay,Version=tostring(UserTags["msbench.benchmark.version"]),
    DatasetHash=tostring(UserTags["msbench.benchmark.dataset_hash"])
| summarize Count=count(),RootRows=make_list(pack_all(),10000)
"""
    disc_rows = run_kusto(f"onboard-{client.lower()}-discovery", disc_q)
    all_roots = disc_rows[0]["RootRows"] if disc_rows and disc_rows[0]["RootRows"] else []
    eligible = [
        m for m in all_roots
        if m["SourceUserEligible"] and m["SourceViewEligible"]
        and m["RunTag"] == "workflow-scheduled" and m["Branch"] == "main"
        and m["Benchmark"]
    ]
    if not eligible:
        raise RuntimeError(f"No eligible scheduled main-branch runs found in Kusto for Agent='{agent}'")

    # Compute per-benchmark mode cutover timestamp (_cohort.kql rule)
    cutover_by_bench = {}
    for m in eligible:
        b = m["Benchmark"]
        if recognized_mode(b, m["RawMode"] or ""):
            ts = m["FirstMetadata"]
            if b not in cutover_by_bench or ts < cutover_by_bench[b]:
                cutover_by_bench[b] = ts

    candidates = []
    for meta in eligible:
        b = meta["Benchmark"]
        raw_m = (meta["RawMode"] or "").strip()
        direct = recognized_mode(b, raw_m)
        bridge = recognized_mode(b, meta["LegacyMode"] or "")
        cutover = cutover_by_bench.get(b)
        before_cutover = cutover is None or meta["FirstMetadata"] < cutover
        if direct:
            mode, status = direct, "agent-mode"
        elif not raw_m and bridge:
            mode, status = bridge, "legacy-mode-bridge"
        elif not raw_m and before_cutover:
            mode = "task-configured" if b.startswith("copilotclibench") else "default"
            status = "legacy-default"
        elif raw_m:
            mode, status = "unknown", "unknown-agent-mode"
        else:
            mode, status = "untagged", "missing-after-cutover"

        track = "dev" if (meta["Suite"] == "cli-clibench-dev-daily") else "nightly"
        replica = meta["Replica"] if track == "dev" else meta["RunId"]
        candidates.append({
            **meta,
            "client": client,
            "harness": agent,
            "track": track,
            "mode": mode,
            "mode_status": status,
            "source_day": meta["SourceDay"],
            "replica_identity": replica,
            "Version": meta["Version"] or b,
        })

    winners = {}
    for meta in candidates:
        k = tuple(meta[f] for f in ["client", "Benchmark", "track", "mode", "Model", "source_day", "replica_identity"])
        old = winners.get(k)
        if old is None or meta["FirstMetadata"] < old["FirstMetadata"]:
            winners[k] = meta
    admitted = sorted(winners.values(), key=lambda r: r["RunId"])

    # Infer repeat expectations per (Benchmark, track) using recent-median rule over daily model run counts
    runs_per_model_day = collections.defaultdict(list)
    counts_by_key = collections.Counter(
        (m["Benchmark"], m["track"], m["Model"], m["source_day"]) for m in admitted
    )
    for (b, tr, _, _), cnt in counts_by_key.items():
        runs_per_model_day[f"{b}|{tr}"].append(cnt)
    repeat_expectations = {"default": 1}
    for bt_key, cnts in sorted(runs_per_model_day.items()):
        med = int(round(quantile(cnts, 0.5)))
        repeat_expectations[bt_key] = max(1, med)

    # Fetch raw outcomes, costs, usage, time, and tokens in chunks of up to 400 runs using ThreadPoolExecutor
    import concurrent.futures
    all_ids = [r["RunId"] for r in admitted]
    raw_by_run = {}
    usage_by_run_inst = {}
    time_by_run_inst = {}
    token_by_run_inst = {}

    chunk_size = 400
    chunks = [(c_idx // chunk_size, all_ids[c_idx:c_idx + chunk_size]) for c_idx in range(0, len(all_ids), chunk_size)]

    def fetch_chunk(idx_and_ids):
        b_idx, chunk_ids = idx_and_ids
        ids_json = json.dumps(chunk_ids, separators=(",", ":"))
        raw_q = f"""let RunIds=dynamic({ids_json});
let Cutoff=datetime({cutoff});
let D=CESBenchmarkMetadataTable
| where RunId in (RunIds) and EventTime <= Cutoff
| summarize arg_max(EventTime,InstanceIds) by RunId
| project RunId,MetadataAt=EventTime,Declared=array_length(InstanceIds),InstanceIds;
let S=CESBenchmarkRunStatusTable
| where run_id in (RunIds) and event_time <= Cutoff
| summarize arg_max(updated_at,status,conclusion),AgentCompleted=maxif(updated_at,tolower(status)=="completed") by run_id
| project RunId=run_id,Status=status,Conclusion=conclusion,UpdatedAt=updated_at,AgentCompleted;
let M=materialize(CESBenchmarkMetricsTable
| where RunId in (RunIds) and EventTime <= Cutoff
| project RunId,BenchmarkName,InstanceId,EventTime,Resolved=tostring(Resolved));
let MT=M | summarize Latest=max(EventTime) by RunId,BenchmarkName,InstanceId;
let O=M | join kind=inner MT on RunId,BenchmarkName,InstanceId
| where EventTime==Latest
| distinct RunId,BenchmarkName,InstanceId,EventTime,Resolved
| summarize RawCanonicalRows=count(),CanonicalRows=make_list(bag_pack("benchmark",BenchmarkName,
    "instance",InstanceId,"eventTime",EventTime,"resolved",Resolved),100000) by RunId;
let C=materialize(CESBenchmarkCustomMetricsTable
| where RunId in (RunIds) and EventTime <= Cutoff
| project RunId,BenchmarkName,InstanceId,EventTime,Properties);
let CT=C | summarize Latest=max(EventTime) by RunId,BenchmarkName,InstanceId;
let Costs=C | join kind=inner CT on RunId,BenchmarkName,InstanceId
| where EventTime==Latest
| extend V=Properties["values"]
| project RunId,BenchmarkName,InstanceId,EventTime,CostJson=tostring(bag_pack(
    "benchmark",BenchmarkName,"instance",InstanceId,"eventTime",EventTime,
    "usd",V["Cost_Total_USD"],"inputTokens",V["InputTokens"]))
| distinct RunId,BenchmarkName,InstanceId,EventTime,CostJson
| summarize RawCostRows=count(),CostRows=make_list(parse_json(CostJson),100000) by RunId;
D | join kind=leftouter S on RunId
| join kind=leftouter O on RunId
| join kind=leftouter Costs on RunId
| project RunId,MetadataAt,Declared,InstanceIds,Status,Conclusion,UpdatedAt,AgentCompleted,
    RawCanonicalRows,CanonicalRows,RawCostRows,CostRows
| order by RunId asc
"""
        time_q = f"""let RunIds=dynamic({ids_json});
let Cutoff=datetime({cutoff});
let Infra = CESBenchmarkInstanceStatusTable
| where run_id in (RunIds) and event_time <= Cutoff and completed_at <= Cutoff and status == "completed"
| extend ExtractedId = extract(@"\\(([^.]+\\.eval\\.[^.]+\\.([^:]+)):", 2, tostring(raw.name)),
         DirectId = tostring(instance_id)
| extend InstanceId = iff(isnotempty(ExtractedId), ExtractedId, DirectId)
| where isnotempty(InstanceId)
| summarize arg_min(completed_at, started_at), HadExtracted = max(iff(isnotempty(ExtractedId), 1, 0)) by run_id, InstanceId
| extend InfraSec = todouble(datetime_diff("second", completed_at, started_at))
| project RunId = run_id, InstanceId, InfraSec = iff(isfinite(InfraSec) and InfraSec >= 0, InfraSec, real(null)), HadExtracted;
let Custom = CESBenchmarkCustomMetricsTable
| where RunId in (RunIds) and EventTime <= Cutoff
| summarize arg_max(EventTime, Properties) by RunId, InstanceId
| extend V = Properties["values"]
| extend AgentSec = todouble(V["msbench.agent_elapsed_time_sec"]),
         TtftSec = todouble(V["msbench.ttft_sec"])
| project RunId, InstanceId,
    AgentSec = iff(isfinite(AgentSec) and AgentSec >= 0, AgentSec, real(null)),
    TtftSec = iff(isfinite(TtftSec) and TtftSec > 0, TtftSec, real(null));
Custom
| join kind=fullouter Infra on RunId, InstanceId
| extend RunId = coalesce(RunId, RunId1), InstanceId = coalesce(InstanceId, InstanceId1)
| where isnotnull(AgentSec) or isnotnull(TtftSec) or isnotnull(InfraSec)
| summarize Instances = count(), Rows = make_list(bag_pack("i", InstanceId, "a", AgentSec, "t", TtftSec, "r", InfraSec, "e", coalesce(HadExtracted, 0)), 100000) by RunId
| order by RunId asc
"""
        tok_q = f"""let RunIds=dynamic({ids_json});
let Cutoff=datetime({cutoff});
CESBenchmarkTrajectoriesTable
| where RunId in (RunIds) and EventTime <= Cutoff
| extend TrajType = case(isnull(TrajectoryReferences), "main", tostring(TrajectoryReferences.trajectory_type) == "", "main", tostring(TrajectoryReferences.trajectory_type))
| where TrajType == "main"
| project RunId, InstanceId,
    InTok = coalesce(tolong(Properties.input_tokens), tolong(Properties.metrics.prompt_tokens)),
    OutTok = coalesce(tolong(Properties.output_tokens), tolong(Properties.metrics.completion_tokens), tolong(0)),
    CacheTok = coalesce(tolong(Properties.cached_input_tokens), tolong(Properties.metrics.cached_tokens), tolong(0)),
    ReasonTok = coalesce(tolong(Properties.metrics.extra.reasoning_tokens), tolong(Properties.metrics.reasoning_tokens))
| summarize
    InRows = countif(isnotnull(InTok)),
    InTok = sum(InTok),
    OutTok = sum(OutTok),
    CacheTok = sum(CacheTok),
    ReasonRows = countif(isnotnull(ReasonTok)),
    ReasonTok = sum(ReasonTok)
    by RunId, InstanceId
| extend
    InTok = iff(InRows > 0, InTok, long(null)),
    ReasonTok = iff(ReasonRows > 0, ReasonTok, long(null))
| summarize Instances = count(), Rows = make_list(bag_pack("i", InstanceId, "in", InTok, "out", OutTok, "c", CacheTok, "r", ReasonTok), 100000) by RunId
| order by RunId asc
"""
        rc = run_kusto(f"onboard-{client.lower()}-raw-{b_idx:02d}", raw_q)
        tmc = run_kusto(f"onboard-{client.lower()}-time-{b_idx:02d}", time_q)
        tkc = run_kusto(f"onboard-{client.lower()}-tok-{b_idx:02d}", tok_q)
        return rc, tmc, tkc

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        for rc, tmc, tkc in pool.map(fetch_chunk, chunks):
            for r in rc:
                raw_by_run[r["RunId"]] = r
            for r in tmc:
                run_id = r["RunId"]
                for x in (r.get("Rows") or []):
                    time_by_run_inst[(run_id, x["i"])] = x
            for r in tkc:
                run_id = r["RunId"]
                for x in (r.get("Rows") or []):
                    token_by_run_inst[(run_id, x["i"])] = x
                    usage_by_run_inst[(run_id, x["i"])] = x.get("in")

    # Build daily & cohort packets across the 32-day window
    metadata = {}
    declarations = {}
    raw_execs = {}
    for source in admitted:
        run = source["RunId"]
        r_data = raw_by_run.get(run)
        if not r_data or not r_data.get("InstanceIds"):
            continue
        declarations[run] = r_data["InstanceIds"]
        tasks = declarations[run]
        normalized = sorted(map(canon, tasks))
        if len(tasks) != r_data["Declared"] or len(set(normalized)) != len(normalized):
            raise RuntimeError(f"Per-root expected-task support/collision on run {run}")
        fp = sha(json.dumps(sorted(tasks), separators=(",", ":"), ensure_ascii=False).encode())
        metadata[run] = {
            "run_id": run,
            "client": client,
            "harness": agent,
            "benchmark": source["Benchmark"],
            "benchmark_version": source["Version"],
            "model": source["Model"],
            "track": source["track"],
            "mode": source["mode"],
            "mode_status": source["mode_status"],
            "source_day": source["source_day"],
            "replica_identity": source["replica_identity"],
            "raw_mode": source["RawMode"] or "",
            "raw_track": source["RawTrack"] or "",
            "reported_rebuild_hash": source["DatasetHash"] or "",
            "creation_time": source["FirstMetadata"],
            "latest_metadata": source["LatestMetadata"],
            "declared": r_data["Declared"],
            "source_status": r_data["Status"] or "unknown",
            "declared_population_fingerprint": fp,
        }
        costs = {(c["benchmark"], c["instance"]): c for c in (r_data.get("CostRows") or [])}
        seen, rows = set(), []
        for s_row in (r_data.get("CanonicalRows") or []):
            ident = (s_row["benchmark"], s_row["instance"])
            if ident in seen:
                raise RuntimeError("Conflicting latest outcomes")
            seen.add(ident)
            outcome = s_row["resolved"].lower()
            if outcome not in ("true", "false", "error"):
                raise RuntimeError(f"Unexpected canonical outcome: {outcome}")
            rows.append({
                "instanceId": s_row["instance"],
                "metricBenchmark": s_row["benchmark"],
                "result": outcome,
                "eventTime": s_row["eventTime"],
                "cost": costs.get(ident),
            })
        raw_execs[run] = rows

    daily_fields = [
        "client", "benchmark", "benchmark_version", "canonical_track",
        "canonical_mode", "model_name", "source_day", "declared_population_fingerprint",
    ]
    cohort_fields = [
        "client", "benchmark", "canonical_track", "canonical_mode", "model_name", "source_day",
    ]
    daily_groups = collections.defaultdict(list)
    for run, meta in sorted(metadata.items()):
        d_dims = {
            "client": meta["client"],
            "benchmark": meta["benchmark"],
            "benchmark_version": meta["benchmark_version"],
            "canonical_track": meta["track"],
            "canonical_mode": meta["mode"],
            "model_name": meta["model"],
            "source_day": meta["source_day"],
            "declared_population_fingerprint": meta["declared_population_fingerprint"],
        }
        daily_groups[tuple(d_dims[f] for f in daily_fields)].append((d_dims, meta))

    daily_packets = []
    cohort_packets = []
    for key, members in sorted(daily_groups.items()):
        dims, first_meta = members[0]
        cohort_id = "|".join([dims["benchmark"], first_meta["harness"], dims["canonical_track"], dims["canonical_mode"]])
        bt_key = f"{dims['benchmark']}|{dims['canonical_track']}"
        exp_rep_cohort = repeat_expectations.get(bt_key, repeat_expectations.get("default", 1))
        exp_rep_daily = 5 if (dims["client"] == "CLI" and dims["benchmark"] == "copilotclibench" and dims["canonical_track"] == "dev") else None

        expected_canon = sorted(map(canon, declarations[first_meta["run_id"]]))
        d_pkt = {
            "dimensions": dims,
            "roots": [],
            "instances": list(expected_canon),
            "metricBenchmarks": [],
            "rows": [],
            "expectedRepeats": exp_rep_daily,
            "sourcePolicyQualified": True,
            "sourceCohortId": cohort_id,
            "reportedBenchmarkDatasetHash": None,
        }
        c_dims = {k: dims[k] for k in cohort_fields}
        c_pkt = {
            "dimensions": c_dims,
            "roots": [],
            "instances": list(expected_canon),
            "metricBenchmarks": [],
            "expectedTaskSets": [list(expected_canon)],
            "rows": [],
            "tokenInputs": [],
            "expectedRepeats": exp_rep_cohort,
            "sourceCohortId": cohort_id,
            "sourceVersions": sorted({m["benchmark_version"] for _, m in members}),
            "sourceRebuildHashes": sorted({m["reported_rebuild_hash"] for _, m in members if m["reported_rebuild_hash"]}),
            "sourcePopulationFingerprints": sorted({m["declared_population_fingerprint"] for _, m in members}),
            "existingObservation": None,
            "sourcePolicyQualified": True,
        }
        for idx, (_, meta) in enumerate(members):
            run = meta["run_id"]
            tasks_canon = sorted(map(canon, declarations[run]))
            if tasks_canon not in c_pkt["expectedTaskSets"]:
                c_pkt["expectedTaskSets"].append(tasks_canon)
            root_base = {
                "id": run,
                "declared": meta["declared"],
                "fingerprint": meta["declared_population_fingerprint"],
                "version": meta["benchmark_version"],
                "replica": meta["replica_identity"],
                "sourceStatus": meta["source_status"],
                "rawMode": meta["raw_mode"],
                "rawTrack": meta["raw_track"],
                "modeStatus": meta["mode_status"],
                "firstMetadata": meta["creation_time"],
                "latestMetadata": meta["latest_metadata"],
            }
            d_pkt["roots"].append(dict(root_base))
            c_pkt["roots"].append({**root_base, "expectedSet": c_pkt["expectedTaskSets"].index(tasks_canon)})
            for row in raw_execs[run]:
                instance, metric = row["instanceId"], row["metricBenchmark"]
                token = usage_by_run_inst.get((run, instance))
                c_pkt["tokenInputs"].append(token)
                if instance not in d_pkt["instances"]:
                    d_pkt["instances"].append(instance)
                    c_pkt["instances"].append(instance)
                if metric not in d_pkt["metricBenchmarks"]:
                    d_pkt["metricBenchmarks"].append(metric)
                    c_pkt["metricBenchmarks"].append(metric)
                inst_idx = d_pkt["instances"].index(instance)
                metric_idx = d_pkt["metricBenchmarks"].index(metric) or None
                cost = row["cost"] or {}
                raw_usd = cost.get("usd")
                usd_v = round(float(raw_usd), 6) if raw_usd is not None else None
                if usd_v is not None and usd_v > 0:
                    code = 1 if row["result"] == "true" else (0 if row["result"] == "false" else -1)
                    vals = [idx, inst_idx, code, usd_v, metric_idx]
                elif usd_v is not None and usd_v <= 0:
                    vals = [idx, inst_idx, row["result"], None, 0.0, 0.0, False, 0.0, 0, 1, metric_idx]
                else:
                    vals = [idx, inst_idx, row["result"], None, None, None, None, None, None, None, metric_idx]
                while len(vals) > 3 and vals[-1] is None:
                    vals.pop()
                d_pkt["rows"].append(vals)
                c_pkt["rows"].append(list(vals))

        if [t for t in map(canon, d_pkt["instances"])] != expected_canon:
            d_pkt["expectedTasks"] = expected_canon
        if len(c_pkt["expectedTaskSets"]) == 1 and [t for t in map(canon, c_pkt["instances"])] == expected_canon:
            c_pkt.pop("expectedTaskSets", None)
        if not d_pkt["metricBenchmarks"]:
            d_pkt["metricBenchmarks"].append(dims["benchmark"])
            c_pkt["metricBenchmarks"].append(dims["benchmark"])
        daily_packets.append(d_pkt)
        cohort_packets.append(c_pkt)

    # Save captured state & update harnesses.json
    capture_doc = {
        "client": client,
        "agent": agent,
        "displayName": display_name,
        "owningTeam": owning_team,
        "windowStart": window_start,
        "cutoff": cutoff,
        "repeatExpectations": repeat_expectations,
        "dailyPackets": daily_packets,
        "cohortPackets": cohort_packets,
        "timeMap": {f"{k[0]}|{k[1]}": v for k, v in time_by_run_inst.items()},
        "tokenMap": {f"{k[0]}|{k[1]}": v for k, v in token_by_run_inst.items()},
    }
    (root / f"onboard-{client.lower()}-capture.json").write_text(json.dumps(capture_doc, separators=(",", ":")) + "\n")

    harnesses_path = root / "harnesses.json"
    harnesses = json.loads(harnesses_path.read_text()) if harnesses_path.exists() else {}
    harnesses[client] = {
        "client": client,
        "displayName": display_name,
        "owningTeam": owning_team,
        "agentNames": [agent],
        "canonicalHarness": agent,
        "defaultModeWhenMissingBeforeCutover": "default",
        "repeatExpectations": repeat_expectations,
    }
    harnesses_path.write_text(json.dumps(harnesses, indent=2) + "\n")

    summary = {
        "stage": "qualify",
        "client": client,
        "agent": agent,
        "displayName": display_name,
        "owningTeam": owning_team,
        "admittedRuns": len(admitted),
        "totalModelDays": len(daily_packets),
        "benchmarks": sorted({p["dimensions"]["benchmark"] for p in daily_packets}),
        "models": sorted({p["dimensions"]["model_name"] for p in daily_packets}),
        "repeatExpectations": repeat_expectations,
        "timeEntries": len(time_by_run_inst),
        "tokenEntries": len(token_by_run_inst),
    }
    print(json.dumps(summary, indent=2))


def get_base_params(cutoff):
    daily_manifest = read("nov10-12-daily-manifest.json")
    sample_req = read(daily_manifest[0]["filename"])
    base_params = {k: v for k, v in sample_req["parameters"].items() if k not in ("effectiveAt", "runIds", "packetJson")}
    base_params["windowStart"] = "2026-10-13T00:00:00.000Z"
    base_params["windowEnd"] = "2026-12-31T00:00:00.000Z"
    base_params["cutoff"] = cutoff
    return base_params


def stage_prepare_daily(client, visible_from):
    cap = read(f"onboard-{client.lower()}-capture.json")
    cutoff = cap["cutoff"]
    base_params = get_base_params(cutoff)
    pkts = [p for p in cap["dailyPackets"] if p["dimensions"]["source_day"] >= visible_from]
    by_day = collections.defaultdict(list)
    for p in pkts:
        by_day[p["dimensions"]["source_day"]].append(p)

    daily_manifest = []
    for day, day_pkts in sorted(by_day.items()):
        batches, cur = [], []
        for pkt in day_pkts:
            cand = cur + [pkt]
            r_ids = [r["id"] for p in cand for r in p["roots"]]
            p_obj = {**base_params, "effectiveAt": day + "T00:00:00.000Z", "runIds": r_ids, "packetJson": json.dumps(cand, separators=(",", ":"))}
            sz = len(json.dumps(p_obj, separators=(",", ":")).encode())
            if cur and (len(r_ids) > 500 or sz > 54000):
                batches.append(cur)
                cur = [pkt]
            else:
                cur = cand
        if cur:
            batches.append(cur)
        for b_idx, batch in enumerate(batches):
            r_ids = [r["id"] for p in batch for r in p["roots"]]
            p_obj = {**base_params, "effectiveAt": day + "T00:00:00.000Z", "runIds": r_ids, "packetJson": json.dumps(batch, separators=(",", ":"))}
            sz = len(json.dumps(p_obj, separators=(",", ":")).encode())
            req = {
                "measure": "source-model-daily-candidate",
                "definition_version": 4,
                "selection": "qualified-source-parameters",
                "idempotency_key": f"onboard-daily-v4/{client}/{day}/{b_idx}",
                "refresh": True,
                "parameters": p_obj,
            }
            fname = f"baseline-onboard-daily-{client.lower()}-{day}-{b_idx:03d}-payload.json"
            raw_bytes = json.dumps(req, separators=(",", ":")).encode()
            (root / fname).write_bytes(raw_bytes)
            for old_f in root.glob(f"baseline-native-dailyNov10_12-{client}-{day}-{b_idx:03d}-*.json"):
                old_f.unlink()
            daily_manifest.append({
                "sourceDay": f"{client}-{day}",
                "batchIndex": b_idx,
                "groups": len(batch),
                "filename": fname,
                "bytes": len(raw_bytes),
                "sha256": sha(raw_bytes),
                "parameterBytes": sz,
            })

    pins_path = root / "baseline-native-operation-pins.json"
    pins = json.loads(pins_path.read_text())
    pins["dailyNov10_12Runs"] = daily_manifest
    pins["readFrom"] = visible_from + "T00:00:00.000Z"
    pins["readTo"] = "2026-12-31T00:00:00.000Z"
    pins["readSeriesFilter"] = {"client": client}
    raw_pins = (json.dumps(pins, sort_keys=True, separators=(",", ":")) + "\n").encode()
    pins_path.write_bytes(raw_pins)
    h_hex = sha(raw_pins)
    update_extension_hash(h_hex)
    print(json.dumps({"stage": "prepare-daily", "client": client, "groups": len(pkts), "batches": len(daily_manifest), "manifestSha256": h_hex}))


def stage_prepare_cohort(client, visible_from):
    cap = read(f"onboard-{client.lower()}-capture.json")
    cutoff = cap["cutoff"]
    base_params = get_base_params(cutoff)
    daily_obs = read("baseline-dailyNov10_12-native-observations.json")["rows"]
    fields = ["client", "benchmark", "canonical_track", "canonical_mode", "model_name", "source_day"]
    by_key = {tuple(r["series"][f] for f in fields): r for r in daily_obs if r["series"]["client"] == client}

    by_day = collections.defaultdict(list)
    for pkt in cap["cohortPackets"]:
        p_copy = json.loads(json.dumps(pkt))
        d = p_copy["dimensions"]
        k = tuple(d[f] for f in fields)
        if k in by_key:
            prior = by_key[k]
            p_copy["existingObservation"] = {name: prior[name] for name in ["observationId", "contentHash", "series", "values"]}
        else:
            p_copy["existingObservation"] = None
        by_day[d["source_day"]].append(p_copy)

    cohort_manifest = []
    for day, day_pkts in sorted(by_day.items()):
        batches, cur = [], []
        for pkt in day_pkts:
            cand = cur + [pkt]
            r_ids = [r["id"] for p in cand for r in p["roots"]]
            p_obj = {**base_params, "effectiveAt": day + "T00:00:00.000Z", "runIds": r_ids, "packetJson": json.dumps(cand, separators=(",", ":"))}
            sz = len(json.dumps(p_obj, separators=(",", ":")).encode())
            if cur and (len(r_ids) > 500 or sz > 54000):
                batches.append(cur)
                cur = [pkt]
            else:
                cur = cand
        if cur:
            batches.append(cur)
        for b_idx, batch in enumerate(batches):
            r_ids = [r["id"] for p in batch for r in p["roots"]]
            p_obj = {**base_params, "effectiveAt": day + "T00:00:00.000Z", "runIds": r_ids, "packetJson": json.dumps(batch, separators=(",", ":"))}
            sz = len(json.dumps(p_obj, separators=(",", ":")).encode())
            req = {
                "measure": "source-cohort-model-day-candidate",
                "definition_version": 2,
                "selection": "source-cohort-parameters",
                "idempotency_key": f"onboard-cohort-v2/{client}/{day}/{b_idx}",
                "refresh": True,
                "parameters": p_obj,
            }
            fname = f"baseline-onboard-cohort-{client.lower()}-{day}-{b_idx:03d}-payload.json"
            raw_bytes = json.dumps(req, separators=(",", ":")).encode()
            (root / fname).write_bytes(raw_bytes)
            for old_f in root.glob(f"baseline-native-cohortNov10_12-{client}-{day}-{b_idx:03d}-*.json"):
                old_f.unlink()
            cohort_manifest.append({
                "sourceDay": f"{client}-{day}",
                "batchIndex": b_idx,
                "groups": len(batch),
                "filename": fname,
                "bytes": len(raw_bytes),
                "sha256": sha(raw_bytes),
                "parameterBytes": sz,
            })

    pins_path = root / "baseline-native-operation-pins.json"
    pins = json.loads(pins_path.read_text())
    pins["cohortNov10_12Runs"] = cohort_manifest
    pins["readFrom"] = "2026-10-13T00:00:00.000Z"
    pins["readTo"] = "2026-12-31T00:00:00.000Z"
    pins["readSeriesFilter"] = {"client": client}
    raw_pins = (json.dumps(pins, sort_keys=True, separators=(",", ":")) + "\n").encode()
    pins_path.write_bytes(raw_pins)
    h_hex = sha(raw_pins)
    update_extension_hash(h_hex)
    print(json.dumps({"stage": "prepare-cohort", "client": client, "groups": len(cap["cohortPackets"]), "batches": len(cohort_manifest), "manifestSha256": h_hex}))


def stage_prepare_comparisons(client, visible_from):
    cap = read(f"onboard-{client.lower()}-capture.json")
    cutoff = cap["cutoff"]
    history_all = [r for r in read("baseline-cohortNov10_12-native-observations.json")["rows"] if r["series"]["client"] == client]
    daily_target = [r for r in read("baseline-dailyNov10_12-native-observations.json")["rows"] if r["series"]["client"] == client and r["series"]["source_day"] >= visible_from]
    scope_fields = ["client", "benchmark", "canonical_track", "canonical_mode"]
    identity_fields = scope_fields + ["model_name", "source_day"]
    by_scope = collections.defaultdict(list)
    by_key = {}
    for row in history_all:
        by_scope[tuple(row["series"][f] for f in scope_fields)].append(row)
        by_key[tuple(row["series"][f] for f in identity_fields)] = row
    daily_fields = [
        "pass_rate", "error_rate", "canonical", "passed", "declared", "matched", "missing_outcomes",
        "cluster_tasks", "cluster_low", "cluster_high", "wilson_low", "wilson_high", "usage_valid",
        "pass_baseline_eligible", "cost_comparisons_eligible", "pricing_unknown", "pricing_partial",
        "pricing_invalid", "cost_known", "cost_missing", "median_usd", "mean_usd", "p90_usd",
        "p95_usd", "observed_total_usd",
    ]
    sort_key = lambda r: tuple(r["series"][f] for f in scope_fields + ["source_day", "benchmark_version", "model_name", "declared_population_fingerprint"])
    comp_packets = []
    for point in sorted(daily_target, key=sort_key):
        s = point["series"]
        eval_day = s["source_day"]
        cohort = [r for r in by_scope[tuple(s[f] for f in scope_fields)] if r["series"]["source_day"] <= eval_day]
        dates = sorted({r["series"]["source_day"] for r in cohort})
        models = sorted({r["series"]["model_name"] for r in cohort})
        tuples = []
        for r in cohort:
            v = r["values"]
            packed = base64.urlsafe_b64encode(uuid.UUID(r["observationId"]).bytes).decode().rstrip("=")
            tuples.append([packed, dates.index(r["series"]["source_day"]), models.index(r["series"]["model_name"]), v["passed"], v["canonical"], v["pass_baseline_eligible"]])
        model_cohort = sorted((r for r in cohort if r["series"]["model_name"] == s["model_name"]), key=lambda r: r["effectiveAt"])
        elig_prior = [r for r in model_cohort if r["series"]["source_day"] < eval_day and r["values"]["pass_baseline_eligible"]][-14:]
        base_hashes = sorted({h for r in elig_prior for h in json.loads(r["values"]["source_rebuild_hashes"])})
        cur_r = by_key[tuple(s[f] for f in identity_fields)]
        cv = cur_r["values"]
        current_entry = {
            "observationId": cur_r["observationId"], "day": eval_day,
            "values": {**{f: cv[f] for f in daily_fields}, "repeats_complete": cv["baseline_repeats_complete"], "reported_dataset_hash": None, "cost_coverage_known": cv["pricing_unknown"] == 0},
            "provenance": {"benchmarkVersions": json.loads(cv["source_versions"]), "reportedDatasetHashes": json.loads(cv["source_rebuild_hashes"]), "declaredPopulationFingerprints": json.loads(cv["source_population_fingerprints"])},
        }
        policy = {"kind": "fixed", "watchPp": 3, "regressionPp": 5, "gainPp": 5, "requireCiConfirmation": False} \
            if s["client"] == "CLI" and s["benchmark"] == "copilotclibench" and s["canonical_track"] in ("dev", "stable") and s["canonical_mode"] == "task-configured" else {"kind": "historical-deviation-v1"}
        comp_packets.append({
            "scope": {f: s[f] for f in scope_fields + ["benchmark_version", "declared_population_fingerprint"]},
            "modelName": s["model_name"], "effectiveAt": point["effectiveAt"], "sourceCutoff": cutoff,
            "dates": dates, "modelNames": models, "calibration": tuples, "daily": [current_entry],
            "baselineDatasetHashes": base_hashes, "sourcePassPolicy": policy,
        })
    batches, cur, cur_coh = [], [], None
    for pkt in comp_packets:
        sc = pkt["scope"]
        coh = (sc["client"], sc["benchmark"], sc["canonical_track"], sc["canonical_mode"], pkt["effectiveAt"])
        p_copy = json.loads(json.dumps(pkt))
        if cur and coh == cur_coh:
            p_copy["calibration"] = []
            p_copy["dates"] = [pkt["effectiveAt"][:10]]
            p_copy["modelNames"] = [pkt["modelName"]]
        cand = cur + [p_copy]
        sz = len(json.dumps({"packetJson": json.dumps(cand, separators=(",", ":"))}, separators=(",", ":")).encode())
        if cur and (len(cand) > 25 or sz > 54000 or coh != cur_coh):
            batches.append(cur)
            cur = [json.loads(json.dumps(pkt))]
            cur_coh = coh
        else:
            cur = cand
            cur_coh = coh
    if cur:
        batches.append(cur)
    comp_manifest = []
    for idx, batch in enumerate(batches):
        params = {"packetJson": json.dumps(batch, separators=(",", ":"))}
        sz = len(json.dumps(params, separators=(",", ":")).encode())
        req = {
            "measure": "source-model-baseline-comparison-v2-candidate", "definition_version": 3,
            "selection": "source-cohort-projections", "idempotency_key": f"onboard-comparison-v3/{client}/{idx}",
            "refresh": True, "parameters": params,
        }
        fname = f"baseline-onboard-comparison-{client.lower()}-{idx:03d}-payload.json"
        raw_bytes = json.dumps(req, separators=(",", ":")).encode()
        (root / fname).write_bytes(raw_bytes)
        for old_f in root.glob(f"baseline-native-comparisonNov10_12-{client}-{idx:03d}-*.json"):
            old_f.unlink()
        comp_manifest.append({
            "sourceDay": f"{client}", "batchIndex": idx, "groups": len(batch),
            "filename": fname, "bytes": len(raw_bytes), "sha256": sha(raw_bytes), "parameterBytes": sz,
        })
    pins_path = root / "baseline-native-operation-pins.json"
    pins = json.loads(pins_path.read_text())
    pins["comparisonNov10_12Runs"] = comp_manifest
    pins["readFrom"] = visible_from + "T00:00:00.000Z"
    pins["readTo"] = "2026-12-31T00:00:00.000Z"
    pins["readSeriesFilter"] = {"client": client}
    raw_pins = (json.dumps(pins, sort_keys=True, separators=(",", ":")) + "\n").encode()
    pins_path.write_bytes(raw_pins)
    h_hex = sha(raw_pins)
    update_extension_hash(h_hex)
    print(json.dumps({"stage": "prepare-comparisons", "client": client, "groups": len(comp_packets), "batches": len(comp_manifest), "manifestSha256": h_hex}))


def stage_prepare_assessments(client, visible_from):
    cap = read(f"onboard-{client.lower()}-capture.json")
    time_map = {tuple(k.split("|", 1)): v for k, v in cap["timeMap"].items()}
    token_map = {tuple(k.split("|", 1)): v for k, v in cap["tokenMap"].items()}
    cohort_packets = {
        (
            p["dimensions"]["client"],
            p["dimensions"]["benchmark"],
            p["dimensions"]["canonical_track"],
            p["dimensions"]["canonical_mode"],
            p["dimensions"]["model_name"],
            p["dimensions"]["source_day"],
        ): p
        for p in cap["cohortPackets"]
    }
    row_usd = lambda r: (r[3] if len(r) > 3 else None) if (isinstance(r[2], int) and not isinstance(r[2], bool)) else (r[4] if len(r) > 4 else None)

    def extract_metrics(pkt):
        cost_vals, cost_zeros, missing_with_tok = [], 0, 0
        agent_vals, runner_vals, ttft_vals = [], [], []
        in_vals, out_vals, reason_vals, cache_vals = [], [], [], []
        io_paired_count = io_paired_sum = cache_valid_count = cache_invalid_count = cache_valid_in_sum = cache_valid_cache_sum = 0
        for idx_r, r in enumerate(pkt["rows"]):
            run_id = pkt["roots"][r[0]]["id"]
            inst_id = pkt["instances"][r[1]]
            raw_u = row_usd(r)
            tok = pkt["tokenInputs"][idx_r] if idx_r < len(pkt.get("tokenInputs", [])) else None
            if raw_u is None:
                if (tok or 0) > 0:
                    missing_with_tok += 1
            else:
                u6 = round(float(raw_u), 6)
                if u6 <= 0:
                    cost_zeros += 1
                else:
                    cost_vals.append(u6)
            tm = time_map.get((run_id, inst_id))
            tk = token_map.get((run_id, inst_id))
            if tm:
                if tm.get("a") is not None and tm["a"] >= 0:
                    agent_vals.append(round(float(tm["a"]), 6))
                if tm.get("r") is not None and tm["r"] >= 0:
                    runner_vals.append(int(round(float(tm["r"]))))
                if tm.get("t") is not None and tm["t"] > 0:
                    ttft_vals.append(round(float(tm["t"]), 6))
            if tk:
                in_t, out_t, c_t, r_t = tk.get("in"), tk.get("out"), tk.get("c"), tk.get("r")
                if out_t is not None and out_t >= 0:
                    out_vals.append(int(out_t))
                if c_t is not None and c_t >= 0:
                    cache_vals.append(int(c_t))
                if r_t is not None and r_t >= 0:
                    reason_vals.append(int(r_t))
                if in_t is not None and in_t >= 0:
                    in_vals.append(int(in_t))
                    if out_t is not None and out_t >= 0:
                        io_paired_count += 1
                        io_paired_sum += int(in_t) + int(out_t)
                    if c_t is not None and c_t >= 0:
                        if c_t <= in_t:
                            cache_valid_count += 1
                            cache_valid_in_sum += int(in_t)
                            cache_valid_cache_sum += int(c_t)
                        else:
                            cache_invalid_count += 1
        return {
            "canonical": len(pkt["rows"]),
            "cost": cost_vals,
            "costZeros": cost_zeros,
            "unpricedInstances": cost_zeros + missing_with_tok,
            "agent": agent_vals,
            "runner": runner_vals,
            "ttft": ttft_vals,
            "in": in_vals,
            "out": out_vals,
            "reason": reason_vals,
            "cache": cache_vals,
            "ioPairedCount": io_paired_count,
            "ioPairedSum": io_paired_sum,
            "cacheValidCount": cache_valid_count,
            "cacheInvalidCount": cache_invalid_count,
            "cacheValidInputSum": cache_valid_in_sum,
            "cacheValidCachedSum": cache_valid_cache_sum,
        }

    metrics_cache = {k: extract_metrics(pkt) for k, pkt in cohort_packets.items()}
    comparisons = [r for r in read("baseline-comparisonNov10_12-native-observations.json")["rows"] if r["series"]["client"] == client]
    daily_all = [r for r in read("baseline-cohortNov10_12-native-observations.json")["rows"] if r["series"]["client"] == client]
    daily_by_id = {r["observationId"]: r for r in daily_all}
    daily_by_key = {(r["series"]["client"], r["series"]["benchmark"], r["series"]["canonical_track"], r["series"]["canonical_mode"], r["series"]["model_name"], r["series"]["source_day"]): r for r in daily_all}

    comparison_fields = ["source_day", "movement_label", "reason", "current_daily_observation_id", "baseline_pass_rate", "baseline_days", "calibration_status", "calibration_watch_pp", "calibration_regression_pp", "calibration_gain_pp", "cost_movement_confirmed", "cost_movement_delta_pct", "cost_reason", "pass_movement_confirmed"]
    daily_fields = ["declared", "canonical", "matched", "passed", "errors", "missing_outcomes", "pending_roots", "usage_valid", "usage_observed", "usage_low", "usage_unknown", "baseline_repeats_complete", "source_policy_qualified", "cost_comparisons_eligible", "pricing_unknown", "pricing_partial", "pricing_invalid", "cost_missing", "cost_known", "cost_zeros", "median_usd"]
    identity_fn = lambda data: json.dumps(data, sort_keys=True, separators=(",", ":"))

    enriched = []
    for row in sorted(comparisons, key=lambda r: identity_fn(r["series"]) + r["effectiveAt"]):
        support = daily_by_id[row["values"]["current_daily_observation_id"]]
        s = row["series"]
        day = row["values"]["source_day"]
        cur_key = (s["client"], s["benchmark"], s["canonical_track"], s["canonical_mode"], s["model_name"], day)
        cur_m = metrics_cache[cur_key]
        cohort_id = cohort_packets[cur_key]["sourceCohortId"]
        prior_days = json.loads(row["values"]["baseline_day_keys"])

        cost_sketch, cur_cost_p50 = make_sketch(cur_m["cost"], 6)
        agent_sketch, cur_agent_p50 = make_sketch(cur_m["agent"], 6)
        runner_sketch, _ = make_sketch(cur_m["runner"], None)
        ttft_sketch, _ = make_sketch(cur_m["ttft"], 6)
        in_sketch, _ = make_sketch(cur_m["in"], None)
        out_sketch, _ = make_sketch(cur_m["out"], None)
        reason_sketch, _ = make_sketch(cur_m["reason"], None)
        cache_sketch, _ = make_sketch(cur_m["cache"], None)

        prior_cost_days, prior_cost_medians, prior_agent_medians, prior_runner_medians = [], [], [], []
        pooled_cost, pooled_agent, pooled_runner, pooled_ttft, pooled_in, pooled_out, pooled_reason, pooled_cache = [], [], [], [], [], [], [], []
        pooled_cache_in_sum = pooled_cache_c_sum = 0

        for b_day in prior_days:
            b_key = (s["client"], s["benchmark"], s["canonical_track"], s["canonical_mode"], s["model_name"], b_day)
            bm = metrics_cache[b_key]
            b_obs = daily_by_key[b_key]
            b_can, b_known, b_unp = bm["canonical"], len(bm["cost"]), bm["unpricedInstances"]
            b_med = round(quantile(bm["cost"], 0.5), 6) if b_known > 0 else 0.0
            prior_cost_days.append([b_day, b_obs["observationId"], b_can, b_known, b_unp, b_med])
            if b_can > 0 and b_known > 0 and (b_can - b_known) / b_can <= 0.2:
                prior_cost_medians.append(b_med)
                pooled_cost.extend(bm["cost"])
            if bm["agent"]:
                prior_agent_medians.append(round(quantile(bm["agent"], 0.5), 6))
                pooled_agent.extend(bm["agent"])
            if bm["runner"]:
                prior_runner_medians.append(round(quantile(bm["runner"], 0.5), 6))
                pooled_runner.extend(bm["runner"])
            pooled_ttft.extend(bm["ttft"])
            pooled_in.extend(bm["in"])
            pooled_out.extend(bm["out"])
            pooled_reason.extend(bm["reason"])
            pooled_cache.extend(bm["cache"])
            pooled_cache_in_sum += bm["cacheValidInputSum"]
            pooled_cache_c_sum += bm["cacheValidCachedSum"]

        supported_mode = s["canonical_mode"] in ("task-configured", "default", "autopilot", "plan", "planwithautopilot")
        d = {f: support["values"].get(f) for f in daily_fields}
        cur_day_base_ok = (
            supported_mode and d["usage_valid"] and d["baseline_repeats_complete"]
            and d["declared"] > 0 and (d["declared"] - d["matched"]) / d["declared"] <= 0.2
            and round1(100.0 * d["errors"] / d["canonical"]) <= 20.0
        )

        need_cost_boot = False
        if cur_day_base_ok and d["canonical"] > 0 and len(cur_m["cost"]) > 0 and (d["canonical"] - len(cur_m["cost"])) / d["canonical"] <= 0.2 and cur_cost_p50 is not None and len(prior_cost_medians) >= 7:
            c_med = quantile(prior_cost_medians, 0.5)
            if c_med and c_med > 0 and abs(100.0 * (cur_cost_p50 - c_med) / c_med) >= 20.0:
                need_cost_boot = True

        need_agent_boot = False
        if cur_day_base_ok and cur_agent_p50 is not None and len(prior_agent_medians) >= 7:
            p_med = quantile(prior_agent_medians, 0.5)
            if p_med and p_med > 0 and abs(100.0 * (cur_agent_p50 - p_med) / p_med) >= 10.0:
                need_agent_boot = True

        cur_tt = {
            "cost": cost_sketch,
            "costZeros": d.get("cost_zeros") or 0,
            "unpricedInstances": cur_m["unpricedInstances"],
            "agent": agent_sketch,
            "runner": runner_sketch,
            "ttft": ttft_sketch,
            "inputTokens": in_sketch,
            "outputTokens": out_sketch,
            "reasoningTokens": reason_sketch,
            "cachedTokens": cache_sketch,
            "ioPairedCount": cur_m["ioPairedCount"],
            "ioPairedSum": cur_m["ioPairedSum"],
            "cacheValidCount": cur_m["cacheValidCount"],
            "cacheInvalidCount": cur_m["cacheInvalidCount"],
            "cacheValidInputSum": cur_m["cacheValidInputSum"],
            "cacheValidCachedSum": cur_m["cacheValidCachedSum"],
        }
        if need_cost_boot:
            cur_tt["costBootstrapMicroUsdDelta"] = delta_encode_int([v * 1e6 for v in cur_m["cost"]])
        if need_agent_boot:
            cur_tt["agentBootstrapMsDelta"] = delta_encode_int([v * 1000.0 for v in cur_m["agent"]])

        pooled_priors = None
        if len(prior_days) >= 7:
            pooled_priors = {
                "cost": make_prior_center(pooled_cost, 6) if len(prior_cost_medians) >= 7 else None,
                "agent": make_prior_center(pooled_agent, 6),
                "runner": make_prior_center(pooled_runner, None),
                "ttft": make_prior_center(pooled_ttft, 6),
                "inputTokens": make_prior_center(pooled_in, None),
                "outputTokens": make_prior_center(pooled_out, None),
                "reasoningTokens": make_prior_center(pooled_reason, None),
                "cachedTokens": make_prior_center(pooled_cache, None),
                "cacheValidInputSum": pooled_cache_in_sum,
                "cacheValidCachedSum": pooled_cache_c_sum,
            }

        fixed = s["client"] == "CLI" and s["benchmark"] == "copilotclibench" and s["canonical_track"] in ("dev", "stable") and s["canonical_mode"] == "task-configured"
        enriched.append({
            "dimensions": s,
            "effectiveAt": row["effectiveAt"],
            "comparisonId": row["observationId"],
            "comparisonHash": row["contentHash"],
            "comparison": {f: row["values"][f] for f in comparison_fields},
            "dailyId": support["observationId"],
            "dailyHash": support["contentHash"],
            "daily": d,
            "requiresCi": not fixed,
            "timeTokens": {
                "costSeed": f"movement.v1|{cohort_id}|{s['model_name']}|cost",
                "elapsedSeed": f"movement.v1|{cohort_id}|{s['model_name']}|elapsed",
                "current": cur_tt,
                "priorCostDays": prior_cost_days,
                "priorDaysCount": len(prior_days),
                "priorAgentMediansSec": prior_agent_medians,
                "priorRunnerMediansSec": prior_runner_medians,
                "pooledPriors": pooled_priors,
            },
        })

    batches, cur_b = [], []
    for pkt in enriched:
        cand = cur_b + [pkt]
        b_len = len(json.dumps({"packetJson": json.dumps(cand, separators=(",", ":"))}, separators=(",", ":")).encode())
        if cur_b and (len(cand) > 30 or b_len > 54000):
            batches.append(cur_b)
            cur_b = [pkt]
        else:
            cur_b = cand
    if cur_b:
        batches.append(cur_b)

    assess_manifest = []
    for idx, batch in enumerate(batches):
        params = {"packetJson": json.dumps(batch, separators=(",", ":"))}
        sz = len(json.dumps(params, separators=(",", ":")).encode())
        req = {
            "measure": "cli-model-display-assessment",
            "definition_version": 5,
            "selection": "exact-native-projections",
            "idempotency_key": f"onboard-assessment-v5-r2/{client}/{idx}",
            "refresh": True,
            "parameters": params,
        }
        fname = f"baseline-onboard-assessment-{client.lower()}-{idx:03d}-payload.json"
        raw_bytes = json.dumps(req, separators=(",", ":")).encode()
        (root / fname).write_bytes(raw_bytes)
        for old_f in root.glob(f"baseline-native-assessmentNov10_12-{client}-{idx:03d}-*.json"):
            old_f.unlink()
        assess_manifest.append({
            "sourceDay": f"{client}", "batchIndex": idx, "groups": len(batch),
            "filename": fname, "bytes": len(raw_bytes), "sha256": sha(raw_bytes), "parameterBytes": sz,
        })

    pins_path = root / "baseline-native-operation-pins.json"
    pins = json.loads(pins_path.read_text())
    pins["assessmentNov10_12Runs"] = assess_manifest
    pins["readFrom"] = visible_from + "T00:00:00.000Z"
    pins["readTo"] = "2026-12-31T00:00:00.000Z"
    pins["readSeriesFilter"] = {"client": client}
    raw_pins = (json.dumps(pins, sort_keys=True, separators=(",", ":")) + "\n").encode()
    pins_path.write_bytes(raw_pins)
    h_hex = sha(raw_pins)
    update_extension_hash(h_hex)
    print(json.dumps({"stage": "prepare-assessments", "client": client, "groups": len(enriched), "batches": len(assess_manifest), "manifestSha256": h_hex}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--client", required=True)
    parser.add_argument("--agent", default="GitHub Copilot Cloud Agent")
    parser.add_argument("--display-name", default=None)
    parser.add_argument("--team", default=None)
    parser.add_argument("--window-start", default="2026-10-13T00:00:00.000Z")
    parser.add_argument("--visible-from", default="2026-11-02")
    parser.add_argument("--cutoff", default="2026-11-13T22:30:03.000Z")
    parser.add_argument("--stage", required=True, choices=["qualify", "prepare-daily", "prepare-cohort", "prepare-comparisons", "prepare-assessments"])
    args = parser.parse_args()
    disp = args.display_name or args.agent
    team = args.team or f"copilot-{args.client.lower()}-evals"
    if args.stage == "qualify":
        stage_qualify(args.client, args.agent, disp, team, args.window_start, args.cutoff)
    elif args.stage == "prepare-daily":
        stage_prepare_daily(args.client, args.visible_from)
    elif args.stage == "prepare-cohort":
        stage_prepare_cohort(args.client, args.visible_from)
    elif args.stage == "prepare-comparisons":
        stage_prepare_comparisons(args.client, args.visible_from)
    elif args.stage == "prepare-assessments":
        stage_prepare_assessments(args.client, args.visible_from)
