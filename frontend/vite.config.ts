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
  },
})
