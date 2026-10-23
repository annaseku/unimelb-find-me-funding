import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it, vi } from 'vitest';
import FilterPanel from './FilterPanel';
import { defaultFilterValues } from '../../data/filterOptions';

it('shows all six filters', () => {
  render(<FilterPanel filters={defaultFilterValues} onChange={vi.fn()} />);
  for (const label of [
    'Field of Research',
    'Type of Activity',
    'Citizenship',
    'Employer Type',
    'Career Stage',
    'Funding Type',
  ]) {
    expect(screen.getByText(`${label} – Any`)).toBeInTheDocument();
  }
});

it('reports a change to one filter with the others kept', async () => {
  const user = userEvent.setup();
  const onChange = vi.fn();
  const filters = { ...defaultFilterValues, citizenship: ['AU'] };
  render(<FilterPanel filters={filters} onChange={onChange} />);

  await user.click(screen.getByText('Employer Type – Any'));
  await user.click(screen.getByRole('radio', { name: 'Industry' }));

  expect(onChange).toHaveBeenCalledWith({ ...filters, employerType: 'industry' });
});
