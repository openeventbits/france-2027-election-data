# Methodology

FR27 Open Data is a public, source-linked, versioned dataset and live map for the French 2027 presidential election.

This methodology is a living blueprint. It will be updated as the project develops, new source types are added, and contributors identify better practices.

## 1. Project Purpose

The project exists to make public election and campaign data easier to inspect, reuse, correct, cite, and build on.

FR27 Open Data is not an analysis product, prediction model, polling average, partisan portal, or editorial ranking system.

The core principle is simple:

> Every visible item should be traceable to a source-linked dataset row.

## 2. Product Shape

FR27 Open Data has two connected surfaces:

1. A live public dashboard.
2. A GitHub-native open dataset.

The dashboard is the visual interface. The repository is the trust layer.

The dashboard may use a map-first layout inspired by live monitoring tools, but the content is limited to French 2027 election and politically relevant campaign data.

## 3. What We Track

The project tracks public, source-linked information related to the French 2027 presidential election.

Initial categories include:

- candidate registry
- candidate status changes
- campaign events
- party and bloc events
- official election documents
- legal and procedural election events
- poll metadata
- source registry
- dataset changelog
- daily dataset snapshots
- daily dashboard/map snapshots

## 4. What Appears On The Map

The map is reserved for geographically meaningful election or campaign events.

Examples:

- public meetings
- rallies
- candidate visits
- party congresses
- debates with a location
- nomination events
- candidacy announcements with a location
- withdrawals with a sourceable place/date context
- official or procedural events when place-based
- legal or institutional events when location matters

The map does not show:

- generic political news
- commentary
- opinion pieces
- sentiment
- candidate momentum
- predictions
- polling averages
- national poll results as map markers
- unsourced social media claims

## 5. Candidate Colors

Candidate-linked events may be displayed using candidate-specific colors.

Color is used only as a visual identifier. It does not represent ranking, popularity, ideology, polling strength, editorial judgment, or prediction.

Recommended visual rules:

- marker color identifies the candidate
- marker shape or icon identifies the event type
- marker border indicates source status where useful
- marker size should not represent poll score

Candidate colors should remain stable once assigned.

## 6. Map Hover And Popup Policy

Map hover or click popups may display:

- candidate name
- event title
- event type
- event date and time
- location
- party or bloc
- source name
- source URL
- verification status
- latest national poll snapshot for the candidate, if available

Poll information inside a map popup must be clearly labeled as a national poll snapshot, not as an explanation of the local event.

Recommended label:

> Latest national poll snapshot

The popup must not imply that a local campaign event caused a polling change.

## 7. Poll Data Policy

Polls are handled separately from the map.

The dashboard may include a live polling metadata card showing:

- polling institute
- sponsor or publisher
- publication date
- fieldwork dates
- sample size
- population
- round type
- public source link
- Commission des sondages notice link
- methodological notes

The project should not blindly republish proprietary poll tables.

If poll results are included later, they must be clearly source-linked, legally reusable, and methodologically labeled.

Poll movement should be described cautiously.

Preferred language:

- `latest_poll_snapshot`
- `change_vs_previous_comparable_poll`
- `previous_comparable_poll`

Avoid:

- momentum
- surge
- collapse
- winner/loser framing
- popularity ranking as editorial judgment

## 8. Poll Change Rules

Polling change should only be calculated when comparison is meaningful.

Preferred comparison order:

1. Same institute, same sponsor/publisher, same scenario, same round type.
2. Same institute and same scenario.
3. Previous published poll, clearly labeled as non-comparable if methodology differs.

If comparison is uncertain, the change field should be blank or marked `not_comparable`.

The dashboard should distinguish:

- latest reported value
- change versus previous comparable poll
- source of latest value
- source of previous value

## 9. Source Policy

Sources are classified by type.

Initial source categories:

- official institution
- official open-data portal
- polling authority
- pollster notice
- candidate official source
- party official source
- major media source
- civic-data reference
- secondary reference

Preferred sources are primary or official sources.

Secondary media sources may be used for verification, but should not become the backbone of the project.

## 10. Initial Source Backbone

The initial source investigation should focus on:

- Conseil constitutionnel
- Commission des sondages
- CNCCFP
- data.gouv.fr
- Ministere de l'Interieur
- Arcom
- HATVP
- Legifrance
- candidate websites
- party websites
- selected major media as secondary verification only

The source registry should record source type, URL, collection method, status, and notes.

## 11. Safe Reuse And Copyright Policy

FR27 Open Data does not republish full articles, images, proprietary documents, paywalled content, or publisher-owned graphics.

The project stores source-linked metadata, factual event records, public-source references, and original structured classifications created by the project.

Allowed public dataset content includes:

