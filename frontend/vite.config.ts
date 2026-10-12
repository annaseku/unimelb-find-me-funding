import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // GitHub Pages serves the site under /<repo>/; Frontend CD sets BASE_PATH.
  base: process.env.BASE_PATH ?? '/',
  test: {
    // Components need a DOM; jsdom is the lightest one Testing Library supports.
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    include: ['src/**/*.test.{ts,tsx}'],
    // Report only, no thresholds, until the team agrees one (KAN-50).
    coverage: {
      provider: 'v8',
      include: ['src/**/*.{ts,tsx}'],
      exclude: ['src/**/*.test.{ts,tsx}', 'src/test/**', 'src/main.tsx', 'src/**/*.d.ts'],
      reporter: ['text'],
    },
  },
})
