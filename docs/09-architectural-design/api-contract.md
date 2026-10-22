# API contract: backend to frontend

The seam between `backend/api/` and `frontend/`. This answers Jira KAN-11 (create API agreement). The authoritative version is the OpenAPI schema the backend serves at `/openapi.json`, with interactive docs at `/docs`. This file is the human summary; if the two disagree, the running backend wins and this file is stale.

All endpoints are under `/api`. Requests and responses are JSON.

## Base URL

| Where | URL |
| --- | --- |
| Deployed | `https://find-me-funding-api.onrender.com` |
| Local | `http://localhost:8000` (`uvicorn backend.api.main:app --reload` from the repository root) |

Read it from an environment variable rather than hardcoding it, so the same build can point at either. The deployed service is on Render's free plan, which sleeps after about 15 minutes idle: the first request after that takes close to a minute while the container wakes, and the UI should say so rather than show a spinner that looks stuck.

CORS allows the Vite dev server (`localhost:5173` and `127.0.0.1:5173`) and the deployed frontend at `https://annaseku.github.io`. Serving the frontend from anywhere else needs that origin adding in `backend/api/main.py`.

## `GET /api/health`

```json
{ "status": "ok", "version": "0.1.0" }
```

## `POST /api/search`

Rank funding opportunities against a researcher's inputs. Every field is optional; `{}` returns everything indexed, ranked with no personalisation.

| Field | Type | Notes |
| --- | --- | --- |
| `for_codes` | `string[]` | ANZSRC 2020 Field of Research codes, two or four digits, e.g. `["3103"]` |
| `toa_codes` | `string[]` | ANZSRC type of activity, `"1"` to `"4"` |
| `citizenships` | `string[]` | ISO 3166-1 alpha-2, multiple allowed |
| `institution_country` | string | ISO 3166-1 alpha-2 of the researcher's institution, default `AU`. Eligibility passes funders in this country (stated, `.au` domain, or text naming Australia) and marks overseas-domain funders `unknown` |
| `employer_type` | enum or null | `university`, `research_institute`, `industry`, `philanthropic` |
| `career_stage` | enum or null | `undergraduate`, `graduate_student`, `postdoc_0_2`, `postdoc_2_5`, `postdoc_5_10`, `postdoc_10_plus` |
| `funding_types` | enum[] | `salary`, `consumables`, `equipment`, `all`, `any` |
| `research_description` | string | Free text describing the research |
| `hide_ineligible` | bool | Default false. True drops likely-ineligible results instead of listing them last |
| `include_closed` | bool | Default false. True includes closed and past-deadline records |
| `limit` | int | 1 to 100, default 10 |
| `offset` | int | 0 or more, default 0 |
| `weights` | object or null | Partial override, e.g. `{"deadline": 0.3}`; keys are `eligibility`, `research_match`, `funding_value`, `deadline` |

Example request:

```json
{
  "citizenships": ["AU"],
  "employer_type": "university",
  "career_stage": "postdoc_2_5",
  "funding_types": ["consumables", "equipment"],
  "for_codes": ["3103", "3708"],
  "research_description": "Coral reef resilience to ocean acidification",
  "limit": 1
}
```

Response, taken from the running prototype on 2026-09-06 and trimmed to one result:

