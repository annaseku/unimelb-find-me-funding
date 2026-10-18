import { expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import FieldOfResearchDropdown from './FieldOfResearchDropdown';

it('allows selecting and deselecting multiple research fields', async () => {
  const user = userEvent.setup();
  const onChange = vi.fn();

  const { rerender } = render(
    <FieldOfResearchDropdown
      value={[]}
      onChange={onChange}
    />
  );

  await user.click(screen.getByRole('button', { name: 'Field of Research – Any' }));
  await user.click(screen.getByRole('button', { name: 'Expand Biological Sciences' }));
  await user.click(screen.getByRole('checkbox', { name: /3103\s*Ecology/i }));
  expect(onChange).toHaveBeenLastCalledWith(['3103']);
  rerender(<FieldOfResearchDropdown value={['3103']} onChange={onChange} />);

  await user.click(screen.getByRole('checkbox', { name: /3104\s*Evolutionary biology/i }));
  expect(onChange).toHaveBeenLastCalledWith(['3103', '3104']);
  rerender(<FieldOfResearchDropdown value={['3103', '3104']} onChange={onChange} />);

  await user.click(screen.getByRole('checkbox', { name: /3103\s*Ecology/i }));
  expect(onChange).toHaveBeenLastCalledWith(['3104']);
});