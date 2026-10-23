import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it, vi } from 'vitest';
import Dropdown from './Dropdown';
it('shows readable labels, emits backend values, and allows clearing', async () => {
  const user = userEvent.setup();
  const onChange = vi.fn();
  const { rerender } = render(
    <Dropdown
      label="Employer Type"
      options={[{ value: 'research_institute', label: 'Research Institute' }]}
      value=""
      onChange={onChange}
    />,
  );
  await user.click(screen.getByText('Employer Type – Any'));
  await user.click(screen.getByRole('radio', { name: 'Research Institute' }));
  expect(onChange).toHaveBeenCalledWith('research_institute');
  rerender(
    <Dropdown
      label="Employer Type"
      options={[{ value: 'research_institute', label: 'Research Institute' }]}
      value="research_institute"
      onChange={onChange}
    />,
  );
  expect(screen.getByText('Research Institute', { selector: 'summary' })).toBeInTheDocument();
  await user.click(screen.getByText('Research Institute', { selector: 'summary' }));
  await user.click(screen.getByRole('radio', { name: 'Any' }));
  expect(onChange).toHaveBeenLastCalledWith('');
});
it('separates the label from "Any" with an en dash in the blank option', () => {
  render(<Dropdown label="Career Stage" options={[]} value="" onChange={vi.fn()} />);
  expect(screen.getByText('Career Stage – Any', { selector: 'summary' })).toBeInTheDocument();
});

it('closes on Escape and when focus tabs out, returning focus to the summary on Escape', async () => {
  const user = userEvent.setup();
  render(
    <>
      <Dropdown label="Career Stage" options={[]} value="" onChange={vi.fn()} />
      <button>Next field</button>
    </>,
  );
  const summary = screen.getByText('Career Stage – Any', { selector: 'summary' });
  const details = summary.closest('details');

  await user.click(summary);
  expect(details).toHaveAttribute('open');
  await user.tab();
  await user.keyboard('{Escape}');
  expect(details).not.toHaveAttribute('open');
  expect(summary).toHaveFocus();

  await user.click(summary);
  await user.tab();
  await user.tab();
  expect(screen.getByRole('button', { name: 'Next field' })).toHaveFocus();
  expect(details).not.toHaveAttribute('open');
});

it('keeps the label in the summary name once a value is chosen', () => {
  render(
    <Dropdown
      label="Employer Type"
      options={[{ value: 'industry', label: 'Industry' }]}
      value="industry"
      onChange={vi.fn()}
    />,
  );
  expect(screen.getByText('Industry', { selector: 'summary' })).toHaveAccessibleName(
    'Employer Type Industry',
  );
});
