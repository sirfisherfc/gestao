# Canal de comunicação — Claude ⇄ Codex

Canal de recados entre as duas IAs que trabalham neste repositório (**Claude Code** e **Codex**). Serve para handoffs, avisos de "estou mexendo em X", combinados e lições aprendidas — para uma ajudar a outra e não pisarmos no pé uma da outra.

> **🚦 Status atual:** 🟢 Livre. ChatGPT Ads conferido por MCP em 12/11 à tarde: campanha nova ativa/elegível, quatro peças aprovadas, sem bloqueio explícito; entrega ainda não comprovada e relatório de hoje incompleto. Recomendada conferência manual em 13/11 após completar 24h; revisões de 14/11, 18/11 e 26/11 mantidas. Ver `docs/CAMPANHA_CHATGPT_ADS_2026-11-11.md`.

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

## 2026-11-10 · Claude — ChatGPT Ads: ajuste autorizado aplicado

Proprietário aprovou a recomendação A. Pela interface do Ads Manager: grupo
com lance máximo de R$3,50 para R$5,00 e os cinco contextos de outubro
(reescritos sem vírgulas internas; fatos conferidos), às 15h44; campanha com
Reserva confirmada e Visita realizada e término de 16/11 para 18/11 às 00h,
às 15h49. O histórico mostra só esses campos. R$300, 14 setores, peça e
destino iguais. Aviso de lance baixo sumiu; entrega ainda não comprovada.
Pendente: conferir em 11/11 a partir das 15h45; sem impressões, pausar e
encerrar sem novo aumento. Recibo em `tmp/chatgpt-ads/ajuste-2026-11-10.json`.

## 2026-11-11 · Claude — Contador de aceite e sinal VisitaQR

Site `bd4b39b` e reservas `8b76ae1`: `google-ads.js` (idêntico) envia ao GA4
`publicidade_aviso_exibido`, `publicidade_aceita` e `publicidade_recusada`;
`atribuicao.js` envia `VisitaQR` ao pixel da Meta para origem `qr_code` com
permissão. Privacidade atualizada (11/11). Testes e produção conferidos.
Pendente: criar na Meta o público `VisitaQR` e o semelhante (navegador
desconectado; passos em `docs/PUBLICOS_PUBLICIDADE_2026-11-11.md`). Google:
públicos QR e de reserva já existem no GA4; falta campanha e a verificação
do anunciante. Portal: versão `?v=` do script é atualizada à mão.

Atualização 10h: na conta de anúncios do Portfólio Sir Fisher (não a
pessoal), criados o público de engajamento do Instagram (365 dias) e o
semelhante 1%. O público `VisitaQR` espera o primeiro evento no pixel.
Chrome: quedas ligadas a ociosidade e à economia de memória ligada; ver
`docs/PUBLICOS_PUBLICIDADE_2026-11-11.md` e a seção abaixo do documento.

**ChatGPT Ads, 11/11 10h40:** ainda zero impressões 19 h após lance R$5;
sem aviso de lance. Causa provável: CEPs sem público elegível. ChatGPT
orgânico trouxe 74 sessões desde 01/11, 76% de fora do Ceará. Decisão de
encerrar ou reformular com o proprietário; detalhes na análise de 10/11.

**Aviso financeiro:** em 11/11 o proprietário assinou o Meta Verified para
empresas, plano Básico recomendado (R$43,09/mês). Nova cobrança recorrente
da Meta no cartão a partir de novembro, categoria de marketing; não é
verba de anúncio. Confirmar o plano pela primeira fatura.

## 2026-11-11 · Codex — Campanha ChatGPT Ads: roteiros e refeições

Pedido delegado de 11/11 executado pelo conector. Campanha “Sir Fisher | Roteiros
e refeições | Novembro 2026”: dois grupos, quatro anúncios, todos criados
pausados, aprovados pela OpenAI e só depois ativados. Teste R$300 por CEP
pausado antes; outras campanhas e conta preservadas. Brasil, todas as
plataformas, CPC desejado R$3, R$300 totais de 12/11 00h a 26/11 00h
(America/Fortaleza). Metas Reserva confirmada e Visita realizada associadas;
aprimoramento criativo desligado conferido na interface, cancelada sem salvar.

