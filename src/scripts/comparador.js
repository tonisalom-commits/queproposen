/* Comparador documental, NO estadístic: reusa les targetes generades per Astro. */
function iniciarComparador(root) {
  const cards = [...document.querySelectorAll('[data-catalog] [data-card]')];
  const a = root.querySelector('[data-compare-a]');
  const b = root.querySelector('[data-compare-b]');
  const topic = root.querySelector('[data-compare-tag]');
  if (!a || !b || !topic) return;

  function mostra(panelName, selected) {
    const output = root.querySelector('[data-compare-output="' + panelName + '"]');
    if (!output) return;
    const headline = document.createElement('h3');
    headline.textContent = selected.selectedOptions[0]?.textContent || 'Grup';
    output.replaceChildren(headline);
    const group = selected.value;
    const theme = topic.value;
    const found = cards.filter((c) =>
      (c.dataset.groups || '').split('|').includes(group) &&
      (!theme || (c.dataset.tags || '').split('|').includes(theme))
    );
    if (!found.length) {
      const note = document.createElement('p');
      note.className = 'comparison-empty';
      note.textContent = "Encara no s'ha incorporat cap expedient d'aquest grup per al filtre triat. No indica absència de propostes al Congrés.";
      output.appendChild(note);
      return;
    }
    const caveat = document.createElement('p');
    caveat.className = 'coverage-note';
    caveat.textContent = "Fitxes de la mostra provisional, no total d'iniciatives del grup.";
    output.appendChild(caveat);
    for (const c of found) {
      const article = document.createElement('div');
      article.className = 'comparison-record';
      const meta = document.createElement('span');
      meta.textContent = (c.dataset.type || '') + ' · ' + (c.dataset.status || 'Estat no incorporat');
      const title = document.createElement('b');
      title.textContent = c.dataset.title || c.querySelector('h3')?.textContent || 'Iniciativa';
      const link = document.createElement('a');
      link.href = c.dataset.url || '#';
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      link.textContent = 'Expedient ' + (c.dataset.id || '') + ' ↗';
      article.append(meta, title, link);
      output.appendChild(article);
    }
  }
  const draw = () => { mostra('a', a); mostra('b', b); };
  a.addEventListener('change', draw);
  b.addEventListener('change', draw);
  topic.addEventListener('change', draw);
  draw();
}

function init() {
  document.querySelectorAll('[data-comparador]').forEach(iniciarComparador);
}
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
