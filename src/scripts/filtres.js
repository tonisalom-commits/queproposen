/* Filtres compartits: mateixa lògica a la portada i a les seccions. */
function normalitza(value) {
  return String(value || '').normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('ca');
}

function iniciaCataleg(root) {
  const cards = [...root.querySelectorAll('[data-card]')];
  const search = root.querySelector('[data-filter-search]');
  const theme = root.querySelector('[data-filter-theme]');
  const tag = root.querySelector('[data-filter-tag]');
  const group = root.querySelector('[data-filter-group]');
  const count = root.querySelector('[data-result-count]');
  const empty = root.querySelector('[data-empty]');
  const kinds = [...root.querySelectorAll('button[data-kind]')];
  let selectedKind = '';

  function dibuixa() {
    const q = normalitza(search?.value.trim());
    const t = theme?.value || '';
    const sub = tag?.value || '';
    const g = group?.value || '';
    let visible = 0;
    for (const card of cards) {
      const groups = (card.dataset.groups || '').split('|');
      const tags = (card.dataset.tags || '').split('|');
      const match = (!q || normalitza(card.dataset.search).includes(q))
        && (!t || card.dataset.theme === t)
        && (!sub || tags.includes(sub))
        && (!g || groups.includes(g))
        && (!selectedKind || card.dataset.type === selectedKind);
      card.hidden = !match;
      if (match) visible += 1;
    }
    if (count) count.textContent = visible + ' de ' + cards.length + ' fitxes de la mostra';
    if (empty) empty.hidden = visible > 0;
    for (const button of kinds)
      button.setAttribute('aria-pressed', String((button.dataset.kind || '') === selectedKind));
  }

  search?.addEventListener('input', dibuixa);
  theme?.addEventListener('change', dibuixa);
  tag?.addEventListener('change', dibuixa);
  group?.addEventListener('change', dibuixa);
  for (const button of kinds)
    button.addEventListener('click', () => { selectedKind = button.dataset.kind || ''; dibuixa(); });
  root.querySelector('[data-filter-reset]')?.addEventListener('click', () => {
    if (search) search.value = '';
    if (theme) theme.value = '';
    if (tag) tag.value = '';
    if (group) group.value = '';
    selectedKind = '';
    dibuixa();
  });
  dibuixa();
}

function init() {
  document.querySelectorAll('[data-catalog]').forEach(iniciaCataleg);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
