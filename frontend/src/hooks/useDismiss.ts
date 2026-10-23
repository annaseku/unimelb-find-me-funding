import { useEffect, useEffectEvent, type RefObject } from 'react';

interface DismissOptions {
  open: boolean;
  onDismiss: () => void;
  // Holds the trigger and the popup; pressing or focusing inside it never dismisses.
  containerRef: RefObject<HTMLElement | null>;
  // Takes focus back on Escape so keyboard users are not left on the page body.
  triggerRef: RefObject<HTMLElement | null>;
}

// Closes an open popup the way a native menu closes: a press outside it, Escape, or
// keyboard focus moving out of it.
export function useDismiss({ open, onDismiss, containerRef, triggerRef }: DismissOptions) {
  const dismiss = useEffectEvent(onDismiss);

  useEffect(() => {
    const container = containerRef.current;
    if (!open || !container) return;
    const isOutside = (target: EventTarget | null) =>
      target instanceof Node && !container.contains(target);

    const handlePointerDown = (event: PointerEvent) => {
      if (isOutside(event.target)) dismiss();
    };
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key !== 'Escape') return;
      dismiss();
      triggerRef.current?.focus();
    };
    // relatedTarget is null when focus goes nowhere, such as a click on plain text in the
    // menu; only focus landing somewhere outside dismisses.
    const handleFocusOut = (event: FocusEvent) => {
      if (isOutside(event.relatedTarget)) dismiss();
    };

    document.addEventListener('pointerdown', handlePointerDown);
    document.addEventListener('keydown', handleKeyDown);
    container.addEventListener('focusout', handleFocusOut);
    return () => {
      document.removeEventListener('pointerdown', handlePointerDown);
      document.removeEventListener('keydown', handleKeyDown);
      container.removeEventListener('focusout', handleFocusOut);
    };
  }, [open, containerRef, triggerRef]);
}
