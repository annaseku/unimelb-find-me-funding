import { expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import FieldOfResearchDropdown from './FieldOfResearchDropdown';

it('allows selecting a research group from a division', async () => {
  const user = userEvent.setup();
  const onChange = vi.fn();

  render(<FieldOfResearchDropdown value={[]} onChange={onChange} />);

  await user.click(screen.getByRole('button', { name: 'Field of Research – Any' }));

  await user.click(screen.getByRole('button', { name: 'Biological Sciences groups' }));

  await user.click(screen.getByRole('checkbox', { name: /3103\s*Ecology/i }));

  expect(onChange).toHaveBeenCalledWith(['3103']);
});

it('names its search box and filters fields of research by it', async () => {
  const user = userEvent.setup();
  render(<FieldOfResearchDropdown value={[]} onChange={vi.fn()} />);

  await user.click(screen.getByRole('button', { name: 'Field of Research – Any' }));
  await user.type(screen.getByRole('textbox', { name: 'Search fields of research' }), 'ecology');

  expect(screen.getByRole('checkbox', { name: /3103\s*Ecology/i })).toBeInTheDocument();
  expect(screen.queryByRole('checkbox', { name: /^30\s*Agricultural/i })).not.toBeInTheDocument();
});

it('reports each division as expanded or collapsed and keeps it open after ticking', async () => {
  const user = userEvent.setup();
  render(<FieldOfResearchDropdown value={[]} onChange={vi.fn()} />);
  const trigger = screen.getByRole('button', { name: 'Field of Research – Any' });
  await user.click(trigger);

  const expand = screen.getByRole('button', { name: 'Biological Sciences groups' });
  expect(expand).toHaveAttribute('aria-expanded', 'false');
  await user.click(expand);
  expect(expand).toHaveAttribute('aria-expanded', 'true');
  expect(document.getElementById(expand.getAttribute('aria-controls') ?? '')).toContainElement(
    screen.getByRole('checkbox', { name: /3103\s*Ecology/i }),
  );

  await user.click(screen.getByRole('checkbox', { name: /3103\s*Ecology/i }));
  expect(trigger).toHaveAttribute('aria-expanded', 'true');
  expect(screen.getByRole('checkbox', { name: /3103\s*Ecology/i })).toHaveFocus();
  await user.click(expand);
  expect(expand).toHaveAttribute('aria-expanded', 'false');
  expect(screen.queryByRole('checkbox', { name: /3103\s*Ecology/i })).not.toBeInTheDocument();
});

it('keeps the label in the trigger name once a field is chosen', () => {
  render(<FieldOfResearchDropdown value={['3103']} onChange={vi.fn()} />);
  expect(screen.getByRole('button', { name: 'Field of Research Ecology' })).toBeInTheDocument();
});

it('reports both selected groups and keeps the menu open between ticks', async () => {
  const user = userEvent.setup();
  const onChange = vi.fn();
  const { rerender } = render(<FieldOfResearchDropdown value={[]} onChange={onChange} />);
  await user.click(screen.getByRole('button', { name: 'Field of Research – Any' }));
  await user.click(screen.getByRole('button', { name: 'Biological Sciences groups' }));
  await user.click(screen.getByRole('checkbox', { name: /3103\s*Ecology/i }));
  expect(onChange).toHaveBeenLastCalledWith(['3103']);

  rerender(<FieldOfResearchDropdown value={['3103']} onChange={onChange} />);
  expect(screen.getByRole('checkbox', { name: /3103\s*Ecology/i })).toBeChecked();
  await user.click(screen.getByRole('checkbox', { name: /3105\s*Genetics/i }));
  expect(onChange).toHaveBeenLastCalledWith(['3103', '3105']);

  rerender(<FieldOfResearchDropdown value={['3103', '3105']} onChange={onChange} />);
  expect(screen.getByRole('checkbox', { name: /3103\s*Ecology/i })).toBeChecked();
  expect(screen.getByRole('checkbox', { name: /3105\s*Genetics/i })).toBeChecked();
});

it('unticks one group while retaining the other selections', async () => {
  const user = userEvent.setup();
  const onChange = vi.fn();
  const { rerender } = render(
    <FieldOfResearchDropdown value={['3103', '3105']} onChange={onChange} />,
  );
  await user.click(screen.getByRole('button', { name: 'Field of Research 2 fields selected' }));
  await user.click(screen.getByRole('button', { name: 'Biological Sciences groups' }));
  await user.click(screen.getByRole('checkbox', { name: /3103\s*Ecology/i }));
  expect(onChange).toHaveBeenLastCalledWith(['3105']);

  rerender(<FieldOfResearchDropdown value={['3105']} onChange={onChange} />);
  expect(screen.getByRole('checkbox', { name: /3103\s*Ecology/i })).not.toBeChecked();
  expect(screen.getByRole('checkbox', { name: /3105\s*Genetics/i })).toBeChecked();
});

it('allows a division and its groups to remain selected together', async () => {
  const user = userEvent.setup();
  const onChange = vi.fn();
  const { rerender } = render(<FieldOfResearchDropdown value={['3103']} onChange={onChange} />);
  await user.click(screen.getByRole('button', { name: 'Field of Research Ecology' }));
  await user.click(screen.getByRole('checkbox', { name: /^31\s*Biological Sciences$/i }));
  expect(onChange).toHaveBeenLastCalledWith(['3103', '31']);

  rerender(<FieldOfResearchDropdown value={['3103', '31']} onChange={onChange} />);
  await user.click(screen.getByRole('button', { name: 'Biological Sciences groups' }));
  expect(screen.getByRole('checkbox', { name: /^31\s*Biological Sciences$/i })).toBeChecked();
  expect(screen.getByRole('checkbox', { name: /3103\s*Ecology/i })).toBeChecked();
});

it('clears all fields with Any while keeping the menu and search open', async () => {
  const user = userEvent.setup();
  const onChange = vi.fn();
  const { rerender } = render(
    <FieldOfResearchDropdown value={['3103', '31']} onChange={onChange} />,
  );
  await user.click(screen.getByRole('button', { name: 'Field of Research 2 fields selected' }));
  await user.type(screen.getByRole('textbox', { name: 'Search fields of research' }), 'ecology');
  await user.click(screen.getByRole('button', { name: 'Any' }));
  expect(onChange).toHaveBeenLastCalledWith([]);

  rerender(<FieldOfResearchDropdown value={[]} onChange={onChange} />);
  expect(screen.getByRole('button', { name: 'Field of Research – Any' })).toHaveAttribute(
    'aria-expanded',
    'true',
  );
  expect(screen.getByRole('textbox', { name: 'Search fields of research' })).toHaveValue('ecology');
  expect(screen.getByRole('checkbox', { name: /3103\s*Ecology/i })).not.toBeChecked();
  expect(screen.getByRole('checkbox', { name: /^31\s*Biological Sciences$/i })).not.toBeChecked();
});

it('shows the number of selected fields and keeps the label in the trigger name', () => {
  render(<FieldOfResearchDropdown value={['3103', '31']} onChange={vi.fn()} />);
  expect(
    screen.getByRole('button', { name: 'Field of Research 2 fields selected' }),
  ).toHaveTextContent('2 fields selected');
});
