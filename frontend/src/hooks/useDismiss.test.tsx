import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useRef, useState } from 'react';
import { expect, it } from 'vitest';
import { useDismiss } from './useDismiss';

function Popup() {
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  useDismiss({ open, onDismiss: () => setOpen(false), containerRef, triggerRef });
  return (
    <>
      <div ref={containerRef}>
        <button ref={triggerRef} aria-expanded={open} onClick={() => setOpen(!open)}>
          Menu
        </button>
        {open && (
          <div>
            <button>Inside</button>
            <p>Plain text</p>
          </div>
        )}
      </div>
      <button>Outside</button>
    </>
  );
}

const trigger = () => screen.getByRole('button', { name: 'Menu' });

it('closes on Escape and returns focus to the trigger', async () => {
  const user = userEvent.setup();
  render(<Popup />);
  await user.click(trigger());
  await user.tab();
  expect(screen.getByRole('button', { name: 'Inside' })).toHaveFocus();

  await user.keyboard('{Escape}');

  expect(trigger()).toHaveAttribute('aria-expanded', 'false');
  expect(trigger()).toHaveFocus();
});

it('closes when keyboard focus leaves the popup', async () => {
  const user = userEvent.setup();
  render(<Popup />);
  await user.click(trigger());
  await user.tab();
  await user.tab();

  expect(screen.getByRole('button', { name: 'Outside' })).toHaveFocus();
  expect(trigger()).toHaveAttribute('aria-expanded', 'false');
});

it('closes on a press outside but not on one inside', async () => {
  const user = userEvent.setup();
  render(<Popup />);
  await user.click(trigger());

  await user.click(screen.getByRole('button', { name: 'Inside' }));
  await user.click(screen.getByText('Plain text'));
  expect(trigger()).toHaveAttribute('aria-expanded', 'true');

  await user.click(screen.getByRole('button', { name: 'Outside' }));
  expect(trigger()).toHaveAttribute('aria-expanded', 'false');
});

it('leaves focus alone on Escape while closed', async () => {
  const user = userEvent.setup();
  render(<Popup />);
  const outside = screen.getByRole('button', { name: 'Outside' });
  outside.focus();

  await user.keyboard('{Escape}');

  expect(outside).toHaveFocus();
});
