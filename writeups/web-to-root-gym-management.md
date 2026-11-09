# Web → Root: SQLi → LFI → reuso de credencial → sudo misconfig

> **Ambiente:** laboratório de treinamento autorizado (caixa-preta).
> **Alvo (genérico):** aplicação web PHP + MySQL de gestão, atrás de Apache.
> **Resultado:** da ausência de credenciais até **root**, encadeando quatro
> falhas independentes.
> **Writeup sanitizado** — sem flags, credenciais ou endereços reais; o foco é a
> metodologia e o mecanismo de cada falha.

---

## Resumo da cadeia

```
Recon (OSINT + vhost fuzzing)
        │
        ▼
SQL Injection (UNION, sem auth)  ──►  credenciais de admin em texto claro
        │
        ▼
LFI (php://filter)  ──►  leitura do código-fonte  ──►  credenciais hard-coded no db.php
        │
        ▼
Reuso de senha (DB ➜ SSH)  ──►  shell como usuário de sistema
        │
        ▼
sudo NOPASSWD + arquivo de config gravável  ──►  ROOT
```

Causa-raiz recorrente da cadeia: **confiar em entrada ou recurso controlável por
quem tem privilégio menor do que quem o consome.**

---

## 1. Reconhecimento

- `nmap` revelou apenas Apache (porta 80).
- Dois virtual hosts no mesmo IP: o site público e um **painel de gestão**
  interno — este último **não** aparecia em wordlists genéricas e só foi
  descoberto por **fuzzing manual do header `Host`** (faltava o termo de negócio
  em português na wordlist; o método do script estava certo, a cobertura é que
  não).
- **OSINT:** o painel era um projeto *open-source* conhecido, implantado **sem
  customização**. Isso entregou o schema do banco (tabelas/colunas) de graça,
  antes de qualquer requisição ao alvo → CWE-200 (exposição por reuso de projeto
  público intacto em produção).

**Hipótese:** app open-source sem customização → provável SQLi nos pontos de
busca e lógica de `include()` previsível.

---

## 2. SQL Injection (UNION-based, sem autenticação)

**Onde:** endpoint de busca acessível por HTTP direto, **sem passar por sessão**
(falha de autorização em módulo isolado — CWE-862).

**Mecanismo:** o parâmetro era concatenado direto na query, sem *prepared
statement*. O formulário de login, em contraste, usava `mysqli_real_escape_string()`
e bloqueava a injeção clássica — ou seja, **a mesma app tinha o padrão certo num
lugar e errado no outro**.

A consulta devolvia 4 colunas renderizadas numa tabela. Um `UNION SELECT` com 4
valores vindos da tabela de login imprime as credenciais nos mesmos campos — o
PHP só exibe o que o MySQL devolve, sem saber de qual tabela a linha veio:

```bash
curl -s -H "Host: <painel>" "http://<alvo>/<busca>.php" \
  --data-urlencode "name=x' UNION SELECT id,uname,pwd,4 FROM login#"
```

Resultado: usuário e senha de admin **em texto claro** (sem hash) → CWE-256.

**O que quebraria:** *prepared statements* matam a classe inteira; e hashing
forte (bcrypt/argon2) neutralizaria o impacto mesmo com a SQLi presente.

---

## 3. LFI + leitura de código-fonte via `php://filter`

**Onde:** parâmetro `info` de um roteador (`home.php?info=<módulo>`), já
autenticado com a credencial da etapa 2.

**Mecanismo:** o roteador tinha uma whitelist de módulos, mas com um
`else { include(@$info); }` no final — qualquer valor não reconhecido ia direto
pro `include()` sem sanitização (CWE-98 / CWE-22). Como `include()` **executa**
arquivos `.php` em vez de exibi-los, usei o wrapper de stream do PHP para ler o
**código-fonte** em Base64:

```
home.php?info=php://filter/convert.base64-encode/resource=db.php
```

Isso expôs o `db.php` com **credenciais de banco hard-coded** (CWE-798).

**O que quebraria:** whitelist fechada sem fallback (remover o `else include`);
nunca passar entrada de usuário direto para `include()`/`require()`.

---

## 4. Reuso de credencial (DB ➜ SSH)

A senha do banco — de formato claramente não-adivinhável — estava **reutilizada**
como senha de um usuário de sistema. Login por SSH com ela deu **shell**.

**Mecanismo/lição:** o problema não é a senha ser fraca (não era) — é a mesma
senha atravessar camadas (aplicação → banco → SO). Uma credencial vazada por
uma falha de *aplicação* virou acesso ao *sistema operacional*.

**O que quebraria:** segredos por serviço, nunca reutilizados; cofre de segredos
em vez de hard-code.

---

## 5. Privesc: sudo NOPASSWD + config gravável

Enumeração como o usuário:

```
$ sudo -l
(ALL) NOPASSWD: /bin/systemctl restart apache2
```

Isoladamente, reiniciar o Apache **não** dá root. O vetor real dependia de uma
**segunda** condição: o arquivo de configuração do Apache era **gravável** pelo
usuário.

**Mecanismo (o ponto-chave):** ao reiniciar via `systemctl`, o processo *master*
do Apache sobe pelo `systemd` **como root** e **relê toda a configuração ainda
como root**, antes de rebaixar privilégio para os *workers* (`www-data`). A
diretiva `CustomLog "|comando"` (log via pipe) faz o master executar o comando
via `popen()` **no startup, como root**. Injetando essa diretiva na config
gravável e disparando o restart permitido pelo `sudo`, o comando roda como root.

```bash
# conceito: injeta diretiva de log com pipe na config gravável
echo 'CustomLog "|/bin/sh -c \"<comando-como-root>\"" combined' >> <apache.conf>
sudo /bin/systemctl restart apache2
```

Classe: **CWE-250** (execução com privilégio desnecessário) + **CWE-732**
(permissão incorreta em recurso crítico). A regra de `sudo`, "segura" em teoria,
vira crítica combinada com o arquivo gravável.

**O que quebraria:** nenhum arquivo relido por processo privilegiado
(config, logs, unit files) deve ser gravável por usuário não-root; e a regra de
`sudo` deveria ser a mínima necessária.

---

## Mapa de CWEs

| Etapa | Falha | CWE |
|---|---|---|
| Recon | Reuso de projeto público sem customização | CWE-200 |
| 2 | SQL Injection | CWE-89 |
| 2 | Módulo acessível sem sessão | CWE-862 |
| 2 | Senha em texto claro | CWE-256 |
| 3 | LFI / path traversal | CWE-98 / CWE-22 |
| 3 | Credencial hard-coded | CWE-798 |
| 5 | Privilégio excessivo + arquivo gravável | CWE-250 / CWE-732 |

## Portão de validação (autoteste)

- **Classe de cada falha?** ✔ (tabela acima)
- **Por que o mecanismo funciona?** ✔ (destaque: Apache relê config como root
  antes do *drop* de privilégio)
- **O que quebraria o exploit?** ✔ (prepared statements, hashing, whitelist
  fechada, segredos por serviço, config não-gravável)
