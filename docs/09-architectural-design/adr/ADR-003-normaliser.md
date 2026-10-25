# ADR-003: Normaliser, from crawled rows to structured opportunities

| Field | Value |
| --- | --- |
| Decision ID | ADR-003 |
| Decision | Convert the crawler's raw rows into structured `Opportunity` records with deterministic rules first and an optional model extractor that fills only prose-derived fields. Write the result to a separate SQLite table in the crawler's database, served to the API through the existing repository seam and selected by an environment variable. |
| Status | ⚪ Proposed (implemented on main, not yet ratified with the client) |
| Owner | Anna Sekulic |
| Date | 2026-09-07 |

## Context

The crawler stores what it can find mechanically on a page: title, page text, a parsed deadline where one was labelled, the first dollar figure, and a 300-character window around the word "eligibility". The ranker needs structured fields: allowed citizenships, employer types, career stages, funding types, an amount in Australian dollars, ANZSRC codes. Nothing converted one into the other, so the ranker ran only on hand-written mock data. This is pipeline stage 3 in the architecture page's diagram and the hybrid split in decision 3: rules for crisp facts, a model for prose.

## Options considered

1. Rules only. Deterministic and testable offline, but citizenship, career stage and research area live in prose the rules catch only when phrased in a familiar way.
2. Rules first, model fills the gaps (chosen). Rules produce a complete record with a per-field provenance stamp. A model extractor with a strict output schema then supplies the prose-derived fields, and the merge policy never lets it override a rule-parsed date or amount unless the rule found nothing. Without a key the pipeline still runs and produces the same shape.
3. Model only. Least code, but every row costs money, nothing is reproducible offline, and CI cannot test it.

## Decision details

- `backend/normaliser/parsers.py` handles amount (currency detection, multipliers, a fixed approximate rate table to AUD, bare `$` assumed AUD), deadline (ISO first, fuzzy date parse second), open or closed status, a stable id derived from the URL, a funder placeholder from the host, a summary cut at a sentence boundary, and title keywords.
- `backend/normaliser/lexicon.py` maps phrases to enum codes for citizenship, employer type, career stage (including numeric "N to M years since PhD" ranges), funding type (with a negation window so "salary is not available" does not count) and two-digit ANZSRC divisions.
- `backend/normaliser/rules.py` composes a `NormalisedRecord`: the `Opportunity`, a provenance map of field name to `rule`, `llm` or `missing`, and a content hash of title plus text.
- `backend/normaliser/llm.py` defines an `Extractor` protocol. The OpenRouter implementation (KAN-69; it replaced Gemini, whose free tier capped the extractor at 5 requests a minute) sends an OpenAI-compatible chat request to a small open-weight model and asks for JSON constrained to the `ExtractedFields` schema and validates the reply, so a malformed answer fails loudly rather than writing junk. The extractor also classifies whether the page is about research funding; non-funding pages are soft-deleted with status `not_funding` (decision 9). The merge policy: prose fields (funder, summary, countries, citizenships, employer types, career stages, funding types, codes, keywords, eligibility text, opening date) take the model's value when non-empty; amount and deadline take it only when the rules found nothing.
- `backend/normaliser/pipeline.py` reads `opportunities` where the fetch succeeded, writes `normalised_opportunities` in the same file, and skips a row whose content hash is unchanged unless a model is now available and the stored row was rules-only. The crawler's table is never written.
- `backend/data/sqlite_repository.py` implements `all()` and `get()` over the new table. `get_repository()` returns it when `FMF_DATA_SOURCE=sqlite`, reading `FMF_DB_PATH`; `sqlite` is the default and `postgres` serves the deployed API.
- Environment: `OPENROUTER_API_KEY` enables the extractor; `FMF_LLM_MODEL` overrides the model, default `qwen/qwen3-30b-a3b-instruct-2507` (Apache 2.0, supports structured outputs); `FMF_LLM=off` disables it even with a key.

## Consequences

Benefits: the ranker and API run on real crawled pages with one environment variable; every field says where it came from, so a wrong value can be traced to a rule or to the model; unchanged pages cost nothing on re-runs; the model is optional, so tests and CI stay free and deterministic.

Costs and known weaknesses: the rules produce false positives the model must clean up, for example a news page saying a laboratory "cost $5 million" becomes an amount; bare dollar signs are assumed Australian; currency rates are a fixed approximation good enough for banding, not for display; deduplication across sources (decision 8) is still not done, so the same scheme on two sites is two records.

## Evidence

Confluence: Project Crawler Architecture, Our Decisions (decisions 3, 7); the crawler README's own note that banding and classification are the ranker's job, not the crawler's. Code: `backend/crawler/storage.py` schema; `backend/ranking/models.py`. Plan: `docs/10-coding/implementation-plans/2026-09-07-normaliser.md`.
