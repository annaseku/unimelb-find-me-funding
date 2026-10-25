# Client Brief: Project Information

> Snapshot of the Confluence page [Client Brief: Project Information](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/3047425), taken 25 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

Date: 8/10/2026

### Client

**The client** — main director, contacted via email (not on LMS). Limited technical knowledge; focused entirely on the _idea_, not the implementation. According to the other group, he says yes to essentially any feature suggestion, so the brief + these notes are your real constraint list, not further client pushback.

**email:** [client email removed]

### Core Vision

* **Google for funding** — a single search tool that surfaces funding opportunities from anywhere in the world, not a curated/static list of known funding sites.
* Client explicitly **rejected** the idea of pre-selecting a fixed set of big funding sites and pulling from just those, he said that "defeats the purpose."

    * not static, he wants a dynamic web crawling tol
    
* This means: **dynamic web crawling/discovery is a hard requirement**, not just a nice-to-have. A hardcoded list of 20 known funding databases would not satisfy the brief as he's described it.
* **English-language only**: no translation/multilingual handling needed.
* Client is agnostic on LLM use, he doesn't understand or care about the technical approach (LLM vs. otherwise). This is our design decision, not his requirement.

### Users / Stakeholders

* Primarily **researchers**: not exclusively University of Melbourne, but that's the anchor example.
* Inspiration: the **Find an Expert** UniMelb page, client wants users to get **profile-specific, personalised search results**.

    * https://findanexpert.unimelb.edu.au/ 
    
* Notably: users should be able to search/view results **for other people's profiles too** (e.g., a colleague's), not just their own.
* No mobile app needed, web application is sufficient but a mobile app would be nice to have.

### Functional Requirements (from brief)

**Inputs (drop-downs + free text):**

* Field of Research (FoR) & Type of Activity (ToA) — per ANZSRC classification
* Citizenship (multi-select)
* Employer type: University / Research Institute / Industry / Philanthropic org
* Career stage: Undergrad → Grad student → post-doc bands (0–2, 2–5, 5–10, 10+ years)
* Funding type requested: Salary / Consumables / Equipment / All / Any
* Free-text field: brief description of the research for which funding is sought

**Ranking algorithm criteria:**

1. Eligibility — likely eligible / unknown / likely not eligible
2. Match to user input — high / medium / low
3. Value of funding available — banded (<$1M, $1–2M, $2–5M, >$5M AUD)
4. Time to deadline — >60d / 60–30d / 30–15d / <15d

**Output:**

* **Top 10 results**, expandable on request 

    * we might be able to use this as a means to limit the web crawl
    
* Direct link to each opportunity
* A visible rating against each of the four criteria per result

### Requirements/Clarifications from the Client Meeting (not in the brief)

* **Eligibility matching is the top priority** 

    * described as "really important," with **strict** requirements expected. 
    
        * If a result is a great match but the user is ineligible, it's considered pointless — client was emphatic about this.
        
    
* Eligibility classification scheme is **flexible**

    * you can use the official ANZSRC/Australian classification or design your own, as long as it functions to filter opportunities properly. This flexibility also extends to how you handle site-specific eligibility criteria that individual funding bodies list (these need to be scraped/considered too, not just the fields the user fills in).
    
* Missing/unspecified user fields → left to your group's judgement on how to handle (e.g., defaulting to a general/broader search).
* No additional documents, diagrams, or resources beyond LMS materials were provided to the client-facing group either.

### Open Questions / Gaps (worth flagging to tutors or noting as assumptions)

These weren't resolved in either the brief or the meeting, worth deciding as a team and documenting as assumptions:

1. **Live crawling vs. periodic indexing vs. APIs** — brief implies dynamic search, but real-time crawling of the entire web for funding is a huge technical ask. Likely need a hybrid (e.g., periodic crawl + index, refreshed on a schedule) — this is a key architecture decision, not something the client specified.
2. **How "eligibility unknown" is determined** — no defined threshold for likely eligible vs unknown vs not eligible.
3. **Whether ineligible opportunities should be shown at all**, or filtered out entirely, or shown but ranked low/flagged.
4. **Weighting of the four ranking criteria relative to each other** — not specified; you'll need to define and justify this.
5. Data freshness / update frequency for funding info — not discussed.
