# Legal, Ethics and Data Handling

> Snapshot of the Confluence page [Legal, Ethics and Data Handling](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/30867457), taken 25 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

**Status** Draft — team review needed  ·  **Owner** Anna Sekulic  ·  **Last reviewed** 21 Sep 2026

Created in response to supervisor feedback asking for a _review of legal policy and terms of service_.

## Why this page exists

The core function of this system is retrieving content from websites we do not own. That carries obligations, and until now our position on them existed only as code. This page states the position so it can be reviewed, challenged and cited.

## What we already do

These are implemented and enforced in the codebase, not aspirations.

| Obligation | How it is met | Where |
| --- | --- | --- |
| **Respect robots.txt** | Every fetch passes through an `is_allowed(url)` check before the request is made. A disallowed URL is never fetched. | `backend/crawler/robotCheck.py` |
| **Controlled crawl rate** | Crawling is driven by a scheduler on a staleness interval, not by user traffic. A user search never triggers a fetch, so load on funder sites cannot spike with our usage. | `backend/crawler/scheduler.py`, `config.py` |
| **Public data only** | We crawl publicly accessible funding opportunity pages. No authentication, no paywall circumvention, no personal data scraped from funder sites. | Crawler scope |
| **No credential storage** | API keys live in environment variables and are gitignored; `.env.example` documents the shape without the values. | `backend/.env.example` |

## Open questions for the team and the client

These are genuinely unresolved. Do not treat this section as settled — it is the agenda for the review.

- [ ] **Terms of service review.** robots.txt is a machine-readable signal, not a licence. Several major funder sites also publish website terms that may restrict automated access regardless of robots.txt. We have not yet read the ToS of our target sites. _Owner: TBC_
- [ ] **Target site list.** Which funders are in scope? The answer determines whose terms we need to read. Needs confirmation with the client.
- [ ] **Attribution and linking.** Do we display funder content verbatim, or summarise and link out to the source? Linking out is lower risk and probably better for the user; this should be an explicit decision, recorded as an ADR.
- [ ] **Data retention.** How long do we keep a crawled opportunity after its deadline passes? No policy currently exists.
- [ ] **Researcher data.** The prototype uses mock profiles. If real researcher profiles are stored later, University privacy obligations apply and this page needs a privacy section before that happens.
- [ ] **LLM data flow.** Page content is sent to the Google Gemini API for field extraction. We should confirm that sending publicly available funder page text to a third-party model is acceptable to the client, and record the answer.
- [ ] **Crawler identification.** Industry practice is to send a descriptive User-Agent with a contact URL so site owners can reach us. Worth confirming whether we do this.

## Our stated position

Pending the review above, the team's working position is:

We crawl only publicly accessible pages, and only where robots.txt permits.Crawl frequency is bounded by our own scheduler, never by user demand.Whether we reproduce funder text or summarise and link out.Retention period for expired opportunities.

## Next step

Raise the open questions at the next client meeting, and record the answers here with the date. Once the terms-of-service review is done, its findings become an ADR so the reasoning is preserved alongside the other architecture decisions.