```json
{
  "results": [
    {
      "opportunity": {
        "id": "gbrf-reef-trust-partnership",
        "title": "Reef Trust Partnership: Reef Restoration and Adaptation",
        "funder": "Great Barrier Reef Foundation",
        "url": "https://barrierreef.org/what-we-do/reef-trust-partnership",
        "source_urls": ["https://barrierreef.org/what-we-do/reef-trust-partnership"],
        "summary": "The Reef Trust Partnership funds large-scale reef restoration and adaptation projects ...",
        "amount_aud": null,
        "amount_note": "scaled to project",
        "deadline": "2026-12-15",
        "opens_at": null,
        "countries": ["AU"],
        "citizenships_allowed": [],
        "employer_types_allowed": ["university", "research_institute", "philanthropic"],
        "career_stages_allowed": [],
        "funding_types_offered": ["consumables", "equipment"],
        "for_codes": ["31", "3103", "3708"],
        "toa_codes": ["3", "4"],
        "keywords": ["coral reef", "ocean acidification", "reef resilience", "restoration", "Great Barrier Reef"],
        "eligibility_text": "Applicants must be an eligible Australian university, research institute or philanthropic partner ...",
        "status": "active"
      },
      "overall": 0.925,
      "eligibility": {
        "score": 1.0,
        "label": "eligible",
        "reasons": [
          "Employer type accepted: open to university, research_institute, philanthropic; you selected university.",
          "Funding type: offers consumables, equipment, which you asked for."
        ]
      },
      "research_match": {
        "score": 1.0,
        "label": "high",
        "reasons": [
          "Matches your field of research code 3103, 3708.",
          "Your description shares terms with the opportunity: acidification, coral, ocean, reef, resilience."
        ]
      },
      "funding_value": { "score": 0.5, "label": "unknown", "reasons": ["Funding amount not stated."] },
      "deadline": { "score": 1.0, "label": "over_60_days", "reasons": ["Closes in 100 days (2026-12-15)."] }
    }
  ],
  "total": 27,
  "limit": 1,
  "offset": 0,
  "weights": { "eligibility": 0.4, "research_match": 0.3, "funding_value": 0.15, "deadline": 0.15 }
}
```

Labels per criterion: `eligibility` is one of `eligible`, `potentially_eligible`, `unknown`, `likely_ineligible`. `research_match` is `high`, `medium`, `low`. `funding_value` is `under_1m`, `from_1m_to_2m`, `from_2m_to_5m`, `over_5m`, `unknown`. `deadline` is `over_60_days`, `days_60_to_30`, `days_30_to_15`, `under_15_days`, `closed`, `unknown`.

## `GET /api/opportunities/{id}`

Returns the `opportunity` object above for one id, including closed records. 404 with `{"detail": "opportunity not found"}` if the id is unknown.

## `GET /api/status`

How the data behind the results was produced, so the frontend can warn when AI summaries are missing (KAN-67).

```json
{
  "last_run": {
    "finished_at": "2026-10-18T09:05:00Z",
    "llm_calls": 5,
    "llm_failures": 1,
    "llm_stop_reason": "daily_quota",
    "llm_stop_detail": "429 Too Many Requests"
  },
  "opportunities": 164,
  "rule_only_summaries": 159
}
```

`last_run` is null before the first recorded run. `llm_stop_reason` is null when the LLM ran to the end, `daily_quota` when the provider kept rate-limiting past every retry, `plan_error` when it rejected the key or the account was out of credits (OpenRouter 401 or 402), and `not_configured` when the run had no OpenRouter key. A rate limit that clears within the retries never appears here. `rule_only_summaries` counts stored opportunities whose summary was built by rules rather than the LLM.

## Contract rules

These are team decisions, not implementation details. Changing one needs a conversation.

1. The four criterion scores are always returned separately alongside `overall` (Confluence decision 5). The frontend renders all four; never collapse them into one number.
2. `weights` is echoed on every response so the UI can show how `overall` was reached without hardcoding backend configuration.
3. `eligibility.label` has four values, not two (decision 4). `unknown` is a normal outcome, not an error.
4. `reasons` are written for a researcher and are meant to be displayed, not just logged.
5. Closed and past-deadline records are excluded unless `include_closed` is true (decision 9). Likely-ineligible records are listed after every other result unless `hide_ineligible` is true.
6. Paging is `limit` plus `offset` over the same ranked set (decision 6). "Show more" never triggers a crawl.
7. `total` is the size of the full ranked set, not of the page. The UI uses it to decide whether to offer "show more".

## Errors

| Status | When |
| --- | --- |
| 422 | Validation failed, for example `limit: 0` or an unknown `career_stage`. FastAPI names the offending field. |
| 404 | Unknown opportunity id. |
| 500 | Unhandled server error. |

## Keeping the two sides in step

The frontend has no generated types yet. When the request or response shape changes, update this file and tell the frontend owners. Generating TypeScript types from `/openapi.json` (for example with `openapi-typescript`) would remove that manual step and is worth doing once the shape stops changing.
