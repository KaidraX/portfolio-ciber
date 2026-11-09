import re, os

src = open('artifact-index.html', encoding='utf-8').read()
css = src[src.index('<style>')+7 : src.index('</style>')]
secs = dict(re.findall(r'<section class="writeup" id="([^"]+)">(.*?)</section>', src, re.S))

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap">')

def nav(prefix):
    items = ['labs','htb','thm','vulnhub','artigos','projetos','contato']
    links = ''.join(f'<a href="{prefix}#{i}">{i}</a>' for i in items)
    return links

def header(prefix, brand_href):
    return (f'<header class="topbar"><div class="wrap">\n'
    f'  <a class="brand" href="{brand_href}"><span class="p">~/</span>ezequiel<span class="blink">_</span></a>\n'
    f'  <nav>{nav(prefix)}</nav>\n'
    f'</div></header>')

def footer(home_href):
    return (f'<footer><div class="wrap">\n'
    f'  <span class="foot-note">// construído para estudo de pentest · labs próprios e autorizados</span>\n'
    f'  <div class="links"><a href="{home_href}">topo ↑</a>'
    f'<span class="foot-note">DCPT → eJPT → Security+ → PenTest+ → CPTS → OSCP</span></div>\n'
    f'</div></footer>')

# ---------- HOME BODY (igual para artifact e repo; só o <head> difere) ----------
HOME = header('#', '#top') + '''
<main>
  <div class="wrap">

    <section class="hero" id="top">
      <div class="term">
        <div class="term-bar">
          <span class="dot r"></span><span class="dot y"></span><span class="dot g"></span>
          <span class="term-title">ezequiel@sec: ~</span>
        </div>
        <div class="term-body">
          <div class="cmd">ezequiel@sec:~$ <b>whoami</b></div>
          <div class="out">
            <span class="name">Ezequiel</span>
            <span class="tag">Segurança ofensiva</span>
          </div>
          <div class="cmd">ezequiel@sec:~$ <b>cat foco.txt</b></div>
          <div class="out hero-p">
            Foco em <b style="color:var(--fg);font-weight:600">segurança de aplicações web e de infraestrutura</b>:
            do recon ao root. Exploração de SQLi, LFI, SSTI, pivoting entre hosts e, principalmente,
            <b style="color:var(--fg);font-weight:600">escalonamento de privilégio</b> em Linux e Windows.
            Em evolução em Active Directory e automação. Cada writeup é um lab próprio ou autorizado,
            documentado com a cadeia completa, o mecanismo por trás da falha e como corrigi-la.
          </div>
          <div class="cmd">ezequiel@sec:~$ <b>ls writeups/</b> <span style="color:var(--accent)">&amp;&amp;</span> <b>./trilha --status</b></div>
        </div>
      </div>
    </section>

    <section class="block" id="trilha">
      <div class="eyebrow">trilha de certificações</div>
      <h2 class="title">Do fundamento ao OSCP</h2>
      <p class="lead">Caminho planejado, do essencial ao avançado. A base prática (home labs, CTFs e os writeups) corre em paralelo com a teoria.</p>
      <div class="trilha">
        <div class="cert"><span class="n">DCPT</span><span class="s plan">base · Desec</span></div>
        <span class="arrow">→</span>
        <div class="cert now"><span class="n">eJPT</span><span class="s">em progresso</span></div>
        <span class="arrow">→</span>
        <div class="cert"><span class="n">Security+</span><span class="s plan">planejado</span></div>
        <span class="arrow">→</span>
        <div class="cert"><span class="n">PenTest+</span><span class="s plan">planejado</span></div>
        <span class="arrow">→</span>
        <div class="cert"><span class="n">CPTS</span><span class="s plan">planejado</span></div>
        <span class="arrow">→</span>
        <div class="cert"><span class="n">OSCP</span><span class="s plan">objetivo</span></div>
      </div>
    </section>

    <section class="block" id="labs">
      <div class="plat-head"><div class="eyebrow">labs — ExploitMind / HackAcademy</div><span class="count">3 writeups</span></div>
      <h2 class="title">Cadeias de exploração documentadas</h2>
      <p class="lead">Labs levados do acesso inicial ao comprometimento total, indexados por técnica. Credenciais e flags mascaradas — o valor está na metodologia, não no spoiler.</p>
      <div class="grid">
        <a class="card" href="writeups/fit-healthy.html">
          <div class="top"><span class="plat">ExploitMind · D002</span><span class="diff critico">CRÍTICO</span></div>
          <h3>FIT Healthy Center — web até root</h3>
          <p>SQLi não autenticada entrega credenciais em texto plano; LFI via <code>php://filter</code> vaza o código-fonte; reuso de senha dá SSH; privesc por regra sudo + config do Apache gravável.</p>
          <div class="tags"><span class="tag">SQLi UNION</span><span class="tag">auth bypass</span><span class="tag">LFI</span><span class="tag">sudo privesc</span></div>
          <span class="go">ler writeup →</span>
        </a>
        <a class="card" href="writeups/cartao-seguro.html">
          <div class="top"><span class="plat">HackAcademy</span><span class="diff critico">CRÍTICO</span></div>
          <h3>Cartão Seguro — SSTI até root</h3>
          <p>Injeção de template Jinja2 não autenticada vira RCE, vaza a <code>SECRET_KEY</code> e, com <code>doas</code> mal configurado, escala direto a root — sem exploit de kernel.</p>
          <div class="tags"><span class="tag">SSTI</span><span class="tag">RCE</span><span class="tag">doas privesc</span></div>
          <span class="go">ler writeup →</span>
        </a>
        <a class="card" href="writeups/windows-privesc.html">
          <div class="top"><span class="plat">Linux → Windows</span><span class="diff alto">ALTO</span></div>
          <h3>Scheduled Task hijack (Windows)</h3>
          <p>Pivot em Linux, reuso de senha do GLPI, acesso via TeamViewer e privesc abusando de uma Scheduled Task que roda como Administrator apontando para um binário gravável por qualquer usuário.</p>
          <div class="tags"><span class="tag">pivoting</span><span class="tag">reuso de senha</span><span class="tag">CWE-732</span><span class="tag">Windows privesc</span></div>
          <span class="go">ler writeup →</span>
        </a>
      </div>
    </section>

    <section class="block" id="htb">
      <div class="plat-head"><div class="eyebrow">HackTheBox</div><span class="count">0 writeups</span></div>
      <div class="empty">Em andamento. Os writeups de máquinas do <b>HackTheBox</b> entram aqui conforme eu avanço na plataforma — mesma estrutura dos labs: cadeia, mecanismo e mitigação.</div>
    </section>

    <section class="block" id="thm">
      <div class="plat-head"><div class="eyebrow">TryHackMe</div><span class="count">0 writeups</span></div>
      <div class="empty">Em andamento. Salas e writeups do <b>TryHackMe</b> entram aqui, indexados por técnica.</div>
    </section>

    <section class="block" id="vulnhub">
      <div class="plat-head"><div class="eyebrow">VulnHub</div><span class="count">1 writeup</span></div>
      <div class="grid">
        <a class="card" href="writeups/vikings.html">
          <div class="top"><span class="plat">VulnHub</span><span class="diff critico">CRÍTICO</span></div>
          <h3>Vikings — da web ao root</h3>
          <p>Enumeração web leva a um Base64 que esconde um ZIP com senha fraca; dentro, esteganografia numa imagem revela credenciais SSH; privesc por um serviço RPyC rodando como root sem autenticação.</p>
          <div class="tags"><span class="tag">dir enum</span><span class="tag">esteganografia</span><span class="tag">password cracking</span><span class="tag">RPyC privesc</span></div>
          <span class="go">ler writeup →</span>
        </a>
      </div>
    </section>

    <section class="block" id="artigos">
      <div class="plat-head"><div class="eyebrow">artigos</div><span class="count">1 artigo</span></div>
      <h2 class="title">Conceitos &amp; cheatsheets</h2>
      <p class="lead">Notas técnicas sobre classes de vulnerabilidade — o mecanismo por trás da falha, além dos writeups de máquina.</p>
      <div class="grid">
        <a class="card" href="artigos/linux-privesc.html">
          <div class="top"><span class="plat">cheatsheet</span><span class="diff estudo">TÉCNICAS</span></div>
          <h3>Arsenal de Linux PrivEsc</h3>
          <p>Compêndio de vetores: sudo/GTFOBins, LD_PRELOAD e LD_LIBRARY_PATH, cron PATH hijack, tar wildcard injection, SUID + Exim CVE-2016-1531, bash function import, PS4/xtrace e NFS no_root_squash.</p>
          <div class="tags"><span class="tag">sudo</span><span class="tag">SUID</span><span class="tag">LD_PRELOAD</span><span class="tag">wildcard inj.</span><span class="tag">NFS</span></div>
          <span class="go">ler notas →</span>
        </a>
      </div>
    </section>

    <section class="block" id="projetos">
      <div class="plat-head"><div class="eyebrow">projetos</div><span class="count">em breve</span></div>
      <div class="empty">Ferramentas e scripts próprios (automação de recon, PoCs didáticos, utilitários) entram aqui, com link para o repositório e o que cada um resolve.</div>
    </section>

    <section class="block" id="contato">
      <div class="eyebrow">contato</div>
      <h2 class="title">Onde me encontrar</h2>
      <p class="lead">Aberto a oportunidades júnior em segurança ofensiva e defensiva — pentest, AppSec, SOC.</p>
      <div class="links">
        <a href="https://www.linkedin.com/in/SEU-PERFIL" target="_blank" rel="noopener">linkedin ↗</a>
        <a href="https://github.com/ezequielpentest" target="_blank" rel="noopener">github ↗</a>
      </div>
    </section>

  </div>
</main>
''' + footer('#top')

