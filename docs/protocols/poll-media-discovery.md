# Poll media discovery protocol

This protocol governs the French media poll-discovery layer in FR27 Open Data.

## Purpose

The media-discovery layer helps identify public article mentions that may point to election-poll material requiring manual review.

It is a discovery layer only. It is not a polling dataset, not a media-scraping pipeline, and not a source of candidate-level polling values.

## Current files

The current staging files are:

- `staging/poll_media_query_feeds.csv`
- `staging/poll_media_mentions.csv`

The current scripts are:

- `scripts/fetch_poll_media_mentions.py`
- `scripts/validate_poll_media_mentions.py`
- `scripts/enrich_dashboard_poll_media_discovery_status.py`

The public dashboard may display aggregate media-discovery status, but it must not display candidate-level poll values from media articles.

## Allowed collection

Allowed:

- RSS/search-result metadata
- article title
- article URL
- source name
- publication timestamp when available
- detected timestamp
- possible polling institute inferred from title/source metadata
- review priority
- review decision
- review notes

Not allowed:

- article body scraping
- extraction of candidate-level poll percentages
- extraction of candidate-level poll rankings as structured data
- publication of candidate-level values from media articles
- automated writes from media discovery into canonical poll tables

## Staging-only rule

Media discovery output must remain in `staging/`.

The media-discovery script must not write to:

- `data/polls_metadata.csv`
- `data/poll_candidate_results.csv`

Canonical poll metadata may only be added through a separate manual review step.

Canonical candidate poll results remain blocked.

## Manual review pathway

The allowed pathway is:

```text
French media RSS/search discovery
        ↓
staging/poll_media_mentions.csv
        ↓
manual review
        ↓
possible pointer to official notice / pollster source
        ↓
metadata-only review queue
        ↓
data/polls_metadata.csv, only if verified
```

Media discovery alone is not sufficient for canonical ingestion.

A media mention may be used to guide an analyst toward an official notice, pollster publication, or other legally safe primary source. It should not be treated as the canonical source for poll values.

## Promotion rule

A media-discovery row may be marked `promote_to_metadata_review` only when the analyst has enough information to justify a metadata-only follow-up.

Promotion does not mean canonical publication.

Before canonical metadata is added, the analyst must verify:

- presidential-election relevance
- poll institute
- client or commissioner when available
- fieldwork dates when available
- sample/methodology when available
- source URL suitable for reuse as metadata
- no candidate-level values extracted into project data

## Candidate-level value block

The field `candidate_level_values_extracted` must remain `false` for every media-discovery row.

The validator must fail if candidate-level percentage or point-delta patterns appear in fields intended for public/staging metadata.

Any accidental candidate-level value detected in media-discovery metadata must be removed or replaced with a non-value placeholder before commit.

## Dashboard rule

The dashboard may show:

- number of query feeds
- number of staged media mentions
- priority counts
- pending-review counts
- candidate-level extraction status

The dashboard must not show:

- candidate percentages
- candidate poll rankings derived from media articles
- article-body extracts
- media-derived candidate movement claims

## Automation status

The current media-discovery layer is a staging prototype.

It is not scheduled as a daily automation.

Scheduling should not be enabled until the repository has:

- stable validation
- clear manual-review capacity
- source/reuse documentation
- safeguards against noisy media-query drift
