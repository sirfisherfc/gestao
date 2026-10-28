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
- Desde 30/10/2026, o Supabase não concede mais acesso da Data API a tabelas
  e views novas no `public`. Quem criar ou recriar um objeto deve incluir no
  mesmo SQL os `GRANT` de cada papel que vai usá-lo, inclusive `service_role`
  para Edge Functions; `anon` só com decisão explícita. Regras completas em
  `gestao/AGENTS.md` e `reservas/docs/supabase.md`.
- Os projetos compartilham o Supabase `portal`; uma mudança deve respeitar os
  outros sistemas. Não usar ferramentas configuradas somente para leitura
  para escrever no banco.

## Acesso ao Perfil da Empresa no Google

- Antes de solicitar novo login ou token temporário, executar
  `python site/tools/analytics/google_oauth_helper.py --verificar`.
- A autorização persistente já configurada em `gestao/scripts/gbp/gbp.py`
  usa `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET` e
  `GOOGLE_OAUTH_REFRESH_TOKEN`, do ambiente ou de `gestao/.env` ignorado.
  Reutilizar essa rotina para leituras e alterações autorizadas do perfil.
- Em 07/10/2026, duas renovações e leituras reais da ficha/avaliações foram
  verificadas sem intervenção do usuário. Não voltar a pedir um Access token
  de uma hora enquanto a credencial existente puder renovar o acesso.
- Só solicitar reconexão depois de confirmar falha da renovação ou ausência
  da credencial necessária. Não exibir, copiar para páginas nem versionar
  os segredos. Não criar uma segunda rotina agendada para o mesmo perfil.

## Acesso ao Supabase portal

- A credencial de implantação e leitura da Management API está em
  `reservas/.env.local`, variável `SUPABASE_ACCESS_TOKEN`. Esse arquivo fica
  no OneDrive para uso nos dois PCs do proprietário e é ignorado pelo Git.
  Não copiar seu conteúdo para documentação, chat, logs ou commits.
- Antes de pedir reconexão, executar
  `python site/tools/analytics/supabase_credentials.py`. Essa verificação
  reutiliza a credencial e confirma acesso ao projeto `portal` sem exibi-la.
- Scripts Python podem reutilizar `access_token()` do módulo
  `site/tools/analytics/supabase_credentials.py`; o ambiente tem precedência.
  Validar o projeto de destino antes de implantar. Um conector que mostre
  somente outros projetos não invalida esse acesso local já configurado.
- Não usar DPAPI vinculado a um PC como armazenamento canônico, pois o
  proprietário alterna entre dois computadores. Manter a pasta e o arquivo
  privados no OneDrive; as permissões locais devem ser verificadas em cada PC.
- O acesso existente não amplia autorização: consultas de auditoria usam
  a rota de leitura; implantações dependem do pedido e preservam autenticação,
  segredos e os outros sistemas. Ferramentas MCP de leitura continuam sem escrita.

## MCP do Google Analytics

- Em 22/10/2026, o usuário autorizou preparar o MCP oficial do Google Analytics
  para uso persistente, com as ferramentas de consulta e sem login a cada uso.
- Quando precisar de Analytics, conferir se `google_analytics` já está
  cadastrado no Codex local. Se faltar neste PC, executar
  `python site/tools/analytics/configurar_mcp.py`, sem pedir nova autorização.
  O instalador reutiliza o `service_account.json` privado existente e mantém
  as dependências em `LOCALAPPDATA`, separadas dos relatórios e do OneDrive.
- Não copiar a chave para configurações, documentação ou chat. Não habilitar
  `--allow-write`. O cadastro é local a cada PC e persiste nas sessões futuras;
  um cliente já aberto pode precisar de um reinício para carregar o servidor.
- Cadastro e lista de ferramentas não comprovam acesso ao Google. Antes de
  pedir login ou nova credencial, validar uma consulta real com o acesso atual.
  Search Console, Perfil da Empresa e operação continuam nas rotinas próprias.

## Instagram e analise de reservas

- O MCP local `instagram_analytics` usa o app/token existente da Meta e
  oferece somente leitura do `@sirfisherfc`. Confirmar identidade; usar
  cache, janelas de ate 30 dias e metricas com sua cobertura original.
- Guia e estado real de cada cliente em
  `gestao/docs/INTEGRACAO_INSTAGRAM_ANALYTICS.md`. Configuracao persistente
  nao comprova leitura por uma sessao antiga; validar a ferramenta nela.
- Manter origem declarada, origem medida e credito atribuido pela Meta
  separados. Publicacao, Direct, comentarios individuais e anuncios ficam
  fora deste servidor. Nao criar outra rotina recorrente ou pedir token no chat.

## Operação do Teknisa pela ferramenta compartilhada

- Para tarefas no Teknisa, ler primeiro `gestao/scripts/teknisa/README.md`
  e executar `node gestao/scripts/teknisa/teknisa.mjs comandos` na raiz.
  Usar os comandos validados para consultas e alterações repetitivas.
- Usar a interface para conhecer uma função nova, capturar a conexão da
  sessão autorizada, conferir uma amostra ou investigar uma divergência.
  Evitar repetir edição de registro em registro quando houver comando
  validado. Ampliar a ferramenta ao validar uma operação nova.
- Conferir o destino e a prévia antes de aplicar o pedido já autorizado.
  Gravação validada, leitura validada e função ainda em preparação são
  estados diferentes. Não habilitar escrita por inferência de um caminho.
- Autenticação permanece em memória. Planos e recibos ficam em
  `gestao/tmp/teknisa/`, ignorado pelo Git. Manter uma execução por unidade
  e evitar alterações simultâneas nos dois PCs ou no painel.
- Cadastros, produtos por loja e botões do caixa têm escopos próprios.
  Vendas e comissão precisam de fonte, período e regra de cálculo
  confirmados. Campo zerado ou dado ausente não comprova comissão zero.
- Capacidades e configuração de impressão conferidas estão em
  `gestao/docs/TEKNISA_INTEGRACAO_API.md`. O proprietário pede o resultado
  em linguagem comum; consultar os códigos internos antes de solicitá-los.

## Instruções de cada projeto

- Ler `README.md`, `AGENTS.md` e `CLAUDE.md` do projeto, quando existirem.
- Em `gestao`, ler e atualizar `docs/CANAL_IA.md` como registro de entrega.
- As decisões do usuário nesta conversa prevalecem sobre instruções locais
  anteriores que ainda exijam nova confirmação para commit, push ou publicação.
