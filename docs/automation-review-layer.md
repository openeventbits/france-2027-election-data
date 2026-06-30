# Automation review layer design

Status: design only. Not implemented.

This document describes how FR27 can move from manual review toward a mostly automated review layer while preserving the distinction between a live signal layer and a canonical public evidence layer.

The goal is not to remove safeguards. The goal is to turn repeated human review checks into explicit gates that software can run consistently.

## Product split

FR27 should eventually have two related but separate layers.

### Live signal layer

The live signal layer may be automated, fast, and frequently updated.

It can show source-linked items that were detected automatically, including newly discovered campaign events, official pages, procedural notices, or media pointers.

Live-layer rows may be marked as:

- auto_detected
- pending_review
- low_confidence
- duplicate_candidate
- rejected_by_policy
- ready_for_canonical_review

The live layer can be useful even before canonical promotion, as long as the dashboard clearly labels its status.

### Canonical evidence layer

The canonical evidence layer is the public reusable dataset.

Canonical rows must remain conservative, source-linked, versioned, and reproducible.

Canonical data includes files such as:

- data/campaign_events.csv
- data/official_documents.csv
- data/sources.csv
- data/polls_metadata.csv, if metadata is later approved

Canonical poll candidate result rows remain blocked unless the project doctrine changes.

Candidate registry statuses should avoid over-claiming. A status such as `tracked_public_actor` means the person is included because source-linked public campaign activity is monitored. It is not a verified formal candidacy claim and not a support measure.

## Review-engine decisions

A future review engine should classify each staged row into one of three decisions.

### auto_promote

The row can be written to canonical data automatically.

This should only be allowed for narrow, low-risk cases where all gates pass.

### needs_review

The row is plausible but requires human review before canonical publication.

This should be the default for ambiguous rows, new source patterns, media-derived pointers, partial extraction, or politically sensitive content.

### reject

The row should not enter canonical data.

Reject reasons may include unsupported source type, missing date, missing location, duplicate row, poll-value risk, unclear reuse status, or failed validation.

## Core gates

A row should not be auto-promoted unless it passes all required gates.

### 1. Source-policy gate

The source must be allowed for the relevant data type.

For campaign events, high-confidence sources may include whitelisted official candidate pages, official party pages, and institutional calendars.

For poll metadata, media articles should not be canonical sources. Media mentions may only point toward official notices, pollster pages, or legally safe primary sources.

For candidate-level poll results, automation remains blocked.

### 2. Extraction-completeness gate

The row must contain the required fields for its data type.

For campaign events, required fields include:

- event date
- event type
- title
- candidate or party association
- location
- source URL
- source type
- verification status

Rows with missing dates, vague locations, or unclear candidate association should go to needs_review.

### 3. Duplicate gate

The row must not duplicate an existing canonical row.

Duplicate checks should compare:

- source URL
- event date
- candidate ID
- commune
- normalized title
- source ID

Near-duplicates should go to needs_review rather than auto_promote.

### 4. Geography gate

The row must have a usable location.

Coordinates may be venue-level, commune-level, or manually verified administrative coordinates.

If coordinates are inferred with low confidence, the row should not auto-promote.

### 5. Poll-safety gate

No automation may extract, store, or publish candidate-level poll values.

Any percent pattern, points-change pattern, candidate-level ranking table, or likely poll-result value in extracted text should force the row into needs_review or reject, depending on the data type.

Canonical poll candidate result rows remain blocked.

### 6. Legal and reuse gate

The source must be compatible with the intended use.

Official pages, official notices, and manually reviewed metadata are safer than article scraping or proprietary tables.

Media-only poll articles should remain discovery pointers, not canonical poll data.

### 7. Validation gate

The row must pass the existing repository validation and dashboard export checks before publication.

A future auto-promotion system should run the same checks currently run manually:

- export_dashboard_json.py
- enrich_dashboard_poll_metadata_review_status.py
- enrich_dashboard_poll_media_discovery_status.py
- validate_data.py
- validate_poll_media_mentions.py

## Auto-promotion policy

Auto-promotion should be allowed only when the row is low-risk and source-linked.

Initial auto-promotion candidates:

- campaign events from whitelisted official candidate or party pages
- official documents from whitelisted institutional pages
- source registry updates from known official domains

Auto-promotion should not initially apply to:

- media articles
- social media posts
- poll candidate values
- candidate-level poll result rows
- ambiguous event pages
- scraped article content
- inferred candidate support
- unverified third-party summaries

## LLM-assisted extraction policy

A language model may help extract fields into staging.

A language model should not be the only reason a row becomes canonical.

A future LLM-assisted pipeline should be constrained as follows:

- it may propose structured fields
- it must preserve source URLs
- it must return uncertainty notes
- it must not extract poll values
- it must not override source-policy gates
- it must not write directly to canonical data without deterministic gates passing

The review engine should be gate-based first and model-assisted second.

## Suggested staging fields

A future staging table for campaign-event candidates could include:

- staged_event_id
- detected_at
- source_id
- source_url
- source_type
- extraction_method
- extracted_title
- extracted_event_date
- extracted_event_time
- extracted_location
- extracted_candidate_id
- extracted_party
- duplicate_status
- geography_confidence
- source_policy_status
- poll_safety_status
- review_decision
- review_confidence
- gate_failures
- canonical_write_allowed
- promoted_event_id
- notes

## Implementation stages

### Stage 0: manual canonical rows

Current stage.

Humans add small numbers of reviewed source-linked rows to canonical CSV files. Existing validators and dashboard export scripts are reused.

### Stage 1: automated discovery into staging

Automation discovers candidate rows from official pages and writes only to staging files.

No canonical writes.

### Stage 2: automated review scoring

A review engine classifies staged rows as auto_promote, needs_review, or reject.

No auto-promotion yet.

### Stage 3: live signal layer

The dashboard may show clearly labeled live detected rows separately from canonical reviewed rows.

This makes the monitor more current without weakening the canonical evidence layer.

### Stage 4: narrow auto-promotion

Only official-source rows that pass every gate may be written automatically to canonical data.

The first safe candidates are likely campaign events and official documents, not polls.

### Stage 5: review by exception

Human review focuses on rows that fail one or more gates, new source patterns, ambiguous geography, near duplicates, and poll-related material.

## Non-negotiable safeguards

- No automation writes candidate-level poll result rows.
- No automation extracts candidate-level poll values.
- No media-only poll article becomes canonical poll data.
- No row enters canonical data without a source URL.
- No row enters canonical data without passing validation.
- No new source class is auto-promoted until it has been manually tested.
- Staging is allowed to be noisy. Canonical data is not.

## Design principle

Manual review should become a set of explicit gates.

Once the gates are stable, automation can run them.

The long-term goal is not review forever. The long-term goal is review by exception.
