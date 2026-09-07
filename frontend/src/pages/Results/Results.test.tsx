import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import Results from './Results';
import { defaultFilterValues } from '../../data/filterOptions';

const findTimeout = { timeout: 2000 };

function renderResults(initialEntry: string | { pathname: string; state?: unknown }) {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <Routes>
        <Route path="/results" element={<Results />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe('Results', () => {
  it('shows Loading... first, then the matching fellowship when state.search is "coral"', async () => {
    renderResults({ pathname: '/results', state: { search: 'coral', filters: defaultFilterValues } });

    expect(screen.getByText('Loading...')).toBeInTheDocument();

    await screen.findByText('1 Results Found', {}, findTimeout);
    expect(screen.getByText('Climate and Ocean Research Fellowship')).toBeInTheDocument();
  });

  it('shows all three results after loading when there is no router state', async () => {
    renderResults('/results');

    await screen.findByText('3 Results Found', {}, findTimeout);
  });

  it('pre-fills the keyword input from state.search', async () => {
    renderResults({ pathname: '/results', state: { search: 'coral', filters: defaultFilterValues } });

    await screen.findByText('1 Results Found', {}, findTimeout);
    expect(screen.getByPlaceholderText('Search by keyword')).toHaveValue('coral');
  });

  it('re-runs the search and updates the results when a new keyword is submitted', async () => {
    const user = userEvent.setup();
    renderResults({ pathname: '/results', state: { search: 'coral', filters: defaultFilterValues } });

    await screen.findByText('1 Results Found', {}, findTimeout);

    const input = screen.getByPlaceholderText('Search by keyword');
    await user.clear(input);
    await user.type(input, 'computer');
    await user.click(screen.getByRole('button', { name: 'Search' }));

    await screen.findByText('Computer Science Research Infrastructure Grant', {}, findTimeout);
    expect(screen.getByText('1 Results Found')).toBeInTheDocument();
    expect(screen.queryByText('Climate and Ocean Research Fellowship')).not.toBeInTheDocument();
  });

  it('reflects state.filters in the dropdowns', async () => {
    renderResults({
      pathname: '/results',
      state: { search: '', filters: { ...defaultFilterValues, fieldOfResearch: 'Marine Biology' } },
    });

    await screen.findByText(/Results Found/, {}, findTimeout);
    expect(screen.getByRole('button', { name: 'Marine Biology' })).toBeInTheDocument();
  });
});
