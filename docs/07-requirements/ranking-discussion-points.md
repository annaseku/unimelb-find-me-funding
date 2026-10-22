# Ranking: decisions that need team and client confirmation

Owner: Anna Sekulic. Date: 2026-09-06. These six behaviours are implemented in the ranking prototype but were never settled on Confluence or with Frank. Each is a constant, a weight or a flag default, so changing any of them is a small edit, not a rewrite. Bring this list to the next client check-in.

## 1. Deadline direction: more lead time scores higher

Implemented: over 60 days 1.0, 60 to 30 days 0.8, 30 to 15 days 0.5, under 15 days 0.2, no deadline 0.5.

Evidence: in the 20/08 meeting Frank said a grant deadline six months out is far more useful than one due next week with no lead time. The architecture page's phrase "deadline urgency" reads the opposite way.

Question for the client: should a grant closing in ten days ever rank above an equivalent one closing in three months? If yes, we flip the table in `backend/ranking/deadline.py`.

## 2. Likely-ineligible results are shown and de-ranked, not hidden

Implemented: they stay in the list, always after every result the researcher could apply for, with a reason such as "Citizenship restricted to AU, NZ; you selected GB". The API flag `hide_ineligible` (default false) removes them, so the frontend can offer a toggle.

Why "always after": the first eval run scored ineligible results purely by the weighted average, and a high-match ineligible grant landed at position 7 for the philanthropic-sector profile, above weaker but applicable ones. With only 30 mock records, a UK industry engineer or a philanthropic-sector researcher has just five applicable opportunities, so ineligible ones fill the rest of the top 10 either way; the tier rule at least guarantees the applicable ones come first.

Evidence: Frank said a great match the researcher cannot apply for is "pointless", but also that uncertain ones must stay in. Confluence lists hidden versus de-ranked as unresolved. The Sprint Description floats a per-input "Mandatory vs Preferred" tick box.

Question for the client: default on or off for hiding? If the per-input Mandatory flag is wanted, the request shape gains one boolean per input and a mandatory mismatch becomes a filter.

## 3. Default weights: eligibility 0.4, research match 0.3, funding value 0.15, deadline 0.15

Implemented in `backend/ranking/weights.py`; any request can override them and the response echoes what was used.

Evidence: eligibility is the client's stated top priority. Nothing else about the ratio was ever discussed.

Question for the client: does this ordering match how a researcher weighs a shortlist? Run `python -m backend.evals.run_evals` to see how the top 5 changes under eligibility-heavy, match-heavy and even weightings for each mock profile.

## 4. Funding bands: under $1M, $1M to $2M, $2M to $5M, $5M and over

Implemented with scores 0.25, 0.5, 0.75, 1.0 and 0.5 for an unknown amount.

Evidence: the brief says "banded" and only "$5M AUD" survived in the notes; the bands are the backend README's proposal. Most single-investigator grants (ARC DECRA, Fulbright, PhD stipends) land in the bottom band together.

Question for the client: are finer bands below $1M wanted, for example under $50k, $50k to $250k, $250k to $1M? Edges live in one list in `backend/ranking/funding_value.py`.

## 5. Score values for the eligibility states

Implemented: eligible 1.0, potentially eligible 0.7, unknown 0.5, likely ineligible 0.1. "Potentially eligible" covers both "some checks passed, others could not be checked" and "the funder states no restrictions we can check".

Evidence: none from the client; chosen so an unknown never outranks a confirmed pass and a contradiction always sinks.

Question for the team: with the tier rule in point 2, the 0.1 only orders ineligible results among themselves. If the team prefers pure weighted ordering instead of the tier rule, 0.1 is not low enough: a perfect match with a large amount reaches about 0.64 and outranks an applicable result with a weak match at about 0.47.

## 6. Institution location defaults to Australia

Implemented: `Opportunity.countries` records where the applicant's institution must be based (for example ERC grants need an EU host), and `SearchRequest.institution_country` (default `AU`) is checked against it. With no stated countries, the funder's domain stands in: a local funder or one that mentions Australia passes, an overseas one is marked unknown. The form has no country input, so every search uses the default.

Evidence: the architecture page lists "country restrictions" as a deterministic check, but the brief's input list has no country field.

Question for the client: is defaulting to Australia right, or should the form offer an "institution country" drop-down?
