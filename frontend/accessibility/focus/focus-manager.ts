export function trapFocus(modal: HTMLElement) {
  const focusable = modal.querySelectorAll<HTMLElement>('button, [href], input, select, textarea, [tabindex]');
  const first = focusable[0];
  const last = focusable[focusable.length - 1];

  modal.addEventListener('keydown', e => {
    if (e.key === 'Tab') {
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  });
}
