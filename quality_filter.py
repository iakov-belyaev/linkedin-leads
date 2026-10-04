"""Lead quality-checking layer.

Scores and filters raw scraped leads *before* they reach SQLite. The goal is
to keep only high-intent, professionally relevant Cyprus decision-makers and
drop noise such as recruiters, job boards, and former employees.
"""

# Geo-markers that indicate the lead is actually based in / relevant to Cyprus.
CYPRUS_GEO_MARKERS = (
    "cyprus",
    "limassol",
    "lemesos",
    "nicosia",
    "larnaca",
    "paphos",
    "famagusta",
)

# Role keywords that indicate a genuine decision-maker in our target depts.
ROLE_KEYWORDS = {
    "HR": (
        "hr",
        "human resources",
        "people",
        "talent",
        "recruit",
        "отдел кадров",
    ),
    "Procurement": (
        "procurement",
        "purchasing",
        "buyer",
        "sourcing",
        "supply chain",
        "закуп",
    ),
}

# Signals that a lead is low-intent / not a real decision-maker.
NEGATIVE_MARKERS = (
    "recruiter",
    "recruiting agency",
    "staffing",
    "job board",
    "we are hiring",
    "looking for a job",
    "open to work",
    "seeking opportunities",
    "former",
    "ex-",
    "previously",
    "past ",
)

# Minimum score required for a lead to be considered acceptable.
MIN_ACCEPTABLE_SCORE = 3


def score_lead(title: str, body: str, target_role: str = "HR") -> int:
    """Return an integer quality score for a raw lead.

    Scoring is additive and intentionally simple/rational:
      +2  Cyprus geo-marker present in title or body
      +2  role keyword for the target department present
      +1  role keyword appears in the title (stronger signal)
      -3  any negative marker present (recruiter, former, job board, ...)
    """
    text = f"{title} {body}".lower()
    title_lower = (title or "").lower()
    score = 0

    if any(marker in text for marker in CYPRUS_GEO_MARKERS):
        score += 2

    role_keywords = ROLE_KEYWORDS.get(target_role, ROLE_KEYWORDS["HR"])
    if any(kw in text for kw in role_keywords):
        score += 2
    if any(kw in title_lower for kw in role_keywords):
        score += 1

    if any(marker in text for marker in NEGATIVE_MARKERS):
        score -= 3

    return score


def is_quality_lead(title: str, body: str, target_role: str = "HR") -> bool:
    """Return True if the lead passes the minimum quality threshold."""
    return score_lead(title, body, target_role) >= MIN_ACCEPTABLE_SCORE
