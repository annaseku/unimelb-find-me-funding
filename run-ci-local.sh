#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

echo "== Backend lint =="
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements-dev.txt
ruff check backend main.py --config backend/pyproject.toml
ruff format --check backend main.py --config backend/pyproject.toml

echo "== Backend tests =="
pytest backend -q
python -m backend.evals.run_evals

echo "== Frontend lint and tests =="
cd "$ROOT/frontend"
npm ci
npm run lint
npm run format:check
npm run test:coverage
npm run build

echo "== Playwright E2E =="
python3 -m pip install -r ../backend/requirements.txt >/dev/null
npx playwright install --with-deps chromium >/dev/null
npm run test:e2e

echo "== Local CI checks passed =="
