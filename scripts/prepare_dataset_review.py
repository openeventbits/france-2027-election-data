import csv
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


def read_csv(path):
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main():
    fetched_rows = read_csv(FETCHED)
    existing_review_rows = read_csv(REVIEW)

    existing_by_id = {
        row["fetch_id"]: row
        for row in existing_review_rows
        if row.get("fetch_id")
    }

    review_rows = []

    for fetched in fetched_rows:
        fetch_id = fetched["fetch_id"]

        if fetch_id in existing_by_id:
            review_rows.append(existing_by_id[fetch_id])
        else:
            review_rows.append({
                "fetch_id": fetch_id,
                "review_status": "pending",
                "relevance": "unclear",
                "review_note": "",
                "reviewed_by": "",
                "reviewed_at": "",
            })

    with REVIEW.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(review_rows)

    print(f"Wrote {REVIEW.relative_to(ROOT)}")
    print(f"Fetched rows: {len(fetched_rows)}")
    print(f"Review rows: {len(review_rows)}")
    print(f"Existing preserved: {len(existing_by_id)}")


if __name__ == "__main__":
    main()
