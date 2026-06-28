# Dataset Schemas

This directory documents the first public data model for FR27 Open Data.

The CSV files in `/data` are the canonical public source of truth. JSON exports and the dashboard should be generated from these files.

The project is designed for automation, but automation should not write directly into canonical public data during the MVP phase. Parsed online data should first pass through staging, validation, and review.

## Dataset Inventory

| Dataset | Purpose | Dashboard Role |
|---|---|---|
| `sources.csv` | Registry of official, primary, secondary, and reference sources. | Source labels, source filters, verification display. |
| `candidates.csv` | Candidate and likely-candidate registry. | Candidate filters, marker colors, candidate cards. |
| `candidate_status_log.csv` | Status history for candidates. | Candidate timeline and status updates. |
| `campaign_events.csv` | Geographically meaningful campaign and election events. | Main France map markers and live event wire. |
| `polls_metadata.csv` | Poll-level metadata. | Latest poll card and poll source context. |
| `poll_candidate_results.csv` | Candidate-level poll values when legally/source-safe. | Candidate poll snapshot and poll change display. |
| `official_documents.csv` | Official institutional, legal, procedural, or campaign documents. | Official document card and source-linked archive. |
| `changelog.csv` | Record of dataset changes and corrections. | Dataset update card and audit trail. |
| `snapshots_manifest.csv` | Index of daily data and dashboard snapshots. | Daily archive and screenshot history. |

## Data Flow

```text
online public sources
  -> fetch and parse scripts
  -> /staging/*.csv
  -> validation
  -> human review when needed
  -> /data/*.csv
  -> /docs/data/*.json
  -> dashboard
  -> daily snapshots
```

## Why Use Staging?

The staging layer protects the public dataset from duplicate rows, weak source links, incomplete dates, uncertain candidate matching, incorrect locations, bad geocoding, legally unsafe poll reuse, non-comparable poll changes, and broad media noise.

During the MVP, `/data` should contain approved rows only.

## Manual vs Automated Work

Manual first:

* source registry
* candidate registry
* candidate color assignment
* campaign event approval
* poll metadata approval
* official document approval
* correction review

Automated later:

* source fetching
* RSS/feed parsing
* Commission des sondages watcher
* official institution watcher
* candidate/party site watcher
* geocoding
* validation
* JSON export
* daily screenshot capture
* daily snapshot manifest updates

## Dataset Design Principles

* CSV files are human-readable and easy to diff.
* Every visible dashboard item should map back to a dataset row.
* Every row should include a source or be marked as needing review.
* The map shows geographically meaningful events, not national polls.
* Poll data is handled carefully and separately from map events.
* Candidate colors are visual identifiers only. They do not imply ranking, ideology, or support.
* Corrections should be recorded in `changelog.csv`.
* Automation should support the data model, not replace verification.

## Relationship Between Datasets

```text
sources.csv
  -> candidates.csv
  -> candidate_status_log.csv
  -> campaign_events.csv
  -> polls_metadata.csv
  -> poll_candidate_results.csv
  -> official_documents.csv

changelog.csv records corrections and dataset edits.
snapshots_manifest.csv records daily data/map snapshots.
```

## Map Data

The dashboard map is primarily powered by:

* `campaign_events.csv`
* `candidates.csv`
* `sources.csv`
* optionally `poll_candidate_results.csv` for compact candidate poll snapshots in popups

Poll values must not be represented as geographic events.

## Poll Data

Polls are split into two tables:

* `polls_metadata.csv` stores poll-level information.
* `poll_candidate_results.csv` stores candidate-level values, when legally and methodologically appropriate.

This separation allows the project to show poll metadata without turning the map into a polling average or prediction product.

## Snapshot Data

Daily snapshots may include:

* data exports
* dashboard state
* map screenshots
* poll card screenshots
* changelog summaries

`snapshots_manifest.csv` records where each snapshot is stored.

## Validation

Validation scripts should eventually check:

* required columns exist
* row IDs are unique
* source IDs exist in `sources.csv`
* candidate IDs exist in `candidates.csv`
* latitude and longitude are present for map events
* poll result rows reference valid poll IDs
* dates use ISO format
* verification status values are controlled
* no unsupported poll comparison is presented as comparable
