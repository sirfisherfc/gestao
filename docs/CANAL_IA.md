# Canal de comunicação — Claude ⇄ Codex

Canal de recados entre as duas IAs que trabalham neste repositório (**Claude Code** e **Codex**). Serve para handoffs, avisos de "estou mexendo em X", combinados e lições aprendidas — para uma ajudar a outra e não pisarmos no pé uma da outra.

> **🚦 Status atual:** 🟢 livre — levantamento Teknisa/Saipos concluído; migração do cardápio ainda não executada. Impresso Big Ben Fries continua pendente.

## Protocolo
- **Ao começar uma tarefa:** ler este arquivo. As mensagens mais recentes ficam **no fim**.
- **Linha 🚦 Status (topo):** ao **começar**, marque 🔴 + sua área/arquivos + commit-base; ao **terminar**, volte para 🟢 livre. É a resposta rápida para "posso mexer agora?". Se estiver 🔴 de outra IA sem sinal de conclusão, parar e confirmar com o Rogério.
- **Ao terminar / entregar:** acrescentar uma mensagem curta no fim, no formato `## AAAA-MM-DD · <autor> — <assunto>`, dizendo **o que mexeu**, **o que ficou pendente** e qualquer coisa que a outra precise saber. Handoff inclui: arquivos alterados · migration criada (nº) e se aplicou · validações rodadas · estado do deploy · pendências/riscos.
- **Mantenha o canal enxuto:** guarde só a linha 🚦 Status + os **últimos ~3 recados**; pode podar os mais antigos ao deixar um recado novo (o `git` preserva tudo — `git log`/`git diff` recuperam o histórico). O que for regra durável vai para o `AGENTS.md`, não fica aqui. Assim a leitura custa ~o mesmo sempre.
- Isto **não substitui** o `AGENTS.md` (regras canônicas) nem os commits — é o "recado rápido" entre nós.
- Combinados fixos já viraram regra no `AGENTS.md` (checar `ls supabase/migrations/` antes de criar migration; migrations idempotentes; uma IA por vez na mesma branch).

---

**PENDÊNCIA aberta:** migration `20260738000000_cartao_credito_entra_dre_temporario.sql` (2026-07-07) é declaradamente temporária — a fatura de cartão BTG entra na DRE só nas fontes vivas até existir uma fonte de ETL com as compras itemizadas do BTG; quando essa fonte existir, reverter `entra_dre` para a expressão de `20260735000000` (senão a despesa duplica). Ver detalhes no `git log`/na própria migration.

**PENDÊNCIA aberta:** os R$462 mil em despesa na categoria `ANALISAR INDIVIDUAL` (134 lançamentos, 2022–2025) precisam de classificação manual. A migration `20260748000000` (2026-07-14) deixou essa categoria dentro da DRE de propósito, com carve-out explícito, por não haver confirmação de que sejam não-operacionais. Boa parte é Pix para "SIR FISHER COMERCIO DE ALIMENTOS LTDA" e para os sócios; vale investigar se são retirada/pró-labore, empréstimo entre empresas do grupo, ou despesa real mal categorizada.

## 2026-10-25 · Codex — Fechamento SEO/IA, painel e acervo portátil (snapshot anterior)

- Resultado atual, sete pontos pedidos, reformulação, histórico, fontes e
  checklist 26/27 em `docs/SEMRUSH_3_DIAS_2026-10-25.md`. Sem tarefa manual
  para proprietário/recepção e sem novo agendamento no Codex.
- Site `5918c99` e `2b04523`: links de almoço/cardápio, rota conforme origem,
  pets e caminhos de grupos/eventos publicados, HTTP 200 e HTML conferido.
  Nova auditoria real: Site Health 96, AI Search Health 99, zero erros e
  vinte avisos. Métricas Semrush e CrUX mantidas com suas definições.
- GSC: inclusão IA padrão confirmada no domínio; 2.672 impressões históricas
  no recorte Web com base em texto, 77 dias. As 13 linhas de páginas têm outra
  agregação e não correspondem às 13 URLs do sitemap. `/eventos/` recebeu
  Indexação solicitada. O envio de `/reservas/` do www falhou duas vezes na
  conexão ao reCAPTCHA; permanece pendente, sem contorno ou mudança no portal.
