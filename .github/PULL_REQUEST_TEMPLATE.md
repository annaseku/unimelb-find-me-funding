<!-- Title: type(scope): what changed. Types: feat, fix, test, docs, ci, infra, chore. Scope: backend, frontend, crawler, ranking, normaliser, api. -->

Jira: KAN-

## Summary

<!-- What this PR does, in a sentence or two. Then a bullet per notable change with the file or module it lives in. -->

## Why

<!-- The problem or ticket this solves. If it changes a decision in docs/adr/ or Confluence, say which. -->

## Test plan

<!-- Tick what you ran. Delete the rows that do not apply. -->

- [ ] `pytest backend` passes; `ruff check backend` and `ruff format --check backend` clean
- [ ] `python -m backend.evals.run_evals` still scores 1.00 (ranking or normaliser changes)
- [ ] `npm test`, `npm run lint` and `npm run build` in `frontend/` pass
- [ ] Manually checked: <!-- what you did in the browser or with curl -->
- [ ] All seven CI jobs green on this PR

## Checklist

- [ ] No secrets, `.env` files or API keys in the diff
- [ ] Docs updated where behaviour changed (`README.md`, `backend/README.md`, `docs/api-contract.md`)
- [ ] Architecture or long-term direction change: ADR added to `docs/adr/`
- [ ] Anything left for a follow-up is listed below, not silently dropped

## Follow-ups

<!-- Known gaps, findings you did not fix here, or things the reviewer should decide. Delete if none. -->
