# FR27 Open Data

**Open, versioned, source-linked data for the French 2027 presidential election.**

FR27 Open Data is a GitHub-native public dataset and live-map prototype for tracking France 2027 election and campaign data.

It is designed as the transparent data layer underneath election dashboards: reusable CSV files, documented schemas, source links, correction workflow, JSON exports, and a public dashboard.

> Every marker should be a source-linked row. Every visible claim should be inspectable. Every correction should leave a trace.

## Repository Status

FR27 Open Data is in prototype stage.

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

Prototype rows are clearly marked as prototype data. Real public-source rows should pass through staging, validation, and review before becoming canonical data.

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

This repository is in early prototype stage.

Current focus:

* methodology
* dataset schemas
* CSV data spine
* staging workflow
* dashboard blueprint
* validation design

Next planned work:

* sample seed data
* JSON export script
* static dashboard prototype in `/docs`
* GitHub Pages preview
* validation workflow
* source/correction issue templates

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


