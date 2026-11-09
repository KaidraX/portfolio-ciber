# Windows: Scheduled Task hijack (CWE-732)

> **Ambiente:** lab de treinamento autorizado.
> **Cenário:** pivot a partir de um host Linux → estação **Windows** → de usuário
> comum a **Administrator** via sequestro de tarefa agendada.
> **Writeup sanitizado** — sem flag, IPs/hostnames e credenciais genericizados.

---

## Cadeia (resumo)

```
Host Linux (foothold)  ──►  credencial encontrada numa CMDB (GLPI)
        │  reuso de senha
        ▼
Conta Windows de usuário comum  ──►  acesso remoto à estação
        │
        ▼
Scheduled Task "Backup" roda como Administrator,
binário gravável por qualquer usuário  ──►  ADMINISTRATOR
```

## 1. Do Linux ao Windows (reuso de credencial)

No host Linux já comprometido, a enumeração de uma CMDB (GLPI) revelou uma
credencial de banco. A **mesma senha** funcionava numa conta Windows de **usuário
comum** na estação — reuso de senha entre sistemas (CWE-522). Daí, acesso remoto
à estação como usuário não-administrativo.

> Vetores fechados pelo alvo (registrados como mitigação real, não falha de
> ferramenta): PrintNightmare inviável — conta com senha expirada + restrição que
> bloqueava a troca self-service via SAMR. Exploit público de uma versão antiga do
> software de acesso remoto também não servia (versão do alvo já corrigida —
> **sempre checar a versão antes de gastar tempo em exploit público**).

## 2. Enumeração de privesc Windows

`whoami /priv` e serviços não renderam (sem *unquoted path*, ACLs corretas). O
achado veio das **tarefas agendadas**:

```cmd
schtasks /query /fo LIST /v
```

Task `\Backup`:
```
Executar como Usuário:   Administrator
Tarefa a ser executada:  "C:\...\Backup\tftpd64.exe"
```

Checando a permissão do binário:
```cmd
icacls "C:\...\Backup\tftpd64.exe"
```
→ `BUILTIN\Usuários:(I)(F)` — **Full Control** para qualquer usuário autenticado.

## 3. Exploração — substituir o binário

**Mecanismo (o ponto-chave):** o serviço Schedule roda como **SYSTEM** e, ao
disparar a task, **impersona o token do usuário configurado** (`Administrator`).
Ele **não revalida** se o binário no caminho ainda é confiável — executa o que
estiver lá. Como `Full Control` inclui `WRITE_DAC`/`DELETE`, dá pra **substituir o
executável inteiro** por um controlado, que então roda como Administrator.
Mesma família de *unquoted service path* e *DLL hijacking*: **confiar em recurso
gravável por usuário de menor privilégio** (CWE-732).

Passos (descritos; sem entregar payload armado):
1. Substituir `tftpd64.exe` por um executável controlado na mesma pasta gravável.
2. **Armadilha encontrada:** `schtasks /run /tn "\Backup"` reportou "êxito" mas
   não lançou processo novo — o binário original era um servidor de longa duração
   ainda "em execução", e a config padrão "não iniciar nova instância" bloqueou o
   disparo. Correção: `schtasks /end /tn "\Backup"` e depois `/run` de novo.
3. Processo disparou como Administrator; evidência coletada na área de trabalho do
   Administrador.

## O que quebraria o exploit

- Permissão correta no binário da task (**não** gravável por usuários comuns).
- Rodar a task com a **menor** conta necessária, não Administrator.
- Não reutilizar senhas entre sistemas (fecharia o acesso inicial à estação).

## Classes (CWE)

| Etapa | Falha | CWE |
|---|---|---|
| Acesso inicial | Reuso de credencial entre sistemas | CWE-522 |
| Privesc | Binário de task gravável por usuário | CWE-732 |
| Privesc | Execução com privilégio excessivo (task como Administrator) | CWE-250 |

## 🧰 Ferramentas / comandos
`schtasks /query /v` · `icacls` · `whoami /priv` · cross-compiler (MinGW) para o
binário de prova · `Invoke-WebRequest`