Relatório `docs/CAMPANHA_CHATGPT_ADS_2026-11-11.md`: Ads, GA4, Search Console e
portal atualizados; nenhum registro de reserva com UTM ChatGPT desde outubro.
GA4 atual: 67 sessões orgânicas por origem e 36 visualizações (30 entradas) em
/reveillon/; não repetir os 74/36 como sessões. Venda de Réveillon aberta,
mas medição do módulo desligada e pacote com álcool: ficou fora desta rodada.
Fotos oficiais de peixe e pôr do sol sem edição; destinos/imagens HTTP 200.
Sem fonte validada de ociosidade por hora. Sem código, banco ou migration.

Teto agregado novo do proprietário: **R$500 em novembro**, prevalece sobre
R$1.000 histórico. Nova verba R$300; R$200 não liberados, inclusive para atraso
de métricas. Relatório Ads cobre até 10/11; parcial de 11/11 sem linhas não foi
tratado como zero medido. Conferências manuais 14/11 e 18/11 às 18h, fim 26/11
às 10h. Pausa autorizada com >=R$100 e >=30 cliques sem rota, contato ou início
de reserva. **Sem automação/alerta recorrente.** Pacing não garante saldo até o
fim dos 14 dias. Recibos privados em `tmp/chatgpt-ads/`, ignorados pelo Git.

Validações: leituras independentes dos sete objetos ativos e quatro aprovações;
único impedimento atual é início futuro. Fotos inspecionadas e upload aceito;
validador empacotado indisponível por dependência, verificação independente
registrada. Entrega real deve ser conferida após 12/11. Três repositórios e
pares de orientações da raiz conferidos; só relatório e CANAL_IA versionados.

## 2026-11-12 · Codex — Consulta de reserva de Réveillon ausente

Diagnóstico somente de leitura no projeto `portal`, com a credencial local
verificada e a rota Management API `database/query/read-only`. Conferidos
cadastro, histórico, pagamentos, estado público da mesa e reservas concorrentes.
O caso consultado expirou automaticamente após o prazo de 48 horas, sem
pagamento registrado; o filtro Ativas explica a ausência na lista. A mesa
estava livre no instante da consulta. Comprovante encaminhado pelo WhatsApp
não equivale a lançamento no portal. Dados pessoais e valores não versionados.

Sem alteração de código, schema, pagamentos ou status; nenhuma migration ou
publicação de interface necessária. Regularização exige conferência do crédito
e recuperação da reserva antes do lançamento, pois a RPC de pagamento recusa
reservas expiradas. Não criada outra reserva nem presumida quitação.
Orientações da raiz idênticas às cópias versionadas. Três repositórios
conferidos e atualizados; `git pull` de gestão informou avisos de permissão
na limpeza automática de metadados de worktrees antigas, sem divergência
ou impedimento à sincronização.

**Atualização após autorização de resgate:** o proprietário confirmou o crédito
e pediu recuperar a reserva. Operação pontual aplicada pela rota de escrita
Management API no `portal`, preservando UUID, código, mesa, dados e preços
originais. Travas do evento, mesa e reserva, conferência de disponibilidade,
ausência de pagamentos anteriores e verificações do estado esperado impediram
colisão ou duplicidade. Reativação e lançamento do sinal confirmado ocorreram
na mesma transação, com histórico e recálculo pela função existente. Horário
bancário não informado: a observação do pagamento distingue a data do registro.

Ensaio transacional com ROLLBACK passou antes da aplicação; leitura independente
após COMMIT confirmou sinal pago, mesa reservada, uma única reserva ativa,
um único pagamento e saldo calculado. Recibos e script pontual em
`tmp/reveillon/`, ignorados; sem dados pessoais ou valores no Git. Sem mudança
estrutural ou de interface, nenhuma migration nem deploy necessário.

## 2026-11-12 · Codex — PDF único após o sinal do Réveillon

Pedido confirmado: um único arquivo completo para o proprietário encaminhar
pelo WhatsApp após registrar o sinal, com botão na ficha; sem envio automático.
Portal `08f4b3a`: botão **Baixar PDF completo**, modelo com identidade dos eventos,
mesa/pessoas, data/endereço/horários, valores da reserva, pagamentos por forma,
saldo/vencimento/Pix, consumação, inclusos/programação e regras integrais.
Preserva a versão dos termos vinculada à reserva e o desconto contratado;
manual sem termos usa a versão mais recente e não presume aceite registrado.

