# Crawler Architecture Decisions

> Snapshot of the Confluence page [Crawler Architecture Decisions](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/12943361), taken 25 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

‌

```
                 ┌──────────────────────┐
                 │    Funding Sources   │
                 │ Websites / Portals   │
                 └──────────┬───────────┘
                            │
                   Dynamic / Hybrid
                       Crawling
                            │
                            ▼
                 ┌──────────────────────┐
                 │   Crawler Workers    │
                 │                      │
                 │ • Discover sources   │
                 │ • Fetch pages        │
                 │ • Detect changes     │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Content Extraction   │
                 │ & Normalisation      │
                 └──────────┬───────────┘
                            │
            ┌───────────────┴───────────────┐
            ▼                               ▼
   ┌─────────────────┐             ┌─────────────────┐
   │ Rules / Filters │             │       LLM       │
   │                 │             │                 │
   │ • Deadline      │             │ • Eligibility   │
   │ • Country       │             │ • Research fit  │
   │ • Citizenship   │             │ • Ambiguity     │
   └────────┬────────┘             └────────┬────────┘
            │                               │
            └───────────────┬───────────────┘
                            ▼
                 ┌──────────────────────┐
                 │ Funding Opportunity  │
                 │ Database + Search    │
                 │ Index                │
                 └──────────┬───────────┘
                            │
                     Search / Ranking
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Researcher Profile   │
                 │ + Search Query       │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Ranked Results       │
                 │                      │
                 │ Top 10 + More        │
                 │ Eligibility          │
                 │ Research Match       │
                 │ Funding              │
                 │ Deadline             │
                 └──────────────────────┘
```

‌

# Architectural Decisions — Web Crawler

These proposed architectural decisions are based on the client questions and answers from **Questions to Ask - 20/08/2** and the current project information.

## 1. Crawler Strategy — Dynamic Discovery vs Fixed Sources

**Question:**    
What exactly do you mean by dynamic web crawling? Do you expect the system to discover completely new funding websites, or is regularly updating a broad collection of funding sources sufficient?

**What we know:**

* The client wants data to be as global and fresh as possible.
* Dynamic crawling has been identified as an architecture decision rather than a fixed client requirement.

**Proposed Decision:**    
Use a **hybrid crawler** consisting of seeded funding sources and dynamic link/source discovery.

**Rationale:**

* A purely static crawler would become difficult to maintain.
* Completely unrestricted crawling creates scope and quality problems.
* A hybrid approach provides controlled discovery while remaining dynamic.

**Priority:** High

---

## 2. Data Freshness and Crawl Frequency

**Client Requirement:**    
The client wants results to be **close to real time**.

**Proposed Decision:**    
Once-per-day batch crawl to start. 

**Priority:** High

---

## 3. LLM Role — LLM vs Rules / Hybrid

**Client Feedback:**

* The LLM should be useful for complicated eligibility decisions.
* The LLM should help with complex research projects.
* Uncertain opportunities should generally still be included rather than discarded.

**Proposed Decision:**    
Use a **hybrid rules + LLM architecture**.

**Proposed flow:**

`Crawler → Information Extraction → Deterministic Checks → LLM Reasoning → Ranking`

**Deterministic checks could include:**

* Citizenship requirements
* Country restrictions
* Funding amount
* Deadline
* Explicit eligibility requirements

**LLM tasks could include:**

* Determining whether a research project matches the funding theme
* Interpreting complicated eligibility descriptions
* Handling ambiguous language
* Explaining why an opportunity is relevant

The system should avoid relying entirely on the LLM for a simple Yes/No eligibility decision.

**Priority:** Critical

---

## 4. Handling Uncertain Eligibility and Information

**Client Feedback:**

* If an opportunity is highly relevant but one eligibility requirement cannot be verified, it should still be included.
* If information cannot be determined, the system should ideally try to find the information elsewhere.

**Proposed Decision:**    
The system should support uncertainty rather than only using an Eligible/Ineligible classification.

**Possible states:**

* Likely Eligible (green)
* Potentially eligible (yellow)
* Unknown (grey)
* Likely ineligible (red)

This approach should apply to uncertain information such as eligibility, funding amount and deadlines.

**Priority:** High

---

## 5. Ranking Architecture

**Question:**    
How should eligibility, research match, funding value and deadline be prioritised relative to each other?

