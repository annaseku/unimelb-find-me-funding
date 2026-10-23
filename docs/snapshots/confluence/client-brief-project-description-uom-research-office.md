# Client Brief: Project Description (UoM Research Office)

> Snapshot of the Confluence page [Client Brief: Project Description (UoM Research Office)](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/2621441), taken 23 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

**Web crawler – Find me funding!**

A web based tool (probably a LLM but I am agnostic) that searchers for available research funding opportunities based on user inputs, and returns funding opportunities ranked by attractiveness.

User input to contain a combination of drop-down menus, including:

* [FoRLinks to an external site. & Links to an external site.ToALinks to an external site.](https://www.abs.gov.au/statistics/classifications/australian-and-new-zealand-standard-research-classification-anzsrc/latest-release) (See link for info).
* Citizenship (could be multiple).
* Employer type (University; Research Institute; Industry; Philanthropic organization).
* Career Stage (Undergraduate, Graduate Student, <2 years post-doc, <5 years post-doc, <10 years post-doc, >10 years post-doc.
* Funding Type Requests(Salary, Consumable, Equipment, All kinds, Any kind).
* Free text field asking for a brief explanation of the kind of research for which funding is being sought.

The tool should search for suitable funding opportunities returning ranked results with ranking based on an algorithm that considers:

* eligibility (likely eligible, eligibility unknown, likely not eligible)
* match to user input (high, medium, low)
* value of available funding (<$5M, $2-5M, $1-2M, <$1M AUD)
* Time to deadline (>60 days, 60-30 days, 30-15 days, <15 days)

Output should include:

* top 10 returns, with an ability to ask for more.
* a web-link to each funding opportunity

**the rating against each of the above criteria for each funding opportunity.**

‌