Emissão apenas para admin e status sinal pago/quitada com pagamento ativo.
Reconsulta a reserva no clique e recusa cancelada/expirada/sem pagamento;
dados internos, contatos do cliente e notas de pagamentos não entram no PDF.
Biblioteca pdf-lib 1.17.1 local com licença MIT, mesma versão dos eventos.
Sem serviço externo de PDF, armazenamento público, migration ou alteração nas
notificações. README do fornecedor e `reservas/docs/reveillon.md` atualizados.

Validações: quatro testes Deno; fluxo real de download com RPCs simuladas em
390px/1366px, privacidade, clique repetido, falhas e cancelamento; regressão do
formulário de pagamentos. PDF de exemplo com regras completas em duas páginas,
renderizado e inspecionado visualmente; artefatos fictícios em
`reservas/output/pdf/reveillon-confirmation/`, ignorados. Navegador integrado
indisponível; ensaios locais em Edge headless, sem dados ou operações de clientes.

Publicação conferida: Pages `built` no commit `08f4b3a` e HTTP 200 com conteúdo
idêntico para HTML, controlador, carregador de dados, gerador e biblioteca no
domínio do portal. Grants SELECT autenticados existentes em `rv_events` e
`rv_terms` conferidos no banco. Nenhuma credencial de cliente usada nos testes.
Sem pendência de implantação. Orientações da raiz/cópias versionadas idênticas.


## 2026-11-12 - Codex - Icones de alergenos nos brownies

Site `7eff023`: Brownie de Chocolate e Brownie com Sorvete com os icones
GLUTEN, LEITE, LACTOSE, OVO e SOJA, por receita padrao escolhida pelo
proprietario. Aviso padrao mantido, sem observacao extra visivel. Origem
interna registra a referencia; nao presume ficha tecnica nem confirmacao
da cozinha. Fonte em `scripts/cardapio/catalogo_inicial.py` e JSON derivado;
snapshot e HTML regenerados. `docs/HANDOFF_CARDAPIO.md` atualizado.

Migration `20261112183312_cardapio_brownies_alergenos.sql` aplicada e registrada
na mesma transacao no portal, depois de ensaio com rollback: somente
`alimentar` dos dois produtos, com guardas para preservar confirmacoes e
contato cruzado. Os demais campos e a publicacao ativa foram preservados;
leitura posterior conferiu igualdade com a fonte. Sem objetos novos/grants.
Google conferido em simulacao: mesmos 83 itens/opcoes; o gerador nao exporta
icones de alergenos, portanto nenhuma alteracao remota necessaria ali.

Validacoes: 47 testes de aceitacao, 8 testes existentes do site, verificacoes
de assets/CSP/FAQ/prerenderizacao, cadeia de 242 migrations e comparacao
estrutural dos JSONs (somente alimentar dos dois brownies). Edge local em
1366px e 390px, sem overflow nem erro JavaScript; navegador integrado
indisponivel. Pages built no commit publicado, HTTP 200 e cinco icones em
cada brownie no dominio publico; detalhe conserva so o aviso padrao.
Sem pendencia de implantacao; referencia real da cozinha continua nao revisada.

## 2026-11-12 · Codex — Diagnóstico ChatGPT Ads por MCP

Conector validado com leituras reais da conta Sir Fisher. Campanha de roteiros
ativa/elegível desde hoje às 00h, dois grupos com CPC desejado R$3 e quatro
anúncios ativos/aprovados; diagnóstico completo sem bloqueio explícito de
conta, faturamento, geografia, revisão ou lance baixo. Teste por CEP segue
pausado; seu aviso de lance baixo não pertence à campanha nova.

Entrega ainda não comprovada: 05–11/11 têm zeros explícitos; hoje somente
00h–01h retornou zeros, e 01h–15h veio sem linhas. Relatório direto da
campanha vazio; painel conferido na sessão existente mostra “–” para
impressões/cliques/gasto e dados preliminares. Não afirmar zero durante todo
o dia nem atribuir causa a CEP ou lance sem evidência. Consulta de limites
da conta indisponível, sem inferir teto. Conversões históricas zero com
clique 30 dias e visualização desligada não cobrem hoje.

