import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import Dropdown from './Dropdown';

const options = ['Marine Biology', 'Climate Science'];

describe('Dropdown', () => {
  it('shows the label when nothing is selected and the value once it is', () => {
    const { rerender } = render(
      <Dropdown label="Field of Research" options={options} value="" onChange={() => {}} />,
    );
    expect(screen.getByRole('button', { name: /field of research/i })).toBeInTheDocument();

    rerender(
      <Dropdown label="Field of Research" options={options} value="Physics" onChange={() => {}} />,
    );
    expect(screen.getByRole('button', { name: /physics/i })).toBeInTheDocument();
    expect(screen.queryByText('Field of Research')).not.toBeInTheDocument();
  });

  it('is closed until clicked and reports its state through aria-expanded', async () => {
    const user = userEvent.setup();
    render(<Dropdown label="Citizenship" options={options} value="" onChange={() => {}} />);
    const toggle = screen.getByRole('button', { name: /citizenship/i });

    expect(toggle).toHaveAttribute('aria-expanded', 'false');
    expect(screen.queryByRole('button', { name: 'Marine Biology' })).not.toBeInTheDocument();

    await user.click(toggle);

    expect(toggle).toHaveAttribute('aria-expanded', 'true');
    expect(screen.getByRole('button', { name: 'Marine Biology' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Climate Science' })).toBeInTheDocument();
  });

  it('calls onChange with the chosen option and closes the menu', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<Dropdown label="Field of Research" options={options} value="" onChange={onChange} />);

    await user.click(screen.getByRole('button', { name: /field of research/i }));
    await user.click(screen.getByRole('button', { name: 'Climate Science' }));

    expect(onChange).toHaveBeenCalledWith('Climate Science');
    expect(screen.queryByRole('button', { name: 'Climate Science' })).not.toBeInTheDocument();
  });

  it('offers an "Any" choice that clears the selection', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(
      <Dropdown label="Field of Research" options={options} value="Physics" onChange={onChange} />,
    );

    await user.click(screen.getByRole('button', { name: /physics/i }));
    await user.click(screen.getByRole('button', { name: 'Any' }));

    expect(onChange).toHaveBeenCalledWith('');
  });
});
