import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
STAGING = ROOT / "staging"
OUT = ROOT / "docs" / "data" / "dashboard_sample.json"


def read_csv(name):
    path = DATA / name
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_optional_csv(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def to_number(value):
    if value is None or value == "":
        return None
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value



def normalize_timestamp(value):
    value = (value or "").strip()
    if not value:
        return None

    if len(value) == 10 and value[4] == "-" and value[7] == "-":
        return f"{value}T00:00:00Z"

    if value.endswith("+00:00"):
        return value[:-6] + "Z"

    return value


def collect_row_timestamps(rows):
    fields = (
        "captured_at",
        "updated_at",
        "last_verified_at",
        "status_as_of",
        "status_date",
        "detected_at",
        "published_at",
        "publication_date",
    )

    values = []
    for row in rows:
        for field in fields:
            value = normalize_timestamp(row.get(field))
            if value:
                values.append(value)

    return values


def latest_dataset_timestamp(row_groups, poll_notice_status):
    values = []
    for rows in row_groups:
        values.extend(collect_row_timestamps(rows))

    poll_latest = normalize_timestamp(poll_notice_status.get("latest_detected_at"))
    if poll_latest:
        values.append(poll_latest)

    return max(values) if values else "2026-06-27T12:00:00Z"

def summarize_poll_notices(polls, poll_results):
    triaged_path = STAGING / "poll_notices_triaged_review.csv"
    raw_path = STAGING / "poll_notices_review.csv"

    rows = read_optional_csv(triaged_path)
    source_file = "staging/poll_notices_triaged_review.csv"

    if not rows:
        rows = read_optional_csv(raw_path)
        source_file = "staging/poll_notices_review.csv"

    triage_counts = Counter(row.get("triage_label") or "untriaged" for row in rows)
    priority_counts = Counter(row.get("review_priority") or "untriaged" for row in rows)

    detected_values = [
        row.get("detected_at")
        for row in rows
        if row.get("detected_at")
    ]

    high_priority_rows = [
        row for row in rows
        if row.get("review_priority") == "high"
    ]

    candidate_values_extracted = any(
        (row.get("candidate_level_values_extracted") or "").lower() == "true"
        for row in rows
    )

    return {
        "status_label": "review_queue_active" if rows else "no_staged_notices",
        "source_name": "Commission des sondages",
        "source_file": source_file,
        "total_staged_notices": len(rows),
        "high_priority_review_count": len(high_priority_rows),
        "canonical_poll_metadata_rows": len(polls),
        "canonical_poll_result_rows": len(poll_results),
        "candidate_level_values_extracted": candidate_values_extracted,
        "latest_detected_at": max(detected_values) if detected_values else None,
        "triage_counts": dict(sorted(triage_counts.items())),
        "review_priority_counts": dict(sorted(priority_counts.items())),
        "high_priority_examples": [
            {
                "poll_notice_stage_id": row.get("poll_notice_stage_id"),
                "link_text": row.get("link_text"),
                "notice_url": row.get("notice_url"),
                "triage_label": row.get("triage_label"),
            }
            for row in high_priority_rows[:5]
        ],
        "note": "Staged poll-notice discovery only. Candidate-level poll values are not extracted or displayed."
    }


def main():
    candidates = read_csv("candidates.csv")
    events = read_csv("campaign_events.csv")
    polls = read_csv("polls_metadata.csv")
    poll_results = read_csv("poll_candidate_results.csv")
    official_documents = read_csv("official_documents.csv")
    candidate_status_rows = read_csv("candidate_status_log.csv")

    latest_poll = polls[0] if polls else {}

    poll_by_candidate = {
        row["candidate_id"]: row
        for row in poll_results
        if row.get("poll_id") == latest_poll.get("poll_id")
    }

    dashboard_candidates = []
    for candidate in candidates:
        poll_row = poll_by_candidate.get(candidate["candidate_id"], {})
        dashboard_candidates.append({
            "candidate_id": candidate["candidate_id"],
            "display_name": candidate["display_name"],
            "party": candidate["party"],
            "bloc": candidate["bloc"],
            "current_status": candidate["current_status"],
            "color_hex": candidate["color_hex"],
            "latest_poll": to_number(poll_row.get("poll_value")),
            "poll_change": to_number(poll_row.get("change_vs_previous_comparable")),
            "poll_unit": poll_row.get("unit") or "%"
        })

    dashboard_events = []
    for event in events:
        dashboard_events.append({
            "event_id": event["event_id"],
            "event_date": event["event_date"],
            "event_type": event["event_type"],
            "title": event["title"],
            "candidate_id": event["candidate_id"],
            "candidate_name": event["candidate_name"],
            "location_name": event["location_name"],
            "commune": event["commune"],
            "region": event["region"],
            "latitude": float(event["latitude"]),
            "longitude": float(event["longitude"]),
            "source_name": event["source_name"],
            "source_url": event["source_url"],
            "verification_status": event["verification_status"]
        })

    dashboard_events = sorted(
        dashboard_events,
        key=lambda row: (
            row.get("event_date") or "",
            row.get("event_time") or "",
            row.get("event_id") or "",
        ),
    )

    poll_notice_status = summarize_poll_notices(polls, poll_results)
    dataset_updated_at = latest_dataset_timestamp(
        [candidates, events, official_documents, candidate_status_rows],
        poll_notice_status,
    )

    payload = {
        "updated_at": dataset_updated_at,
        "dataset_updated_at": dataset_updated_at,
        "poll_notice_latest_detected_at": poll_notice_status.get("latest_detected_at"),
        "timestamp_note": "updated_at and dataset_updated_at are derived from the latest canonical or staged-row timestamp. poll_notice_latest_detected_at is poll-notice discovery time.",
        "project": "France 2027 Monitor",
        "data_layer": "FR27 Open Data",
        "status": "prototype",
        "candidates": dashboard_candidates,
        "events": dashboard_events,
        "latest_poll": {
            "poll_id": latest_poll.get("poll_id"),
            "institute": latest_poll.get("institute"),
            "publisher": latest_poll.get("publisher"),
            "publication_date": latest_poll.get("publication_date"),
            "fieldwork": f"{latest_poll.get('fieldwork_start')} to {latest_poll.get('fieldwork_end')}",
            "sample_size": latest_poll.get("sample_size"),
            "notice_url": latest_poll.get("commission_notice_url"),
            "note": latest_poll.get("notes")
        },
        "poll_notice_status": poll_notice_status
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Wrote {OUT.relative_to(ROOT)}")
    print(f"Candidates: {len(dashboard_candidates)}")
    print(f"Events: {len(dashboard_events)}")
    print(f"Canonical poll metadata rows: {len(polls)}")
    print(f"Canonical poll result rows: {len(poll_results)}")
    print(f"Staged poll notices: {poll_notice_status['total_staged_notices']}")
    print(f"High-priority poll notice review rows: {poll_notice_status['high_priority_review_count']}")
    print(f"Candidate-level values extracted: {poll_notice_status['candidate_level_values_extracted']}")


if __name__ == "__main__":
    main()
