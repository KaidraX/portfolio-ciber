# Linux Privilege Escalation — catálogo de vetores praticados

> **Ambiente:** labs de treinamento autorizados / VMs próprias.
> Compilação de **vetores de escalonamento de privilégio em Linux** que pratiquei,
> cada um com o **mecanismo** (por que funciona) e **o que o quebraria**. Técnicas
> públicas e padrão; foco didático.

---

## 1. `sudo -l` + escape de shell (GTFOBins)

`sudo -l` lista o que o usuário pode rodar como root. Muitos binários permitidos
têm **escape de shell** documentado no GTFOBins (ex.: `vim`, `less`, `awk`, `find`,
`nmap`...). Via esse escape, herda-se o contexto root.

**Mecanismo:** o GTFOBins classifica por *função concedida* (Shell, Command, File
read/write, etc.); um binário rodado via `sudo` que abre shell herda o privilégio.
**Quebra:** restringir `sudo` ao mínimo; evitar binários com escape conhecido.

## 2. `LD_PRELOAD` (quando preservado pelo sudo)

Com `env_keep += LD_PRELOAD` no `sudo -l`, o sudo preserva a variável no processo
root. Uma biblioteca compartilhada com um **construtor** malicioso é carregada à
força e executa **antes** do programa principal.

**Mecanismo:** `__attribute__((constructor))` roda no *load* da lib, como root.
**Quebra:** nunca preservar `LD_PRELOAD`/`LD_LIBRARY_PATH` no sudoers.

## 3. `LD_LIBRARY_PATH` hijack

Com `LD_LIBRARY_PATH` preservado, aponta-se o linker dinâmico para um diretório
controlado. Só funciona com o **nome exato** de uma biblioteca realmente listada
como `NEEDED` do binário (checado com `ldd`).

**Mecanismo:** o binário grava só o *nome* da lib; a resolução acontece em runtime
pelo `ld.so`, que `LD_LIBRARY_PATH` redireciona. **Quebra:** idem acima.

## 4. Cron job — PATH hijack

Um `cron` com `PATH` incluindo diretório gravável, chamando um script **sem
caminho absoluto**, permite plantar um binário homônimo que roda com o privilégio
do cron (geralmente root).

**Mecanismo:** quebra de fronteira de confiança — quem **escreve** o recurso tem
privilégio menor que quem o **executa**. **Quebra:** caminho absoluto nos cron
jobs; diretórios de PATH não graváveis.

## 5. `tar` wildcard injection

Um script que roda `tar -czf backup.tar.gz *` num diretório onde o atacante cria
arquivos. Criando arquivos chamados `--checkpoint=1` e
`--checkpoint-action=exec=...`, o **glob** expande esses nomes como **flags** do
tar, que executa o comando.

**Mecanismo:** o `*` do shell expande nomes de arquivo que o `tar` interpreta como
opções (*argument injection*). Mesma lógica em `chown -R`, `rsync`, `zip`.
**Quebra:** usar `./*` ou `--` para encerrar opções; não usar glob cru em scripts
privilegiados.

## 6. SUID hunting + Exim (CVE-2016-1531)

```bash
find / -type f -a \( -perm -u+s -o -perm -g+s \) -exec ls -l {} \; 2>/dev/null
```
Achado de um `exim` SUID vulnerável. O exploit usa `PERL5LIB`/`PERL5OPT` para
carregar um módulo Perl controlado; a inicialização do Perl acontece **antes** do
exim derrubar o privilégio root.

**Mecanismo:** variável de ambiente controlada pelo atacante consumida por um
processo ainda privilegiado (timing errado no *drop* de privilégio).
**Quebra:** patch do exim; sanitizar env em binários SUID.

## 7. SUID binary com PATH hijack

Binário SUID root que chama um comando (ex.: `service apache2 start`) **sem caminho
absoluto**. Plantando um binário homônimo e ajustando o `PATH`, ele roda como root.
**Mecanismo/quebra:** igual ao item 4, mas direto no binário SUID (sem cron).

## 8. Import de função bash (bash < 4.2-048)

Mesmo com caminho **absoluto**, versões antigas do bash permitiam **exportar uma
função** com nome de caminho, que tinha prioridade sobre o binário real:

```bash
function /usr/sbin/service { /bin/bash -p; }; export -f /usr/sbin/service
```
**Quebra:** atualizar o bash; não executar binários SUID que invoquem subshell.

## 9. Abuso de `PS4` / xtrace

`PS4` (prompt de debug do bash) pode conter `$(...)`, executado a cada linha
traçada em modo `xtrace`:

```bash
env -i SHELLOPTS=xtrace PS4='$(cp /bin/bash /tmp/rootbash; chmod +xs /tmp/rootbash)' <binário-suid>
/tmp/rootbash -p
```
**Mecanismo:** `SHELLOPTS=xtrace` liga o debug via env herdada; o `PS4` malicioso
roda a cada linha. **Quebra:** sanitizar env; não invocar bash a partir de SUID.

## 10. Vetores de configuração / credenciais

- **Senha no histórico de shell** (`~/.*history`): senha digitada na linha de
  comando fica em texto claro (e visível em `ps aux`). **Quebra:** não passar
  segredo via argumento.
- **Chave SSH exposta** (legível por todos): qualquer um loga como o dono. O
  próprio cliente SSH exige `chmod 600`. **Quebra:** permissão `600` e chaves fora
  de diretórios world-readable.
- **NFS `no_root_squash`**: o UID root remoto é mantido como root real no
  servidor; monta-se o share, cria-se um SUID root e executa-se no alvo.
  **Quebra:** manter o *root squash* (default) habilitado.

---

## Nota de técnica (shared libraries)

Vários vetores acima dependem de entender **linkagem dinâmica**: o binário grava o
*nome* da lib (`NEEDED`), não o caminho; o `ld.so` resolve em runtime; o construtor
da lib roda no carregamento. É por isso que `LD_PRELOAD`/`LD_LIBRARY_PATH`
funcionam — e por isso preservá-los no `sudo` é perigoso.

## 🧰 Ferramentas
`sudo -l` · GTFOBins · `gcc` (libs de PoC) · `ldd` · `find` (SUID/SGID hunting) ·
`cron` · `tar` · `ssh`
