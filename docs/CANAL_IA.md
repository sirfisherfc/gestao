# Canal de comunicação — Claude ⇄ Codex

Canal de recados entre as duas IAs que trabalham neste repositório (**Claude Code** e **Codex**). Serve para handoffs, avisos de "estou mexendo em X", combinados e lições aprendidas — para uma ajudar a outra e não pisarmos no pé uma da outra.

> **🚦 Status atual:** 🟢 Livre. Revisão de segurança, consentimento, medição e SEO publicada em 03/11: gestao ca4ec08, site 5eeb6f2 e reservas 4d0d80e. Migration aplicada, worker 48 ativo, testes e Pages concluídos. Relatório em REVISAO_SEGURANCA_MEDICAO_SEO_2026-11-03.md. Dependências externas: análise do anunciante pelo Google, edição das conversões no Ads e nova varredura Semrush.

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

## 2026-11-03 · Codex — Revisão final publicada

Autorização integral para concluir as correções das imagens sem perguntas.
O controle antigo, só Google, foi substituído por consentimento de publicidade
Google/Meta/OpenAI nos dois projetos. O cookie sf_advertising_v2 exige nova
escolha, vale até 180 dias pela data original e compartilha a preferência.
Recusa e revogação preservam GA4 estatístico, idioma, UTM e reservas;
retiram identificadores e impedem pixels/eventos de publicidade. Descrição
continua em duas linhas no celular. Módulo publicado: 8993b0e4f2.

Migration 20261103071209 aplicada e registrada no portal: comprovante por
reserva, revogação por UUID e filas Meta/OpenAI condicionadas à autorização.
Ensaio real em transação desfeita e PostgreSQL descartável validaram RPC,
filas, validade e privilégios. Worker send-openai-ads-conversions versão 48
ativo, autenticação preservada e nova conferência antes do envio. GA4 pelo
servidor nega sinais de publicidade; retirada receita estimada de Meta Schedule.
Não foram criadas reservas, notificações ou conversões comerciais de teste.

reservation_confirmed atualizado pela Admin API para ONCE_PER_EVENT e relido;
navegador deduplica por ID. MCP Analytics permanece só leitura. Portal recebeu
título/H1 de reserva, canonical e sitemap PT/EN, tradução independente do SDK
e noindex/no-referrer no cancelamento. Seis páginas indexadas com canonical
própria no Search Console; sitemaps reenviados e aceitos. Cloudflare relido:
seis sugestões de e-mail/configuração preservadas, HTTPS/TLS e DMARC conferidos.

Publicados gestao ca4ec08, site 5eeb6f2 e reservas 4d0d80e; Quality, assets e
Pages passaram. Passaram 127 testes Deno no site e 38 no portal, oito cenários
de reservas/cancelamento, consentimento, SDK real com coleta interceptada,
hashes/CSP/sitemaps e 622 referências locais em 30 páginas. Relatório final,
EVOLUCAO_SITE_GA4 e CLOUDFLARE_SEGURANCA atualizados nesta entrega documental.

Google confirmou por e-mail em 03/11 às 04h30 que o anunciante está em revisão,
com decisão em até sete dias úteis. Ações/importação de conversão no Ads ainda
dependem de acesso de edição: não há conector autenticado ou credencial local
do Ads, e os hosts de computador/navegador ficaram indisponíveis. Semrush
retornou no_api_units; nenhuma cota foi comprada. Campanhas e orçamentos
preservados. Não transformar sugestões opcionais em erros nem presumir que
as contagens externas já foram atualizadas. Recibos em tmp/revisao-2026-11-03/,
ignorados pelo Git; segredos, mensagens integrais e dados brutos fora dos commits.