- Google/Fortaleza/mobile/PT: 40 termos coletados, visibilidade 13,97%, oito
  Top 10 e cinco Top 3, única data 25/10. Original Brasil preservado e cópia
  identificada. ChatGPT/Fortaleza/PT: 12 prompts, três diretos e nove genéricos;
  nove Mentioned (três diretos e seis genéricos), três Missed genéricos.
  Os scores 74,33% e 68,84% da mesma tela foram preservados como divergência.
- Backups API e UI, CSVs nativos/derivados e relatório no ZIP privado
  `output/semrush-3-dias/sir-fisher-acervo-completo-2026-10-25.zip`, na raiz do
  workspace. Hash e validações no sidecar `.verificacao.json`. API histórica
  preservada com 78 relatórios; ledger atual com 79 e 21.070 unidades
  confirmadas. UI confirmou saldo 28.830, reserva 4.900 e espaço 23.930 no
  teto autorizado. A reserva histórica 2.900 sem metadata não virou débito
  individual por chamada. Assinatura/recorrência só lidas: 31/10, US$199, ativa.
- Duas alterações externas de `site/robots.txt` e `tools/analytics/README.md`
  foram preservadas sem publicação por esta rodada. A origem da autorização
  do toggle Google-Extended não foi confirmada. Público às 04:40 mantinha
  Googlebot/OAI-SearchBot permitidos e GPTBot/Google-Extended bloqueados.
- Helper/testes no histórico `8be6a3a`/`62975fc`, com onze regressões offline,
  oito GBP, quality e CI/Pages aprovados. Este fechamento altera só documentos;
  sem migration, escrita no banco, alteração financeira ou credencial versionada.
  Pares de orientações da raiz e cópias versionadas conferidos idênticos.

— Codex

## 2026-10-25 · Codex — Rodada adicional, cardápio Google e alvo EN

- Documentei a atribuição em `docs/ROTINA_PERFIL_GOOGLE.md` e acrescentei
  adendo em `docs/SEMRUSH_3_DIAS_2026-10-25.md`. O ZIP anterior conserva
  os mesmos bytes/hash. Sem migration ou alteração financeira.
- Google-Extended `bafeeaf` e site `7c2b72c` publicados e conferidos no
  domínio. O segundo preserva regras e esclarece grupos/eventos e posição
  de mesa. Passaram 108 Deno, quatro verificadores e quatro casos de navegador.
- Fechamento posterior: site `475e9b2` documenta o estado EN/CF e `78cd544`
  corrige horário/feriados do executivo na página EN fish. CI e Pages passaram;
  reservas, eventos e EN fish responderam HTTP 200 com HTML igual ao local.
  Relatório e ZIP anteriores preservados.
- GBP: um PATCH somente em `url_menu` acrescentou UTM `gbp_menu`; leitura
  real às 05:41 confirmou o destino. Outros 60 atributos, ficha e FoodMenus
  iguais. HTTP 200 e canonical limpa. Recibo agregado em
  `output/seo-rodada-adicional-2026-10-25/gbp-url-menu-recibo.json`, fora do Git.
- ChatGPT/Fortaleza/English: `31731868_5693988`, quatro prompts coletados,
  quatro Mentioned (três genéricos e um de marca). Linha de base de 25/10;
  percentuais divergentes da consolidação não viraram taxa de mercado.
  Export nativo bloqueado pelo Trial; snapshots e CSV derivado preservados.
- On Page Checker: causa do 403 identificada na regra Block AI bots on ad
  pages. Exceção restrita publicada e relida Active na UI, Skip de todas as
  regras `http_request_sbfm` só no conjunto definido, com
  logs. Evento real `skip` às 05:53:47 e recoleta EN fish comprovaram acesso;
  o relatório passou a cinco ideias, sem 403. Bot Management/robots iguais.
  A prova cobre essa página; detalhes, recibos e rollback no adendo.
- Quality estático e diffcheck passaram; pares de orientação da raiz idênticos.
  Sem API Standard paga nova, nova rotina, upgrade ou mudança de recorrência.
  A coleta manual de clientes sem reserva continua adiada pelo usuário.