This remains unresolved and should become a team/client architecture decision.

**Proposed Decision:**    
Produce separate scores for:

* Eligibility
* Research/project match
* Funding value
* Deadline urgency

These scores can then be combined using configurable weights to produce the overall ranking.

The system should avoid relying on the LLM to produce one unexplained overall score.

**Benefits:**

* More transparent
* Easier to modify
* Easier to test
* Easier to explain to users

**Priority:** Critical  
  
**Proposed Architecture**

```
                Candidate Opportunity
                        │
         ┌──────────────┼───────────────┐
         ▼              ▼               ▼
    Eligibility    Research Match   Opportunity
    assessment      assessment       attributes
         │              │               │
         ▼              ▼               ▼
    confidence      confidence      structured data
         │              │               │
         └──────────────┼───────────────┘
                        ▼
                Ranking Engine
                        │
              configurable weights
                        │
                        ▼
                 Overall Score
                        │
                        ▼
              Ranked Opportunities
```

  

---

## 6. Search and Index Architecture

**Project Requirement:**    
The system should return the top 10 results, with the ability to ask for more.

**Question:**    
When users request more than 10 results, should the system return existing indexed results or perform additional crawling?

**Proposed Decision:**    
Search the existing index first.

**Proposed architecture:**

`Crawler → Continuously builds/updates index`

`User Search → Queries index`

`Request for more → Queries the same index`

`Insufficient results → Trigger additional discovery/crawling if necessary`

This keeps normal searches fast while still allowing dynamic discovery when required.

**Priority:** Critical

---

## 7. Storage and Search Technology

This is primarily a technical team decision rather than something the client has specified.

**Proposed Decision:**    
Separate raw content storage, structured funding data and the search index.

**Raw data storage:**

* Original page/content
* Crawl metadata
* Source URL

**Structured database:**

* Funding organisation
* Deadline
* Funding amount
* Eligibility
* Countries
* Research areas

**Search index:**

* Keyword search
* Filtering
* Ranking
* Potentially semantic/vector search

A hybrid search approach combining keyword/filter search with semantic/vector search should be investigated because the system needs to match researcher projects with funding descriptions.

**Priority:** High

---

## 8. Duplicate Funding Opportunities

**Question:**    
If the same funding opportunity appears on multiple websites, should the system combine those into one result?

This remains unresolved.

**Proposed Decision:**    
Deduplicate opportunities at the funding-opportunity level while retaining multiple source URLs.

For example, the same opportunity may be discovered through:

* The funding organisation's website
* A university funding page
* A research portal

The user should see one opportunity, while the backend retains the different discovered sources.

**Priority:** Medium-High

---

## 9. Stale, Closed or Disappearing Funding Pages

**Question:**    
What should happen when a funding webpage disappears or an opportunity closes?

**Proposed Decision:**    
Use soft deletion/archiving rather than immediately deleting the record.

**Possible lifecycle:**

`Active → Deadline Passed → Inactive / Archived`

The user interface can hide inactive opportunities by default.

**Benefits:**

* Auditing
* Debugging
* Historical records
* Avoiding unnecessary rediscovery

**Priority:** Medium

---

## 10. Researcher Profile Architecture

**Client Feedback:**

* Direct University of Melbourne access verification is difficult.
* Unique profiles could save preferences.
* Users should ideally be able to filter using another person's projects.

**Proposed Decision:**    
Use a researcher profile containing information that can be used for personalised funding searches.

**Possible profile information:**

* Name / identifier
* Research projects
* Research areas
* Citizenship
* Preferences
* Saved searches

**Proposed flow:**

`Researcher Profile → Search → Funding Opportunities`

This allows the same search system to be reused for different researchers.

**Priority:** Medium

---

# Recommended Architecture Decision Priorities

1. **LLM vs Rules / Hybrid Eligibility Architecture** — Critical
2. **Crawler Strategy** — High / Critical
3. **Data Freshness / Crawl Scheduling** — High
4. **Search + Ranking Architecture** — Critical
5. **Storage + Indexing** — High
6. **Unknown / Uncertain Information Handling** — High
7. **Deduplication** — Medium-High
8. **Researcher Profile Architecture** — Medium
9. **Expired / Dead Opportunity Handling** — Medium
10. **More-than-10 Results Behaviour** — Medium
