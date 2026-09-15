import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it, vi } from 'vitest';
import Dropdown from './Dropdown';
it('shows readable labels, emits backend values, and allows clearing', async () => {
  const user = userEvent.setup(); const onChange = vi.fn();
  const { rerender } = render(<Dropdown label="Employer Type" options={[{ value: 'research_institute', label: 'Research Institute' }]} value="" onChange={onChange} />);
  await user.selectOptions(screen.getByRole('combobox'), 'research_institute');
  expect(onChange).toHaveBeenCalledWith('research_institute');
  rerender(<Dropdown label="Employer Type" options={[{ value: 'research_institute', label: 'Research Institute' }]} value="research_institute" onChange={onChange} />);
  expect(screen.getByRole('combobox')).toHaveDisplayValue('Research Institute');
  await user.selectOptions(screen.getByRole('combobox'), '');
  expect(onChange).toHaveBeenLastCalledWith('');
});
