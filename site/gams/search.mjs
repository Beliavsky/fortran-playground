export function matchesSearch(text, query) {
  const normalize = value => value.normalize('NFKC').toLocaleLowerCase();
  const haystack = normalize(text);
  return normalize(query).trim().split(/\s+/u).every(word => haystack.includes(word));
}

export function initializeSearch(doc = document, win = window) {
  const input = doc.getElementById('package-search');
  if (!input) return;
  const cards = [...doc.querySelectorAll('[data-search]')];
  const url = new URL(win.location.href);
  input.value = url.searchParams.get('q') || '';
  function filter() {
    let count = 0;
    for (const card of cards) {
      card.hidden = !matchesSearch(card.dataset.search, input.value);
      if (!card.hidden) count++;
    }
    doc.getElementById('result-count').textContent = `${count} of ${cards.length} packages`;
    doc.getElementById('no-results').hidden = count !== 0;
    if (input.value.trim()) url.searchParams.set('q', input.value.trim());
    else url.searchParams.delete('q');
    try { win.history.replaceState(null, '', url); } catch { /* Browsing still works without history access. */ }
  }
  input.addEventListener('input', filter);
  doc.getElementById('clear-search').addEventListener('click', () => {
    input.value = '';
    filter();
    input.focus();
  });
  doc.getElementById('search-controls').hidden = false;
  filter();
}

if (typeof document !== 'undefined') initializeSearch();
