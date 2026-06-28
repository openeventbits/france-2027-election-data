import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

EXPECTED_COLUMNS = {
    "sources.csv": ["source_id", "source_name", "url", "status"],
    "candidates.csv": ["candidate_id", "display_name", "color_hex", "source_id"],
    "campaign_events.csv": ["event_id", "event_date", "event_type", "title", "candidate_id", "latitude", "longitude", "source_id"],
    "polls_metadata.csv": ["poll_id", "institute", "publication_date", "source_id"],
    "poll_candidate_results.csv": ["poll_result_id", "poll_id", "candidate_id", "poll_value", "source_id"],
    "source_feeds.csv": ["feed_id", "source_id", "feed_name", "feed_type", "url", "collection_method", "automation_stage", "status", "refresh_cadence", "review_required"],
    "reference_datasets.csv": ["reference_dataset_id", "title", "producer", "source_id", "url", "topic", "reference_type", "status", "last_verified_at"],
}

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
URL_RE = re.compile(r"^https?://")

VALID_SOURCE_STATUS = {"active", "inactive", "needs_review"}
VALID_COLLECTION_METHOD = {"manual", "manual_review", "automated", "staging"}
VALID_SOURCE_LEVEL = {"primary", "secondary"}

VALID_FEED_TYPE = {"source_page", "legal_page", "catalog", "api"}
VALID_AUTOMATION_STAGE = {"not_automated", "planned", "staging", "active"}
VALID_REFRESH_CADENCE = {"hourly", "daily", "weekly", "monthly", "manual"}
VALID_BOOLEAN = {"true", "false"}
VALID_REFERENCE_TYPE = {"historical_schema_reference", "historical_baseline", "official_dataset", "methodology_reference"}


def read_csv(name):
    path = DATA / name
    if not path.exists():
        raise AssertionError(f"Missing file: data/{name}")

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        return reader.fieldnames or [], rows


def require_columns(name, columns):
    fieldnames, rows = read_csv(name)
    missing = [col for col in columns if col not in fieldnames]
    if missing:
        raise AssertionError(f"{name} missing columns: {', '.join(missing)}")
    return rows


def require_unique(rows, key, name):
    seen = set()
    for row in rows:
        value = row.get(key, "").strip()
        if not value:
            raise AssertionError(f"{name} has blank {key}")
        if value in seen:
            raise AssertionError(f"{name} has duplicate {key}: {value}")
        seen.add(value)


