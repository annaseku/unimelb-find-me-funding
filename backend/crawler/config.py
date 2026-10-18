"""
Shared configuration for the funding-opportunity crawler.
"""

from dotenv import load_dotenv

load_dotenv()  # loads variables from a .env file in the project root, if present

# --- Storage ---------------------------------------------------------------
DB_PATH = "funding_crawler.db"

# --- Networking --------------------------------------------------------------
# The "Mozilla/5.0 (compatible; ...)" form is the convention well-behaved
# crawlers use (Googlebot does the same) and still names us. ARC and NHMRC
# stalled requests carrying the bare crawler name until they timed out.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; FindMeFundingCrawler/0.3; university project; "
        "+mailto:frank.a@unimelb.edu.au)"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-AU,en;q=0.9",
}
REQUEST_TIMEOUT = 30          # seconds, per HTTP request; some gov.au sites are slow
REQUEST_DELAY_SECONDS = 1.5   # pause between outbound requests to any one host

# --- Discovery ---------------------------------------------------------------
MAX_RESULTS_PER_QUERY = 10

# Generic terms appended to every research-area query so discovery isn't
# tied to a fixed list of funding sites. Three ask for Australian schemes,
# since the client wants results tailored to Australian funding and
# unqualified searches return mostly US pages; one stays unqualified so major
# international schemes still turn up. "funding opportunity" and "scholarship
# funding" were dropped after the first real crawls returned dictionary
# entries for "opportunity" and US undergraduate scholarship lists.
FUNDING_TERMS = [
    "research grant Australia",
    "research fellowship Australia",
    "funding opportunities for Australian researchers",
    "research grant",
]

# Excluded in the search itself, so they don't use up the results per query.
# The normaliser blocks a longer list (backend/normaliser/relevance.py);
# these are the ones the first crawls returned most often.
EXCLUDED_SITES = [
    "wikipedia.org",
    "youtube.com",
    "merriam-webster.com",
    "dictionary.cambridge.org",
]

# --- Scheduling ---------------------------------------------------------------
# How old a stored opportunity can get before we consider it stale and
# worth re-fetching.
STALE_AFTER_DAYS = 7

# How often the scheduler loop wakes up to check for due work, in seconds.
SCHEDULER_POLL_INTERVAL_SECONDS = 60 * 60  # hourly