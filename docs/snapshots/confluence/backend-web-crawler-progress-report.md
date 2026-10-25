# Backend — Web Crawler (Progress Report)

> Snapshot of the Confluence page [Backend — Web Crawler (Progress Report)](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/21626920), taken 25 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

## Overview

The backend's core responsibility is dynamic discovery of research funding opportunities, a hard requirement from the client, who explicitly rejected a fixed/curated list of funding sites ("defeats the purpose"). Over Weeks 1–6, a working, tested crawler pipeline was built, debugged against real production failures, verified across multiple research fields, and put behind a CI pipeline enforcing linting and multi-version test coverage.

## Architectural Design

The backend is split into independently swappable stages, so that upgrading any one piece (e.g. the search provider, or extraction sophistication) never requires changes elsewhere in the pipeline:

1. **Query building** (`queryBuilder.py`) — turns a user's search profile (field of research, type of activity, career stage, funding type, free-text description) into a set of search queries.
2. **Discovery** (`discoverURL.py`) — runs those queries against a search API to find candidate URLs.
3. **robots.txt compliance** (`robotCheck.py`) — checks each candidate URL against that site's crawling rules before fetching.
4. **Fetch & extraction** (`extract.py`) — retrieves each page and extracts structured signals: title, deadline, funding amount, eligibility text.
5. **Storage** (`storage.py`) — persists results to SQLite, keyed by URL, with staleness tracking for periodic re-crawling.
6. **Scheduling** (`scheduler.py`) — a background loop that refreshes stale entries and re-runs discovery for known profiles, avoiding the need to live-crawl the entire web on every user search.

**Design rationale, evidenced in code:** the API layer (in progress) and ranking engine only ever interact with the crawler through two stable calls — trigger a crawl, read from storage — regardless of how discovery or extraction work internally. This was tested directly: when the discovery backend was replaced entirely (see below), zero changes were needed to `storage.py`, `extract.py`, or the orchestration layer.

A deliberate scoping decision is documented directly in `queryBuilder.py`'s docstring: citizenship and employer type are excluded from search query generation and reserved for eligibility filtering instead, because folding them into search queries would narrow discovery without improving it (few funding pages mention citizenship in their marketing copy) — an example of the team adding reasoning beyond what the brief specified, not just implementing it literally.

## Coding Standards

Every module carries docstrings explaining not just _what_ a function does but _why_ specific decisions were made — e.g. why extraction returns raw signals (a funding amount string, a raw deadline) rather than pre-classified bands, deferring that judgement to the ranking engine.

Standards are enforced automatically, not just documented: the CI pipeline runs `ruff` linting on every pull request to the backend, alongside `eslint` for the frontend. Both are required checks — a PR with lint failures is visibly blocked before merge, e.g.:

```
✓ Backend CI / Lint (ruff)              Successful in 15s
✓ Frontend CI / Lint (eslint)           Successful in 13s
```

## Testing & Verification

Testing was conducted at three levels, moving from synthetic to real-world data:

1. **Unit-level, against constructed mock data**, before ever touching the network — e.g. extraction was verified against a constructed funding page containing a known deadline and amount, confirming the parser correctly recovered:

```
title: Marine Research Grant 2027
deadline_parsed: 2027-03-15
funding_amount_raw: AUD 2,500,000
eligibility_snippet: "...applicants must hold a PhD and be affiliated
                       with an Australian research institution..."
```

2. **Cross-profile generalisation testing.** Query generation was run against profiles varying career stage, funding type, and field of research to confirm the system doesn't just work for one hardcoded topic. Example — the same generator, given a physics/graduate-student/equipment profile vs. a history/early-postdoc/any-funding profile, correctly produced distinct, non-overlapping query sets (including correctly generating _no_ funding-type-specific query when the profile requested "any" funding type — the intended behaviour).

3. **End-to-end, against live production data.** The full pipeline was run against five deliberately varied profiles (marine biology, machine learning, public health, astrophysics, history) with real, verifiable results — e.g. one run discovered 51 candidate URLs and successfully extracted and stored 40+ real funding opportunities, including NSF solicitations, Sea Grant programs, and foundation grants, while correctly and gracefully handling every failure mode encountered in the wild:

```
[crawl] skipping (robots.txt disallows): facebook.com/groups/...
[fetch] failed for seagrant.noaa.gov/...: 403 Client Error: Forbidden
[fetch] failed for guampdn.com/...: 429 Client Error: Too Many Requests
[fetch] failed for aims.gov.au/...: Read timed out
```

None of these caused the crawl to halt — each is caught, logged, and the crawl continues, which was verified by inspection of the run rather than assumed.

**CI enforcement:** the test suite runs automatically across Python 3.11, 3.12, and 3.13 on every pull request, catching version-specific issues before merge rather than after.

## Problems Encountered and Resolved

Two significant defects were found and root-caused through direct debugging against live output, not assumed to be working after a single successful run:

