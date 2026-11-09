# Home Lab Ofensivo

Ambiente pessoal para praticar **pentest** de forma segura, reproduzível e
isolada: atacante + alvos vulneráveis em rede fechada, provisionados como código.

> ⚠️ **Isolamento é obrigatório.** O lab é deliberadamente vulnerável. Deve ficar
> em **rede isolada (host-only / NAT interna)**, nunca exposto à internet nem à
> sua LAN doméstica. Nada aqui deve tocar sistema sem autorização.

---

## Objetivo

Ter, na própria máquina, um ambiente onde eu controlo **atacante** e **alvos**,
para treinar o ciclo completo: recon → exploração → pós-exploração → privesc →
**documentação**. Cada alvo derrubado vira um writeup sanitizado em
[`../writeups/`](../writeups/).

---

## Arquitetura (fase 1 — mínimo viável)

Rede isolada única (ex.: `192.168.56.0/24`, host-only), três peças:

```
┌─────────────────────────────────────────────┐
│            Rede host-only (isolada)          │
│                                              │
│   [Kali/Parrot]      [Alvo Linux]            │
│    atacante   ──────► web + privesc          │
│                                              │
│                      [Alvo Windows]          │
│                 ──────► AD / privesc local   │
└─────────────────────────────────────────────┘
```

| Papel | VM sugerida | Para quê |
|---|---|---|
| **Atacante** | Kali Linux ou Parrot OS | ferramentas (nmap, Burp, ffuf, Metasploit, BloodHound...) |
| **Alvo web/Linux** | Metasploitable 2/3, ou VMs do VulnHub, ou DVWA/Juice Shop em Docker | SQLi, LFI, RCE, privesc Linux |
| **Alvo Windows** | Windows 10/Server avaliação (ISO oficial, 180 dias) | privesc local, AD básico |

**Hypervisor:** VirtualBox (grátis) ou VMware Workstation. Snapshot antes de cada
sessão — reverter é parte do fluxo.

---

## Evolução (fase 2 — Active Directory como código)

Quando a fase 1 estiver dominada, subir um **mini-AD vulnerável**. Em vez de
montar na mão, usar _lab-as-code_:

- **GOAD — Game of Active Directory** (Orange Cyberdefense): AD vulnerável como
  código (Vagrant/Ansible), feito **para red team**. É a referência mantida hoje
  para praticar ataque a AD (Kerberoasting, AS-REP roasting, ACL abuse, etc.).
  👉 esta é a escolha certa para o seu objetivo ofensivo.
- **DetectionLab** (clong): excelente, porém **blue team** (Splunk/Sysmon/Zeek) e
  **sem manutenção desde 01/2023**. Útil como **rede-alvo defendida** para
  treinar evasão e entender o que o defensor enxerga — não como lab ofensivo
  principal.

---

## Caminho de construção (passo a passo)

1. [ ] Instalar o hypervisor e criar uma **rede host-only** isolada.
2. [ ] Subir a VM atacante (Kali/Parrot) e tirar snapshot limpo.
3. [ ] Subir **um** alvo vulnerável (começar simples: DVWA ou Metasploitable 2).
4. [ ] Confirmar isolamento: o alvo **não** deve alcançar a internet nem a LAN.
5. [ ] Rodar o ciclo completo num alvo e **documentar** → primeiro writeup do lab.
6. [ ] Adicionar um alvo Windows e repetir para privesc local.
7. [ ] (Fase 2) Subir o GOAD e praticar ataque a AD.
8. [ ] "Lab as code": versionar os scripts/compose de provisionamento aqui, para
       reconstruir o lab do zero — isso é o que transforma "montei um lab" em
       "sei automatizar infraestrutura de teste".

---

## Checklist de segurança (não pular)

- [ ] Rede isolada, sem bridge para a LAN.
- [ ] Alvos vulneráveis **nunca** acessíveis pela internet.
- [ ] Credenciais default dos alvos trocadas **apenas** se o exercício pedir;
      caso contrário, tratar o lab como hostil e não reutilizar nada dele fora.
- [ ] Snapshots antes de cada sessão.
