from __future__ import annotations

import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path


MENTIONS_PATH = Path("staging") / "poll_media_mentions.csv"
QUEUE_PATH = Path("staging") / "poll_media_source_resolution_queue.csv"

FIELDNAMES = [
    "source_resolution_id",
    "poll_media_mention_id",
    "source_name",
    "article_title",
    "article_url",
    "published_at",
    "possible_institute",
    "media_review_decision",
    "candidate_level_values_extracted",
    "resolution_status",
    "resolved_source_type",
    "resolved_source_name",
    "resolved_source_url",
    "matched_commission_notice_url",
    "matched_pollster_publication_url",
    "methodology_url",
    "ready_for_metadata_review",
    "metadata_review_action",
    "canonical_poll_metadata_written",
    "resolution_notes",
    "created_at",
    "last_reviewed_at",
]

ALLOWED_RESOLUTION_STATUS = {
    "pending",
    "resolved_official_notice",
    "resolved_pollster_publication",
    "resolved_methodology_page",
    "defer_media_only",
    "reject_not_suitable",
}

ALLOWED_SOURCE_TYPES = {
    "",
    "official_notice",
    "pollster_publication",
    "methodology_page",
    "media_only",
    "unknown",
}

ALLOWED_METADATA_ACTIONS = {
    "pending",
    "promote_to_poll_metadata_review",
    "defer",
    "reject",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stable_id(value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]
    return f"poll_media_source_resolution_{digest}"


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def load_existing_queue(path: Path) -> dict[str, dict[str, str]]:
    existing = {}
    for row in read_csv(path):
        key = row.get("poll_media_mention_id", "")
        if key:
            existing[key] = row
    return existing


def validate_row(row: dict[str, str], row_number: int) -> None:
    if row.get("media_review_decision") != "promote_to_metadata_review":
        raise SystemExit(f"Row {row_number} is not promoted from media review.")

    if row.get("candidate_level_values_extracted") != "false":
        raise SystemExit(f"Row {row_number} candidate_level_values_extracted must be false.")

    if row.get("resolution_status") not in ALLOWED_RESOLUTION_STATUS:
        raise SystemExit(f"Row {row_number} invalid resolution_status: {row.get('resolution_status')}")

    if row.get("resolved_source_type") not in ALLOWED_SOURCE_TYPES:
        raise SystemExit(f"Row {row_number} invalid resolved_source_type: {row.get('resolved_source_type')}")

    if row.get("metadata_review_action") not in ALLOWED_METADATA_ACTIONS:
        raise SystemExit(f"Row {row_number} invalid metadata_review_action: {row.get('metadata_review_action')}")

    if row.get("canonical_poll_metadata_written") != "false":
        raise SystemExit(f"Row {row_number} canonical_poll_metadata_written must remain false.")

    if row.get("ready_for_metadata_review") not in {"false", "true"}:
        raise SystemExit(f"Row {row_number} ready_for_metadata_review must be true/false.")


def main() -> int:
    mentions = read_csv(MENTIONS_PATH)
    existing = load_existing_queue(QUEUE_PATH)
    generated_at = now_utc()

    promoted = [
        row for row in mentions
        if row.get("review_decision") == "promote_to_metadata_review"
    ]

    rows: list[dict[str, str]] = []

    for mention in promoted:
        mention_id = mention.get("poll_media_mention_id", "")
        previous = existing.get(mention_id, {})

        row = {
            "source_resolution_id": previous.get("source_resolution_id") or stable_id(mention_id),
            "poll_media_mention_id": mention_id,
            "source_name": mention.get("source_name", ""),
            "article_title": mention.get("article_title", ""),
            "article_url": mention.get("article_url", ""),
            "published_at": mention.get("published_at", ""),
            "possible_institute": mention.get("possible_institute", ""),
            "media_review_decision": mention.get("review_decision", ""),
            "candidate_level_values_extracted": "false",
            "resolution_status": previous.get("resolution_status") or "pending",
            "resolved_source_type": previous.get("resolved_source_type") or "",
            "resolved_source_name": previous.get("resolved_source_name") or "",
            "resolved_source_url": previous.get("resolved_source_url") or "",
            "matched_commission_notice_url": previous.get("matched_commission_notice_url") or "",
            "matched_pollster_publication_url": previous.get("matched_pollster_publication_url") or "",
            "methodology_url": previous.get("methodology_url") or "",
            "ready_for_metadata_review": previous.get("ready_for_metadata_review") or "false",
            "metadata_review_action": previous.get("metadata_review_action") or "pending",
            "canonical_poll_metadata_written": "false",
            "resolution_notes": previous.get("resolution_notes") or "",
            "created_at": previous.get("created_at") or generated_at,
            "last_reviewed_at": previous.get("last_reviewed_at") or "",
        }

        rows.append(row)

    for i, row in enumerate(rows, start=2):
        validate_row(row, i)

    QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with QUEUE_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    print("Poll media source-resolution queue prepared")
    print("Promoted media mentions:", len(promoted))
    print("Resolution queue rows:", len(rows))
    print("Ready for metadata review:", sum(1 for r in rows if r["ready_for_metadata_review"] == "true"))
    print("Canonical poll metadata written:", sum(1 for r in rows if r["canonical_poll_metadata_written"] == "true"))
    print("Candidate-level values extracted: false")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
