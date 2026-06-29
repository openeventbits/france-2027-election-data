import csv
import hashlib
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
STAGING = ROOT / "staging"

FEED_ID = "feed_commission_sondages_notices"
OUT = STAGING / "poll_notices_review.csv"

# Conservative target for MVP automation:
# detect official Commission des sondages 2027 presidential notice/index links.
COMMISSION_2027_TAG_URL = (
    "https://www.commission-des-sondages.fr/notices/medias/fichiers/bytag/14/2027-Presidentielle"
)

USER_AGENT = (
    "FR27-Open-Data-poll-notice-watcher/0.4 "
    "(+https://github.com/openeventbits/france-2027-election-data)"
)

OUT_FIELDS = [
    "poll_notice_stage_id",
    "feed_id",
    "source_id",
    "source_name",
    "source_page_url",
    "notice_url",
    "link_text",
    "detected_at",
    "http_status",
    "content_type",
    "page_title",
    "match_reason",
    "candidate_level_values_extracted",
    "review_decision",
    "review_notes",
]


class LinkExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.in_title = False
        self.title_parts = []
        self.current_href = None
        self.current_text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag.lower() == "title":
            self.in_title = True
        if tag.lower() == "a":
            self.current_href = attrs.get("href")
            self.current_text = []

    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self.in_title = False
        if tag.lower() == "a" and self.current_href:
            text = re.sub(r"\s+", " ", "".join(self.current_text)).strip()
            self.links.append((self.current_href, text))
            self.current_href = None
            self.current_text = []

    def handle_data(self, data):
        if self.in_title:
            self.title_parts.append(data)
        if self.current_href:
            self.current_text.append(data)

    @property
    def title(self):
        return re.sub(r"\s+", " ", "".join(self.title_parts)).strip()


def read_csv(name):
    path = DATA / name
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def get_feed():
    feeds = read_csv("source_feeds.csv")
    matches = [row for row in feeds if row.get("feed_id") == FEED_ID]
    if not matches:
        raise RuntimeError(f"Feed not found in data/source_feeds.csv: {FEED_ID}")

    feed = matches[0]

    if feed.get("source_id") != "src_commission_sondages":
        raise RuntimeError(f"Unexpected source_id for {FEED_ID}: {feed.get('source_id')}")

    if feed.get("automation_stage") not in {"staging", "planned"}:
        raise RuntimeError(f"Feed is not approved for staging/planned automation: {feed.get('automation_stage')}")

    if feed.get("review_required") != "true":
        raise RuntimeError("Poll notice feed must require review.")

    return feed


def get_source_name(source_id):
    for row in read_csv("sources.csv"):
        if row.get("source_id") == source_id:
            return row.get("source_name") or source_id
    return source_id


def fetch_page(url):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT},
        method="GET",
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        status = getattr(response, "status", "")
        final_url = response.geturl()
        content_type = response.headers.get("Content-Type", "")
        body = response.read(800000)

    text = body.decode("utf-8", errors="ignore")
    return str(status), final_url, content_type, text


def is_commission_url(url):
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and "commission-des-sondages.fr" in parsed.netloc


def classify_notice_candidate(url, text, source_page_url):
    parsed = urlparse(url)
    path = parsed.path.lower()
    link_text = re.sub(r"\s+", " ", text or "").strip()
    link_text_lower = link_text.lower()
    source_page_lower = source_page_url.lower()
    reasons = []

    # Reject broad site navigation and legal/static pages.
    broad_paths = [
        "/commun/",
        "/competences/",
        "/droits/",
        "/pdf/loi77.pdf",
    ]
    if any(path.startswith(p) for p in broad_paths):
        return []

    # Commission notice files are useful only when the visible link text
    # indicates a presidential/political national poll, not a municipal poll.
    is_notice_file = "/notices/medias/fichiers/" in path

    presidential_text_patterns = [
        r"(^|\s)pres(\s|$)",
        r"présidentielle",
        r"presidentielle",
        r"présidentielles",
        r"presidentielles",
        r"présidentiel",
        r"presidentiel",
        r"barometre politique",
        r"baromètre politique",
        r"bloc central",
        r"confiance",
    ]

    has_presidential_text = any(
        re.search(pattern, link_text_lower)
        for pattern in presidential_text_patterns
    )

    # Explicitly reject municipal rows unless the row also contains a clear presidential signal.
    looks_municipal = bool(re.search(r"(^|\s)mun(\s|$)", link_text_lower))
    if looks_municipal and not has_presidential_text:
        return []

    if is_notice_file and has_presidential_text:
        reasons.append("commission_notice_file_path")
        reasons.append("presidential_link_text")

    # Keep official communiqué only when explicitly presidential/polling related.
    if "/hist/communiques/" in path and (
        "presidentielle" in link_text_lower
        or "présidentielle" in link_text_lower
        or "presidentielles" in link_text_lower
        or "présidentielles" in link_text_lower
        or "elections-presidentielles" in path
    ):
        reasons.append("official_presidential_polling_communique")

    # The tag page is useful as a source page, but it is not enough by itself.
    # Do not accept rows merely because source_page_url contains 2027-Presidentielle.
    if "2027-presidentielle" in source_page_lower and reasons:
        reasons.append("source_page_2027_presidentielle_tag")

    return reasons


