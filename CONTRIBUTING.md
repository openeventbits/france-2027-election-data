# Contributing

Thank you for considering a contribution to France 2027 Monitor / FR27 Open Data.

This project is a conservative, source-linked election-data layer. The goal is not volume. The goal is a small public dataset where every visible claim can be inspected, sourced, reviewed, and corrected.

## Good first contributions

Useful first contributions include:

- add one verified campaign event from an official source
- suggest one official source for the source registry
- resolve one promoted poll-media pointer to an official or pollster source
- test the dashboard on another browser or screen size
- file a correction for a source, location, date, candidate link, or metadata issue

A good first contribution is small, specific, and source-linked.

## Data contribution rules

### Campaign events

Campaign-event rows belong in:

```text
data/campaign_events.csv
```

A campaign event should have:

- a stable `event_id`
- an event date
- an event type
- a short title
- a candidate or party link where relevant
- a commune, department, and region
- manually checked latitude and longitude
- a registered `source_id`
- an HTTPS `source_url`
- `verification_status` set to `verified_primary` only when the source is official or primary
- a short note explaining the source and coordinate choice

Preferred sources:

- official candidate pages
- official party pages
- official institutional pages
- official event agendas
- official campaign pages

Avoid adding rows from broad media coverage when an official or primary source exists.

### Sources

Source rows belong in:

```text
data/sources.csv
```

A source should be added only if it is useful for future evidence collection.

Good source candidates include:

- official candidate pages
- official party pages
- institutional election pages
- Commission des sondages pages
- CNCCFP pages
- legally safe pollster source pages
- official open-data catalog entries

Do not add sources only to increase the source count.

### Polls

Poll handling is intentionally conservative.

Do not add candidate-level poll values.

Do not extract candidate scores from media articles.

Do not add polling averages, polling rankings, or forecast-style fields.

Canonical poll metadata may be added only after manual review confirms:

- source authority
- institute
- sponsor or publisher context
- publication date
- fieldwork period
- sample and method where available
- reuse conditions

Until that review is complete, staged poll rows remain review material and should not be treated as canonical public data.

## Local validation

Before opening a pull request, run:

```powershell
python .\scripts\validate_data.py
python .\scripts\validate_poll_media_mentions.py
node --check .\docs\app.js
```

For dashboard-data changes, also regenerate the public dashboard JSON:

```powershell
python .\scripts\export_dashboard_json.py
python .\scripts\enrich_dashboard_poll_metadata_review_status.py
python .\scripts\enrich_dashboard_poll_media_discovery_status.py
```

Then run validation again.

## Pull request checklist

Before submitting a pull request, check that:

- every new canonical row has a source URL
- every new event has manually checked coordinates
- every new event uses a registered source ID
- no candidate-level poll values were added
- canonical poll metadata remains empty unless a reviewed source supports promotion
- generated dashboard JSON is updated when canonical data changes
- validation passes locally

## Scope boundaries

These poll-safety boundaries and scope limits protect the dataset from weak, unsafe, or interpretive election claims.

This project does not accept:

- polling averages
- forecast models
- candidate rankings
- broad media scraping
- social-media scraping
- automated publication of unreviewed poll values
- partisan analysis

## Correction policy

Corrections are welcome.

Useful correction reports include:

- the row ID
- the field that appears wrong
- the proposed correction
- the supporting source URL
- a short explanation

Corrections should improve traceability, not add interpretation.

## Operating principle

Prefer one verified row over ten weak rows.

Every public row should be source-linked, reviewable, and correctable.
