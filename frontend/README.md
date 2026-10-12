## Funding API integration

The frontend sends searches to `POST /api/search` and renders the four ranked criteria and their reasons. It uses `https://find-me-funding-api.onrender.com` by default.

For a local backend, copy `.env.example` to `.env.local` and set `VITE_API_BASE_URL=http://localhost:8000`. Restart Vite after changing it. Vite embeds this public URL at build time; never place secrets in a `VITE_` variable. The Pages workflow reads the optional repository variable `VITE_API_BASE_URL`, falling back to the deployed API.

Filter labels and API values live together in `src/data/filterOptions.ts`. Empty selections send no restriction. The current list preserves the dropdown branch's selected FoR codes and countries; it is not an exhaustive classification list. Keep new values aligned with `backend/ranking/models.py` and `docs/09-architectural-design/api-contract.md`.

Results use the server's total and load further pages against the last submitted search. Editing controls takes effect on Search. Requests are cancelled when superseded or the page is left, and have a two-minute timeout to accommodate service cold starts. Failures offer a retry without falling back to placeholder data.

Run `npm test`, `npm run lint`, and `npm run build` before submitting changes. Tests stub the HTTP boundary, so they do not depend on the live service or its data.

---

# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])

```

You can also install [eslint-plugin-react-x](https://npmx.dev/package/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://npmx.dev/package/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])

```
