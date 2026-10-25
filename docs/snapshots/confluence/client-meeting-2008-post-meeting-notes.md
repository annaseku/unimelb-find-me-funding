# Client Meeting 20/08: Post-Meeting Notes

> Snapshot of the Confluence page [Client Meeting 20/08: Post-Meeting Notes](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/9469953), taken 25 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

‌

**Project:** Web Crawler – "Find Me Funding!" **Type:** Joint check-in (all three student teams building the funding-finder tool)

---

## Key Decisions / Action Items

* **Split the search into two modes:**

    * **Project-specific search (must-have):** user describes a specific piece of research/project they need funding for.
    * **Generic profile-based search (nice-to-have):** broader search based on the researcher's overall profile/fields of research.
    
* **Support multiple Fields of Research per user** — researchers typically work across several FoR areas, not just one.
* **No University of Melbourne SSO required.** IT will not approve real login integration — mock it up if a login flow is needed. Manual profile entry (or linking to a public _Find an Expert_ page) is the accepted fallback.
* **Auto-importing profile data from Find an Expert is a stretch goal**, not core functionality — university pages may block crawlers, and this should only be tackled after core features work.
* **Include upcoming (not-yet-open) funding opportunities**, but only if a deadline is known, and apply a time-frame filter (\~6–9 months out). Add a toggle for "upcoming vs. currently open."
* **Geographic scope:** broadly worldwide (US, South America, UK, Europe, parts of Asia) — nothing explicitly excluded by region.
* **Language scope:** English-language opportunities only.
* **Funding scope:** research funding only — exclude arts, education, and other non-research funding types.
* **Sign-in / saved searches:** guest access without login is the baseline and considered critical; optional sign-in to save searches/preferences is a nice-to-have.
* **Eligibility handling:**

    * Each funder describes eligibility differently with no standard format — rule-based/mechanical filtering is impractical.
    * Recommended approach: use **LLM-based confidence scoring** to classify eligibility as **likely eligible / uncertain / likely not eligible**, rather than a fixed rules engine.
    * Ambiguous cases (e.g., citizenship not required but funds must be spent domestically) should generally fall into the "uncertain/likely" middle ground rather than being force-fit into eligible/ineligible.
    

---

## Discussion Highlights

**Profile vs. project search confusion** The client used a University of Melbourne _Find an Expert_ profile (a colleague, an optometrist/researcher) to illustrate that researchers usually have multiple overlapping fields of research and multiple active projects. He clarified that it wasn't obvious to him which inputs (profile vs. project fields) actually drove the search — prompting the decision to separate the two search types above.

**Login/data source** Since Find an Expert pages are public, no university login is needed to view them, but the university may still block automated crawling of its own site. Manual entry (or the user pasting in a profile link) is the safer path for now.

**Upcoming opportunities** The client confirmed a grant deadline six months out is far more useful to surface than one due next week with no lead time — deadline visibility matters more than "open now" status.

**Scope questions** The client confirmed the tool should stay focused on _research_ funding specifically (not arts/education), English-language only, and broadly global with no particular country excluded upfront.

**Eligibility** The client was clear that mechanical rule-based eligibility filtering won't work well because funders phrase eligibility conditions inconsistently. He recommends leaning on an LLM's confidence judgement rather than a strict binary/rules-based approach.

---

## Open Notes for Follow-Up (not resolved in this meeting)

* Exact weighting between eligibility, match quality, funding value, and deadline proximity in the ranking algorithm.
* Whether ineligible results should be hidden entirely or shown but flagged/de-ranked.
* Concrete "success" examples for demo/MVP scope (e.g., should the tool be expected to surface known international schemes like NIH, ERC, Wellcome from day one?).
* Mobile app: reconfirmed as out of scope / not a real requirement, just a "nice to have" aside.

### Jummana’s Follow-Up Notes 

* make a storyboard
* can make searches based on projects?
* project scope is global 
* perhaps using an LLM to tailor to research
* LLM definitely needs to be used

---

_Notes compiled from transcript of joint client check-in meeting, 2026._

# Transcript and Notion Meeting Summary

‌

[https://www.notion.so/Meeting-3c246958f85980a09792d98e9f45ba49?source=copy_link](https://www.notion.so/Meeting-3c246958f85980a09792d98e9f45ba49?source=copy_link)

‌
