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
