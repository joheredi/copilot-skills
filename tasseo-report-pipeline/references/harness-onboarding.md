# Onboarding a New Harness to the Daily Evaluation Report Pipeline

The Tasseo Daily Evaluation Report Pipeline (`CLI`, `App`, `CCA`, and future harnesses) is architected so **no Measure schema changes and no Report Template code edits** are required to onboard a new harness:
- All 4 shared Measures (`source-model-daily-candidate` v4, `source-cohort-model-day-candidate` v2, `source-model-baseline-comparison-v2-candidate` v3, `cli-model-display-assessment` v5) key on open `client: z.string().min(1)`.
- Shared Template `33abc5cd-61aa-493d-9846-99acc5c62ae7` accepts `harness: z.string().default("ALL")`, `displayName: z.string().nullable().default(null)`, and `owningTeam: z.string().nullable().default(null)` (`rev 8e0e0af845b6ac26affa35bb7aaf8830cc5ecc6a968a72cdd0ef1dc4e8f9d561`). Each harness has its own dedicated Report Series (**Benchmark → Mode → Track → Version → Metric**, with no redundant `Client` selector), and benchmarks, versions, tracks, modes, and models are 100% auto-discovered from the Measure observations.

---

## 1. Self-Serve MSBench Producer Contract (What Partner Teams Emit)

A partner harness team is **100% self-serve** for new benchmarks, benchmark versions, models, and execution modes once their `Agent` is registered in `harnesses.json`, provided their MSBench runs emit:

| Requirement | Kusto Table & Field | Expected Value / Rule |
| --- | --- | --- |
| **Scheduled Main Run** | `CESBenchmarkMetadataTable` (`UserTags["run"]`, `UserTags["branch"]`, `User`) | `run == "workflow-scheduled"`, `branch == "main"`, `User startswith "76d3a380"`, and visible in `CESBenchmarkMetadataV2View`. |
| **Agent Identity** | `CESBenchmarkMetadataTable.Agent` | Stable canonical string (e.g., `"Copilot CLI"`, `"GitHub Copilot App"`, `"GitHub Copilot Cloud Agent"`). |
| **Benchmark & Version** | `UserTags["benchmark"]`, `UserTags["msbench.benchmark.version"]` | Non-empty benchmark slug (e.g., `"ccaprbench"`) and version tag (e.g., `"ccaprbench@2.1.0"`). |
| **Declared Task Population** | `CESBenchmarkMetadataTable.InstanceIds` | Complete array of declared instance IDs for the run. |
| **Execution Mode** | `UserTags["agent-mode"]` (or legacy `UserTags["mode"]`) | One of `"default"`, `"autopilot"`, `"plan"`, `"planwithautopilot"`. Harnesses that have not yet cut over to `agent-mode` default to `"default"` (`mode_status = "legacy-default"`). |
| **Canonical Outcomes** | `CESBenchmarkMetricsTable.Resolved` | `"True"`, `"False"`, or `"Error"` per `(RunId, BenchmarkName, InstanceId)`. |
| **Cost, Agent Time & TTFT** | `CESBenchmarkCustomMetricsTable.Properties.values` | `Cost_Total_USD` (`> 0` priced; `0` treated as unknown/unpriced), `msbench.agent_elapsed_time_sec` (`>= 0`), `msbench.ttft_sec` (`> 0`). |
| **Main-Agent Tokens** | `CESBenchmarkTrajectoriesTable` (`TrajType == "main"`) | `input_tokens`, `output_tokens`, `cached_input_tokens`, `reasoning_tokens`. |

---

## 2. Automated Copilot Onboarding Workflow (3 Required Inputs)

When asked to onboard a new harness, collect only **3 required inputs** (inferring defaults when unambiguous):
1. **`client`**: Short uppercase/slug identifier used in the `Client` selector (e.g., `"CCA"`, `"Padawan"`).
2. **`agent`**: Exact `CESBenchmarkMetadataTable.Agent` string in Kusto (e.g., `"GitHub Copilot Cloud Agent"`).
3. **`owningTeam`** (and optional **`displayName`**): Owning team slug (e.g., `"copilot-cca-evals"`) and human-readable title (defaults to `agent`).

