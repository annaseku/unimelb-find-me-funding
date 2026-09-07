// Loaded by Vitest before every test file (see vite.config.ts).
// Adds the jest-dom matchers (toBeInTheDocument, toHaveAttribute, ...) to expect
// and unmounts rendered trees between tests so state never leaks across them.
import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

afterEach(() => {
  cleanup();
});
