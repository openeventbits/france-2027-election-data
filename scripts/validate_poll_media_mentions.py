from __future__ import annotations

import csv
import re
from pathlib import Path


QUERY_FEEDS_PATH = Path("staging") / "poll_media_query_feeds.csv"
MENTIONS_PATH = Path("staging") / "poll_media_mentions.csv"

EXPECTED_FEED_COLUMNS = [
    "feed_id",
    "source_id",
    "feed_name",
    "feed_type",
    "url",
    "topic",
    "collection_method",
    "automation_stage",
    "status",
    "refresh_cadence",
    "review_required",
    "notes",
    "last_checked_at",
]

EXPECTED_MENTION_COLUMNS = [
    "poll_media_mention_id",
    "feed_id",
    "query",
    "source_name",
    "article_title",
    "article_url",
    "published_at",
    "detected_at",
    "possible_institute",
    "review_priority",
    "poll_relevance_label",
    "candidate_level_values_extracted",
    "review_decision",
    "review_notes",
]

ALLOWED_PRIORITIES = {"high", "medium", "low"}
ALLOWED_LABELS = {
    "likely_poll_media_mention",
    "possible_poll_media_mention",
    "context_only",
}
ALLOWED_REVIEW_DECISIONS = {
    "pending",
    "defer",
    "reject",
    "reviewed_context_only",
    "promote_to_metadata_review",
}

FORBIDDEN_VALUE_PATTERNS = [
    re.compile(r"\b\d{1,2}(?:[,.]\d)?\s?%"),
    re.compile(r"\b\d{1,2}(?:[,.]\d)?\s+points?\b", re.I),
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"Missing required file: {path}")

    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        columns = reader.fieldnames or []

    return rows, columns


def check_columns(path: Path, columns: list[str], expected: list[str]) -> None:
    if columns != expected:
        raise SystemExit(
            f"{path} has unexpected columns.\nExpected: {expected}\nFound: {columns}"
        )


def check_no_candidate_values(row: dict[str, str], row_number: int) -> None:
    searchable_fields = [
        "article_title",
        "source_name",
        "possible_institute",
        "review_notes",
    ]

    for field in searchable_fields:
        value = row.get(field, "")
        for pattern in FORBIDDEN_VALUE_PATTERNS:
            if pattern.search(value):
                raise SystemExit(
                    f"Possible candidate-level poll value found in row {row_number}, field {field}: {value}"
                )


def main() -> int:
    feed_rows, feed_columns = read_csv(QUERY_FEEDS_PATH)
    mention_rows, mention_columns = read_csv(MENTIONS_PATH)

    check_columns(QUERY_FEEDS_PATH, feed_columns, EXPECTED_FEED_COLUMNS)
    check_columns(MENTIONS_PATH, mention_columns, EXPECTED_MENTION_COLUMNS)

    if len(feed_rows) != 3:
        raise SystemExit(f"Expected exactly 3 poll media query feeds, found {len(feed_rows)}")

    if len(mention_rows) > 30:
        raise SystemExit(f"Expected at most 30 poll media mentions, found {len(mention_rows)}")

    seen_ids = set()
    seen_urls = set()

    for i, row in enumerate(feed_rows, start=2):
        if row.get("feed_type") != "rss":
            raise SystemExit(f"Feed row {i} feed_type must be rss")
        if row.get("topic") != "poll_media_discovery":
            raise SystemExit(f"Feed row {i} topic must be poll_media_discovery")
        if row.get("automation_stage") != "staging":
            raise SystemExit(f"Feed row {i} automation_stage must be staging")
        if row.get("review_required") != "true":
            raise SystemExit(f"Feed row {i} review_required must be true")

    for i, row in enumerate(mention_rows, start=2):
        mention_id = row.get("poll_media_mention_id", "")
        article_url = row.get("article_url", "")

        if not mention_id.startswith("poll_media_mention_"):
            raise SystemExit(f"Row {i} has invalid poll_media_mention_id: {mention_id}")

        if mention_id in seen_ids:
            raise SystemExit(f"Duplicate poll_media_mention_id in row {i}: {mention_id}")
        seen_ids.add(mention_id)

        if article_url:
            if article_url in seen_urls:
                raise SystemExit(f"Duplicate article_url in row {i}: {article_url}")
            seen_urls.add(article_url)

        if row.get("candidate_level_values_extracted") != "false":
            raise SystemExit(f"Row {i} candidate_level_values_extracted must be false")

        if row.get("review_priority") not in ALLOWED_PRIORITIES:
            raise SystemExit(f"Row {i} invalid review_priority: {row.get('review_priority')}")

        if row.get("poll_relevance_label") not in ALLOWED_LABELS:
            raise SystemExit(f"Row {i} invalid poll_relevance_label: {row.get('poll_relevance_label')}")

        if row.get("review_decision") not in ALLOWED_REVIEW_DECISIONS:
            raise SystemExit(f"Row {i} invalid review_decision: {row.get('review_decision')}")

        check_no_candidate_values(row, i)

    print("POLL MEDIA DISCOVERY VALIDATION PASSED")
    print(f"Query feeds: {len(feed_rows)}")
    print(f"Media mentions: {len(mention_rows)}")
    print("Candidate-level values extracted: false")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
