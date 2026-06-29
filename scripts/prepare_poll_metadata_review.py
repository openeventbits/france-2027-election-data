import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IN_PATH = ROOT / "staging" / "poll_notices_triaged_review.csv"
OUT_PATH = ROOT / "staging" / "poll_metadata_high_priority_review.csv"

OUT_FIELDS = [
    "review_queue_id",
    "source_poll_notice_stage_id",
    "notice_url",
    "notice_link_text",
    "triage_label",
    "review_priority",
    "suggested_metadata_scope",
    "source_id",

    # Canonical polls_metadata.csv fields to fill manually after review.
    "poll_id",
    "institute",
    "sponsor",
    "publisher",
    "publication_date",
    "fieldwork_start",
    "fieldwork_end",
    "sample_size",
    "population",
    "method",
    "round_type",
    "scenario",
    "commission_notice_url",
    "public_report_url",
    "verification_status",
    "notes",
    "captured_at",
    "updated_at",

    # Review-control fields.
    "metadata_review_decision",
    "ready_for_canonical_metadata",
    "candidate_level_values_extracted",
    "review_notes",
    "canonical_promotion_notes",
    "created_at",
]

PRESERVE_FIELDS = [
    "poll_id",
    "institute",
    "sponsor",
    "publisher",
    "publication_date",
    "fieldwork_start",
    "fieldwork_end",
    "sample_size",
    "population",
    "method",
    "round_type",
    "scenario",
    "public_report_url",
    "verification_status",
    "notes",
    "captured_at",
    "updated_at",
    "metadata_review_decision",
    "ready_for_canonical_metadata",
    "review_notes",
    "canonical_promotion_notes",
    "created_at",
]


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stable_id(value):
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]
    return f"poll_metadata_review_{digest}"


def read_csv(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUT_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    triaged_rows = read_csv(IN_PATH)
    existing_rows = read_csv(OUT_PATH)

    existing_by_notice_url = {
        row.get("notice_url"): row
        for row in existing_rows
        if row.get("notice_url")
    }

    now = utc_now()

    high_priority = [
        row for row in triaged_rows
        if row.get("review_priority") == "high"
        and row.get("triage_label") == "likely_presidential_voting_intention_notice"
    ]

    out_rows = []
    preserved = 0
    new_rows = 0

    for row in high_priority:
        notice_url = row.get("notice_url", "")
        existing = existing_by_notice_url.get(notice_url, {})

        if existing:
            preserved += 1
        else:
            new_rows += 1

        out = {
            "review_queue_id": stable_id(notice_url),
            "source_poll_notice_stage_id": row.get("poll_notice_stage_id", ""),
            "notice_url": notice_url,
            "notice_link_text": row.get("link_text", ""),
            "triage_label": row.get("triage_label", ""),
            "review_priority": row.get("review_priority", ""),
            "suggested_metadata_scope": row.get("suggested_metadata_scope", ""),
            "source_id": row.get("source_id", ""),

            "poll_id": "",
            "institute": "",
            "sponsor": "",
            "publisher": "",
            "publication_date": "",
            "fieldwork_start": "",
            "fieldwork_end": "",
            "sample_size": "",
            "population": "",
            "method": "",
            "round_type": "",
            "scenario": "",
            "commission_notice_url": notice_url,
            "public_report_url": "",
            "verification_status": "needs_review",
            "notes": "Metadata-only review queue. Do not enter candidate-level poll values here.",
            "captured_at": row.get("detected_at", ""),
            "updated_at": "",

            "metadata_review_decision": "pending",
            "ready_for_canonical_metadata": "false",
            "candidate_level_values_extracted": "false",
            "review_notes": "Open Commission des sondages notice and verify metadata only.",
            "canonical_promotion_notes": "",
            "created_at": now,
        }

        for field in PRESERVE_FIELDS:
            if existing.get(field):
                out[field] = existing[field]

        # Hard safety invariants.
        out["candidate_level_values_extracted"] = "false"
        if out["ready_for_canonical_metadata"].lower() not in {"true", "false"}:
            out["ready_for_canonical_metadata"] = "false"

        out_rows.append(out)

    out_rows = sorted(out_rows, key=lambda item: item["notice_url"])

    write_csv(OUT_PATH, out_rows)

    print(f"Wrote {OUT_PATH.relative_to(ROOT)}")
    print(f"High-priority metadata review rows: {len(out_rows)}")
    print(f"Existing review rows preserved: {preserved}")
    print(f"New review rows created: {new_rows}")
    print("Candidate-level values extracted: false")

    if out_rows:
        print()
        print("Review queue examples:")
        for row in out_rows[:7]:
            print(f"- {row['review_queue_id']} | {row['notice_link_text'][:90]} | {row['notice_url']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
