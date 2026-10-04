import re
import time
from config import (
    APIFY_API_KEY,
    GEO_MARKERS,
    USE_APIFY,
    iter_search_queries,
)
from db import init_db, insert_lead
from quality_filter import score_lead, is_quality_lead

# URL path segments that indicate a non-personal LinkedIn page.
INVALID_URL_MARKERS = ("/jobs/", "/company/", "/posts/", "/dir/")

# A valid personal LinkedIn profile URL must contain a "/in/<slug>" segment.
# The slug is the vanity handle (letters, digits, hyphens, underscores, and
# unicode word chars for non-Latin names).
VALID_PROFILE_URL_RE = re.compile(
    r"linkedin\.com/in/[A-Za-z0-9\-_%\w]+",
    re.IGNORECASE,
)

# Phrases that indicate a stale / past-tense profile (no longer relevant).
PAST_TENSE_MARKERS = (
    "former ",
    "ex-",
    "previously ",
    "used to ",
    "was a ",
    "worked at ",
    "бывший",
    "ранее работал",
)


def is_valid_profile_url(url: str) -> bool:
    """Return True only for personal LinkedIn profile URLs.

    Uses a regex to require a well-formed ``linkedin.com/in/<slug>`` path and
    rejects known non-personal segments (jobs, company, posts, dir).
    """
    if not url:
        return False
    lowered = url.lower()
    if any(marker in lowered for marker in INVALID_URL_MARKERS):
        return False
    return bool(VALID_PROFILE_URL_RE.search(url))


def has_geo_marker(title: str, body: str) -> bool:
    """Return True if the snippet references a Cyprus geo-marker."""
    haystack = f"{title} {body}".lower()
    return any(marker in haystack for marker in GEO_MARKERS)


def is_past_tense(title: str, body: str) -> bool:
    """Return True if the snippet looks like a stale / former-role profile."""
    haystack = f"{title} {body}".lower()
    return any(marker in haystack for marker in PAST_TENSE_MARKERS)


def passes_relevance_gate(title: str, body: str) -> bool:
    """Geo + freshness gate applied before the quality filter."""
    if not has_geo_marker(title, body):
        return False
    if is_past_tense(title, body):
        return False
    return True


# ---------------------------------------------------------------------------
# Ingestion adapters
# ---------------------------------------------------------------------------
def _fetch_duckduckgo(query: str, max_results: int):
    """Fetch results via DuckDuckGo (ddgs)."""
    try:
        from ddgs import DDGS
    except ImportError as exc:
        raise RuntimeError(
            "The 'ddgs' package is required for DuckDuckGo ingestion. "
            "Install it with: pip install ddgs"
        ) from exc

    with DDGS() as ddgs:
        return list(ddgs.text(query, max_results=max_results))


def _fetch_apify(query: str, max_results: int):
    """Fetch results via the Apify Google Search scraper actor."""
    if not APIFY_API_KEY:
        raise RuntimeError(
            "APIFY_API_KEY missing from environment/.env file. "
            "Set it or switch USE_APIFY=False."
        )

    try:
        from apify_client import ApifyClient
    except ImportError as exc:
        raise RuntimeError(
            "The 'apify-client' package is required for Apify ingestion. "
            "Install it with: pip install apify-client"
        ) from exc

    client = ApifyClient(APIFY_API_KEY)
    run_input = {
        "queries": query,
        "maxPagesPerQuery": 1,
        "resultsPerPage": max_results,
    }
    run = client.actor("apify/google-search-scraper").call(run_input=run_input)

    results = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        for organic in item.get("organicResults", []):
            results.append(
                {
                    "href": organic.get("url", ""),
                    "title": organic.get("title", ""),
                    "body": organic.get("description", ""),
                }
            )
    return results


def fetch_results(query: str, max_results: int):
    """Dispatch to the active ingestion engine based on USE_APIFY."""
    if USE_APIFY:
        return _fetch_apify(query, max_results)
    return _fetch_duckduckgo(query, max_results)


def run_scraper(max_results_per_query=50):
    init_db()
    print("[Db] Database initialized.")
    engine = "Apify" if USE_APIFY else "DuckDuckGo"
    print(f"[Scraper] Ingestion engine: {engine}")

    total_added = 0
    for query, role_tag in iter_search_queries():
        print(f"\n[Scraper] Executing search: {query} (dept: {role_tag})")

        try:
            results = fetch_results(query, max_results_per_query)
            raw_count = len(results)
            added_count = 0
            valid_count = 0
            relevant_count = 0
            quality_count = 0
            for res in results:
                url = res.get('href', '')
                title = res.get('title', '')
                body = res.get('body', '')

                if not is_valid_profile_url(url):
                    continue

                valid_count += 1

                # Relevance gate: geo-marker + freshness before quality scoring.
                if not passes_relevance_gate(title, body):
                    print(f"[Relevance] Rejected (geo/past-tense): {url}")
                    continue

                relevant_count += 1

                # Quality gate: score and filter before hitting SQLite.
                score = score_lead(title, body, target_role=role_tag)
                if not is_quality_lead(title, body, target_role=role_tag):
                    print(f"[Quality] Rejected (score={score}): {url}")
                    continue

                quality_count += 1
                if insert_lead(url, title, body, target_role=role_tag):
                    added_count += 1

            total_added += added_count
            print(
                f"[Scraper] Raw hits: {raw_count}, passed URL validation: {valid_count}, "
                f"passed relevance gate: {relevant_count}, passed quality filter: {quality_count}, "
                f"new leads inserted: {added_count}."
            )
        except Exception as e:
            print(f"[Scraper] Error during query execution: {e}")

        time.sleep(2)  # Respect rate limits

    print(f"\n[Scraper] Complete. Total new leads inserted: {total_added}")

if __name__ == "__main__":
    run_scraper()
