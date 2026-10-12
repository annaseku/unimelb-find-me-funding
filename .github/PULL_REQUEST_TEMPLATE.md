<!-- Title: type(scope): what changed. Types: feat, fix, test, docs, ci, infra, chore. Scope: backend, frontend, crawler, ranking, normaliser, api. -->

Jira: KAN-  ·  User story: US

## Summary

<!-- What this PR does, in a sentence or two. Then a bullet per notable change with the file or module it lives in. -->

## Why

<!-- The problem or ticket this solves. If it changes a decision in docs/09-architectural-design/adr/ or Confluence, say which. -->

## Test plan

<!-- Tick what you ran. Delete the rows that do not apply. -->

- [ ] `pytest backend` passes; `ruff check backend` and `ruff format --check backend` clean
- [ ] `python -m backend.evals.run_evals` runs and the report has not regressed (ranking or normaliser changes)
- [ ] `npm test`, `npm run lint` and `npm run build` in `frontend/` pass
- [ ] Manually checked: <!-- what you did in the browser or with curl -->
- [ ] All seven CI jobs green on this PR

## Checklist

- [ ] No secrets, `.env` files or API keys in the diff
- [ ] Docs updated where behaviour changed (`README.md`, `backend/README.md`, `docs/09-architectural-design/api-contract.md`)
- [ ] Architecture or long-term direction change: ADR added to `docs/09-architectural-design/adr/`
- [ ] Anything left for a follow-up is listed below, not silently dropped

## GenAI use

<!-- None, or which tool and what it did (drafted code, tests, docs, review). Commits it helped write carry a Co-Authored-By trailer. Add a row to the GenAI Usage Log on Confluence. -->

## Follow-ups

<!-- Known gaps, findings you did not fix here, or things the reviewer should decide. Delete if none. -->