— Codex

## 2026-10-25 · Codex — Instagram analytics e continuidade das reservas

- `scripts/instagram_analytics/`: cliente Meta v26.0, MCP stdio com sete
  ferramentas fixas de leitura e coletor com cache/paginacao limitados.
  Reaproveita `META_IG_TOKEN` pelo loader do GBP; nenhum segredo/config MCP
  local ou dado bruto versionado. Guia em `docs/INTEGRACAO_INSTAGRAM_ANALYTICS.md`.
- Conta @sirfisherfc e SYSTEM_USER validos comprovados por API; identidade,
  publicacoes, nove metricas da conta, insights de posts e Stories lidos.
  Codex, Claude Code, Qwen e Antigravity CLI executaram identidade com
  refresh=true, duas leituras HTTP e cache=false. GUI configurada, sem
  reiniciar tarefa ativa; validacao propria em nova sessao ainda pendente.
- 23/09–22/10: Instagram em 17 das 28 reservas publicas criadas (60,7%).
  Origem de bio/perfil permite medir canal, sem atribuir post especifico.
  Credito Meta Ads indisponivel: os edges de contas retornaram listas vazias;
  nao inferir zero Schedule, ausencia de anuncios ou causa do acesso.
- Site `5988034` e reservas `f92378d`/`bf2f08d` publicados: TTL90 dias nas
  duas copias; telefone internacional/data Meta corrigidos; IDs preservados.
  Funcao send-openai-ads-conversions v22 ACTIVE, autenticacao igual e tres
  modulos remotos iguais aos revisados. Sem SQL, worker/testevents em producao
  ou escrita no Instagram. Valor legado Meta continua estimativa separada.
- Validacoes locais: 20 testes do cliente, oito de seguranca independentes,
  sete handlers SDK, 113 Deno/site e 32 Deno/reservas. Artefatos agregados,
  recibos dos clientes e fontes em output/instagram-analytics-2026-10-25/ na
  raiz. Sem nova consulta Semrush, cobranca, app Meta ou agendamento.

— Codex

## 2026-10-25 · Codex — Nova decisão sobre robôs de IA

- O usuário autorizou liberar os 31 agentes restantes no conteúdo público
  do `www`, incluindo GPTBot, ClaudeBot e CCBot. O grupo anterior veio da
  Cloudflare. Coleta para treino pode ocorrer; menções e posições exigem
  observação própria.
- Site `84cbb26` com robots publicado, CI/Pages aprovados e bytes públicos
  iguais ao Git. Diretivas permitiram 40 nomes em três caminhos; GETs usaram
  SirFisher-Audit, sem prova de visita autêntica dos provedores.
- Cloudflare: regra `7af7f90de3944407842037ebdd674f5d` relida Active, ordem 2,
  com host www, GET/HEAD, 15 caminhos e os 31 textos de user-agent. Skip só
  `http_request_sbfm`, logs ligados; custom/rate/Managed WAF/autenticação e
  outros hosts preservados. Regra SI e Bot Management globais ficaram iguais.
  Ao publicar novas rotas, revisar a exceção. Recibos e rollback no adendo.
- Adendo atualizado em `docs/SEMRUSH_3_DIAS_2026-10-25.md`; históricos e ZIPs
  congelados preservados. Quality estático e diffcheck passaram. Esta tarefa
  altera somente os dois documentos; root executa site e Cloudflare.

— Codex

## 2026-10-25 · Claude — Big Ben Fries com 250 g

- Decisão do proprietário: Big Ben Fries tem 250 g, como a Macaxeira Frita
  ou Batata Frita (TXT, HTML antigo e impresso diziam 200 g).
- `scripts/cardapio/catalogo_inicial.py` (com nota) → JSON → snapshot do
  site (`dcfb37f`; o pre-commit regenerou o catálogo pré-renderizado).
- Migration `20261025170000_cardapio_big_ben_250g.sql` aplicada por
  `aplicar_migrations_pendentes.py` (só ela pendente; 223 versões); banco
  relido com 250 g. Não há publicação ativa em `cardapio_publico`.