# ---------- WRITEUP PAGES ----------
pages = {
 'fit-healthy':    ('writeups', 'labs',    'FIT Healthy Center — Ezequiel'),
 'cartao-seguro':  ('writeups', 'labs',    'Cartão Seguro — Ezequiel'),
 'windows-privesc':('writeups', 'labs',    'Scheduled Task Hijack — Ezequiel'),
 'vikings':        ('writeups', 'vulnhub', 'Vikings — Ezequiel'),
 'linux-privesc':  ('artigos',  'artigos', 'Arsenal de Linux PrivEsc — Ezequiel'),
}

def standalone(title, body, style_extra=''):
    return ('<!doctype html>\n<html lang="pt-BR">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
    '<meta name="description" content="Ezequiel — portfólio de segurança ofensiva.">\n'
    f'<title>{title}</title>\n{FONTS}\n<style>{css}{style_extra}</style>\n</head>\n<body>\n'
    f'{body}\n</body>\n</html>\n')

os.makedirs('repo/writeups', exist_ok=True)
os.makedirs('repo/artigos', exist_ok=True)

artifact_files = {}
for slug,(folder,anchor,title) in pages.items():
    inner = secs[slug]
    # remove o "portão de validação" (ferramenta de estudo, não vai no portfólio)
    inner = re.sub(r'\s*<div class="wu-sec"><div class="gate">.*?</div></div>', '', inner, flags=re.S)
    inner = inner.replace('<a class="back" href="#writeups">← voltar aos writeups</a>',
                          f'<a class="back" href="../index.html#{anchor}">← voltar ao portfólio</a>')
    body = (header('../index.html#', '../index.html')
            + f'\n<section class="writeup" id="{slug}">{inner}</section>\n'
            + footer('../index.html'))
    page = standalone(title, body, style_extra='.writeup{display:block}')
    path = f'repo/{folder}/{slug}.html'
    open(path,'w',encoding='utf-8').write(page)
    artifact_files[f'{folder}/{slug}.html'] = path

# ---------- HOME: repo (standalone) + artifact (skeleton-free) ----------
open('repo/index.html','w',encoding='utf-8').write(standalone('Ezequiel — Offensive Security', HOME))

art_home = ('<meta name="claude:viewport-fit-sides" content="cover">\n'
    '<title>Ezequiel — Offensive Security</title>\n'
    f'{FONTS}\n<style>{css}</style>\n{HOME}')
os.makedirs('artifact', exist_ok=True)
open('artifact/index.html','w',encoding='utf-8').write(art_home)

print('WROTE repo/index.html + ', list(artifact_files.keys()))
import json
print(json.dumps(artifact_files))
