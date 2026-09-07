import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import Result from './Result';
import type { FundingOpportunity } from '../../types/funding';

const opportunity: FundingOpportunity = {
  url: 'https://example.org/fund/1',
  title: 'Early Career Research Grant',
  raw_text: 'Funding for early career researchers.',
  deadline_raw: '31 October 2026',
  funding_amount_raw: 'AUD 500,000',
  eligibility_snippet: 'Open to postdoctoral researchers based in Australia.',
};

describe('Result', () => {
  it('renders the title, deadline, funding amount, eligibility and a link to the opportunity', () => {
    render(<Result opportunity={opportunity} />);

    expect(screen.getByRole('heading', { name: opportunity.title })).toBeInTheDocument();
    expect(screen.getByText(opportunity.deadline_raw as string)).toBeInTheDocument();
    expect(screen.getByText(opportunity.funding_amount_raw as string)).toBeInTheDocument();
    expect(screen.getByText(opportunity.eligibility_snippet as string)).toBeInTheDocument();

    const link = screen.getByRole('link', { name: 'View opportunity' });
    expect(link).toHaveAttribute('href', opportunity.url);
    expect(link).toHaveAttribute('target', '_blank');
    expect(link).toHaveAttribute('rel', 'noreferrer');
  });

  it('falls back to placeholder text when deadline, funding amount and eligibility are null', () => {
    render(
      <Result
        opportunity={{
          ...opportunity,
          deadline_raw: null,
          funding_amount_raw: null,
          eligibility_snippet: null,
        }}
      />,
    );

    expect(screen.getAllByText('Not specified')).toHaveLength(2);
    expect(screen.getByText('Not available')).toBeInTheDocument();
  });
});
