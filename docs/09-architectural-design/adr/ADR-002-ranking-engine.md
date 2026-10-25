# ADR-002: Ranking engine design

| Field | Value |
| --- | --- |
| Decision ID | ADR-002 |
| Decision | Rank opportunities with four separately computed criterion scores (eligibility, research match, funding value, deadline), each returning a score, a label and plain-English reasons, combined by a weighted average with configurable weights. Deterministic rules only in this sprint; a named seam is left for an LLM or embedding scorer. |
| Status | ⚪ Proposed (implemented on main, not yet ratified with the client) |
| Owner | Anna Sekulic |
| Date | 2026-09-06 |

## Context

The client brief requires each result to show a rating against four criteria and the results to be ordered by attractiveness. Confluence decision 5 (Critical) says the four scores must stay separate and be combined with configurable weights rather than collapsed into one unexplained LLM score. Decision 4 says eligibility has four states and uncertain opportunities stay in the results. Decision 3 says deterministic checks handle the simple yes/no questions and the LLM is reserved for research fit and complicated eligibility prose. The Sprint Description (31 Aug) puts LLM implementation out of scope for this sprint.

The crawler currently stores raw signals (page text, a parsed deadline, a raw dollar string, an eligibility snippet), not structured fields. The ranker therefore consumes a structured `Opportunity` model fed from illustrative mock data; normalising crawler rows into that model is a later step.

## Options considered

1. One ranking module with four functions. Fastest to write; grows past what a teammate can hold in their head and puts every test in one file.
2. One module per criterion plus a combiner (chosen). Each file is under 150 lines, has one job, and its own test file. Weights live in one place.
3. Pluggable scorer classes with a registry. Flexible, but abstraction for a future that has not arrived; the LLM only needs a function seam.
4. One LLM-produced overall score. Rejected by decision 5: opaque, untestable, not explainable to the researcher.

## Decision details

Scores per criterion, all in the range 0.0 to 1.0:

| Criterion | Labels and scores |
| --- | --- |
| Eligibility | eligible 1.0, potentially eligible 0.7, unknown 0.5, likely ineligible 0.1 |
| Research match | high (0.75 and above), medium (0.4 and above), low; from FoR code overlap (weight 0.5), free-text coverage (0.4), ToA overlap (0.1), renormalised over the signals available. Text uses Porter2 English stemming (snowballstemmer), stop words matched on stems, funding and career vocabulary (fellowship, early career, scholarship and so on) ignored by the text match because other filters cover it, and corpus IDF weights log((N + 1) / (df + 1)) + 1 over open/closed-filtered opportunities; half of the description's term weight present gives a full text score. Single-call scoring without corpus weights uses uniform term weights; reasons show the researcher's words, highest weight first |
| Funding value | under $1M 0.25, $1M to $2M 0.5, $2M to $5M 0.75, $5M and over 1.0, unknown 0.5 |
| Deadline | over 60 days 1.0, 60 to 30 days 0.8, 30 to 15 days 0.5, under 15 days 0.2, unknown 0.5, closed 0.0 |

Overall is the weighted average with default weights eligibility 0.4, research match 0.3, funding value 0.15, deadline 0.15. Callers may override any weight per request and the response echoes the weights used. Likely-ineligible results always sort after every other result regardless of overall, because the client said a great match the researcher cannot apply for is pointless. Within a tier, ties break on eligibility score, then id.

Closed opportunities (status closed, or deadline passed) are filtered out at read time and retrievable with `include_closed`, per decision 9. Likely-ineligible results are shown and de-ranked by default and hidden with `hide_ineligible`.

## Consequences

Benefits: every result explains itself; each rule is a constant or a small function a teammate can change in one place; the eval suite (`backend/evals`) catches ranking regressions; the frontend contract does not change when the LLM arrives.

Costs: keyword overlap is a weak proxy for research fit until the semantic scorer lands; the four-band funding scale puts most single-project grants in the bottom band; six behaviours were decided without client confirmation and are listed in `docs/07-requirements/ranking-discussion-points.md`.

## Evidence

Confluence: Project Crawler Architecture, Our Decisions (decisions 3, 4, 5, 6, 9); 20/08 Post Meeting Notes (eligibility is the top priority, uncertain results stay in, a six-month deadline beats one due next week); Sprint Description (LLM out of scope). Spec: `docs/09-architectural-design/design-specs/2026-09-06-ranking-engine-design.md`.
