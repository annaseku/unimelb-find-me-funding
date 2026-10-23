"""
Shared configuration for the funding-opportunity crawler.
"""

from dotenv import load_dotenv

load_dotenv()  # loads variables from a .env file in the project root, if present

# --- Storage ---------------------------------------------------------------
DB_PATH = "funding_crawler.db"

# --- Networking --------------------------------------------------------------
HEADERS = {
    "User-Agent": "FindMeFundingCrawler/0.2 (university project; +https://github.com/annaseku/unimelb-find-me-funding)"
}
REQUEST_TIMEOUT = 10  # seconds, per HTTP request
REQUEST_DELAY_SECONDS = 1.5  # pause between outbound requests to any one host

# --- Discovery ---------------------------------------------------------------
MAX_RESULTS_PER_QUERY = 10

# Generic terms appended to every research-area query so discovery isn't
# tied to a fixed list of funding sites.
FUNDING_TERMS = [
    "research grant",
    "funding opportunity",
    "research fellowship",
    "scholarship funding",
]

# --- Scheduling ---------------------------------------------------------------
# How old a stored opportunity can get before we consider it stale and
# worth re-fetching.
STALE_AFTER_DAYS = 7

# How often the scheduler loop wakes up to check for due work, in seconds.
SCHEDULER_POLL_INTERVAL_SECONDS = 60 * 60  # hourly
