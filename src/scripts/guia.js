/* Obre l'instrument seleccionat des d'un enllaç amb #pnl, #proposicio... */
function obreIniciativa() {
  const slug = decodeURIComponent(location.hash.slice(1));
  if (!slug) return;
  const candidate = document.getElementById(slug);
  if (candidate?.tagName === 'DETAILS') candidate.open = true;
}
function init() {
  obreIniciativa();
  window.addEventListener('hashchange', obreIniciativa);
  const buttons = [...document.querySelectorAll('[data-answer]')];
  const feedback = document.querySelector('[data-feedback]');
  for (const button of buttons) {
    button.addEventListener('click', () => {
      for (const other of buttons)
        other.setAttribute('aria-pressed', String(other === button));
      if (feedback) feedback.textContent = button.dataset.answer === 'correcte'
        ? "Correcte. L'article 86 de la Constitució estableix que el Congrés n'ha de decidir la convalidació o derogació en 30 dies."
        : "No ben bé. Un reial decret llei té rang de llei, però el Congrés l'ha de convalidar o derogar dins el termini constitucional de 30 dies.";
    });
  }
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
else init();
