/* KaidraX — tema. Escuro é o padrão; guarda a escolha em localStorage. Sem libs, sem inline. */
(function () {
  var root = document.documentElement;
  // aplica antes do paint (script carregado no <head>)
  try {
    var saved = localStorage.getItem('kx-theme');
    if (saved === 'light' || saved === 'dark') root.setAttribute('data-theme', saved);
  } catch (e) {}

  function wire() {
    var btn = document.getElementById('themeToggle');
    if (!btn) return;
    btn.addEventListener('click', function () {
      var isLight = root.getAttribute('data-theme') === 'light';
      var next = isLight ? 'dark' : 'light';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('kx-theme', next); } catch (e) {}
    });
  }
  if (document.readyState !== 'loading') wire();
  else document.addEventListener('DOMContentLoaded', wire);
})();
