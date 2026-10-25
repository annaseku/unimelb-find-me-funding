# User Stories and Acceptance Criteria

> Snapshot of the Confluence page [User Stories and Acceptance Criteria](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/33423361), taken 25 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

**Status: Draft, 24/09. Sophia, please check these against the original** [**User Story Board**](user-story-board-original-2408.md) **and correct anything that drifted (KAN-46).** Written as text so each story has an ID that Jira cards and test cases can point to. This answers the Week 9 tutor feedback that it was hard to connect Jira tasks to user stories: every related Jira card now carries a label with its story ID, so searching the board for `labels = US04` lists that story's work.

Format from the Week 3 lecture: _As a \[type of user\], I want \[goal\] so that \[reason\]._ Acceptance criteria from the Week 7 lecture: one to three per story, written before implementation, independently testable, with a clear pass or fail.

## Traceability and estimates

Estimates are story points on the Fibonacci scale (Week 2 lecture). **They are a draft for the team to replace with planning poker at the next workshop (KAN-47).** Jira estimation is not switched on for KAN yet, so the numbers live here until it is.

| Story | Priority | Estimate (draft) | Requirements | Jira | Test cases |
| --- | --- | --- | --- | --- | --- |
| US01 Search by research profile | Must | 5 | FR-03 to FR-08 | KAN-36, KAN-35 | TC01, TC02 |
| US02 Ineligible results never outrank eligible ones | Must | 5 | FR-09, FR-13 | KAN-27, KAN-29 | TC03 |
| US03 Top ten, with more on request | Must | 3 | FR-14, FR-15 | KAN-35, KAN-37 | TC04 |
| US04 See each result's rating on all four criteria | Must | 8 | FR-10 to FR-12, FR-17 | KAN-28, KAN-38 | TC05 |
| US05 Go straight to the funder | Must | 1 | FR-16 | KAN-20 | TC05 |
| US06 Only current opportunities | Must | 3 | FR-12, freshness constraint | KAN-21, KAN-34 | TC06 |
| US07 Coverage beyond a fixed list | Must | 8 | FR-02 | KAN-4, KAN-18 | TC07 |
| US08 A crawler that behaves | Must | 2 | Politeness constraint | KAN-19, KAN-22, KAN-49 | TC08 |
| US09 Researcher profile | Could | 13 | Additional feature | Not started |  |
| US10 Expert- and project-specific search | Could | 13 | Additional feature | Not started |  |

## Stories

### US01 Search by research profile

As a University of Melbourne researcher, I want to describe my research using FoR and ToA codes, citizenship, employer type, career stage, funding type and a short description, so that the results fit my situation.

| # | Given | When | Then |
| --- | --- | --- | --- |
| AC1 | I am on the search form | I pick values in any of the six filters and submit | Results load for exactly those values |
| AC2 | I leave a filter empty | I submit | That filter places no restriction on the results |

### US02 Ineligible results never outrank eligible ones

As a researcher, I want opportunities I am likely ineligible for to appear after everything I could apply for, so that I do not waste time on them.

| # | Given | When | Then |
| --- | --- | --- | --- |
| AC1 | One eligible and one likely-ineligible opportunity | Results are ranked | The likely-ineligible one sorts after the eligible one, whatever its other scores |
| AC2 | An opportunity whose eligibility cannot be determined | Results are ranked | It is included and labelled "unknown", not dropped |

### US03 Top ten, with more on request

As a researcher, I want to see the ten best matches first and ask for more, so that I am not overwhelmed but can keep looking.

| # | Given | When | Then |
| --- | --- | --- | --- |
| AC1 | More than ten opportunities match | I search | Ten results show, with the total number found |
| AC2 | I have seen the first ten | I ask for more | The next results are appended, with no repeats |

### US04 See each result's rating on all four criteria

As a researcher, I want each result to show how it rates on eligibility, match, funding value and deadline, so that I understand why it ranked where it did.

| # | Given | When | Then |
| --- | --- | --- | --- |
| AC1 | Any search result | It is displayed | It shows a label and a reason for each of the four criteria |

### US05 Go straight to the funder

As a researcher, I want a link to the funder's page on every result, so that I can check the details and apply.

| # | Given | When | Then |
| --- | --- | --- | --- |
| AC1 | Any search result | I click its link | The funder's source page opens |

### US06 Only current opportunities

As a researcher, I want closed opportunities hidden by default, so that I only see what I can still apply for.

| # | Given | When | Then |
| --- | --- | --- | --- |
| AC1 | An opportunity marked closed, even with a future deadline | I search with default settings | It is not shown |
| AC2 | The same opportunity | I ask to include closed opportunities | It is shown |

### US07 Coverage beyond a fixed list

As the Research Office, I want the tool to discover funders across the web, so that researchers find opportunities a curated list would miss.

| # | Given | When | Then |
| --- | --- | --- | --- |
| AC1 | A search profile | The crawler runs discovery | Candidate pages come from funders that are not in any seed list |

### US08 A crawler that behaves

As the Research Office, I want the crawler to obey robots.txt and identify itself, so that the University is not blocked or in breach of a site's terms.

| # | Given | When | Then |
| --- | --- | --- | --- |
| AC1 | A URL disallowed by the site's robots.txt | The crawler reaches it | It is never fetched |
| AC2 | Any request the crawler makes | It is sent | It carries a descriptive User-Agent with a contact URL (KAN-22, open) |
