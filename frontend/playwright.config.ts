import { defineConfig, devices } from '@playwright/test'

// End-to-end: the real frontend against the real API on a seeded evals corpus database.
// Locally, point PYTHON at a venv that has backend/requirements.txt installed.
const python = process.env.PYTHON ?? 'python3'
// Port 8001, not the usual 8000, so a dev API already running is never mistaken for this one.
const apiUrl = 'http://127.0.0.1:8001'

export default defineConfig({
  testDir: './e2e',
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [['list'], ['html', { open: 'never' }]] : 'list',
  use: {
    baseURL: 'http://127.0.0.1:5173',
    trace: 'retain-on-failure',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: [
    {
      command: `"${python}" -m backend.evals.seed_sqlite frontend/e2e/.fixture.db && "${python}" -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8001`,
      cwd: '..',
      url: `${apiUrl}/api/health`,
      // Use the seeded corpus database independently of a developer's shell settings.
      env: { FMF_DATA_SOURCE: 'sqlite', FMF_DB_PATH: 'frontend/e2e/.fixture.db' },
      reuseExistingServer: false,
    },
    {
      command: 'npm run dev -- --host 127.0.0.1 --port 5173 --strictPort',
      url: 'http://127.0.0.1:5173',
      env: { VITE_API_BASE_URL: apiUrl },
      reuseExistingServer: false,
    },
  ],
})
