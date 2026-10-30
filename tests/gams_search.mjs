import assert from 'node:assert/strict';
import {matchesSearch, initializeSearch} from '../site/gams/search.mjs';

assert.ok(matchesSearch('D2 Linear systems JacobWilliams LAPACK', 'jacobwilliams linear'));
assert.ok(!matchesSearch('D2 Linear systems', 'D2 optimization'));
assert.ok(matchesSearch('Bessel functions', '  BESSEL  '));
assert.ok(matchesSearch('Bessel functions', ''));
assert.ok(matchesSearch('Federico Perini (perazz) LAPACK', 'federico perini'));
assert.ok(matchesSearch('Federico Perini (perazz) LAPACK', 'perazz'));

const element = () => ({hidden: true, value: '', listeners: {},
  addEventListener(type, fn) {this.listeners[type] = fn;}, focus() {this.focused = true;}});
const elements = Object.fromEntries(['package-search', 'clear-search', 'search-controls', 'result-count', 'no-results'].map(id => [id, element()]));
const cards = ['D2 linear algebra LAPACK', 'I1 ODE solver'].map(text => ({dataset: {search: text}, hidden: false}));
const doc = {getElementById: id => elements[id], querySelectorAll: () => cards};
let updated;
const win = {location: {href: 'https://example.test/gams/?q=lapack'}, history: {replaceState(a,b,url) {updated = new URL(url);}}};
initializeSearch(doc, win);
assert.deepEqual(cards.map(c => c.hidden), [false,true]);
assert.equal(elements['result-count'].textContent, '1 of 2 packages');
assert.equal(elements['search-controls'].hidden, false);
elements['package-search'].value = 'no match';
elements['package-search'].listeners.input();
assert.equal(elements['no-results'].hidden, false);
assert.equal(updated.searchParams.get('q'), 'no match');
elements['clear-search'].listeners.click();
assert.ok(cards.every(c => !c.hidden));
assert.equal(updated.searchParams.has('q'), false);
assert.equal(elements['package-search'].focused, true);
elements['result-count'].dataset = {resultUnit: 'owners'};
initializeSearch(doc, win);
assert.equal(elements['result-count'].textContent, '1 of 2 owners');
console.log('GAMS search: combined terms, restored query, empty results and clearing passed.');