### Step-by-Step Execution (`onboard-harness.py` + Staging MCP)

1. **Stage 1 — Preflight Qualification & 32-Day Kusto Capture (`--stage=qualify`):**
   ```bash
   python3 onboard-harness.py \
     --client "<CLIENT>" \
     --agent "<KUSTO_AGENT_NAME>" \
     --display-name "<DISPLAY_NAME>" \
     --team "<OWNING_TEAM>" \
     --stage=qualify
   ```
   - Verifies scheduled main-branch runs in Kusto, auto-infers per-benchmark `repeatExpectations` via the reference `recent-median` rule over daily model run counts, captures outcomes + `msbench_reported_cost_usd` + `Time` + `Tokens` in parallel, and registers the harness in `harnesses.json`.
   - **Gate:** If `admittedRuns == 0`, stop and report which Kusto tag predicate (`run`, `branch`, `User`, `CESBenchmarkMetadataV2View`) failed.

2. **Stage 2 — Publish Visible-Window Daily Observations (`source-model-daily-candidate` v4):**
   ```bash
   python3 onboard-harness.py --client "<CLIENT>" --stage=prepare-daily
   ```
   - Call `extensions_reload`, then `execute_pinned_baseline_native({ action: "runDailyNov10_12" })` and `execute_pinned_baseline_native({ action: "readDailyNov10_12" })`.

3. **Stage 3 — Publish Rolling Baseline History (`source-cohort-model-day-candidate` v2):**
   ```bash
   python3 onboard-harness.py --client "<CLIENT>" --stage=prepare-cohort
   ```
   - Call `extensions_reload`, then `execute_pinned_baseline_native({ action: "runCohortNov10_12" })` (splitting into ~40-batch chunks if `> 45` batches) and `execute_pinned_baseline_native({ action: "readCohortNov10_12" })`.

4. **Stage 4 — Publish Calibrated Baseline Comparisons (`source-model-baseline-comparison-v2-candidate` v3):**
   ```bash
   python3 onboard-harness.py --client "<CLIENT>" --stage=prepare-comparisons
   ```
   - Call `extensions_reload`, then `execute_pinned_baseline_native({ action: "runComparisonsNov10_12" })` and `execute_pinned_baseline_native({ action: "readComparisonsNov10_12" })`.

5. **Stage 5 — Publish 4-Metric Assessments (`cli-model-display-assessment` v5):**
   ```bash
   python3 onboard-harness.py --client "<CLIENT>" --stage=prepare-assessments
   ```
   - Call `extensions_reload`, then `execute_pinned_baseline_native({ action: "runAssessmentsNov10_12" })` and `execute_pinned_baseline_native({ action: "readAssessmentsNov10_12" })`.

6. **Stage 6 — Instantiate Per-Harness Report Series & Register in Daily Automation:**
   - Call `template_instantiate` on shared template `33abc5cd-61aa-493d-9846-99acc5c62ae7` with `{ harness: "<CLIENT>", displayName: "<DISPLAY_NAME>", owningTeam: "<OWNING_TEAM>", reportDay, windowStart, windowEnd, cutoff }` for the anchor day (`Seq 1`), followed by `report_compute` and `report_series_create_next` + `reports_rename` + `report_compute` for each subsequent day through the current UTC date.
   - Add `<CLIENT>`'s `seriesId`, `anchorReportId`, `latestDay`, `latestReportId`, and `sequence` to `daily-series-state.json` and add its anchor/tail refs to Automation `6b91e434-55d7-4459-82d0-e4e86482e3af`.

---

## 3. Active Staging Series & Post-Deployment Cutover Checklist (Path 1 → Path 2)

### Active Per-Harness Report Series (Tasseo Staging)
- **Copilot CLI (`CLI`, `copilot-cli-evals`):**
  - Series ID: `1a7cf226-2de2-4567-9a5e-1d2a4385fd19`
  - Anchor (`2026-11-08`, Seq 1): `492584c4-223d-4829-8b7c-a4378575b8b0`
  - Latest (`2026-11-13`, Seq 6): `455fefd1-d93d-4f96-b910-559c48960b70`
