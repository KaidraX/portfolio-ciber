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
    if (btn) {
      btn.addEventListener('click', function () {
        var isLight = root.getAttribute('data-theme') === 'light';
        var next = isLight ? 'dark' : 'light';
        root.setAttribute('data-theme', next);
        try { localStorage.setItem('kx-theme', next); } catch (e) {}
      });
    }
    // no celular: ao escolher um item do menu, fecha o menu (evita a pessoa ficar perdida)
    var nt = document.getElementById('nt');
    var links = document.querySelectorAll('.sb-nav a');
    for (var i = 0; i < links.length; i++) {
      links[i].addEventListener('click', function () { if (nt) nt.checked = false; });
    }
  }
  if (document.readyState !== 'loading') wire();
  else document.addEventListener('DOMContentLoaded', wire);
})();
