# SSTI → RCE → doas: do formulário público ao root

> **Ambiente:** lab de treinamento autorizado (black-box).
> **Alvo (genérico):** aplicação web **Flask/Jinja2** com um formulário público.
> **Resultado:** de uma injeção em formulário anônimo até **root**.
> **Writeup sanitizado** — sem flag, sem credenciais reais, sem nomear a plataforma.

---

## Cadeia do ataque

```
Formulário público (campo "nome")
        │  input refletido sem sanitização
        ▼
SSTI (Jinja2)  ──►  {{7*7}} = 49  ──►  {{config}} vaza SECRET_KEY
        │
        ▼
RCE como usuário de serviço (via __globals__ → os.popen)
        │
        ▼
doas sem restrição de comando  ──►  ROOT
```

---

## 1. Recon

Fingerprint pelos headers HTTP (`Server: Werkzeug ... Python`) → stack **Flask**.
Duas rotas: `/` (formulário público "veja se seu cartão vazou") e `/admin`
(login). O painel de login estava limpo (sem debug do Werkzeug, sem oracle de
enumeração de usuário). A superfície real era o **formulário público**.

**Hipótese:** input refletido numa app Flask → testar **SSTI**.

## 2. SSTI confirmado

O valor do campo `nome` era concatenado numa string de template e passado a
`render_template_string()` — ou seja, **dado do usuário virava sintaxe de
template**.

```
nome={{7*7}}      → resposta contém "49"   (confirmação)
nome={{config}}   → despeja o objeto Config do Flask, incluindo a SECRET_KEY
```

**Mecanismo:** `render_template_string()` compila e avalia a string como template
Jinja2. Se a entrada do usuário entra nessa string, qualquer expressão Jinja2 é
executada no servidor. **Classe:** CWE-1336 (Server-Side Template Injection).

## 3. Divulgação da SECRET_KEY

`{{config}}` expôs a `SECRET_KEY`. Ela não garante confidencialidade — só assina
(HMAC) os cookies de sessão. Com ela, dá pra **forjar** qualquer cookie de sessão
válido (ex.: `flask-unsign --sign --cookie "{'logged_in': True}" --secret <chave>`),
contornando autenticação em rotas que dependem de `session`.
**Classe:** CWE-200 / uso de segredo previsível.

## 4. SSTI → RCE

Escalando a SSTI para execução de comando, navegando a cadeia de objetos Python
a partir do template até o módulo `os`:

```
{{ config.__class__.__init__.__globals__['os'].popen('id').read() }}
```

**Mecanismo (o ponto-chave):** em Jinja2 dá pra "andar" pela hierarquia de classes
Python (`__class__` → `__init__` → `__globals__`) até alcançar módulos já
importados no processo (aqui, `os`), e então chamar `popen()`. A resposta
confirmou execução como o **usuário de serviço** da aplicação.
**Classe:** CWE-94 (Code Injection) / RCE.

## 5. Privesc — doas sem restrição

Com shell como o usuário de serviço, a enumeração mostrou uma regra de **`doas`**
(equivalente OpenBSD do `sudo`) **sem restrição de comando** para esse usuário.
Isso permite executar comando arbitrário como root:

```bash
echo "id" | doas        # executa como root
```

**Mecanismo:** `doas` com `permit nopass` genérico, sem `cmd` específico, dá ao
usuário de serviço um caminho direto a root — sem precisar de exploit de kernel
(que, aliás, estava pré-posicionado no lab mas foi **desnecessário**).
**Classe:** CWE-269 (Improper Privilege Management).

---

## Observação de pós-exploração

O banco da aplicação (`SQLite`) guardava dados de cartão (número, validade, CVV,
senha) em **texto claro** — CWE-312. Qualquer leitura no servidor (como a RCE
acima) expõe tudo. Em cenário real, violação direta de PCI-DSS.

## Mapa de riscos → correções

| Risco | Falha | CWE | Correção |
|---|---|---|---|
| Crítico | SSTI → RCE | CWE-1336 / CWE-94 | `render_template()` com arquivo fixo; passar input como **variável de contexto**, nunca na string do template |
| Alto | SECRET_KEY exposta/previsível | CWE-200 | Rotacionar; carregar de secret manager com alta entropia |
| Crítico | doas sem restrição | CWE-269 | Regra mínima, sempre com `cmd` específico; nunca `permit nopass` genérico |
| Alto | Dados de cartão em texto claro | CWE-312 | Nunca armazenar PAN/CVV/senha em claro |

**Correção de maior prioridade:** a 1 (SSTI) — eliminá-la quebra toda a cadeia.

## 🧰 Ferramentas
`curl` · análise de headers · payloads Jinja2 · `sqlite3` · `doas`
