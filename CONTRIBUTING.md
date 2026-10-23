# Contributing

How the team writes, reviews and ships code. Work is tracked on the [KAN board](https://annaseku01.atlassian.net/jira/software/projects/KAN/boards); this file covers what happens in the repository.

## Workflow

1. Pick up a card on the KAN board and move it to In Progress.
2. Branch from an up-to-date main, named after the card: `KAN-42-client-cadence`. The Jira key in the branch name and commit messages links the code to the card automatically.
3. Commit in small, coherent steps. Messages follow `type(scope): what changed`, the same convention as PR titles (types: feat, fix, test, docs, ci, infra, chore; scopes: backend, frontend, crawler, ranking, normaliser, api).
4. Open a pull request against main. The template fills itself in; complete every section.
5. CI must pass (all seven jobs) and one teammate must approve. Then the author merges.
6. Move the card to Done once merged.

Nobody pushes to main directly; the ruleset blocks it.

## Coding standards

Python (`backend/`):

- Python 3.11 or newer, formatted and linted with ruff (`ruff format backend`, `ruff check backend`). CI rejects anything ruff flags.
- Type hints on public functions. Data crossing a boundary (API, database, crawler rows) is a Pydantic model, not a dict.
- One test file per module in `backend/tests/`, named `test_<module>.py`.
- Layers stay separate: `api/` handles HTTP only, `ranking/` and `normaliser/` hold the logic, and the API reads data only through the repositories in `data/`.

TypeScript (`frontend/`):

- React 19 function components in TypeScript, type-checked by `npm run build` and ESLint clean (`npm run lint`).
- Formatted with Prettier (`npm run format`); CI runs `npm run format:check` and rejects unformatted code.
- One component per folder, with its test beside it (`Result/Result.tsx`, `Result/Result.test.tsx`).
- Filter labels and API values live only in `src/data/filterOptions.ts` and must match `backend/ranking/models.py`.

Both:

- Name things after what they mean in the domain: `eligibility`, `opportunity`, `deadline_band`, not `data` or `temp`.
- Comment why, not what. Delete commented-out code rather than committing it.
- No secrets in the repository. Keys go in `.env` locally (gitignored) and in GitHub or Render secrets for deployments.
- Add a dependency only when nothing already in the project does the job, and say why in the PR.

## Code review

At least one approval is required before merge, enforced by the ruleset on main.

**Authors**

- Keep PRs small and about one thing; aim for under 400 changed lines.
- Self-review the diff and get CI green before requesting review.
- Explain what changed and why in the PR template, and link the Jira card and user story.
- Respond to every comment. Resolve a thread only when the change is made or the reviewer agrees it is not needed.

**Reviewers**

- Anyone except the author. Cross-team reviews (front end reviewing back end and the reverse) are encouraged.
- First response within one working day. Review in short sessions rather than one long one.
- Focus on the things below before style. Be specific and kind: suggest, don't command. Take contentious points to a call, then record the outcome on the PR.

**Checklist** (from the Week 7 lecture and Google's engineering practices):

- [ ] Design: does it fit the documented architecture (`docs/09-architectural-design/`) and the layer rules above?
- [ ] Requirements: does it satisfy the acceptance criteria of the linked user story?
- [ ] Tests: are there tests, would they fail if the behaviour broke, and do they cover the edge cases?
- [ ] Complexity: could a teammate change this in a month without asking the author?
- [ ] Naming: do names say what things are?
- [ ] Comments: are they accurate and necessary?
- [ ] Security: no secrets, no unvalidated input reaching a query or a fetch.
- [ ] Docs: are `README.md`, `backend/README.md` or the API contract updated if behaviour changed?

Artefacts other than code, such as test plans, diagrams and requirements, get reviewed too: ask a teammate to read them before they are marked final on Confluence.

## Generative AI

COMP30022 requires GenAI use to be transparent. If a GenAI tool helped with a change:

- Say so in the PR template's GenAI section: which tool, and what it did.
- Add a `Co-Authored-By` trailer naming the tool to the commits it helped write.
- Review every line yourself before committing. You are accountable for it.
- Add a row to the [GenAI Usage Log](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/33488897).

## Bugs

Found in your own PR: fix it there. Found anywhere else: raise a Task labelled `bug` on the KAN board (or a GitHub issue using the bug template if it is only in code you are reviewing) with steps to reproduce, then fix it in a PR that adds a failing test first. The full process is in the test plan under [11. Testing](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/10780673).

## Releases

Every merge to main deploys; the handover build is tagged `v1.0.0`. See `docs/12-deployment/README.md`.
