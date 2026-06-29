# France 2027 Monitor

**A live civic-intelligence dashboard for tracking the French presidential election through source-linked public data.**

France 2027 Monitor is the public-facing dashboard and project identity.

FR27 Open Data is the source-linked open-data layer behind the monitor: reusable CSV files, documented schemas, source links, correction workflow, review protocols, JSON exports, and dashboard-ready public data files.

The project is designed for transparent election monitoring, not prediction. Every visible claim should resolve to inspectable data, source links, and review history.

> Every monitor item should resolve to a source-linked dataset row.

<!-- naming-convention:start -->
## Naming convention

This repository uses two related names intentionally:

France 2027 Monitor is the public-facing dashboard and project identity. Use this name for the website, interface, dashboard preview, and user-facing product description.

FR27 Open Data is the source-linked open-data layer that powers the monitor. Use this name for the datasets, schemas, source registry, validation workflow, review protocols, and CSV/JSON data exports.

In short: France 2027 Monitor is the monitor; FR27 Open Data is the data layer behind it.

<!-- naming-convention:end -->

## Repository Status

France 2027 Monitor is an early public dashboard preview.

FR27 Open Data, the source-linked data layer behind the monitor, is an early source-linked dataset with reviewed seed rows and staging queues.

Current working components:

- source-linked CSV data model
- source registry
- candidate registry
- campaign event schema
- poll metadata schema
- candidate-level poll snapshot schema
- dashboard JSON export
- static live-map prototype
- data validation script
- GitHub Actions data-check workflow
- correction and contribution workflow

The dashboard currently includes source-linked campaign-event seed rows and source-linked official-document rows. Seed rows demonstrate the public data model; they are not comprehensive campaign coverage. New public-source rows should pass through staging, validation, and review before becoming canonical data.

## Current Data Pipeline

The repository now includes a first metadata-only automation pipeline.

```text
data/source_feeds.csv
  -> scripts/fetch_data_gouv_metadata.py
  -> staging/fetched_dataset_metadata.csv
  -> scripts/prepare_dataset_review.py
  -> staging/fetched_dataset_review.csv
  -> scripts/triage_dataset_review.py
  -> reviewed staging rows
  -> later: promotion into canonical /data files
```

The current fetcher reads approved API feeds from `data/source_feeds.csv`, fetches public `data.gouv.fr` metadata, and writes results into `/staging`.

The auto-triage layer labels fetched rows conservatively:

* `likely_useful`
* `likely_noise`
* `needs_review`

This keeps automation useful without allowing scripts to publish directly into canonical public data.

The repository also includes a first poll-notice watcher for Commission des sondages:

    data/source_feeds.csv
      -> scripts/fetch_poll_notices.py
      -> staging/poll_notices_review.csv
      -> scripts/triage_poll_notices.py
      -> staging/poll_notices_triaged_review.csv
      -> later: manual review and possible promotion into data/polls_metadata.csv

This watcher detects and triages presidential-election poll notice candidates. It does not extract candidate-level poll values, does not publish poll percentages, and does not write directly into canonical `/data` files.

## What This Is

FR27 Open Data is an open civic-data project for the French 2027 presidential election.

The project tracks public, source-linked information such as:

- candidate registry
- candidate status changes
- campaign events
- party and bloc events
- poll metadata
- candidate-level poll snapshots when legally/source-safe
- official documents
- legal and procedural election events
- source registry
- dataset changelog
- daily data and dashboard snapshots

## What This Is Not

FR27 Open Data is not:

- a prediction model
- a polling average site
- a candidate ranking system
- a partisan election portal
- a sentiment analysis project
- an AI summary product
- a general news scraper
- a replacement for official institutions

The project does not score candidates, forecast results, or label political momentum.

## Why It Exists

Election dashboards often show polished outputs, but the underlying data can be hard to inspect, reuse, correct, or cite.

FR27 Open Data starts from the opposite direction:

1. public rows first
2. sources first
3. schemas first
4. corrections first
5. dashboard second

The repository itself is part of the product.

## Dashboard Concept

The public dashboard is intended to include:

- France live map
- candidate-colored event markers
- live event wire
- event filters by candidate, party/bloc, event type, region, and source type
- hover/click popups with event details and source links
- latest national poll snapshot card
- candidate status card
- official documents card
- dataset update card
- daily map/data snapshots

Candidate colors are visual identifiers only. They do not imply ranking, ideology, popularity, polling strength, or editorial judgment.

Polls are handled separately from the map. National polls are not geographic events.

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

During the MVP phase, automation should not write directly into canonical public data. Parsed rows should pass through staging, validation, and review first.

## Dataset Inventory

