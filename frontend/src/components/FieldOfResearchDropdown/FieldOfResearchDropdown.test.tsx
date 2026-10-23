import { expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import FieldOfResearchDropdown from './FieldOfResearchDropdown';

it('allows selecting a research group from a division', async () => {
  const user = userEvent.setup();
  const onChange = vi.fn();

  render(<FieldOfResearchDropdown value="" onChange={onChange} />);

  await user.click(screen.getByRole('button', { name: 'Field of Research – Any' }));

  await user.click(screen.getByRole('button', { name: 'Expand Biological Sciences' }));

  await user.click(screen.getByRole('button', { name: /3103\s*Ecology/i }));

  expect(onChange).toHaveBeenCalledWith('3103');
});

it('names its search box and filters fields of research by it', async () => {
  const user = userEvent.setup();
  render(<FieldOfResearchDropdown value="" onChange={vi.fn()} />);

  await user.click(screen.getByRole('button', { name: 'Field of Research – Any' }));
  await user.type(screen.getByRole('textbox', { name: 'Search fields of research' }), 'ecology');

  expect(screen.getByRole('button', { name: /3103\s*Ecology/i })).toBeInTheDocument();
  expect(screen.queryByRole('button', { name: /^30\s*Agricultural/i })).not.toBeInTheDocument();
});
