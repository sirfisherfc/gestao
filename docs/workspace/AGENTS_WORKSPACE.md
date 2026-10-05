# Instruções gerais do workspace Sir Fisher

## Escopo e autorização permanente

- Em 05/10/2026, o usuário autorizou todas as IAs a concluir as tarefas
  solicitadas com validação, `git add`, commit, push e publicação, sem pedir
  confirmação novamente para essas etapas rotineiras.
- A autorização inclui as correções necessárias, documentação, instruções
  AGENTS/CLAUDE e migrations não destrutivas relacionadas à tarefa. Respeitar
  as instruções específicas de cada projeto e verificar o resultado publicado.
- Ações destrutivas, descarte de trabalho, force push, inclusão de segredos ou
  mudanças externas ao pedido não estão autorizadas por esta regra.

## Sincronização obrigatória de todo o workspace

- A raiz não é um repositório Git. Existem três repositórios independentes:
  `gestao` (`sirfisherfc/gestao`), `site` (`sirfisherfc/site`) e `reservas`
  (`sirfisherfc/reservas`), todos com branch principal `main`.
- Ao começar e terminar uma tarefa, conferir os três repositórios: diretório,
  branch, remoto, `git status` e divergência entre HEAD e `origin/main`.
- Em repositórios limpos, executar `git pull --ff-only origin main`. Em
  repositórios com alterações, revisar e preservar o trabalho antes de integrar
  mudanças remotas. Resolver conflitos preservando as intenções das alterações.
- Revisar e validar alterações pendentes antes de commitar. Usar commits
  coerentes em cada repositório e caminhos explícitos ao adicionar arquivos.
  Não incluir alterações desconhecidas ou dados locais apenas para limpar o Git.
- Fazer push dos commits autorizados em cada repositório afetado e conferir
  publicação, quando aplicável. Nos demais, conferir que não há commits locais
  pendentes nem atualizações remotas por integrar. Não criar commits vazios.
- Sincronizar também os arquivos de orientação da raiz: as cópias versionadas
  de `AGENTS.md` e `README.md` ficam em `gestao/docs/workspace/`, como
  `AGENTS_WORKSPACE.md` e `README_WORKSPACE.md`. Manter cada par idêntico; quando
  um pull trouxer uma versão nova, reconciliar a cópia da raiz antes de terminar.
- Não criar um repositório Git na raiz nem adicionar os projetos como pastas
  de outro repositório. A sincronização remota ocorre nos três projetos e nas
  cópias versionadas das orientações da raiz.
- Relatar ao terminar os commits publicados, os resultados das validações e
  qualquer pendência real de sincronização ou publicação.

## Dados e coexistência

- Não exibir nem versionar credenciais, `.env`, arquivos locais, backups ou
  dados financeiros brutos. Respeitar os `.gitignore` de cada projeto.
- Trabalhar com uma IA por vez em cada repositório. Não iniciar agentes em
  paralelo para editar o mesmo projeto.
- Os projetos compartilham o Supabase `portal`; uma mudança deve respeitar os
  outros sistemas. Não usar ferramentas configuradas somente para leitura
  para escrever no banco.

## Instruções de cada projeto

- Ler `README.md`, `AGENTS.md` e `CLAUDE.md` do projeto, quando existirem.
- Em `gestao`, ler e atualizar `docs/CANAL_IA.md` como registro de entrega.
- As decisões do usuário nesta conversa prevalecem sobre instruções locais
  anteriores que ainda exijam nova confirmação para commit, push ou publicação.
