# Corrections Policy

Corrections are part of the project.

FR27 Open Data is designed so that public election data can be inspected, challenged, corrected, and reused without requiring personal trust in the maintainer.

## What Can Be Corrected

Corrections may apply to:

* incorrect source links
* missing source links
* wrong dates
* wrong candidate names
* wrong candidate status
* wrong location
* incorrect geocoding
* duplicate rows
* unclear poll comparison
* outdated status
* schema problems
* misleading notes

## Correction Requirements

A correction should include:

* the affected dataset
* the affected row ID, if available
* what is wrong
* the proposed correction
* a supporting source URL
* any uncertainty or caveat

## Correction Workflow

The preferred workflow is:

```text
correction issue or pull request
  -> review source
  -> update row
  -> update changelog
  -> regenerate exports
  -> update dashboard
```

## Changelog

Corrections to canonical public data should be recorded in `data/changelog.csv`.

The changelog should capture:

* what changed
* when it changed
* why it changed
* which source or issue supported the correction
* who made the change, when available

## Poll Corrections

Poll corrections require extra care.

A poll correction may involve:

* poll metadata
* fieldwork dates
* sample size
* sponsor or publisher
* scenario
* candidate-level values
* comparison status
* change versus previous comparable poll

If poll comparability is uncertain, the comparison should be marked `not_comparable` rather than forced into a movement number.

## Map Corrections

Map corrections may involve:

* commune
* department
* region
* latitude
* longitude
* event type
* candidate linkage
* source status

A campaign event should only appear on the map when it has a meaningful location.

## Correction Principle

The goal is not to hide mistakes.

The goal is to make correction visible, traceable, and useful.