* **Discovery silently returning zero results.** The original discovery approach (scraping DuckDuckGo's HTML search page) began returning HTTP 202 responses. Inspecting the raw response body directly (rather than trusting the absence of an exception) revealed DuckDuckGo was serving its homepage shell — a bot-detection response — instead of search results. Root-caused and resolved by switching to SerpAPI, a documented, authenticated search API, with the change isolated entirely to `discoverURL.py` and zero changes required elsewhere.
* **robots.txt compliance silently blocking 100% of URLs, regardless of domain.** Every single discovered URL — across dozens of unrelated domains including NSF, NOAA, and Facebook — was being rejected as "disallowed." Investigation traced this to Python's `RobotFileParser.read()`, which uses a default network client many sites block (returning HTTP 403) — and `RobotFileParser` treats a 403 on the robots.txt fetch itself as "disallow everything," the opposite of correct fail-open behaviour. Fixed by fetching `robots.txt` manually with proper request headers and feeding the content directly to the parser. Verified fixed by re-running the crawl and confirming the same 57 URLs that were all previously rejected were now correctly evaluated (some legitimately disallowed, e.g. Facebook's actual `/groups/` restriction — most correctly allowed).

Both defects would have been invisible in a superficial demo — the crawler ran without crashing in both cases — and were only caught through deliberate output inspection rather than assuming success from the absence of an error.

**Security incident, caught and resolved:** a live API key was accidentally committed to a feature branch. This was identified, the key was immediately rotated at the provider (invalidating the exposed credential), the offending commit was removed from branch history via `git reset` and a force-push, and `.gitignore` was corrected to prevent recurrence — with the fix verified by confirming the corrected commit no longer contained the secret.

## Current Status

| Component | Status |
| --- | --- |
| Query building (all user input fields) | Complete, tested across 5 profiles |
| Dynamic discovery (search API-based) | Complete, verified against live data |
| robots.txt compliance | Complete, bug found and fixed |
| Structured extraction (deadline, funding amount, eligibility text) | Complete, unit-tested |
| Storage with staleness tracking | Complete |
| Scheduled re-crawling | Complete (basic implementation) |
| CI pipeline (lint + multi-version test matrix) | Complete |
| Ranking/matching engine | Built and unit-tested; not yet merged to main |
| API layer (frontend integration) | In progress |
| Planned Crawler Enhancements | In progress |

## Repository Practices

The project uses a branch-per-feature workflow (e.g. `feature/backend-crawler`) with pull requests into `main` rather than direct commits, enforced in practice by CI checks that must pass before merge. Merge conflicts (e.g. in `.gitignore`, where `main` and the feature branch had diverged) were resolved deliberately by comparing both versions and keeping the more complete ruleset, not by blind acceptance of either side. Secrets are excluded from version control via `.gitignore`, loaded from a local `.env` file at runtime, with `.env.example` committed so required configuration is discoverable without exposing credentials — and this policy was tested under real conditions when a key was accidentally committed and the incident was fully remediated (see above).

## Next Steps

Per the team's Stage 1 (basic functionality) plan: merge the already-built and tested ranking engine (eligibility classification, match scoring, deadline/funding-value banding) into the main repository, then complete the FastAPI layer connecting the React frontend to search results. Stage 2 (production-grade search infrastructure, LLM-assisted extraction, Postgres migration) is scoped in the team's roadmap but deliberately deferred until the basic end-to-end pipeline is demonstrable end-to-end.

## Planned Enhancements: Crawler Performance

Beyond the Stage 1 scope above, a specific technical plan has been developed for evolving the crawler from a functional prototype toward production-grade crawling architecture, informed by patterns used in established open-source crawlers (e.g. Scrapy's downloader model). This work is intentionally sequenced after ranking and API integration are complete.

**Planned Improvements — near-term:**

1. **Concurrent fetching.** The current crawler fetches pages sequentially with a single blocking `requests` call per URL. Replacing this with a thread pool (or async I/O) allows many pages to be fetched simultaneously, directly addressing the crawl-time bottleneck observed in testing (fetching \~57 pages sequentially takes on the order of a minute purely from network wait time).
2. **Per-domain rate limiting**, replacing the current flat global delay. Tracking last-request-time per host (rather than one shared delay across all domains) allows the crawler to be simultaneously fast across many different sites while still being polite to any single one — matching how production crawlers balance throughput against politeness.
3. **Respecting** `Crawl-delay` **directives** from `robots.txt`, which are already being parsed for allow/disallow rules but not yet read for timing guidance — sites that specify a crawl delay are communicating exactly how fast they're willing to be crawled.
4. **Retry with exponential backoff** for transient failures. Real crawl runs have already surfaced concrete examples of exactly this failure class — a `429 Too Many Requests` and a connection timeout, both currently treated as permanent failures on first attempt rather than retried.
5. **URL canonicalisation before deduplication**, to avoid treating trivially-different URLs (trailing slashes, tracking parameters) as distinct pages and wasting fetch requests on duplicates.

‌

**Planned for later in the project timeline:**

6. **Recursive/link-following crawling**, bounded by a depth limit (1–2 hops), so a discovered funding page can surface related opportunities on the same site that search queries alone don't directly return.
7. **Sitemap.xml discovery** as a first-pass check before falling back to search-query-based discovery — many funding/grant sites publish a systematic page listing this way.
8. **Conditional re-fetching** using `ETag`/`Last-Modified` response headers, avoiding redundant downloads of unchanged pages — increasingly valuable once the scheduler is running regular re-crawls over the remaining project weeks rather than one-off manual runs.
9. **Structured crawl metrics** (success rate, pages/sec, failures categorised by type) replacing ad hoc print-statement logging, providing an actual basis for evaluating whether future performance changes help.