| Dataset                           | Purpose                                                                     |
| --------------------------------- | --------------------------------------------------------------------------- |
| `data/sources.csv`                | Registry of official, primary, secondary, and reference sources.            |
| `data/candidates.csv`             | Candidate and likely-candidate registry, including stable dashboard colors. |
| `data/candidate_status_log.csv`   | Candidate status history.                                                   |
| `data/campaign_events.csv`        | Geographically meaningful campaign and election events for the map.         |
| `data/polls_metadata.csv`         | Poll-level metadata.                                                        |
| `data/poll_candidate_results.csv` | Candidate-level poll values when legally/source-safe.                       |
| `data/official_documents.csv`     | Official institutional, legal, procedural, or campaign documents.           |
| `data/changelog.csv`              | Dataset changes and corrections.                                            |
| `data/snapshots_manifest.csv`     | Index of daily data and dashboard snapshots.                                |

## Initial Source Backbone

Initial source investigation focuses on:

* Conseil constitutionnel
* Commission des sondages
* CNCCFP
* data.gouv.fr
* Ministere de l'Interieur
* Arcom
* HATVP
* Legifrance
* candidate websites
* party websites
* selected major media as secondary verification only

Preferred sources are official or primary sources. Secondary media sources may be used for verification, but should not become the backbone of the project.

## Poll Policy

Poll data is handled cautiously.

The project may record poll metadata such as:

* institute
* sponsor or publisher
* publication date
* fieldwork dates
* sample size
* population
* method
* round type
* scenario
* Commission des sondages notice link
* public report link
* methodological notes

Candidate-level poll values may be included only when legally/source-safe and clearly attributed.

Poll movement should be displayed only when comparison is meaningful. Preferred language is:

* `latest_poll_snapshot`
* `previous_comparable_poll`
* `change_vs_previous_comparable_poll`

The project avoids language such as momentum, surge, collapse, winner, or loser.

## Map Policy

The map shows geographically meaningful election and campaign events, such as:

* rallies
* public meetings
* candidate visits
* debates with location
* party congresses
* nomination events
* candidacy announcements with location
* official or procedural events when place-based

The map does not show:

* national poll results as markers
* generic political news
* opinion articles
* sentiment
* candidate momentum
* predictions
* unsourced social media claims

## Current Status

This repository is in early public-preview stage.

Already present:

* source registry and schema documentation
* candidate registry
* source-linked campaign-event seed rows
* source-linked official-document rows
* staging queues for public metadata, Commission des sondages notices, poll-media discovery, and source resolution
* dashboard JSON export and GitHub Pages preview
* validation script and GitHub Actions data-check workflow
* correction, source-suggestion, and campaign-event issue templates
* roadmap and contribution guidance

Next milestones are tracked in `ROADMAP.md`.

The immediate priority is to expand verified source-linked rows conservatively while keeping canonical poll metadata empty until manual verification and keeping candidate-level poll result rows blocked.

## Repository Structure

```text
/data                 canonical public CSV datasets
/schemas              dataset documentation
/staging              parsed data awaiting validation/review
/scripts              validation, export, parsing, and snapshot scripts
/docs                 static dashboard for GitHub Pages
/docs/data            dashboard JSON exports
.github/workflows     validation/export automation
.github/ISSUE_TEMPLATE source suggestions, corrections, schema proposals
```

## Corrections

Corrections are welcome.

Every dataset row should be correctable through GitHub issues or pull requests. Corrections should preserve the audit trail where possible and be recorded in `data/changelog.csv`.

## Roadmap

- [Roadmap](ROADMAP.md)

## Contributing

Useful contributions include:

* source suggestions
* candidate/party source links
* schema review
* poll metadata review
* official document discovery
* dashboard improvements
* validation scripts
* accessibility improvements
* French election-law/source expertise

## License

FR27 Open Data uses separate licenses for code and original structured data.

* Code: MIT License. See `LICENSE`.
* Original structured data: Creative Commons Attribution 4.0 International, CC BY 4.0. See `LICENSE-DATA.md`.
* External sources: linked official pages, articles, documents, poll notices, and media materials remain governed by their original publishers' terms. FR27 Open Data does not claim ownership over external source material.

Reuse should preserve attribution, source links, and relevant methodological caveats where possible.

## Project Principle

FR27 Open Data should be small, transparent, and useful before it becomes ambitious.

The goal is not to predict the French 2027 election.

The goal is to make the public evidence layer easier to inspect, reuse, correct, fork, and cite.

## Review protocols

- [Poll metadata review protocol](docs/protocols/poll-metadata-review.md): metadata-only review rules for high-priority Commission des sondages notices.
- [Poll media discovery protocol](docs/protocols/poll-media-discovery.md): staging-only RSS/search metadata discovery rules for media mentions, with no article scraping, no candidate-level values, and no canonical writes.

### Poll media discovery

French media poll discovery is a staging-only RSS/search metadata layer. It may collect article titles, source names, URLs, timestamps, inferred polling institutes, priority labels, and manual review decisions. It does not scrape article bodies, extract candidate-level poll values, or write to canonical poll tables. Media mentions may only guide manual review toward official notices, pollster publications, or other legally safe primary sources.


## Status

Current public-data status: the dashboard preview now includes three source-linked campaign-event seed rows, four source-linked official-document rows, staged Commission des sondages notice candidates, staged poll-media discovery, and a poll-media source-resolution queue. Canonical poll metadata and candidate-level poll result tables remain empty.