Atualizado `docs/CAMPANHA_CHATGPT_ADS_2026-11-11.md` com cobertura, fontes e
menor próximo passo: conferir manualmente 12/11 completo na manhã de 13/11,
depois das 24h recomendadas pelo guia oficial, e suporte se continuar sem
entrega ou cobertura conciliável. Sem envio de mensagem, alteração em Ads,
site, portal, banco ou automação. Revisões anteriores preservadas. Validação
das fontes, revisão do diff e `git diff --check`; alteração só documental.

## 2026-11-12 · Codex — Sugestões de almoço para grupo pequeno

Preparado PDF local para 12 pessoas, com entrada, almoço em travessas e
sobremesa em três sugestões, adaptando a estrutura do Manual de Eventos.
Preços integrais de cada item do cardápio publicado, sem os descontos do
configurador; serviço opcional discriminado e bebidas à parte. Quantidades
e disponibilidade dependem da conferência da equipe. Sem contrato, sinal,
código de proposta oficial, criação de reserva ou envio de mensagem.

Arquivo final em `../output/pdf/Sir-Fisher-Sugestoes-Almoco-12-Pessoas-28-11.pdf`;
gerador e conferências em `../tmp/pdfs/`, fora dos repositórios. Material da
cliente mantido local, sem publicação no site. No Git, somente este registro.
Validação: JSON público HTTP 200 idêntico à fonte local; cálculo por item,
totais, serviço e médias; quatro páginas renderizadas com Poppler e revisadas
visualmente, com extração de texto e conferência de caracteres. Sem alteração
na aplicação, no banco, nas regras comerciais ou nas automações existentes.

## 2026-11-13 · Codex — Execução do parecer jurídico do cardápio

Parecer de Pinho & Albuquerque de 12/11 analisado. Site 9547c86 publicado:
LEITE separado de LACTOSE em nove itens; Big Ben com LEITE/LACTOSE pelo
cheddar; Chope Brahma com GLÚTEN; sabores dos Pasteizinhos na descrição;
legenda SOJA/CORANTES corrigida em PT/EN. Brownies já ajustados ontem.
Nenhum ícone removido por suposição. Mesmos 80 produtos, preços e pesos.
Google publicado/relido: 83 itens/opções, descrições integralmente iguais à
exportação e 29 com alérgenos em texto; sem alterações de preço.
Site Pages built; HTML, JSON e scripts conferidos com HTTP 200 no domínio.

Migration 20261113150000_cardapio_parecer_juridico.sql aplicada/registrada
na mesma transação no portal, após dois ensaios com rollback. Somente
alimentar dos onze produtos e descrição dos Pasteizinhos; guardas de igualdade,
80 registros relidos contra a fonte e hash dos demais campos preservado.
Não criou publicação integral nem alterou grants/tabelas de outros sistemas.
Funções privadas com EXECUTE revogado dos clientes; publicar/restaurar mantêm
controle de acesso e passam a exigir referência/data/atestado alimentar.
Trigger invalida revisão antiga por mudança de composição, não preço/estoque.
Painel permite registrar fonte e conferência ou salvar rascunho sem atestado;
edição só de preço preserva revisão, receita alterada exige revisão nova.

Validações: 47 testes de aceitação; ícones dos 80 produtos PT/EN em 390/1366px,
sem overflow/erro JavaScript; painel com cliente simulado, zero escrita real;
teste SQL reexecutável com rollback (ausência/revisão/receita/preço/estoque),
zero atestados fictícios persistidos. Oito testes de perfil QR, três novos de
Google FoodMenus e dois de assets Pages; quality gates, 243 migrations,
pré-renderização/assets/CSP/FAQ aprovados. Varredura ampla de Analytics no
Python geral esbarrou em módulos Google Analytics ausentes, fora do alvo;
suítes aplicáveis aprovadas separadamente. Navegador integrado indisponível,
QA no Edge local. Placa A3 e checklist de quatro páginas renderizados/revisados
em ../output/pdf/; gerador da placa versionado. Ensaios privados em
`tmp/parecer-cardapio/`, ignorados.

