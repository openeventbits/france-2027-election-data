# Roadmap

France 2027 Monitor is a public, source-linked election data prototype.

The goal is not to predict the election. The goal is to maintain a transparent, reusable evidence layer for campaign events, official documents, poll metadata review, and legally safe public election data.

## Current public-data status

The repository currently includes:

- 6 source-linked campaign-event seed rows
- 4 source-linked official-document rows
- 86 staged Commission des sondages notice candidates
- 7 high-priority poll metadata review rows
- 30 staged poll-media discovery rows
- 7 promoted media pointers awaiting source resolution
- 0 canonical poll metadata rows
- 0 candidate-level poll result rows

Candidate-level poll values remain blocked until verified public notices, source methodology, and reuse conditions are reviewed.

## Near-term roadmap

### 1. Expand source-linked campaign events

Add a small number of real, source-linked, geographically meaningful campaign or election events.

Good examples:

- public meetings
- candidate visits
- party congresses
- campaign launches
- debates with a clear location
- official procedural events with a place

Each event should have a date, place, source URL, source ID, candidate or party link when relevant, and manually checked coordinates.

### 2. Resolve promoted poll-media pointers

Use staged media mentions only as pointers toward safer sources.

Preferred source-resolution targets:

- Commission des sondages notice page
- pollster publication page
- methodology page
- official candidate or party page when relevant

Media articles should not be used to extract candidate-level poll values.

### 3. Promote verified poll metadata only

Canonical poll metadata may be added only after manual review confirms the source, fieldwork period, institute, commissioner/publication context, and reuse conditions.

Candidate-level result rows remain blocked.

### 4. Improve source registry coverage

Useful additions include:

- official candidate pages
- party event pages
- institutional election pages
- legally safe pollster source pages
- relevant official open-data catalog entries

### 5. Improve dashboard clarity

Near-term dashboard improvements should focus on explaining review status, source provenance, and data caveats.

The dashboard should not imply polling prediction, candidate ranking, or electoral forecasting.

## Good first contributions

Useful small contributions include:

- suggest one official source
- correct one source URL
- add one source-linked campaign event
- verify one staged poll notice
- resolve one promoted media pointer to an official or pollster source
- improve documentation wording
- test the dashboard on mobile or another browser

## Not in scope

This project does not aim to provide:

- election prediction
- polling averages
- automated candidate-level poll extraction
- broad media scraping
- social-media scraping
- partisan analysis
- sentiment scoring

## Operating principle

Prefer a small number of verified rows over a large number of weak rows.

Every canonical row should be source-linked, reviewable, and correctable.
