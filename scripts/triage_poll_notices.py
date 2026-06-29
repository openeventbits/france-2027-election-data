import csv
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGING = ROOT / "staging"

IN = STAGING / "poll_notices_review.csv"
OUT = STAGING / "poll_notices_triaged_review.csv"

ADDED_FIELDS = [
    "triage_label",
    "triage_reason",
    "review_priority",
    "suggested_metadata_scope",
    "ready_for_canonical_metadata",
]


def normalize(value):
    value = value or ""
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"\s+", " ", value).strip().lower()
    return value


def has_any(text, patterns):
    return any(re.search(pattern, text) for pattern in patterns)


def triage(row):
    link_text = row.get("link_text", "")
    notice_url = row.get("notice_url", "")
    match_reason = row.get("match_reason", "")

    text = normalize(link_text)
    url = notice_url.lower()
    reason_text = normalize(match_reason)

    # Source/index rows are useful for monitoring, but should not become poll metadata rows.
    if "/bytag/14/2027-presidentielle" in url or text == "2027 - presidentielle":
        return {
            "triage_label": "source_index_reference",
            "triage_reason": "Official 2027 presidential tag/index page, not an individual poll notice.",
            "review_priority": "low",
            "suggested_metadata_scope": "source_index",
            "ready_for_canonical_metadata": "false",
        }

    if text.startswith("2022 -") or "/2022-" in url:
        return {
            "triage_label": "historical_reference",
            "triage_reason": "Historical presidential-election tag/reference, not France 2027 poll metadata.",
            "review_priority": "low",
            "suggested_metadata_scope": "historical_reference",
            "ready_for_canonical_metadata": "false",
        }

    if "official_presidential_polling_communique" in reason_text:
        return {
            "triage_label": "official_communique",
            "triage_reason": "Official Commission des sondages communiqué related to presidential polling.",
            "review_priority": "medium",
            "suggested_metadata_scope": "official_document_or_polling_context",
            "ready_for_canonical_metadata": "review_required",
        }

    voting_intention_patterns = [
        r"(^|\s)iv(\s|$)",
        r"intention",
        r"intentions",
        r"1er tour",
        r"1e tour",
        r"2e tour",
        r"2eme tour",
        r"second tour",
        r"seconds tours",
        r"enquete electorale",
        r"potentiel electoral",
        r"potentiel vote",
    ]

    candidate_or_field_patterns = [
        r"primaire",
        r"attal",
        r"retailleau",
        r"le pen",
        r"bardella",
        r"melenchon",
        r"melanchon",
        r"philippe",
        r"hanouna",
        r"candidature",
        r"bloc central",
        r"droite",
        r"(^|\s)rn(\s|$)",
    ]

    political_context_patterns = [
        r"barometre",
        r"barometer",
        r"popularite",
        r"confiance",
        r"indices popularite",
        r"observatoire",
        r"tableau de bord",
        r"personnalite",
        r"personnalites",
        r"stature",
        r"ambition",
        r"president ideal",
        r"bon president",
        r"elites",
        r"vacances",
        r"carburants",
        r"violences",
        r"femme elysee",
        r"prix des carburants",
    ]

    if has_any(text, voting_intention_patterns):
        return {
            "triage_label": "likely_presidential_voting_intention_notice",
            "triage_reason": "Visible notice text suggests vote intention, electoral survey, round scenario, or comparable presidential-election polling metadata.",
            "review_priority": "high",
            "suggested_metadata_scope": "polls_metadata_candidate",
            "ready_for_canonical_metadata": "review_required",
        }

    if has_any(text, candidate_or_field_patterns):
        return {
            "triage_label": "candidate_or_field_context_notice",
            "triage_reason": "Visible notice text mentions candidates, party field, primary, RN, right/centre-right, or presidential field context.",
            "review_priority": "medium",
            "suggested_metadata_scope": "polling_context_or_metadata_candidate",
            "ready_for_canonical_metadata": "review_required",
        }

    if has_any(text, political_context_patterns):
        return {
            "triage_label": "political_barometer_context_notice",
            "triage_reason": "Visible notice text suggests political barometer, popularity, confidence, or public-opinion context rather than direct voting intention.",
            "review_priority": "low",
            "suggested_metadata_scope": "polling_context_only",
            "ready_for_canonical_metadata": "false",
        }

    return {
        "triage_label": "needs_manual_review",
        "triage_reason": "Presidential-looking notice, but text is not specific enough for automatic classification.",
        "review_priority": "medium",
        "suggested_metadata_scope": "manual_review",
        "ready_for_canonical_metadata": "review_required",
    }


def main():
    if not IN.exists():
        raise FileNotFoundError(f"Missing input file: {IN.relative_to(ROOT)}")

    with IN.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        raise RuntimeError(f"No rows found in {IN.relative_to(ROOT)}")

    input_fields = list(rows[0].keys())
    out_fields = input_fields + [field for field in ADDED_FIELDS if field not in input_fields]

    triaged_rows = []
    for row in rows:
        triage_fields = triage(row)
        out_row = dict(row)
        out_row.update(triage_fields)

        # Hard safety invariant: this triage does not approve poll values.
        out_row["candidate_level_values_extracted"] = "false"

        triaged_rows.append(out_row)

    with OUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(triaged_rows)

    counts = {}
    priorities = {}
    for row in triaged_rows:
        counts[row["triage_label"]] = counts.get(row["triage_label"], 0) + 1
        priorities[row["review_priority"]] = priorities.get(row["review_priority"], 0) + 1

    print(f"Wrote {OUT.relative_to(ROOT)}")
    print(f"Rows triaged: {len(triaged_rows)}")
    print("Candidate-level values extracted: false")
    print()
    print("Triage labels:")
    for key, value in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        print(f"- {key}: {value}")
    print()
    print("Review priorities:")
    for key, value in sorted(priorities.items(), key=lambda item: (-item[1], item[0])):
        print(f"- {key}: {value}")

    high_rows = [row for row in triaged_rows if row["review_priority"] == "high"]
    if high_rows:
        print()
        print("High-priority metadata candidates:")
        for row in high_rows[:30]:
            print(f"- {row['poll_notice_stage_id']} | {row['triage_label']} | {row['link_text']} | {row['notice_url']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
