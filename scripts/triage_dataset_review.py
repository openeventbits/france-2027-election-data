import csv
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGING = ROOT / "staging"
FETCHED = STAGING / "fetched_dataset_metadata.csv"
REVIEW = STAGING / "fetched_dataset_review.csv"

FIELDS = [
    "fetch_id",
    "review_status",
    "relevance",
    "review_note",
    "reviewed_by",
    "reviewed_at",
]


LOCAL_ORGS = [
    "mairie",
    "ville de",
    "métropole",
    "metropole",
    "commune",
    "départemental",
    "departemental",
    "gironde",
    "marseille",
    "toulouse",
    "dijon",
    "boé",
    "boe",
    "onet-le-château",
    "onet-le-chateau",
]

HISTORICAL_TERMS = [
    "1965",
    "1969",
    "1981",
    "1988",
    "2002",
    "2007",
    "2012",
    "2017",
    "2022",
]


def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def classify(row):
    text = " ".join([
        row.get("title", ""),
        row.get("slug", ""),
        row.get("organization", ""),
        row.get("feed_name", ""),
    ]).lower()

    if "conseil constitutionnel" in text and "parrainages" in text:
        return "likely_useful", "core", "Official Conseil constitutionnel parrainages dataset metadata."

    if any(term in text for term in LOCAL_ORGS):
        return "likely_noise", "local_noise", "Local or municipal dataset; not core FR27 MVP data."

    if "présidentielle" in text or "presidentielle" in text or "présidentielles" in text or "presidentielles" in text:
        if any(year in text for year in HISTORICAL_TERMS):
            return "likely_useful", "historical", "Historical presidential election dataset; useful as reference, not 2027 live data."
        return "needs_review", "supporting", "Presidential election dataset; requires review before use."

    return "needs_review", "unclear", "No conservative auto-triage rule matched."


def main():
    fetched_rows = read_csv(FETCHED)
    review_rows = read_csv(REVIEW)
    fetched_by_id = {row["fetch_id"]: row for row in fetched_rows}

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    output_rows = []

    for review in review_rows:
        fetch_id = review["fetch_id"]

        if review.get("review_status") not in {"pending", "likely_useful", "likely_noise", "needs_review"}:
            output_rows.append(review)
            continue

        fetched = fetched_by_id.get(fetch_id)
        if not fetched:
            review["review_status"] = "needs_review"
            review["relevance"] = "unclear"
            review["review_note"] = "Fetched row missing; review queue is out of sync."
        else:
            status, relevance, note = classify(fetched)
            review["review_status"] = status
            review["relevance"] = relevance
            review["review_note"] = note

        review["reviewed_by"] = "auto_triage"
        review["reviewed_at"] = now
        output_rows.append(review)

    write_csv(REVIEW, output_rows)

    counts = {}
    for row in output_rows:
        counts[row["review_status"]] = counts.get(row["review_status"], 0) + 1

    print(f"Wrote {REVIEW.relative_to(ROOT)}")
    for key in sorted(counts):
        print(f"{key}: {counts[key]}")


if __name__ == "__main__":
    main()
