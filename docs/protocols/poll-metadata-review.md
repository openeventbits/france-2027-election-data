# Poll Metadata Review Protocol

This protocol governs manual review of high-priority polling notices before any poll metadata is promoted into the canonical FR27 Open Data tables.

The review is intentionally metadata-only. It does not extract, store, publish, summarize, rank, or compare candidate-level poll values.

## Files

Review queue:

`staging/poll_metadata_high_priority_review.csv`

Canonical metadata target, after separate approval:

`data/polls_metadata.csv`

Canonical result table, not used at this stage:

`data/poll_candidate_results.csv`

## Scope

This protocol applies to high-priority polling notices detected from the Commission des sondages notice watcher.

A row may be reviewed only as polling metadata. The reviewer may identify the poll, institute, dates, sponsor, publisher, method, sample, population, round type, scenario, and source URLs.

The reviewer must not extract candidate percentages, candidate rankings, candidate vote shares, second-round scores, changes since a previous poll, margins, or any other candidate-level quantitative result.

## Fields to fill during manual review

Fill only fields that can be verified from the Commission des sondages notice, the pollster/publication page, or another legally safe public source.

Recommended fields:

- `poll_id`
- `institute`
- `sponsor`
- `publisher`
- `publication_date`
- `fieldwork_start`
- `fieldwork_end`
- `sample_size`
- `population`
- `method`
- `round_type`
- `scenario`
- `commission_notice_url`
- `public_report_url`
- `verification_status`
- `notes`
- `captured_at`
- `updated_at`
- `metadata_review_decision`
- `ready_for_canonical_metadata`
- `review_notes`
- `canonical_promotion_notes`

## Field guidance

`poll_id`

Use a stable, human-readable ID. Prefer the pattern:

`poll_fr27_YYYYMMDD_institute_shortslug`

Use the publication date when available. If only fieldwork date is available, use the fieldwork end date and note this in `review_notes`.

`institute`

Use the polling institute responsible for the survey. If multiple institutes are named, record all material institutes in a concise form.

`sponsor`

Use the commissioning client when clearly identified. If not identified, leave blank or write `not_identified` only if the source makes that clear.

`publisher`

Use the media outlet, organization, or public page where the poll or notice is published.

`publication_date`

Use ISO format:

`YYYY-MM-DD`

`fieldwork_start` and `fieldwork_end`

Use ISO format:

`YYYY-MM-DD`

If fieldwork dates are unavailable, leave blank and explain in `review_notes`.

`sample_size`

Use the total sample size only. Do not enter candidate subsamples or voter-intention subgroup counts.

`population`

Describe the surveyed population, for example:

`registered_voters_france`
`adults_france`
`french_population_18plus`
`not_identified`

`method`

Use a concise method label, for example:

`online_panel`
`telephone`
`mixed`
`not_identified`

`round_type`

Allowed values:

`first_round`
`second_round`
`first_and_second_round`
`barometer_context`
`not_identified`

`scenario`

Describe only the scenario structure. Do not include poll results.

Acceptable examples:

`first_round_with_declared_and_potential_candidates`
`second_round_hypothetical_pairings`
`voting_potential_context`
`not_identified`

Not acceptable:

`Candidate A 28, Candidate B 24`
`Candidate A leads Candidate B`
`RN +2`
`Philippe 25 / Le Pen 31`

`verification_status`

Allowed values:

`pending_review`
`verified_metadata_only`
`rejected_not_presidential`
`rejected_not_poll`
`insufficient_metadata`
`duplicate`
`deferred`

`metadata_review_decision`

Allowed values:

`pending`
`approve_metadata`
`reject`
`defer`
`duplicate`

`ready_for_canonical_metadata`

Allowed values:

`true`
`false`

Set to `true` only when the row satisfies the readiness rules below.

## Readiness rules

A row may be marked `ready_for_canonical_metadata = true` only if all conditions are met:

1. The Commission des sondages notice URL is present.
2. The row concerns a French presidential-election-relevant poll or presidential voting-intention context.
3. The polling institute is identified.
4. The publication date is identified.
5. The fieldwork period is identified, or its absence is explicitly documented in `review_notes`.
6. The sample size, population, or method is identified where available from the source.
7. The row is not a duplicate of an existing reviewed poll.
8. No candidate-level values have been extracted.
9. No candidate-level values are entered in any field.
10. `verification_status` is set to `verified_metadata_only`.
11. `metadata_review_decision` is set to `approve_metadata`.

If any of these conditions are not met, keep `ready_for_canonical_metadata = false`.

## Rejection and deferral rules

Use `reject` when the notice is clearly outside scope, not a poll, not presidential-relevant, or not legally safe to reuse even as metadata.

Use `defer` when the notice may be relevant but essential metadata is unclear.

Use `duplicate` when the notice refers to a poll already reviewed under another row.

## Candidate-level values rule

Candidate-level values must not be extracted at this stage.

Do not enter:

- candidate percentages
- first-round vote shares
- second-round vote shares
- candidate rankings
- poll deltas
- poll-change values
- margins between candidates
- candidate-level subgroup values
- inferred trends

This applies even when such values are visible in a source. The current workflow is metadata-only.

## Promotion rule

Manual review does not automatically promote rows to canonical data.

Promotion to `data/polls_metadata.csv` must be a separate reviewed step.

Promotion to `data/poll_candidate_results.csv` is out of scope for this protocol and must remain blocked until a separate candidate-result reuse, comparability, and source-method protocol exists.

## Review cadence

Daily automation refreshes the staging and review queues.

The reviewer does not need to review rows daily. Review is needed only when new high-priority rows appear or when the project intentionally moves from watcher/demo status toward canonical metadata publication.

## Public communication

Until canonical poll metadata exists, the dashboard may show the existence of the review queue but must not imply that verified poll metadata or poll results have been published.

Candidate cards may continue to show:

`Poll change pending verified comparable poll`
