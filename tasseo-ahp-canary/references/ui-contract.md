# Presentation contract

Preserve the current accepted behavior; inspect live source before editing.
Do not treat the original target screenshot as a data source.

## Cards and structure

- Two equal scenario columns: `say_hello` left, mapped-drive detection right.
- Each model has a compact monospace identifier, separate actual-status
  badge, theme-compatible neutral surface/border, and verdict-colored accent.
  Do not color all card text with the verdict.
- Corresponding headings, metric groups, comparison plots, supporting
  statistics, history headings, chart panels, and disclosure footers align
  using shared rows, not per-column offsets.
- Supporting statistics may wrap at narrow widths without hiding/truncation
  or breaking structural alignment.
- Open comparison summaries use three aligned metric groups, thin rules,
  source confidence-interval caps, a tolerance band, and a shared legend.

## History

- Every nonempty day has a median dot, light connecting line, a vertical
  P25-P75 whisker, and approximately 9 CSS pixels total of horizontal caps.
- Native `tick` with a half-length of 4.5 was observed to produce these caps.
  Re-read the deployed API rather than assuming future signatures.
- Caps/whiskers stay visible and unclipped. Use subtle horizontal gridlines,
  sparse horizontal dates, and consistent margins across columns.
- Preserve exact scales: the initial domain included all quartile endpoints
  with 8% span padding. Do not use decorations to evade normal domain logic.
- Desktop panel bounds were approximately 232 CSS pixels; narrow wrapping
  can legitimately increase height. Measure combined header/chart bounds,
  including actual grid gap, rather than nominal plot height alone.
- Supporting labels use readable body typography; identifiers and primary
  numeric values remain bold monospace. Notes may wrap without overlap.

## Secondary information and navigation

- Methodology and model/scenario audits remain collapsed by default, with
  subdued full-width `Sources & windows` disclosure footers.
- Keep genuine source-run links, audit IDs/hashes, and global report actions.
- History-dot tooltips retain compact date/sample/median/P25/P75/run fields;
  UUID/hash details stay in disclosures, not oversized hover grids.
- Native mark link behavior was observed to route to trace navigation, not
  arbitrary MSBench run URLs. Do not fake run URLs through trace links.
- Native HTML downloads can inert application/outbound navigation. Verify
  live and exported behavior separately instead of promising active links
  in an intentionally inert artifact.

## Native alert and issue controls

- Keep controls within each model/scenario/cadence comparison, not a separate
  competing filing table. Offer issue-management controls only for eligible,
  non-provisional source `ALERT` comparisons with an exact native occurrence.
- Show a persisted issue link when present; otherwise navigate to the exact
  native Alert for management. Historical violations with no live incident
  need an honest backfill/no-live-incident notice, not an invented Alert ID.
- A submitted GitHub new-issue form does not persist a Tasseo association.
  Do not restore direct filing forms or infer links from titles/search matches.
- Use supported native external-link components and verify their live behavior.
  Raw Markdown HTML `target="_blank"` was subject to sanitization; exported
  artifacts can deliberately inert links.
- Match exact evidence, not just model/cadence or nearby timestamps. If the
  native alert is newer than the displayed last-good cycle, label that distinction
  without changing plotted values or implying those values caused the alert.
- Do not render shared-parent/group ownership from identical issue URLs.
  Investigation grouping is external unless separately designed and approved.

See [native alerts](native-alerts.md) for lifecycle and disclosure checks.

## Formatting and verification

Use an en dash for displayed ranges, consistent percentage precision, trimmed
unnecessary decimals, and thousands separators. Formatting must not alter
underlying values or mark channels.

Reuse native layouts/chart marks and existing theme tokens. Scoped Markdown
CSS is an observed workaround for missing generic card APIs; avoid invented
helpers or fake policy alerts. Native inline/custom-property spacing can
override an intended CSS variable; measure computed styles and actual bounds.

Verify reader-facing values/scales with the snapshot checker, then use a
read-only task-owned browser preview for alignment, typography, cap width,
clipping, tooltip wrapping, theme compatibility, and narrow widths. Never
capture another user's windows or use an ambiguous browser handle.
