// Display preferences are independent of compilation and editor contents.
export function initializeViewControls(doc = document, win = window) {
  const root = doc.documentElement;
  const themeButton = doc.getElementById('theme-toggle');
  const focusButton = doc.getElementById('focus-toggle');
  if (!themeButton || !focusButton) return;
  const media = win.matchMedia?.('(prefers-color-scheme: dark)');
  let preference;
  try { preference = win.localStorage.getItem('fortran-playground-theme'); } catch {}
  if (!['light', 'dark'].includes(preference)) preference = null;
  const applyTheme = () => {
    const dark = preference ? preference === 'dark' : Boolean(media?.matches);
    root.dataset.theme = dark ? 'dark' : 'light';
    themeButton.textContent = dark ? 'Light mode' : 'Dark mode';
    themeButton.setAttribute('aria-pressed', String(dark));
    themeButton.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
  };
  themeButton.addEventListener('click', () => {
    preference = root.dataset.theme === 'dark' ? 'light' : 'dark';
    try { win.localStorage.setItem('fortran-playground-theme', preference); } catch {}
    applyTheme();
  });
  media?.addEventListener?.('change', applyTheme);
  applyTheme();

  let previousScroll = 0;
  const status = doc.getElementById('status');
  const focusStatus = doc.getElementById('focus-status');
  const updateStatus = () => { if (focusStatus && status) focusStatus.textContent = status.textContent; };
  if (status && win.MutationObserver) new win.MutationObserver(updateStatus).observe(status, {childList: true, characterData: true, subtree: true});
  const setFocus = enabled => {
    if (enabled) previousScroll = win.scrollY;
    root.dataset.focus = String(enabled);
    focusButton.textContent = enabled ? 'Exit focus mode' : 'Focus mode';
    focusButton.setAttribute('aria-pressed', String(enabled));
    if (focusStatus) focusStatus.hidden = !enabled;
    updateStatus();
    // Refresh sizes without recreating editors or losing undo history.
    for (const element of doc.querySelectorAll('.CodeMirror')) element.CodeMirror?.refresh();
    win.scrollTo(0, enabled ? 0 : previousScroll);
  };
  focusButton.addEventListener('click', () => setFocus(root.dataset.focus !== 'true'));
  doc.addEventListener('keydown', event => {
    if (event.key === 'Escape' && root.dataset.focus === 'true') {
      event.preventDefault();
      event.stopPropagation();
      setFocus(false);
      focusButton.focus();
    }
  }, true);
}

if (typeof document !== 'undefined') initializeViewControls();