def stable_id(url):
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return f"poll_notice_stage_{digest}"


def load_existing_review_rows(path):
    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    return {
        row.get("notice_url"): row
        for row in rows
        if row.get("notice_url")
    }


def preserve_existing_review_state(rows, existing_by_url):
    preserved_count = 0
    new_count = 0

    for row in rows:
        existing = existing_by_url.get(row.get("notice_url"))

        if existing:
            preserved_count += 1

            # Preserve the original first-seen timestamp and human review fields.
            for field in ["detected_at", "review_decision", "review_notes"]:
                if existing.get(field):
                    row[field] = existing[field]
        else:
            new_count += 1

        # Hard safety invariant: this watcher never extracts candidate-level values.
        row["candidate_level_values_extracted"] = "false"

    return preserved_count, new_count


def extract_rows_from_page(page_url, feed, source_name, detected_at):
    rows = []
    warnings = []

    try:
        http_status, final_url, content_type, html = fetch_page(page_url)
    except urllib.error.HTTPError as exc:
        warnings.append(f"HTTP error for {page_url}: {exc.code} {exc.reason}")
        return rows, warnings, str(exc.code), "", ""
    except Exception as exc:
        warnings.append(f"Fetch error for {page_url}: {type(exc).__name__}: {exc}")
        return rows, warnings, "", "", ""

    parser = LinkExtractor()
    parser.feed(html)

    for href, link_text in parser.links:
        if not href:
            continue

        notice_url = urljoin(final_url, href)

        if not is_commission_url(notice_url):
            continue

        reasons = classify_notice_candidate(notice_url, link_text, page_url)
        if not reasons:
            continue

        rows.append({
            "poll_notice_stage_id": stable_id(notice_url),
            "feed_id": FEED_ID,
            "source_id": feed["source_id"],
            "source_name": source_name,
            "source_page_url": page_url,
            "notice_url": notice_url,
            "link_text": link_text[:300],
            "detected_at": detected_at,
            "http_status": http_status,
            "content_type": content_type,
            "page_title": parser.title[:300],
            "match_reason": "|".join(reasons),
            "candidate_level_values_extracted": "false",
            "review_decision": "pending",
            "review_notes": "Staged poll-notice discovery only. No candidate-level values extracted.",
        })

    return rows, warnings, http_status, content_type, parser.title


def main():
    STAGING.mkdir(exist_ok=True)

    feed = get_feed()
    source_name = get_source_name(feed["source_id"])

    detected_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    source_pages = [
        feed["url"],
        COMMISSION_2027_TAG_URL,
    ]

    all_rows = []
    all_warnings = []
    page_reports = []

    for page_url in source_pages:
        rows, warnings, http_status, content_type, page_title = extract_rows_from_page(
            page_url=page_url,
            feed=feed,
            source_name=source_name,
            detected_at=detected_at,
        )
        all_rows.extend(rows)
        all_warnings.extend(warnings)
        page_reports.append((page_url, http_status, len(rows), page_title))

    deduped = {}
    for row in all_rows:
        deduped[row["notice_url"]] = row

    rows = sorted(deduped.values(), key=lambda row: (row["source_page_url"], row["notice_url"]))

    existing_by_url = load_existing_review_rows(OUT)
    preserved_count, new_count = preserve_existing_review_state(rows, existing_by_url)

    with OUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {OUT.relative_to(ROOT)}")
    print("Candidate-level values extracted: false")
    print()
    print("Source pages checked:")
    for page_url, http_status, row_count, page_title in page_reports:
        print(f"- {http_status} | rows={row_count} | {page_title[:90]} | {page_url}")

    print()
    print(f"Staged poll notice candidates after tightening: {len(rows)}")
    print(f"Existing rows preserved: {preserved_count}")
    print(f"New rows detected: {new_count}")

    if all_warnings:
        print()
        print("Warnings/errors:")
        for warning in all_warnings:
            print(f"- {warning}")

    if rows:
        print()
        print("First staged rows:")
        for row in rows[:20]:
            print(f"- {row['poll_notice_stage_id']} | {row['match_reason']} | {row['link_text'][:90]} | {row['notice_url']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
