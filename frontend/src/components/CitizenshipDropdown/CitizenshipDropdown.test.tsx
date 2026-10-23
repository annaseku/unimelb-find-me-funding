import { expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import CitizenshipDropdown from './CitizenshipDropdown';

it('allows selecting multiple citizenships', async () => {
  const user = userEvent.setup();
  const onChange = vi.fn();
  const { rerender } = render(<CitizenshipDropdown value={[]} onChange={onChange} />);

  await user.click(screen.getByRole('button', { name: 'Citizenship – Any' }));

  await user.click(screen.getByRole('checkbox', { name: 'Australia' }));

  expect(onChange).toHaveBeenCalledWith(['AU']);

  // Simulate the parent updating the controlled value.
  rerender(<CitizenshipDropdown value={['AU']} onChange={onChange} />);

  await user.click(screen.getByRole('checkbox', { name: 'New Zealand' }));

  expect(onChange).toHaveBeenLastCalledWith(['AU', 'NZ']);
}, 15000);

it('names its search box and filters countries by it', async () => {
  const user = userEvent.setup();
  render(<CitizenshipDropdown value={[]} onChange={vi.fn()} />);

  await user.click(screen.getByRole('button', { name: 'Citizenship – Any' }));
  await user.type(screen.getByRole('textbox', { name: 'Search citizenships' }), 'zeal');

  expect(screen.getByRole('checkbox', { name: 'New Zealand' })).toBeInTheDocument();
  expect(screen.queryByRole('checkbox', { name: 'Australia' })).not.toBeInTheDocument();
});
