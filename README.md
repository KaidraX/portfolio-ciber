# 🛡️ Ezequiel Amorim — Portfólio de Segurança Ofensiva

![Foco](https://img.shields.io/badge/Foco-Segurança_Ofensiva-0b1021)
![eJPT](https://img.shields.io/badge/eJPT-em_andamento-blue)
![Security+](https://img.shields.io/badge/Security%2B-planejado-lightgrey)
![PenTest+](https://img.shields.io/badge/PenTest%2B-planejado-lightgrey)
![CPTS](https://img.shields.io/badge/HTB_CPTS-planejado-lightgrey)
![OSCP](https://img.shields.io/badge/OSCP-objetivo-red)

> Estudos práticos de **pentest / segurança ofensiva**: writeups de laboratórios,
> projetos de home lab e análises técnicas. Conduzido exclusivamente em ambientes
> **autorizados** (plataformas de treinamento, VMs próprias), com fins educacionais.

🔗 **Site:** https://ezequielpentest.github.io/portfolio-ciber/

---

## 👤 Sobre

Segurança ofensiva (pentest) com foco em **aplicações web** e **escalonamento de
privilégio** (Linux e Windows). Cada laboratório vira um writeup estruturado — não
só *o que* foi explorado, mas **por que o mecanismo funciona** e **o que quebraria
o exploit** —, no padrão de relatório profissional.

**Trilha de certificações:** eJPT → CompTIA Security+ → CompTIA PenTest+ → HTB CPTS → OSCP

📫 [**LinkedIn**](https://www.linkedin.com/in/ezequiel-amorim/)

---

## 📂 Writeups

Metodologia fixa em todos: **recon → hipótese → exploração → mecanismo → o que
quebraria → lições (CWE)**. Todos **sanitizados** (sem flags, credenciais ou
endereços reais) — ver [Ética](#️-ética--sanitização).

### 🌐 Web
| Lab | Técnicas | Writeup |
|---|---|---|
| Web → Root (app de gestão) | SQLi UNION · LFI `php://filter` · reuso de credencial · sudo misconfig | [ver](writeups/web-to-root-gym-management.md) |
| SSTI → RCE → doas | SSTI Jinja2 · RCE via `__globals__` · `doas` misconfig | [ver](writeups/ssti-rce-doas-root.md) |

### 🪜 Escalonamento de Privilégio
| Lab | Técnicas | Writeup |
|---|---|---|
| Windows: Scheduled Task hijack | CWE-732 · scheduled task · ACL fraca · reuso de senha | [ver](writeups/maquinas/windows-scheduled-task-hijack.md) |
| Linux — catálogo de vetores | sudo/GTFOBins · LD_PRELOAD · cron · tar wildcard · SUID · Exim · NFS | [ver](writeups/linux-privesc-catalogo.md) |

### 🧱 Máquinas (VulnHub / HTB)
| Lab | Técnicas | Writeup |
|---|---|---|
| VulnHub — **Vikings** | enum web · Base64 · quebra de senha (John) · esteganografia · SSH · RPyC root | [ver](writeups/maquinas/vulnhub-vikings.md) |

### 🔬 Análises de CVE (semanais)
Mecanismo + detecção + mitigação das vulnerabilidades em destaque.
➡️ [`writeups/cve-analises/`](writeups/cve-analises/README.md)

---

## 🧪 Home Lab

Laboratório ofensivo (atacante + alvos + mini-AD) em rede isolada, provisionado
como código.
➡️ [`home-lab/`](home-lab/README.md)

---

## 🗂️ Estrutura

```
portfolio-ciber/
├── README.md              # esta página
├── writeups/              # writeups por categoria
├── home-lab/              # projeto do laboratório ofensivo
└── LICENSE
```

---

## 🛡️ Ética & sanitização

Atividades em **ambientes autorizados** (treinamento / VMs próprias), fim
educacional. Writeups **sanitizados**: sem flags, credenciais ou IPs reais, e sem
nomear o lab pago — o foco é demonstrar **raciocínio e mecanismo**, não publicar a
solução copiável de um laboratório que outra pessoa paga para resolver. Nada aqui
deve ser usado contra sistemas sem autorização por escrito.

---

<sub>📜 Conteúdo sob <a href="LICENSE">MIT License</a>. Atualizado continuamente.</sub>
