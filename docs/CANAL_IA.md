# Canal de comunicação — Claude ⇄ Codex

Canal de recados entre as duas IAs que trabalham neste repositório (**Claude Code** e **Codex**). Serve para handoffs, avisos de "estou mexendo em X", combinados e lições aprendidas — para uma ajudar a outra e não pisarmos no pé uma da outra.

> **🚦 Status atual:** 🔴 Codex revisa segurança Cloudflare, consentimento/medição e SEO das imagens, com autorização integral de 03/11 para concluir sem perguntas. Bases gestao f119786, site 6ae7998 e reservas df3962d, limpas e atualizadas. Uma IA nos três projetos. API Semrush sem unidades; computador/navegador sem conexão. Preservar operações e registrar limites reais.

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

## 2026-11-03 · Codex — Vínculo Google Ads/GA4 concluído

Proprietário confirmou Administrador no Ads. Fluxo pela Central de dados
encontrou Sir Fisher — Site Oficial 353205396; antes ele havia aberto o
painel da Tag do Google. Causa do seletor vazio no Analytics sem confirmação.
Após esclarecer que públicos são opcionais e podem apoiar remarketing,
o proprietário criou o vínculo e a tela mostrou Vinculado.

API confirmou um link com cliente 1493778788, recurso 16259936791,
personalização ativa e can_manage_clients=false, criado em 03/11 às 05:34:24Z
(02:34 Fortaleza). Importar métricas estava ativo na prévia; endpoint não
expõe esse botão. API também confirmou um fluxo Web no www e os mesmos
seis eventos principais; reservation_confirmed por sessão. Firebase é
alternativa do fluxo de conexão; a propriedade do site está vinculada.

Atualizados este canal e EVOLUCAO_SITE_GA4. Aprovação do anunciante ainda
sem confirmação. Conferir codificação automática e ações de conversão
existentes antes de importar reservas. Nenhuma campanha, orçamento, papel
ou evento alterado pelas ferramentas; vínculo criado manualmente pelo
proprietário. Sem código de produto, migration ou credencial versionada.

## 2026-11-03 · Codex — Tag Ads e janela de escolha publicadas

Pedido confirmado: janela pequena só para os novos cookies de publicidade
Google; recusar preserva os cookies anteriores. Site e portal usam o mesmo
módulo, hash 3ca950b5fc, com três sinais de publicidade negados até aceitar.
Preferência de 180 dias entre subdomínios, alteração pelo rodapé e PT/EN.
Recusar/revogar remove somente _gcl_*. Preservar GA4/Meta/atribuição anteriores
não comprova a base legal dessas coletas; o controle é específico do Google.

Tag AW-10856025003 reutiliza o SDK existente. Eventos do restaurante seguem
para GA4, sem criar conversão Ads ou enviar contatos. URLs Ads sem parâmetros
e conversões otimizadas desligadas. Cancelamento privado sem Ads/Meta e GA4
com URL sem parâmetros. Aviso de privacidade e guias dos dois projetos atualizados.

Publicado site 3bfb6b8 + ff07526 (ordem do guia) e reservas aeff2b0; Pages e
assets passaram. HTTP 200 e módulo com hash esperado nos dois domínios.
Visita isolada confirmou config Ads única, recusa e ausência de _gcl_*;
coleta de teste interceptada, sem conversão ou reserva real. Não foi relido
o aviso da Central de dados para confirmar seu desaparecimento.

Passaram 126 testes Deno do site, 30 do portal, teste de consentimento em
navegador, oito cenários de reservas/cancelamento e SDK real em quatro páginas.
Sintaxe, hashes, CSP, cardápio e diff também conferidos. Sem migration ou
mudança de banco. Documentação da entrega em EVOLUCAO_SITE_GA4_2026-11-02.md.
Continuam pendentes aprovação do anunciante, codificação automática e revisão
das ações de conversão antes de importar reservas. Campanhas/orçamentos intactos.

## 2026-11-03 · Codex — Texto do aviso em duas linhas no celular

Encurtadas somente as descrições PT/EN de assets/js/google-ads.js no site e
portal. Texto PT: “Permitir cookies para medir e personalizar anúncios? Os
demais seguem ativos.” Fonte de 13 px, título, botões e consentimento preservados.
Novo hash b25d5c1153 nas 14 páginas do site e nas duas páginas públicas do portal;
CSP regenerada no site. Commits publicados: site 6ae7998 e reservas df3962d.

Navegador confirmou exatamente duas linhas e ausência de rolagem horizontal
em 16 combinações: 320/360/390/430 px, site/portal e PT/EN. Imagem de 360 px
conferida; nenhum serviço externo recebeu dados do teste. Sintaxe, assets,
CSP e diff passaram. Pages dos dois repositórios e CI de assets concluídos;
HTTP 200 e módulo com hash esperado nos dois domínios. Sem mudança de banco
ou migration. Nenhum segredo, dado bruto ou arquivo de teste local versionado.
