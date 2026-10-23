import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it } from 'vitest';
import Result from './Result';
import { ranked } from '../../test/fundingFixture';

const toggle = () => screen.getByRole('button', { name: ranked.opportunity.title });

it('renders all four criteria, researcher-facing reasons, labels, and the funder link', async () => {
  render(<Result result={ranked} />);
  await userEvent.setup().click(toggle());
  for (const name of ['Eligibility', 'Research match', 'Funding value', 'Time to deadline'])
    expect(screen.getByRole('heading', { name })).toBeInTheDocument();
  for (const key of ['eligibility', 'research_match', 'funding_value', 'deadline'] as const)
    for (const reason of ranked[key].reasons) expect(screen.getByText(reason)).toBeInTheDocument();
  expect(screen.getAllByText(/Potentially eligible/)).toHaveLength(2);
  expect(screen.getByText(/Over 60 days/)).toBeInTheDocument();
  expect(screen.getByRole('link', { name: /View opportunity/i })).toHaveAttribute(
    'href',
    ranked.opportunity.url,
  );
  expect(screen.getAllByText(/Not specified/)).toHaveLength(2);
});

it('names the card toggle with the title alone, inside the level 2 heading', () => {
  render(<Result result={ranked} />);
  expect(screen.getByRole('heading', { level: 2 })).toContainElement(toggle());
  expect(toggle()).toHaveAccessibleName('ARC Research Grant');
});

it('expands and collapses the ranking details', async () => {
  const user = userEvent.setup();
  render(<Result result={ranked} />);
  expect(toggle()).toHaveAttribute('aria-expanded', 'false');
  expect(screen.queryByRole('heading', { name: 'Eligibility' })).not.toBeInTheDocument();

  await user.click(toggle());
  expect(toggle()).toHaveAttribute('aria-expanded', 'true');
  const details = document.getElementById(toggle().getAttribute('aria-controls') ?? '');
  expect(details).toBeVisible();
  expect(details).toContainElement(screen.getByRole('heading', { name: 'Eligibility' }));

  await user.click(toggle());
  expect(toggle()).toHaveAttribute('aria-expanded', 'false');
  expect(details).not.toBeVisible();
});
