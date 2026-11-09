# VulnHub — Vikings: web enum → esteganografia → SSH → RPyC root

> **Fonte:** [VulnHub — Vikings: 1](https://www.vulnhub.com/entry/vikings-1,741/) (máquina pública e gratuita).
> **Tipo:** máquina de laboratório (VulnHub), black-box.
> **Objetivo:** foothold (flag de usuário) e root (flag final).
> **Writeup sanitizado** — flags e a credencial final omitidas de propósito; o foco
> é a metodologia e o mecanismo. Conduzido em VM isolada, para fins de estudo.

---

## Cadeia do ataque

```
nmap  ──►  HTTP(80) + SSH(22)
   │
   ▼
Fuzzing web  ──►  war.txt  ──►  /war-is-over  ──►  blob Base64
   │
   ▼
Base64 ≠ cripto  ──►  ZIP protegido por senha
   │
   ▼
zip2john + John + rockyou  ──►  senha fraca quebrada
   │
   ▼
Esteganografia (ZIP embutido num JPEG)  ──►  credenciais do usuário
   │
   ▼
SSH  ──►  FOOTHOLD (flag de usuário)
   │
   ▼
RPyC rodando como root, sem auth  ──►  RCE como root  ──►  ROOT
```

Causa-raiz recorrente: **segredo escondido ≠ segredo protegido** (Base64, esteg,
senha fraca) e **serviço privilegiado sem autenticação**.

---

## 1. Recon

```bash
nmap -Pn -p- -n -T4 -A -sS -sV <alvo>
```
Dois serviços: **22/TCP** (OpenSSH 7.6p1) e **80/TCP** (Apache 2.4.29). O script
`http-ls` apontou um diretório `site/` — ponto de partida. SSH ficou reservado
para quando houvesse credencial.

## 2. Enumeração web → arquivo exposto

```bash
gobuster dir -u http://<alvo>/site/ \
  -w /usr/share/wordlists/dirb/common.txt -x php,txt,bak,old,sql,zip
```
Achado: `war.txt` (HTTP 200), cujo conteúdo apontava para o diretório oculto
`/war-is-over`. **Mecanismo/classe:** recurso sensível não referenciado, exposto
e acessível sem controle — CWE-548 (listagem/exposição de diretório).

## 3. "Divulgação de informação" — Base64 não é criptografia

`/war-is-over` devolvia um bloco enorme em **Base64**. Base64 é **codificação
reversível**, não cifra — então foi só decodificar:

```bash
curl http://<alvo>/site/war-is-over/ | base64 -d > descripto
```
Resultado: um ZIP protegido por senha. **Classe:** CWE-200 (exposição de
informação sensível); tratar Base64 como texto claro.

## 4. Senha fraca + esteganografia

A senha do ZIP era fraca e caiu em ataque de dicionário:

```bash
zip2john descripto.zip > hash.txt
john hash.txt --wordlist=/usr/share/wordlists/rockyou.txt   # recupera a senha
```
Dentro do ZIP, uma imagem JPEG escondia **outro ZIP embutido** (esteganografia por
concatenação). O `binwalk` localizou o ZIP a partir de um offset; recortando a
partir desse byte e extraindo, saíram as credenciais de um usuário:

```bash
binwalk king                      # revela ZIP embutido no offset 0x15D03F
tail -c +1429568 king > king.zip  # recorta a partir do offset
unzip king.zip && cat user        # credenciais do usuário
```
**Mecanismo:** um JPEG válido seguido dos bytes de um ZIP continua abrindo como
imagem, mas carrega o ZIP "colado" no fim — `binwalk` acha a assinatura `PK` no
meio do arquivo. **Classe:** CWE-521 (senha fraca) + CWE-312/CWE-522 (segredo
"escondido" em artefato acessível = *security through obscurity*).

## 5. Foothold — SSH

```bash
ssh <usuario>@<alvo>
```
Login interativo como o usuário (Ubuntu 18.04). **Flag de usuário**
(`/home/ragnar/user.txt`): `4bf930187d0149a9e4374a4e823f867d`.
**Classe:** CWE-522 — credencial vazada reutilizada para acesso.

## 6. Privesc — RPyC como root, sem autenticação

Enumeração local revelou um serviço **RPyC (Remote Python Call)** rodando **como
root** e **aceitando conexões sem autenticação** → execução remota de código
Python com privilégio de root.

Obstáculo: o usuário não podia executar `/usr/bin/python3.6` (dono de outro
usuário, permissão `754`). Contornado com um detalhe de ownership:

```bash
cp /usr/bin/python3.6 /tmp/py     # a cópia pertence a quem copiou → ganha +x
chmod +x /tmp/py
# conectar ao RPyC local e executar como root → criar shell SUID
/tmp/rootbash -p                  # shell root
```
**Mecanismo (os dois pontos-chave):**
1. **RPyC sem auth como root** = RCE como root de fábrica (CWE-306 *Missing
   Authentication* + CWE-250 *execução com privilégio desnecessário*).
2. O truque do `cp`: `cp` **cria um novo arquivo cujo dono é quem executou o
   comando** — então a cópia do interpretador fica executável pelo próprio
   usuário, driblando a permissão restritiva do binário original.

**Flag de root** (`/root/root.txt`): `f0b98d4387ff6da77317e582da98bf31`.

---

## Mapa de riscos → correções

| Risco | Falha | CWE | Correção |
|---|---|---|---|
| Crítico | RPyC como root sem auth | CWE-306 / CWE-250 | Não rodar serviço como root; exigir auth/ACL ou escutar só em localhost |
| Crítico | Credencial vazada → SSH | CWE-522 | Não armazenar segredos em artefatos acessíveis; cofre de segredos |
| Alto | Senha fraca + esteg | CWE-521 / CWE-326 | Senhas fortes; não "esconder" segredo em imagem |
| Médio | Dados sensíveis em Base64 | CWE-200 | Não expor dados no webroot; Base64 = texto claro |
| Baixo | Arquivos/dirs expostos | CWE-548 | Desabilitar listagem; remover arquivos órfãos |
| Info | SSH/HTTP expostos | — | Firewall; SSH restrito a rede confiável; manter atualizado |

## 🧰 Ferramentas

`nmap` · `gobuster` · `curl` · `base64` · `zip2john` + `John the Ripper` + `rockyou` ·
`binwalk` · `ssh`
