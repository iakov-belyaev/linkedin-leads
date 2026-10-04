import os
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# API keys / environment hooks
# ---------------------------------------------------------------------------
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
APIFY_API_KEY = os.getenv("APIFY_API_KEY")

DB_PATH = "cyprus_leads.db"

# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------
# Toggle the enrichment engine: True -> Gemini, False -> DeepSeek.
USE_GEMINI = os.getenv("USE_GEMINI", "False").strip().lower() in ("1", "true", "yes")
# Toggle the ingestion source: True -> Apify, False -> DuckDuckGo.
USE_APIFY = os.getenv("USE_APIFY", "False").strip().lower() in ("1", "true", "yes")

# ---------------------------------------------------------------------------
# Geo markers used by the quality-filtering layer.
# ---------------------------------------------------------------------------
GEO_MARKERS = ("cyprus", "limassol", "nicosia", "larnaca", "paphos", "кипр", "лимасол")

# ---------------------------------------------------------------------------
# Search query registry
# ---------------------------------------------------------------------------
# Queries are grouped by department so new terms can be appended easily.
# Each entry is a plain X-Ray query string targeting Cyprus decision-makers.
# To add a new term, just append a string to the relevant department list
# (or add a whole new department key).
SEARCH_QUERIES_BY_DEPARTMENT = {
    "HR": [
        'site:linkedin.com/in "Cyprus" "HR Manager"',
        'site:linkedin.com/in "Limassol" "HR"',
        'site:linkedin.com/in "Limassol" "Head of People"',
        'site:linkedin.com/in "Cyprus" "Talent Acquisition"',
        'site:linkedin.com/in "Nicosia" "HR Director"',
    ],
    "Procurement": [
        'site:linkedin.com/in "Cyprus" "Procurement"',
        'site:linkedin.com/in "Limassol" "Purchasing"',
        'site:linkedin.com/in "Cyprus" "Отдел Закупок"',
        'site:linkedin.com/in "Nicosia" "Head of Procurement"',
        'site:linkedin.com/in "Cyprus" "Supply Chain Manager"',
    ],
}


def iter_search_queries():
    """Yield (query, department) tuples for every registered query.

    Flattening the registry here keeps the scraper decoupled from the
    registry's internal structure, so new departments are picked up
    automatically without touching scraper.py.
    """
    for department, queries in SEARCH_QUERIES_BY_DEPARTMENT.items():
        for query in queries:
            yield query, department


# Backwards-compatible flat list (derived from the registry above).
SEARCH_QUERIES = [query for query, _ in iter_search_queries()]