- Google: `gbp.py cardapio --publicar` relido; lá o item não leva porção.
- Pendente: impresso no Canva (mesa `DAHYx8a8mAI` e A3 da entrada) ainda
  com 200 g; sem conector do Canva nesta sessão.

— Claude

## 2026-10-25 · Codex — Extração adicional, hóspedes e plano Google Search

- Novos documentos: `docs/SEMRUSH_MAXIMO_2026-10-25.md` e
  `docs/PLANO_GOOGLE_SEARCH_2026-10-25.md`. Históricos e ZIPs anteriores
  preservados. Esta entrega em gestão altera só os dois documentos e o canal.
- Site `de2f863`: alergênicos compactos com nomes acessíveis/ficha/legenda
  PT/EN e seção de hóspedes no guia existente. Passaram 113 Deno, quatro
  verificadores e 47 verificações de aceitação no navegador; CI/Pages
  concluídos e 14 GETs públicos HTTP 200 com conteúdo igual ao commit.
- A medição da seção usa página do guia + click_menu/maps/reservation +
  `cta_position=conteudo`; quatro links exclusivos dessa combinação nesta
  versão. Botões finais usam `visita`. Sem evento novo, UTM interna ou
  mudança do contrato de reservas; resultados dependem da cobertura dos IDs.
- API: cinco relatórios, duas respostas com dados e três no_data finais;
  2.160 unidades confirmadas. A reserva de 1.800 protegeu a exposição de
  3.960 antes da releitura. UI confirmou saldo 26.400 desde 28.560, diferença
  igual ao consumo. Reserva protegida de 4.900 preservada. Illa e NOM são do
  mesmo grupo; fontes/links compartilhados não são endossos independentes.
- Maps Free: uma palavra, grade inicial com 25 pontos e segundo recorte com
  14 terrestres após remover onze sobre água; onze créditos restantes.
  Avg. Rank 14,2/16,5 e SoV 2,6%/2,79% pertencem a geometrias diferentes;
  a comparação não mede evolução de SEO. Centro em posição 1 não representa
  Fortaleza inteira. Sem Basic/Local Pro ou alteração da ficha Google.
- IA: Brasil/todas as plataformas, referência 24/10, com 25 temas, 66 registros
  de prompts e 109 domínios de fontes guardados. Prompt Research tem quinze
  respostas com pergunta/plataforma/cabeçalho conferidos, de 15/09–19/10.
  A menção ao Sir Fisher para primeira visita/hóspedes já aparece em resposta
  ChatGPT de 14/10; antecede as mudanças de hoje. Cortesias antigas de terceiros
  não viraram oferta. Capturas sem validação ficaram fora dos resumos.
- Dados e pacote privado em `output/semrush-maximo-2026-10-25/`, na raiz.
  Dois CSVs nativos de palavra do Maps preservados; exportações de IA falharam e
  foram substituídas por DOM/derivados identificados. PDF do Maps não gerado,
  pois o aceite de privacidade solicitado não foi dado.
- Scanner local: alerta 36/38, com doze diretórios visíveis e expansão falha;
  três avisos de telefone exibiam os mesmos dígitos oficiais. Instagram já
  validado também foi marcado ausente. Sem erro cadastral confirmado,
  alteração do perfil, trial de sincronização ou sincronização de diretórios.
- Plano Search contém grupos, palavras, negativas qualificadas, textos nos
  limites e medição. Objetivo, economia, teto e configuração da conta ainda
  precisam de revisão antes de lançar. Sem anúncio, novo orçamento, contato
  com terceiros ou coleta manual de salão. Sem SQL ou alteração financeira.
- Quality estático, limites dos textos, links relativos, codificação e
  diffcheck conferidos; pares de orientação da raiz idênticos.

— Codex

## 2026-10-25 · Codex — Consulta de vendas do bolinho de calabresa

- Consulta somente de leitura na API Saipos, loja conferida. O usuário
  esclareceu que queria o Bolinho Calabresa e Alho Poró (item 15125411).
- Últimas 15 porções conferidas por horário de lançamento, em ordem
  decrescente; cada registro tem quantidade 1, pagamento e fechamento.
  Itens excluídos, vendas canceladas e cópias de transferência foram filtrados.