def main():
    errors = []

    try:
        sources = require_columns("sources.csv", EXPECTED_COLUMNS["sources.csv"])
        candidates = require_columns("candidates.csv", EXPECTED_COLUMNS["candidates.csv"])
        events = require_columns("campaign_events.csv", EXPECTED_COLUMNS["campaign_events.csv"])
        polls = require_columns("polls_metadata.csv", EXPECTED_COLUMNS["polls_metadata.csv"])
        poll_results = require_columns("poll_candidate_results.csv", EXPECTED_COLUMNS["poll_candidate_results.csv"])
        source_feeds = require_columns("source_feeds.csv", EXPECTED_COLUMNS["source_feeds.csv"])
        reference_datasets = require_columns("reference_datasets.csv", EXPECTED_COLUMNS["reference_datasets.csv"])

        require_unique(sources, "source_id", "sources.csv")
        require_unique(candidates, "candidate_id", "candidates.csv")
        require_unique(events, "event_id", "campaign_events.csv")
        require_unique(polls, "poll_id", "polls_metadata.csv")
        require_unique(poll_results, "poll_result_id", "poll_candidate_results.csv")
        require_unique(source_feeds, "feed_id", "source_feeds.csv")
        require_unique(reference_datasets, "reference_dataset_id", "reference_datasets.csv")

        source_ids = {row["source_id"] for row in sources}
        candidate_ids = {row["candidate_id"] for row in candidates}
        poll_ids = {row["poll_id"] for row in polls}

        for row in sources:
            if not URL_RE.match(row["url"]):
                errors.append(f"Invalid source URL for {row['source_id']}: {row['url']}")
            if row["status"] not in VALID_SOURCE_STATUS:
                errors.append(f"Invalid source status for {row['source_id']}: {row['status']}")
            if row["collection_method"] not in VALID_COLLECTION_METHOD:
                errors.append(f"Invalid collection_method for {row['source_id']}: {row['collection_method']}")
            if row["primary_or_secondary"] not in VALID_SOURCE_LEVEL:
                errors.append(f"Invalid primary_or_secondary for {row['source_id']}: {row['primary_or_secondary']}")

        for row in source_feeds:
            if row["source_id"] not in source_ids:
                errors.append(f"Unknown source_id in source_feeds.csv: {row['source_id']}")
            if not URL_RE.match(row["url"]):
                errors.append(f"Invalid feed URL for {row['feed_id']}: {row['url']}")
            if row["feed_type"] not in VALID_FEED_TYPE:
                errors.append(f"Invalid feed_type for {row['feed_id']}: {row['feed_type']}")
            if row["collection_method"] not in VALID_COLLECTION_METHOD:
                errors.append(f"Invalid collection_method for {row['feed_id']}: {row['collection_method']}")
            if row["automation_stage"] not in VALID_AUTOMATION_STAGE:
                errors.append(f"Invalid automation_stage for {row['feed_id']}: {row['automation_stage']}")
            if row["status"] not in VALID_SOURCE_STATUS:
                errors.append(f"Invalid feed status for {row['feed_id']}: {row['status']}")
            if row["refresh_cadence"] not in VALID_REFRESH_CADENCE:
                errors.append(f"Invalid refresh_cadence for {row['feed_id']}: {row['refresh_cadence']}")
            if row["review_required"] not in VALID_BOOLEAN:
                errors.append(f"Invalid review_required for {row['feed_id']}: {row['review_required']}")

        for row in reference_datasets:
            if row["source_id"] not in source_ids:
                errors.append(f"Unknown source_id in reference_datasets.csv: {row['source_id']}")
            if not URL_RE.match(row["url"]):
                errors.append(f"Invalid reference dataset URL for {row['reference_dataset_id']}: {row['url']}")
            if row["status"] not in VALID_SOURCE_STATUS:
                errors.append(f"Invalid reference dataset status for {row['reference_dataset_id']}: {row['status']}")
            if row["reference_type"] not in VALID_REFERENCE_TYPE:
                errors.append(f"Invalid reference_type for {row['reference_dataset_id']}: {row['reference_type']}")
            if not DATE_RE.match(row["last_verified_at"]):
                errors.append(f"Invalid last_verified_at for {row['reference_dataset_id']}: {row['last_verified_at']}")

        for row in candidates:
            if row["source_id"] not in source_ids:
                errors.append(f"Unknown source_id in candidates.csv: {row['source_id']}")
            if not HEX_RE.match(row["color_hex"]):
                errors.append(f"Invalid color_hex for {row['candidate_id']}: {row['color_hex']}")

        for row in events:
            if row["source_id"] not in source_ids:
                errors.append(f"Unknown source_id in campaign_events.csv: {row['source_id']}")
            if row["candidate_id"] not in candidate_ids:
                errors.append(f"Unknown candidate_id in campaign_events.csv: {row['candidate_id']}")
            if not DATE_RE.match(row["event_date"]):
                errors.append(f"Invalid event_date for {row['event_id']}: {row['event_date']}")
            try:
                float(row["latitude"])
                float(row["longitude"])
            except ValueError:
                errors.append(f"Invalid coordinates for {row['event_id']}")

        for row in polls:
            if row["source_id"] not in source_ids:
                errors.append(f"Unknown source_id in polls_metadata.csv: {row['source_id']}")
            if not DATE_RE.match(row["publication_date"]):
                errors.append(f"Invalid publication_date for {row['poll_id']}: {row['publication_date']}")

        for row in poll_results:
            if row["poll_id"] not in poll_ids:
                errors.append(f"Unknown poll_id in poll_candidate_results.csv: {row['poll_id']}")
            if row["candidate_id"] not in candidate_ids:
                errors.append(f"Unknown candidate_id in poll_candidate_results.csv: {row['candidate_id']}")
            if row["source_id"] not in source_ids:
                errors.append(f"Unknown source_id in poll_candidate_results.csv: {row['source_id']}")
            try:
                float(row["poll_value"])
            except ValueError:
                errors.append(f"Invalid poll_value for {row['poll_result_id']}: {row['poll_value']}")

    except AssertionError as e:
        errors.append(str(e))

    if errors:
        print("VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        sys.exit(1)

    print("VALIDATION PASSED")
    print(f"Sources: {len(sources)}")
    print(f"Candidates: {len(candidates)}")
    print(f"Events: {len(events)}")
    print(f"Polls: {len(polls)}")
    print(f"Poll result rows: {len(poll_results)}")
    print(f"Source feeds: {len(source_feeds)}")
    print(f"Reference datasets: {len(reference_datasets)}")


if __name__ == "__main__":
    main()


