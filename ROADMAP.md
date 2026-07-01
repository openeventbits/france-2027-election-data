# Roadmap

France 2027 Monitor / FR27 Open Data is in a public-preview phase.

The project goal is to build a transparent, source-linked civic-data layer and dashboard preview for the French 2027 presidential election.

The roadmap prioritizes evidence quality, source provenance, correction paths, and conservative poll handling over prediction, ranking, or volume.

## Current public-data status

| Layer | Current status |
| --- | --- |
| Source registry | 20 registered sources |
| Tracked public actors | 5 source-linked actor rows |
| Campaign events | 10 source-linked seed rows |
| Official documents | 4 source-linked rows |
| Commission des sondages notices | 87 staged notice candidates; 7 high-priority metadata review rows |
| Poll-media discovery | 30 staged RSS/search mentions; 7 promoted to source resolution; 23 pending review |
| Canonical poll metadata | 0 rows |
| Candidate-level poll results | 0 rows; candidate-level values remain blocked |

Staged rows are discovery or review material. They are not canonical public data until reviewed and promoted into `/data`.

## Completed since v0.1.0-preview

The first public preview established the project structure, dashboard, source registry, validation workflow, staged poll-notice review, and public release.

Post-preview work completed:

- surfaced official-document rows in the dashboard
- expanded tracked public actors from 3 to 5
- expanded source-linked campaign-event rows from 6 to 10
- expanded registered sources from 18 to 20
- differentiated candidate dashboard colors for readability
- preserved poll-safety boundaries:
  - canonical poll metadata rows remain 0
  - candidate-level poll result rows remain 0
  - candidate-level poll values remain blocked

## Near-term roadmap

### 1. Expand geographically diverse campaign events

Add a small number of real, source-linked, geographically meaningful campaign or election events.

Priority should be given to:

- regions outside Île-de-France
- official candidate or party pages
- clearly dated and located public events
- events with manually checked coordinates
- under-represented blocs or actors where official sources are available

Good examples:

- public meetings
- candidate visits
- party congresses
- campaign launches
- debates with a clear location
- official procedural events with a place

Each event should have a date, place, source URL, source ID, candidate or party link when relevant, and manually checked coordinates.

### 2. Improve source registry coverage

Useful additions include:

- official candidate pages
- party event pages
- institutional election pages
- legally safe pollster source pages
- relevant official open-data catalog entries

Source-registry growth should remain conservative. A source should be useful for future evidence collection, not added only to increase the count.

### 3. Resolve promoted poll-media pointers

Use staged media mentions only as pointers toward safer sources.

Preferred source-resolution targets:

- Commission des sondages notice page
- pollster publication page
- methodology page
- official candidate or party page when relevant

Media articles should not be used to extract candidate-level poll values.

### 4. Promote verified poll metadata only

Canonical poll metadata may be added only after manual review confirms:

- source authority
- institute
- sponsor or publisher context
- publication date
- fieldwork period
- sample and method where available
- reuse conditions

Candidate-level result rows remain blocked.

### 5. Improve dashboard evidence clarity

Near-term dashboard improvements should focus on explaining review status, source provenance, and data caveats.

Useful improvements include:

- clearer distinction between canonical rows and staged review queues
- visible source-count and event-count summaries
- better source links from dashboard cards
- clearer language around poll-notice review status

The dashboard should not imply polling prediction, candidate ranking, or electoral forecasting.

## Good first contributions

Useful first contributions include:

- add one verified campaign event from an official source
- suggest one official source for the source registry
- resolve one promoted poll-media pointer to an official or pollster source
- test the dashboard on another browser or screen size
- file a correction for a source, location, date, or metadata issue

## Not in scope

The following are not part of the near-term roadmap:

- polling averages
- forecast models
- candidate ranking
- broad media scraping
- social-media scraping
- candidate-level poll result extraction
- automated publication of unreviewed poll values
- partisan analysis

## Operating principle

Build the smallest useful public evidence layer first.

Every visible claim should resolve to inspectable data, a source link, and a review path.
