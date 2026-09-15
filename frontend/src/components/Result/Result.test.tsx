import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';
import Result from './Result';
import { ranked } from '../../test/fundingFixture';
it('renders all four criteria, researcher-facing reasons, labels, and the funder link', () => {
  render(<Result result={ranked} />);
  for (const name of ['Eligibility', 'Research match', 'Funding value', 'Time to deadline']) expect(screen.getByRole('heading', { name })).toBeInTheDocument();
  for (const key of ['eligibility', 'research_match', 'funding_value', 'deadline'] as const) expect(screen.getByText(ranked[key].reasons[0])).toBeInTheDocument();
  expect(screen.getByText(/Potentially eligible/)).toBeInTheDocument();
  expect(screen.getByText(/Over 60 days/)).toBeInTheDocument();
  expect(screen.getByRole('link', { name: 'View opportunity' })).toHaveAttribute('href', ranked.opportunity.url);
  expect(screen.getAllByText(/Not specified/)).toHaveLength(2);
});
