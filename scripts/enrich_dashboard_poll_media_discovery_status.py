from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


DASHBOARD_PATH = Path("docs") / "data" / "dashboard_sample.json"
MENTIONS_PATH = Path("staging") / "poll_media_mentions.csv"
QUERY_FEEDS_PATH = Path("staging") / "poll_media_query_feeds.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main() -> int:
    dashboard = json.loads(DASHBOARD_PATH.read_text(encoding="utf-8"))

    mentions = read_csv(MENTIONS_PATH)
    query_feeds = read_csv(QUERY_FEEDS_PATH)

    priority_counts = Counter(row.get("review_priority", "") for row in mentions)
    label_counts = Counter(row.get("poll_relevance_label", "") for row in mentions)
    decision_counts = Counter(row.get("review_decision", "") for row in mentions)

    candidate_values_extracted = any(
        row.get("candidate_level_values_extracted") != "false"
        for row in mentions
    )

    latest_detected_at = ""
    detected_values = [
        row.get("detected_at", "")
        for row in mentions
        if row.get("detected_at", "")
    ]
    if detected_values:
        latest_detected_at = max(detected_values)

    high_priority_examples = [
        {
            "source_name": row.get("source_name", ""),
            "article_title": row.get("article_title", ""),
            "article_url": row.get("article_url", ""),
            "published_at": row.get("published_at", ""),
            "possible_institute": row.get("possible_institute", ""),
        }
        for row in mentions
        if row.get("review_priority") == "high"
    ][:3]

    media_status = {
        "source_file": str(MENTIONS_PATH).replace("\\", "/"),
        "query_feed_file": str(QUERY_FEEDS_PATH).replace("\\", "/"),
        "query_feed_count": len(query_feeds),
        "total_media_mentions": len(mentions),
        "high_priority_count": priority_counts.get("high", 0),
        "medium_priority_count": priority_counts.get("medium", 0),
        "low_priority_count": priority_counts.get("low", 0),
        "pending_review_count": decision_counts.get("pending", 0),
        "promote_to_metadata_review_count": decision_counts.get("promote_to_metadata_review", 0),
        "candidate_level_values_extracted": candidate_values_extracted,
        "latest_detected_at": latest_detected_at,
        "priority_counts": dict(priority_counts),
        "label_counts": dict(label_counts),
        "review_decision_counts": dict(decision_counts),
        "high_priority_examples": high_priority_examples,
        "note": "Staged media-discovery metadata only. No article scraping and no candidate-level poll values.",
    }

    poll_status = dashboard.setdefault("poll_notice_status", {})
    poll_status["media_discovery_status"] = media_status

    DASHBOARD_PATH.write_text(
        json.dumps(dashboard, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print("Enriched dashboard with poll media discovery status")
    print("Query feeds:", len(query_feeds))
    print("Media mentions:", len(mentions))
    print("High priority:", priority_counts.get("high", 0))
    print("Pending review:", decision_counts.get("pending", 0))
    print("Candidate-level values extracted:", candidate_values_extracted)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
