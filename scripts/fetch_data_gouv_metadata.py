import csv
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
STAGING = ROOT / "staging"
RAW_DIR = STAGING / "raw" / "data_gouv"
OUT = STAGING / "fetched_dataset_metadata.csv"

FIELDS = [
    "fetch_id",
    "feed_id",
    "source_id",
    "feed_name",
    "url",
    "dataset_id",
    "title",
    "slug",
    "organization",
    "page",
    "created_at",
    "last_modified",
    "resources_count",
    "license",
    "raw_json_path",
    "fetched_at",
    "status",
    "notes",
]


def read_feeds():
    with (DATA / "source_feeds.csv").open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def fetch_json(url):
    req = Request(url, headers={"User-Agent": "FR27 Open Data prototype metadata fetcher"})
    with urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def value_from_object(value, *keys):
    if isinstance(value, dict):
        for key in keys:
            if value.get(key):
                return value.get(key)
        return ""
    if isinstance(value, str):
        return value
    return ""


def normalize_dataset_rows(feed, payload, raw_path, fetched_at):
    rows = []

    if isinstance(payload, dict) and "data" in payload and isinstance(payload["data"], list):
        datasets = payload["data"]
    elif isinstance(payload, dict):
        datasets = [payload]
    else:
        datasets = []

    for item in datasets:
        if not isinstance(item, dict):
            continue

        dataset_id = item.get("id") or item.get("slug") or ""
        fetch_key = f"{feed['feed_id']}::{dataset_id}"
        fetch_id = hashlib.sha1(fetch_key.encode("utf-8")).hexdigest()[:16]

        rows.append({
            "fetch_id": fetch_id,
            "feed_id": feed["feed_id"],
            "source_id": feed["source_id"],
            "feed_name": feed["feed_name"],
            "url": feed["url"],
            "dataset_id": dataset_id,
            "title": item.get("title") or "",
            "slug": item.get("slug") or "",
            "organization": value_from_object(item.get("organization"), "name", "id", "slug"),
            "page": item.get("page") or "",
            "created_at": item.get("created_at") or "",
            "last_modified": item.get("last_modified") or "",
            "resources_count": len(item.get("resources") or []),
            "license": value_from_object(item.get("license"), "title", "id"),
            "raw_json_path": str(raw_path.relative_to(ROOT)),
            "fetched_at": fetched_at,
            "status": "fetched",
            "notes": "Staged metadata only; not canonical data",
        })

    return rows


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    fetched_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    feeds = [
        row for row in read_feeds()
        if row.get("feed_type") == "api"
        and row.get("status") == "active"
        and "data.gouv.fr/api/" in row.get("url", "")
    ]

    all_rows = []

    for feed in feeds:
        print(f"Fetching {feed['feed_id']}")

        try:
            payload = fetch_json(feed["url"])
            raw_path = RAW_DIR / f"{feed['feed_id']}.json"
            raw_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

            all_rows.extend(normalize_dataset_rows(feed, payload, raw_path, fetched_at))

        except Exception as exc:
            all_rows.append({
                "fetch_id": hashlib.sha1(feed["feed_id"].encode("utf-8")).hexdigest()[:16],
                "feed_id": feed["feed_id"],
                "source_id": feed["source_id"],
                "feed_name": feed["feed_name"],
                "url": feed["url"],
                "dataset_id": "",
                "title": "",
                "slug": "",
                "organization": "",
                "page": "",
                "created_at": "",
                "last_modified": "",
                "resources_count": "",
                "license": "",
                "raw_json_path": "",
                "fetched_at": fetched_at,
                "status": "fetch_failed",
                "notes": str(exc),
            })

    with OUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"Wrote {OUT.relative_to(ROOT)}")
    print(f"Feeds checked: {len(feeds)}")
    print(f"Rows staged: {len(all_rows)}")


if __name__ == "__main__":
    main()