- Resultado entregue na conversa. Consultas e recibos privados ficaram em
  `tmp/` na raiz, fora dos repositórios. Sem importação ou escrita no banco.
- Três repositórios conferidos em `main`, sem divergência após pull;
  pares de orientação da raiz idênticos. Só este registro foi alterado.

— Codex

## 2026-10-25 · Codex — Ícones originais do cardápio

- Site `8efb640`: dez PNGs fornecidos pelo usuário copiados intactos, com
  cores originais e nomes com hash. O recorte ocorre apenas na exibição.
  Ícones de 24 px nos cards/detalhes e 32 px na legenda; fundo claro circular
  mantém a leitura no tema escuro, sem filtros ou recoloração.
- Nomes acessíveis, ficha e legenda PT/EN preservados, com 78 cards e 61
  ícones. Declarações culinárias, preços, porções e JSON-LD ficaram iguais.
- Passaram 113 Deno, quatro verificadores e 47 critérios no navegador, em
  celular 375/390 px e desktop 1525 px. Assets/Pages concluídos; 28 GETs
  públicos retornaram 200. Os PNGs publicados são idênticos às fontes;
  HTML/CSS/JS conferem com o commit após normalizar quebras de linha.
- Recibos privados em `output/alergenos-originais-2026-10-25/`, na raiz.
  Gestão altera só este canal, com quality/diffcheck e pares raiz conferidos;
  sem relatório novo ou alteração do banco. Históricos preservados.

— Codex

## 2026-10-25 · Codex — Logo oficial no topo do cardápio

- Site `eb28af2`: HTML e CSS usam o logo-emblem WebP oficial das homes,
  exibido em 40×43 px. A imagem fornece o nome acessível; o texto visual
  repetido fica oculto do leitor de tela. Até 360 px, o bloco da marca mostra
  só o logo para dar espaço aos controles; as categorias permanecem nas abas.
- Passaram 47 verificações de aceitação e quatro verificadores, com PT/EN
  em 320/390 px e desktop, sem overflow. Assets e Pages concluídos.
  Oito GETs públicos retornaram 200 e HTML/CSS/logos conferem com o Git.
- Recibo privado em `output/logo-cardapio-2026-10-25/publicacao.json`.
  Gestão altera só este canal, com quality/diffcheck e pares raiz conferidos.
  Históricos preservados.

— Codex

## 2026-10-26 · Codex — Teknisa e referência ativa do Saipos

- Levantamento em `docs/TEKNISA_MIGRACAO_CARDAPIO.md`: módulos e telas
  vistos no Teknisa, unidade 0002, grupos de CAIXA/POS e tabela 001 com
  114 códigos. Recursos de menu, campos lidos e ações propostas estão
  separados. Nenhum cadastro, configuração ou preço foi alterado.
- Saipos: 12 grupos ativos, 107 IDs únicos, 57 produtos com opções,
  121 vínculos e 20 conjuntos com 82 opções. Definições globais foram
  relacionadas por IDs, nomes e preços das opções; limites e impressão
  registrados. Máximos 111 de Rum/Martini exigem revisão na migração.
- O usuário reafirmou as retiradas de Crispy, Marine, Smirnoff Ice e
  Cachaças Premium. A seleção local tem 103 IDs, 54 produtos com opções,
  118 vínculos e 19 conjuntos com 78 opções. Leitura original preservada;
  nenhuma alteração no Saipos. O limite 222 de Premium ficou fora da seleção.
- Comparação dos 103 com a tabela lida: 65 preços iguais, nove estruturas
  ou correspondências para conferir e 29 sem correspondência direta nessa
  tabela. Caipirinha Ypioca, Caipiroska Sky/Absolut e Gin Nacional/Gordon’s
  têm diferenças documentadas. Executivos e opcionais estão preparados
  para conferência dos vínculos e posterior gravação no Teknisa.
- Artefatos e evidências locais em `output/teknisa-2026-10-26/`, na raiz,
  fora do Git. Contagens, IDs, grupos ativos e cruzamento das definições
  conferidos; quality estático e diffcheck passaram. Apenas os dois
  documentos de gestão foram alterados; sem migration ou deploy de produto.

— Codex
