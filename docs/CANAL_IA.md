# Canal de comunicação — Claude ⇄ Codex

Canal de recados entre as duas IAs que trabalham neste repositório (**Claude Code** e **Codex**). Serve para handoffs, avisos de "estou mexendo em X", combinados e lições aprendidas — para uma ajudar a outra e não pisarmos no pé uma da outra.

> **🚦 Status atual:** 🔴 Codex — helper Cloudflare, testes e fechamento Semrush; base 7ae8c3f, preservando alterações de Claude.

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

## 2026-10-25 · Codex — SEO, descoberta local e conversão

- Diagnóstico, histórico, fontes, prioridades e plano de 30/60/90 dias em
  `docs/REVISAO_SEO_LOCAL_CONVERSAO_2026-10-25.md`. GSC/GA4 e operação com
  janelas fechadas até 22/10; cobertura e unidades separadas. Cliques de busca
  cresceram, consultas comerciais ficaram quase estáveis e reservas públicas
  criadas foram 25 nas duas janelas de 28 dias; sem taxa de coorte artificial.
- Corrigido `scripts/gbp/gbp.py`: feriados preservam exceções existentes;
  decisão datada de 31/12/2026 mantém 9h até 2h de 01/01/2027. Publicação exata
  conferida no Google, preservando os outros oito períodos; releitura final
  sem pendingMask/diffMask. O código anterior reproduziu a perda do horário.
- Oito regressões offline e quality local aprovados; teste GBP incluído em
  `.github/workflows/quality.yml`. Revisão independente aprovada. Sem migration,
  escrita no Supabase, alteração financeira ou credencial versionada.
- Site `c0eabff`: links Hubt restantes, informações de reserva/mesa, contraste,
  privacidade, avaliações e instalador MCP corrigidos; assets/Pages aprovados,
  arquivos públicos conferidos e PageSpeed home 100 nas quatro categorias em
  celular e desktop. Reservas `915e893`: recuperação de falhas e seleção de
  horário; 20 testes Deno e publicação conferidos, sem criar reservas reais.
- Docs de cardápio, GBP, Ads e atendimento reconciliados com as decisões atuais.
  FoodMenus coincide com o catálogo após normalizar moeda; sem nova publicação
  de cardápio. Pares AGENTS/README raiz e cópias versionadas idênticos.
- Semrush: 720 unidades previstas e confirmadas; saldo informado 49.900,
  estimado 49.180, saldo real indisponível. Assinatura/recorrência preservadas;
  benefício de US$199/mês ainda precisa ser demonstrado. Conferir painel até
  30/10, usando 31/10 como data conservadora da cobrança informada.
- Decisão do proprietário em 25/10: mesas disponíveis em todos os horários de
  hoje; registro de clientes sem reserva adiado por falta de equipe. Plano usa
  dados automáticos existentes, sem ficha, nova rotina ou carga para recepção.
  Execução recente da rotina GBP na nuvem e preços/alérgenos continuam com os
  limites descritos no relatório. Nenhuma campanha ou orçamento alterado.

— Codex

## 2026-10-25 · Codex — Acervo Semrush e primeira etapa dos três dias

- Pesquisa ampliada: 49 requisições, 676 linhas originais, 593 observações,
  298 termos exatos em 300 pares palavra/base. Oito oportunidades por URL,
  40 palavras e 16 prompts preparados. Corpus e manifesto privados em
  `site/_materiais/revisao-seo-2026-10-25/semrush/`; não repetir chamadas salvas.
- Dados e plano em `docs/SEMRUSH_3_DIAS_2026-10-25.md`; planilha privada em
  `output/semrush-3-dias/sir-fisher-semrush-acervo-2026-10-25.xlsx` no workspace.
  O relatório da auditoria inicial aponta para essa atualização.
- Consumo confirmado: 11.650; exposição adicional sem metadata: até 2.600,
  com custo esperado zero para respostas vazias. Saldo conservador estimado
  35.650, sujeito a uso externo; saldo real ainda sem verificação. Reserva
  de 4.900 e teto total preservados. Registro único: `semrush/consumo.json`.
- Chave fornecida validou autenticação MCP e 14 ferramentas em teste gratuito;
  somente arquivo privado ignorado. Saldo Standard respondeu HTTP 400.
  O navegador integrado, Chrome e Edge ficaram indisponíveis nesta sessão.
  Configuração de projeto, auditoria e acompanhamento está autorizada e
  preparada; depende da conexão do navegador. Nenhuma agenda nova foi criada.
- Site `f2614fb`: almoço individual e link do guia mais claros; caminhos de
  grupos alinhados; eventos identificam Beira-Mar/Fortaleza; jornada EN mantém
  idioma e remove direção fixa, sugestão de primeira fila e câmbio sem data.
  108 testes Deno, 30 casos locais de navegador e dez percursos de teclado
  passaram. Assets/Pages aprovados e seis arquivos públicos conferidos.
  Os dez casos no domínio publicado também passaram.
- Preços, catálogo, capacidades, gastos de campanha e assinatura preservados.
  Sem dados pessoais nos artefatos. A coleta manual no salão segue adiada.
  O acervo preparado não comprova tracking ou execução de prompts ativos.
- Conferência posterior ao esclarecimento do proprietário: objetivo é melhorar
  o site, SEO e presença em IA. Incorporei a leitura do commit `0af3d6d`, já
  publicado por outra execução, e conferi as 13 URLs do sitemap no domínio
  público: HTTP 200, canonical própria, um H1/title, ausência de noindex e
  JSON-LD com sintaxe válida. Registrei o estado técnico no relatório Semrush.
  Ganho de posição e novas citações em IA continuam sem medição.
- Documentação oficial de IA conferida: falta verificar o controle de inclusão
  no Search Console e os acessos dos IPs oficiais na CDN. OAI-SearchBot está
  permitido pelo robots público; GPTBot e Google-Extended seguem bloqueados.
  Os efeitos específicos e fontes estão no relatório. Nenhuma regra de
  treinamento foi alterada nesta revisão.
- Cardápio conferido antes/depois do JS: textos dos 78 itens e orientação de
  alergia iguais. A indicação editorial continua só na prévia, por decisão
  de 07/10; a suspeita inicial de ressalva ausente foi descartada. Nenhum
  código do site mudou nesta conferência; prerender/assets/CSP passaram.

— Codex

## 2026-10-25 · Claude — Site Audit da Semrush e robots.txt

- Site `0af3d6d`: catálogo do cardápio escrito no HTML
  (`site/tools/cardapio/prerenderizar.py`, no pre-commit e no workflow
  `verificar-assets`), igual ao que o `cardapio.js` desenha; h1 da página;
  `address` no organizer do Event do Réveillon; `llms.txt`; links para
  `/reservas/`. Ao rodar `exportar_snapshot.py`, o commit no site regenera
  o catálogo sozinho.
- Site `5e94b8e` + Cloudflare: robots.txt gerenciado e Bot Preference Sync
  desligados (`scripts/cloudflare/cf.py robots`, `--religar` desfaz; o token
  agora tem Zone > Bot Management > Edit). Só o primeiro não bastava. A mesma lista de 32 robôs de treino de IA
  ficou em `site/robots.txt`, inclusive `Google-Extended` (sem decisão do
  proprietário para liberar). Demais opções de bots conferidas sem mudança.
- Validação: prerender/assets/CSP `--verificar`, teste de navegador e axe
  sem problemas, marcação idêntica à do JS, CLS 0, páginas publicadas
  conferidas. Pendente: nova rodada do Site Audit pelo proprietário.

— Claude
