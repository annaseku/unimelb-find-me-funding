import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import App from './App';

import { page } from './test/fundingFixture';
beforeEach(() => { vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => page })); });
afterEach(() => vi.unstubAllGlobals());

const findTimeout = { timeout: 2000 };

function renderApp(initialEntry: string) {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <App />
    </MemoryRouter>,
  );
}

describe('App', () => {
  it('renders the Home heading at /', () => {
    renderApp('/');

    expect(screen.getByRole('heading', { name: 'Find Me Funding' })).toBeInTheDocument();
  });

  it('renders the Results heading at /results', async () => {
    renderApp('/results');

    expect(screen.getByRole('heading', { name: 'Search Results' })).toBeInTheDocument();
    await screen.findByText(/Results Found/, {}, findTimeout);
  });

  it('renders a nav landmark on the home route', () => {
    renderApp('/');

    expect(screen.getByRole('navigation')).toBeInTheDocument();
  });

  it('renders a nav landmark on the results route', async () => {
    renderApp('/results');

    await screen.findByText(/Results Found/, {}, findTimeout);
    expect(screen.getByRole('navigation')).toBeInTheDocument();
  });

  it('runs a full search flow from Home through to the matching Results entry', async () => {
    const user = userEvent.setup();
    renderApp('/');

    await user.type(
      screen.getByPlaceholderText('What kind of research are you searching for funding for?'),
      'coral',
    );
    await user.click(screen.getByRole('button', { name: 'Search funding' }));

    await screen.findByText('1 Results Found', {}, findTimeout);
    expect(screen.getByText('ARC Research Grant')).toBeInTheDocument();
  });
});
