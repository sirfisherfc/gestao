# Canal de comunicação — Claude ⇄ Codex

Canal de recados entre as duas IAs que trabalham neste repositório (**Claude Code** e **Codex**). Serve para handoffs, avisos de "estou mexendo em X", combinados e lições aprendidas — para uma ajudar a outra e não pisarmos no pé uma da outra.

> **🚦 Status atual:** 🟢 Livre. Arquivo Semrush de 03/11 lido: 262 linhas detalhadas, controle completo em docs/seo/SEMRUSH_IDEIAS_2026-11-03.md e JSON. Melhorias pertinentes em cinco páginas publicadas no site 078652a. Nomes de concorrentes preservados para pesquisa. Pendentes sete redistribuições e nova coleta no Semrush, além de links de terceiros; não declarar 43/43 aplicadas. Ads segue com o acesso limitado registrado na entrega anterior.

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

## 2026-11-03 · Codex — Anunciante aprovado e serviços relidos

Proprietário informou aprovação e pediu conferir o restante. E-mail do Google
das 08h07 confirma conta 149-377-8788 verificada e todas as tarefas obrigatórias
concluídas; metadados com DKIM/SPF/DMARC válidos. O estado anterior em revisão
foi substituído. Vínculo Ads/GA4 e ONCE_PER_EVENT relidos; coleta recente presente.

Sitemaps processados, isPending=false e zero erros/avisos nos dois hosts.
Worker 48 ACTIVE e migration 20261103071209 presente. Consulta agregada somente
de leitura encontrou, desde as 05h00 até a releitura das 18h12, três visitas GA4,
quatro schedules Meta e quatro OpenAI enviados, sem erro registrado, e zero
evento publicitário ativo/enviado sem autorização válida. Contagens por provedor
podem corresponder às mesmas reservas. Leitor segue restrito a service_role;
nenhum privilégio foi ampliado para contornar a recusa à chamada da função.

Cloudflare retornou os mesmos seis insights e configurações HTTPS/TLS. Três
hosts com HTTP 200 sob identificação de navegador; módulos com hash 8993b0e4f2
nos dois hosts. Identificação Python recebe 403/1010 com browser_check ligado.
Pages e assets anteriores concluídos com sucesso. Sem mudança de produto,
reserva, fila, migração, credencial ou campanha nesta releitura.

Semrush continua no_api_units. O host de computador/navegador segue indisponível,
e não há conector de edição Google Ads autenticado nesta sessão. A aprovação
está concluída; conferir/importar ações de conversão no Ads segue dependendo
desse acesso. Atualizados este canal, EVOLUCAO_SITE_GA4 e relatório final.
Bases locais conferidas: gestao bea5d03, site 5eeb6f2 e reservas 4d0d80e.
Recibos agregados em tmp/revisao-2026-11-03/, ignorados pelo Git.

## 2026-11-03 · Codex — Arquivo completo de ideias Semrush e projeção

Proprietário pediu conferir todas as ideias e baixou
ideas_www.sirfisher.com.br_20261103.xlsx. Aba SEO Ideas A1:D263: cabeçalho e
262 linhas detalhadas por página/palavra/ideia; painel mostra 43 grupos.
Fonte preservada em Downloads. Controle JSON cobre todas as linhas 2–263,
com SHA-256, categoria, contexto, decisão e evidência. Relatório em docs/seo.

Usuário esclareceu que imaginava keywords escondidas no código. Explicado:
keywords do Semrush configuram pesquisa/acompanhamento; Google ignora meta
keywords. Nomes de concorrentes podem ser monitorados e usados em comparação
factual, inclusive num H1 desse assunto. Não houve exclusão de palavras na
ferramenta nem inclusão automática de nomes no H1 da home. Preservar essa
distinção; a conversa não proíbe pesquisa de concorrência.

Documentação Semrush define o potencial como primeira posição para todas as
palavras. Imagem: 13,1 mil → 56,5 mil significa +331,3%; +1000% significaria
144,1 mil. Motivo da divergência não foi demonstrado pela fonte. Não usar
esse percentual como previsão de clientes. Usuário pediu só o que fizer sentido.

Site 078652a: títulos/H1/descrições com localização e intenção, rota do almoço,
atalhos do guia, duas versões do prato com fichas EN e método solar em parágrafos.
Lastmod atualizado só nas cinco páginas alteradas. Guia de Analytics atualizado.
Passaram 42 testes de CTA, dez cenários de navegador e quatro releituras após
ajuste visual; duas fichas EN, JSON-LD/XML, assets/CSP, cardápio e 626 referências
locais sem destino ausente. Coleta externa de teste interceptada.

Sete redistribuições na ferramenta e nova coleta continuam sem acesso;
Semrush sem cota e host autenticado indisponível. Links de terceiros exigem
publicação editorial. Estrelas do próprio negócio não aplicadas conforme Google.
Portal preservado com função de reserva e idioma EN preservado. Sem migration,
mudança de banco, anúncio, orçamento ou credencial. Bases gestao e0e8715,
site 5eeb6f2 e reservas 4d0d80e. Recibos em tmp/revisao-2026-11-03/, ignorados.

Pages e assets do site concluídos; cinco URLs públicas com HTTP 200 e texto
esperado. Sitemap www reenviado às 18h50 (204, nova coleta pendente, sem erros).

## 2026-11-03 · Claude Code — Grupo Garçom Sênior no Teknisa

Criado `05 — GARCOM SENIOR` (cópia do 04, com retirar taxa de serviço,
desconto, cancelar item e suprimento liberados; sangria bloqueada), supervisionado pelo 02. Um garçom foi
movido do 04 para o 05; releitura sem divergências. Detalhes e teste
pendente no POS em `docs/TEKNISA_ACESSOS_OPERACAO.md`. Feito pela interface;
a ferramenta `teknisa.mjs` não tem comando para grupos (Node ausente neste PC).
