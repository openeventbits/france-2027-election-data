from __future__ import annotations

import csv
import hashlib
import html
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

MAX_ROWS = 30

QUERIES = [
    ("poll_media_presidentielle_2027_sondage", '"presidentielle 2027" sondage when:90d'),
    ("poll_media_intention_vote_2027", '"intention de vote" "presidentielle 2027" when:90d'),
    ("poll_media_second_tour_2027", '"second tour" "presidentielle 2027" sondage when:90d'),
]

POLLSTERS = [
    "IFOP", "Ipsos", "BVA", "OpinionWay", "Elabe", "Odoxa",
    "Cluster17", "Toluna", "Harris", "Harris Interactive"
]

FIELDS = [
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

FEED_FIELDS = [
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


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def rss_url(query: str) -> str:
    return "https://news.google.com/rss/search?q=" + quote_plus(query) + "&hl=fr&gl=FR&ceid=FR:fr"


def clean_text(value: str) -> str:
    value = html.unescape(value or "")
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    value = re.sub(r"\b\d{1,2}(?:[,.]\d)?\s?%", "[poll-value-hidden]", value)
    value = re.sub(r"\b\d{1,2}(?:[,.]\d)?\s+points?\b", "[poll-delta-hidden]", value, flags=re.I)
    return value[:240]


def parse_date(value: str) -> str:
    if not value:
        return ""
    try:
        dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return clean_text(value)


def make_id(url: str, title: str) -> str:
    key = url or title
    return "poll_media_mention_" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def institute_from_text(text: str) -> str:
    found = []
    low = text.lower()
    for name in POLLSTERS:
        if name.lower() in low:
            found.append(name)
    return "; ".join(dict.fromkeys(found))


def classify(text: str, institute: str) -> tuple[str, str]:
    low = text.lower()
    pollish = any(x in low for x in ["sondage", "intention de vote", "intentions de vote", "second tour"])
    presidential = "2027" in low and ("presidentielle" in low or "présidentielle" in low)

    if pollish and presidential and institute:
        return "high", "likely_poll_media_mention"
    if pollish and presidential:
        return "medium", "possible_poll_media_mention"
    return "low", "context_only"


def fetch(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": "FR27-Open-Data/0.1"})
    with urlopen(req, timeout=25) as response:
        return response.read()


def load_existing_mentions(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}

    rows = list(csv.DictReader(path.open(encoding="utf-8-sig", newline="")))
    existing: dict[str, dict[str, str]] = {}

    for row in rows:
        key = row.get("article_url") or row.get("poll_media_mention_id")
        if key:
            existing[key] = row

    return existing


def main() -> int:
    staging = Path("staging")
    staging.mkdir(exist_ok=True)

    detected_at = now_utc()
    mentions_path = staging / "poll_media_mentions.csv"
    existing_mentions = load_existing_mentions(mentions_path)

    feed_rows = []
    rows_by_url = {}

    for feed_id, query in QUERIES:
        url = rss_url(query)
        feed_rows.append({
            "feed_id": feed_id,
            "source_id": "src_google_news_fr_discovery",
            "feed_name": feed_id.replace("_", " "),
            "feed_type": "rss",
            "url": url,
            "topic": "poll_media_discovery",
            "collection_method": "automated",
            "automation_stage": "staging",
            "status": "active",
            "refresh_cadence": "manual",
            "review_required": "true",
            "notes": "Discovery metadata only. No article scraping and no candidate-level poll values.",
            "last_checked_at": detected_at[:10],
        })

        try:
            root = ET.fromstring(fetch(url))
        except Exception as exc:
            print(f"Fetch warning for {feed_id}: {exc}")
            continue

        for item in root.findall(".//item"):
            title_raw = item.findtext("title", "")
            desc_raw = item.findtext("description", "")
            link = clean_text(item.findtext("link", ""))
            pub = parse_date(item.findtext("pubDate", ""))

            source_el = item.find("source")
            source_name = clean_text(source_el.text if source_el is not None and source_el.text else "")

            joined = " ".join([title_raw, desc_raw, query])
            institute = institute_from_text(joined)
            priority, label = classify(joined, institute)

            title = clean_text(title_raw)

            row_key = link or make_id(link, title)
            existing_row = existing_mentions.get(row_key, {})

            rows_by_url[row_key] = {
                "poll_media_mention_id": existing_row.get("poll_media_mention_id", make_id(link, title)),
                "feed_id": feed_id,
                "query": query,
                "source_name": source_name,
                "article_title": title,
                "article_url": link,
                "published_at": pub,
                "detected_at": existing_row.get("detected_at", detected_at),
                "possible_institute": institute,
                "review_priority": priority,
                "poll_relevance_label": label,
                "candidate_level_values_extracted": "false",
                "review_decision": existing_row.get("review_decision", "pending"),
                "review_notes": existing_row.get("review_notes", ""),
            }

    rows = list(rows_by_url.values())
    rows.sort(key=lambda r: (r["review_priority"] != "high", r["published_at"]), reverse=False)
    rows = rows[:MAX_ROWS]

    with (staging / "poll_media_query_feeds.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FEED_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(feed_rows)

    with mentions_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    print("Query feeds:", len(feed_rows))
    print("Media mentions:", len(rows))
    print("High priority:", sum(1 for r in rows if r["review_priority"] == "high"))
    print("Medium priority:", sum(1 for r in rows if r["review_priority"] == "medium"))
    print("Low priority:", sum(1 for r in rows if r["review_priority"] == "low"))
    print("Candidate-level values extracted: false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