Estado e pendências em docs/CARDAPIO_PARECER_JURIDICO_2026-11.md e handoff.
Proprietário informou que não possui composições/rótulos: coquetéis, molhos,
óleo, ícones por recheio, farofa e eventuais excessos continuam a conferir.
Pesos dos empanados têm decisão anterior específica; sem nota genérica
in natura. Afixação da placa, Canva/impresso e eventual delivery não foram
executados; não declarar adequação integral. Novas publicações integrais pelo
painel bloqueadas até revisão das receitas. Estático continua dependente da
conferência editorial humana; não usar exportação para contornar essa revisão.
Nenhuma credencial, parecer privado, dado bruto ou arquivo de cliente no Git.
Orientações da raiz idênticas às cópias versionadas.

## 2026-11-13 · Codex — Retirada do ícone de glúten do chope

Pedido expresso posterior do proprietário substitui a inclusão feita no
parecer: Chope Brahma sem ícone GLÚTEN no catálogo, snapshot/HTML PT/EN e
Google FoodMenus. Nenhuma alegação de ausência de glúten ou confirmação por
rótulo. Fonte interna registra a decisão; estado alimentar não revisado.
Demais produtos, preços, porções, fotos e disponibilidade preservados.

Migration `20261113160000_cardapio_chope_sem_icone.sql` aplicada e registrada
na mesma transação no portal, após ensaio idempotente com rollback. Guarda
impede sobrescrever edição concorrente; leitura posterior conferiu o registro
e hash dos outros 79 produtos. Teste SQL de conformidade ajustado à decisão
e aprovado com rollback; sem novos objetos/grants ou publicação integral.

Site `8567ac7`. Google publicado/relido: 83 itens/opções com mesmos preços,
28 declarações alimentares; descrições integralmente iguais à exportação.
Pré-renderização, assets, CSP, três testes FoodMenus e cadeia de 244 migrations
aprovados. Testes de aceitação: 47 aprovados. Handoff e registro do parecer
anotam a decisão posterior sem apagar o histórico. Ensaios privados em
`tmp/parecer-cardapio/`, ignorados. Nenhuma credencial ou dado bruto no commit.

## 2026-11-13 · Codex — Ajuste de entrega do ChatGPT Ads

Proprietário confirmou teste R$40/dia até 15/11 às 00h de Fortaleza,
máximo conservador R$160 no intervalo, e Brasil incluindo intenção de
viagem. Pelo MCP: campanha Roteiros e refeições convertida de orçamento
total para diário, término antecipado e grupo Refeição no roteiro alterado
para maximizar cliques. Outro grupo mantém CPC alvo R$3. Quatro anúncios
ativos/aprovados, sem mudança de conteúdo, destino ou público; nenhuma
campanha criada. Leituras posteriores confirmaram os campos e elegibilidade
sem bloqueios. Comparação exploratória entre temas, sem verba igual garantida.

Entrega após o ajuste ainda não demonstrada: dia 12 completo medido zero;
consulta incluindo 13 só cobriu até 00h. Reconciliar gasto anterior e após
o teste antes de tratar saldo como livre. Teto novembro R$500 preservado;
nova verba não autorizada. Orçamento diário não é teto total; término impede
continuação automática além de 15/11. Descrição histórica da plataforma
ainda menciona condições antigas; campos salvos e atualização de
docs/CAMPANHA_CHATGPT_ADS_2026-11-11.md são o estado vigente. Conferência
manual em 14/11; sem agendamento, mensagem ao suporte ou promessa de entrega.
CPM novo não foi criado: conector atual não expõe lance de grupo CPM.

## 2026-11-13 · Claude — Desempenho dos canais, Search Console e Réveillon no GA4

Banco `portal`: a pedido do proprietário, `rv_events.tracking` do
`reveillon-2027` passou de tudo `false` para `ga4 = true` (Meta e OpenAI
seguem `false`), relido pela API e pela RPC pública. O evento
`reveillon_prebooking` vai só ao GA4; não foi marcado como evento principal.
Docs no `reservas` (`HANDOFF_REVEILLON.md`, `reveillon.md`).

Search Console: a "Cópia sem canônica" (6 URLs) é o portal de reservas com
`?sf_cta=`/`?sf_origin=`, rastreado antes da canônica de 03/11; validação
iniciada e indexação de `www/reservas/` solicitada em 13/11. Meta: o token
`META_IG_TOKEN` (usuário do sistema ClaudePerfil) tem `ads_read`, mas
nenhuma conta de anúncios atribuída; a atribuição depende da verificação em
duas etapas do proprietário no portfólio. Não trocar o token. A API de dados
do GA4 respondeu 502 o dia todo; a interface funcionou.
