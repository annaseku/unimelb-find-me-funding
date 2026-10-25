# 10. Coding

> Snapshot of the Confluence page [10. Coding](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/10747905), taken 25 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

**Progress Checklist item 10 (Artefacts).** The Week 7 lecture covers coding standards and linters, repository setup (README, licensing, branch protection, integrations), development through pull requests, meaningful PRs, releases, pair programming and code review.

## Repository

[github.com/annaseku/unimelb-find-me-funding](https://github.com/annaseku/unimelb-find-me-funding): a two-package monorepo, `backend/` (Python 3.11+, FastAPI) and `frontend/` (React 19, TypeScript, Vite).

| Lecture practice | How we do it |
| --- | --- |
| README | Root README: pipeline, status, layout, quick start |
| Coding standards and linters | `CONTRIBUTING.md`; ruff and ESLint enforced in CI |
| Branch protection | Ruleset on main: PR required, one approving review, all seven CI jobs green, no force pushes |
| Development via pull requests | Feature branches named after the Jira key, for example `KAN-42-client-cadence` |
| Meaningful pull requests | PR template: summary, why, test plan, checklist, GenAI use |
| Integrations | Branch names and commit messages carrying `KAN-nn` link the code to the Jira card |
| Releases | A tagged GitHub release at the end of each sprint |
| Code review | Policy and checklist in `CONTRIBUTING.md` (below) |

## Code review policy

From the Week 7 lecture's list of questions a team's policy should answer:

| Question | Our answer |
| --- | --- |
| How many reviewers? | At least one approval before merge, enforced by the ruleset |
| Who reviews? | Anyone except the author. Cross-team reviews (front end reviewing back end and the reverse) are encouraged, to close the knowledge gap from the Sprint 2 retrospective |
| How large? | Aim for under 400 changed lines; split bigger work |
| How fast? | First response within one working day |
| Author preparation | Fill in the PR template, self-review the diff, CI green before requesting review |
| What reviewers look for | The checklist in `CONTRIBUTING.md`: design fit, acceptance criteria met, tests, naming, complexity, comments, security |

## Still to do

- [ ] Licence: the repo has none. Check the project's IP agreement with the client and the University before choosing one
- [ ] Coding standards, testing strategy and deployment documented (KAN-43): closed by this page, [11. Testing](11-testing.md) and [12. Deployment](12-deployment.md) once the repo PR merges