- **Copilot App (`App`, `copilot-app-evals`):**
  - Series ID: `e3f5d594-d159-4ce8-81b1-94d0a07875dd`
  - Anchor (`2026-11-08`, Seq 1): `14a8121f-7ea6-4393-abe8-1af73442c55c`
  - Latest (`2026-11-13`, Seq 6): `be39289f-ca6c-4081-9873-e82e9a61c414`
- **GitHub Copilot Cloud Agent (`CCA`, `copilot-cca-evals`):**
  - Series ID: `7cf0cc97-f789-4292-b72a-edddc1b0afd5`
  - Anchor (`2026-11-08`, Seq 1): `d2ffa201-15c7-4724-85d1-df6b85aaca69`
  - Latest (`2026-11-13`, Seq 6): `c8fd7add-52e8-4987-b0df-4318126c97c4`

### What Needs to Happen Once Remaining Platform Changes Are Deployed
Currently, daily operation runs via **Path 1** (local scheduled runner `run-daily-pipeline.py` + `onboard-harness.py` preparing `packetJson` batches and triggering Automation `6b91e434-55d7-4459-82d0-e4e86482e3af` at `15:30` and `22:30 UTC`). Once the remaining platform changes in `microsoft/cae` are merged and deployed to Staging/Prod, execute this 4-step update to cut over to **Path 2 (100% cloud-native `schedule.cron` in Tasseo)** and update this skill:

1. **When `microsoft/cae#4945` (Idempotent same-`effectiveAt` Report Series upsert/refresh & Automation-to-Measure run handoff) is deployed:**
   - **Update Automation `6b91e434-55d7-4459-82d0-e4e86482e3af`:**
     - Switch trigger from `api.input(...)` to `schedule.cron("30 15,22 * * *")`.
     - Remove the manual `cliTail` / `appTail` / `ccaTail` static refs and `append-next` vs `refresh-tail` branching; instead call `report.series.append(anchor, { effectiveAt: `${reportDay}T00:00:00.000Z`, ... })` with same-`effectiveAt` tail reuse so the `15:30 UTC` pass creates today's Series member (`created: true`) and the `22:30 UTC` pass reuses that exact tail member (`created: false`) and supersedes its snapshot in place via `await report.run(...)`.
   - **Switch Measures from `packetJson` to Native `msbench.ingest` → Measure Selection:**
     - Replace `run-daily-pipeline.py` / `onboard-harness.py` Kusto `packetJson` preparation with `msbench.query` / `msbench.kql` + `msbench.ingest` in the Automation and native `selection.rows()` / `selection.msbench.runs()` in `source-model-daily-candidate` and `source-cohort-model-day-candidate`.
     - Move the `harnesses.json` registry directly into the Tasseo Automation source (or a pinned Tasseo Dataset) so onboarding a new harness requires only a Tasseo MCP update and zero local files.

2. **When `microsoft/cae#5006` (`#4946` Part 2 — `atif_final_metrics_extra` projection) is deployed (Optional enhancement):**
   - Cost is already unblocked using `msbench_reported_cost_usd > 0` (with `msbench_reported_cost_usd === 0` treated as unknown cost and counted in `unpriced_instances`), and orphan-child recovery (`#4690`) is already deployed.
   - Once `#5006` ships and newly imported traces populate `atif_final_metrics_extra`, update the native Measure Selection to read main-agent token breakdowns (`atif_final_metrics_extra.usage_breakdown.steps.{prompt_tokens,completion_tokens,cached_tokens,reasoning_tokens,llm_call_count}`) and `unbilled_llm_call_count` directly from `traces` instead of querying `CESBenchmarkTrajectoriesTable`.

3. **Retire Local Path 1 Runner & Update Skill:**
   - Verify one `15:30 UTC` append pass and one `22:30 UTC` in-place refresh pass executed by Tasseo's cloud `schedule.cron` worker.
   - Stop the local Copilot CLI schedule (`manage_schedule({ action: "stop" })`) and Windows `keepAlive` helper.
   - Update this reference (`references/harness-onboarding.md`) to replace the `onboard-harness.py` steps with the pure-MCP Automation registry update + native Measure backfill call.