- source name
- source URL
- publication date
- captured date
- event date
- event type
- candidate, party, institution, or actor names
- location metadata when relevant
- short original neutral descriptions
- verification status
- source type
- dataset update metadata

The project should not copy:

- full article text
- long article excerpts
- copyrighted images
- publisher graphics
- paywalled material
- proprietary poll tables unless reuse is clearly allowed
- private or non-public personal data

Citation and source linking are required, but citation alone does not make external material reusable. External articles, official pages, documents, poll notices, media materials, and third-party datasets remain governed by their original publishers' terms.

When in doubt, the project should link to the source and store only minimal factual metadata.


## 12. Verification Status

Each row should include a verification status.

Suggested values:

- `official_source`
- `primary_source`
- `secondary_verified`
- `needs_review`
- `archived`
- `corrected`

Rows marked `needs_review` should not be treated as fully verified.

## 13. Event Inclusion Rules

An event may be included when it has:

- a clear date
- a source URL
- a relevant election or campaign connection
- a candidate, party, institution, or process link
- a location, if it is intended for the map

Events should be excluded when they are:

- purely speculative
- unsourced
- only commentary
- only social media noise
- impossible to locate
- not meaningfully related to the 2027 presidential election

## 14. Core MVP Datasets

The initial datasets are:

- `sources.csv`
- `candidates.csv`
- `candidate_status_log.csv`
- `campaign_events.csv`
- `polls_metadata.csv`
- `official_documents.csv`
- `changelog.csv`

The heart of the map is `campaign_events.csv`.

## 15. Campaign Events Schema

Proposed fields for `campaign_events.csv`:

- `event_id`
- `event_date`
- `event_time`
- `event_type`
- `title`
- `description_short`
- `candidate_id`
- `candidate_name`
- `party`
- `bloc`
- `location_name`
- `commune`
- `department`
- `region`
- `latitude`
- `longitude`
- `source_id`
- `source_name`
- `source_url`
- `source_type`
- `verification_status`
- `captured_at`
- `updated_at`
- `notes`

## 16. Dashboard Surfaces

The first dashboard should include:

- France live map
- live event wire
- candidate filter
- party or bloc filter
- event type filter
- region filter
- source type filter
- latest poll metadata card
- candidate status card
- official documents card
- dataset update card
- download links for CSV and JSON exports

The dashboard should remain readable before it becomes complex.

## 17. Daily Snapshots

The project may preserve daily snapshots of the dataset and dashboard state.

Possible snapshot outputs:

- daily event JSON
- daily candidate JSON
- daily poll metadata JSON
- daily dashboard screenshot
- daily map screenshot
- daily changelog summary

Example structure:

```text
snapshots/YYYY-MM-DD/events.json
snapshots/YYYY-MM-DD/polls.json
snapshots/YYYY-MM-DD/candidates.json
snapshots/YYYY-MM-DD/fr27-live-map.png
```

The purpose is to preserve a historical record of how the campaign data layer evolved over time.

## 18. Corrections

Corrections are part of the methodology.

Every dataset row should be correctable through GitHub issues or pull requests.

Corrections should preserve the audit trail where possible. The changelog should record:

* what changed
* when it changed
* why it changed
* which source or issue supported the correction
* who made the change, when available

## 19. Ethical And Legal Boundaries

The project avoids:

* partisan ranking
* candidate scoring
* prediction
* sentiment labeling
* unsupported claims
* private or non-public personal data
* scraping beyond reasonable public-interest use
* copying copyrighted article text
* misleading use of polls
* implying causality between campaign events and poll movement

The project should make uncertainty visible instead of hiding it.

## 20. Manual First, Automated Later

Manual-first data entry is acceptable in the MVP.

Manual first:

* source registry
* candidate registry
* campaign event log
* poll metadata
* official documents
* changelog

Automate later:

* CSV validation
* JSON export
* dashboard refresh
* Commission des sondages watcher
* official institution source watcher
* candidate or party feed watcher
* geocoding from commune names
* daily screenshot capture

Do not automate broad media scraping in the MVP.

## 21. Current MVP Scope

The first prototype focuses on:

* candidate-colored map events
* live event feed
* candidate registry
* source registry
* poll metadata card
* official documents table
* JSON export
* daily snapshot design
* correction workflow
* methodology documentation

## 22. Deferred Features

The following should not be built until after the project has traction:

* prediction model
* polling average as the main product
* candidate ranking
* AI summaries
* sentiment analysis
* social media ingestion
* large-scale media scraping
* backend database
* user accounts
* paywall
* complex scoring system
* real-time websocket infrastructure

## 23. Methodology Updates

This file will evolve as the project evolves.

Methodology changes should be documented through commits and, when substantial, explained in the changelog.


