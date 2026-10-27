import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {initializeViewControls} from '../site/view_controls.mjs';

function fixture({saved = null, dark = false, blocked = false} = {}) {
  const element = () => ({textContent: '', hidden: false, attributes: {}, listeners: {},
    setAttribute(key, value) { this.attributes[key] = value; },
    addEventListener(key, handler) { this.listeners[key] = handler; },
    focus() { this.focused = true; }});
  const elements = Object.fromEntries(['theme-toggle', 'focus-toggle', 'status', 'focus-status'].map(id => [id, element()]));
  elements.status.textContent = 'Ready';
  let refreshes = 0;
  const doc = {documentElement: {dataset: {}}, getElementById: id => elements[id],
    querySelectorAll: () => [{CodeMirror: {refresh() { refreshes++; }}}],
    addEventListener(key, handler) { this[key] = handler; }};
  const media = {matches: dark, addEventListener(key, handler) { this.change = handler; }};
  const stored = {};
  const win = {scrollY: 140, scrollTo(x, y) { this.scrollY = y; }, matchMedia: () => media,
    localStorage: {getItem() { if (blocked) throw Error(); return saved; },
      setItem(key, value) { if (blocked) throw Error(); stored[key] = value; }},
    MutationObserver: class { constructor(handler) { win.updateStatus = handler; } observe() {} }};
  initializeViewControls(doc, win);
  return {doc, win, elements, media, stored, refreshes: () => refreshes};
}
const f = fixture({dark: true});
assert.equal(f.doc.documentElement.dataset.theme, 'dark');
f.media.matches = false; f.media.change();
assert.equal(f.doc.documentElement.dataset.theme, 'light');
f.elements['theme-toggle'].listeners.click();
assert.equal(f.stored['fortran-playground-theme'], 'dark');
f.media.change();
assert.equal(f.doc.documentElement.dataset.theme, 'dark');
assert.equal(f.elements['theme-toggle'].attributes['aria-pressed'], 'true');
assert.equal(fixture({saved: 'light', dark: true}).doc.documentElement.dataset.theme, 'light');
const blocked = fixture({blocked: true});
blocked.elements['theme-toggle'].listeners.click();
assert.equal(blocked.doc.documentElement.dataset.theme, 'dark');
f.elements['focus-toggle'].listeners.click();
assert.equal(f.doc.documentElement.dataset.focus, 'true');
assert.equal(f.win.scrollY, 0);
assert.equal(f.elements['focus-status'].textContent, 'Ready');
f.elements.status.textContent = 'Running'; f.win.updateStatus();
assert.equal(f.elements['focus-status'].textContent, 'Running');
let prevented = false;
f.doc.keydown({key: 'Escape', preventDefault() { prevented = true; }, stopPropagation() {}});
assert.equal(prevented, true);
assert.equal(f.doc.documentElement.dataset.focus, 'false');
assert.equal(f.win.scrollY, 140);
assert.equal(f.elements['focus-toggle'].focused, true);
assert.equal(f.refreshes(), 2);
for (const name of ['view_controls.mjs', 'view_controls.css']) {
  assert.equal(readFileSync(new URL('../site/' + name, import.meta.url), 'utf8'),
    readFileSync(new URL('../local_site/' + name, import.meta.url), 'utf8'));
}
for (const name of ['site/index.html', 'site/fpm/index.html', 'local_site/index.html', 'local_site/fpm/index.html']) {
  const html = readFileSync(new URL('../' + name, import.meta.url), 'utf8');
  for (const token of ['id="theme-toggle"', 'id="focus-toggle"', 'view_controls.css', 'view_controls.mjs', 'data-focus-panel']) assert.ok(html.includes(token), name + ': ' + token);
  if (name.includes('/fpm/')) for (const link of ['https://fpm.fortran-lang.org/', 'https://github.com/topics/fortran-package-manager', 'https://beliavsky.github.io/Fortran-packages-list/', 'https://github.com/Beliavsky/Fortran-Tools']) assert.ok(html.includes(link));
}
console.log('View controls tests passed');
