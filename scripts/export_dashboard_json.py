import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "docs" / "data" / "dashboard_sample.json"


def read_csv(name):
    path = DATA / name
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


def main():
    candidates = read_csv("candidates.csv")
    events = read_csv("campaign_events.csv")
    polls = read_csv("polls_metadata.csv")
    poll_results = read_csv("poll_candidate_results.csv")

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

    payload = {
        "updated_at": "2026-06-27T12:00:00Z",
        "project": "FR27 Open Data",
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
        }
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")
    print(f"Candidates: {len(dashboard_candidates)}")
    print(f"Events: {len(dashboard_events)}")


if __name__ == "__main__":
    main()
