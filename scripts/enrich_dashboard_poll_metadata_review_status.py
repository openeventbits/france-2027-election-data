import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_PATH = ROOT / "docs" / "data" / "dashboard_sample.json"
REVIEW_PATH = ROOT / "staging" / "poll_metadata_high_priority_review.csv"


def read_csv(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main():
    if not DASHBOARD_PATH.exists():
        raise SystemExit(f"Missing dashboard JSON: {DASHBOARD_PATH}")

    dashboard = json.loads(DASHBOARD_PATH.read_text(encoding="utf-8"))
    poll_status = dashboard.setdefault("poll_notice_status", {})

    rows = read_csv(REVIEW_PATH)

    ready_count = sum(
        1 for row in rows
        if row.get("ready_for_canonical_metadata", "").lower() == "true"
    )
    pending_count = sum(
        1 for row in rows
        if row.get("metadata_review_decision", "") == "pending"
    )
    values_extracted = any(
        row.get("candidate_level_values_extracted", "").lower() == "true"
        for row in rows
    )

    examples = []
    for row in rows[:3]:
        examples.append({
            "review_queue_id": row.get("review_queue_id", ""),
            "notice_link_text": row.get("notice_link_text", ""),
            "notice_url": row.get("notice_url", ""),
            "metadata_review_decision": row.get("metadata_review_decision", ""),
            "ready_for_canonical_metadata": row.get("ready_for_canonical_metadata", ""),
        })

    poll_status["metadata_review_status"] = {
        "source_file": str(REVIEW_PATH.relative_to(ROOT)).replace("\\", "/"),
        "total_review_rows": len(rows),
        "pending_review_count": pending_count,
        "ready_for_canonical_metadata_count": ready_count,
        "candidate_level_values_extracted": values_extracted,
        "examples": examples,
        "note": "Metadata-only manual review queue. Candidate-level poll values are not stored here.",
    }

    DASHBOARD_PATH.write_text(
        json.dumps(dashboard, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print(f"Wrote {DASHBOARD_PATH.relative_to(ROOT)}")
    print(f"Metadata review rows: {len(rows)}")
    print(f"Pending review rows: {pending_count}")
    print(f"Ready for canonical metadata: {ready_count}")
    print(f"Candidate-level values extracted: {values_extracted}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
