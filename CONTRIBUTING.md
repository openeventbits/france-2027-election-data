# Contributing

FR27 Open Data welcomes contributions that improve the public, source-linked data layer for the French 2027 presidential election.

The project is in early prototype stage. The most useful contributions are small, specific, and source-backed.

## Good Contributions

Useful contributions include:

- suggesting official or primary sources
- adding candidate or party source links
- improving dataset schemas
- reviewing poll metadata fields
- finding official documents
- improving validation scripts
- improving dashboard accessibility
- identifying duplicate or incorrect rows
- improving French election-law/source documentation

## Source-First Rule

Every proposed data row should include a source.

Preferred sources:

- official institutions
- official open-data portals
- polling authorities
- candidate or party official sources
- pollster notices
- public official documents

Secondary media sources may be useful for verification, but should not become the backbone of the project.

## Data Workflow

The preferred workflow is:

```text
source suggestion
  -> staging row
  -> validation
  -> review
  -> canonical /data row
  -> JSON export
  -> dashboard
```

During the MVP phase, automation should write to `/staging`, not directly to `/data`.

## Pull Requests

A good pull request should:

* keep changes small
* explain what changed
* link the source
* avoid unrelated edits
* update `data/changelog.csv` when correcting public data
* update methodology or schemas when changing the data model

## What Not To Submit

Please do not submit:

* predictions
* candidate rankings
* sentiment labels
* unsourced claims
* copied article text
* proprietary poll tables without clear reuse rights
* private or non-public personal data
* broad scraped media dumps

## Tone

Keep contributions neutral, civic, precise, and source-first.

This project is not partisan. It is a public evidence layer.
