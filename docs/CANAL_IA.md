# Canal de comunicação — Claude ⇄ Codex

Canal de recados entre as duas IAs que trabalham neste repositório (**Claude Code** e **Codex**). Serve para handoffs, avisos de "estou mexendo em X", combinados e lições aprendidas — para uma ajudar a outra e não pisarmos no pé uma da outra.

> **🚦 Status atual:** 🟢 Livre. Medição do configurador publicada e validada no endereço público; entrega abaixo.

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
nenhuma conta de anúncios atribuída. Depois da verificação em duas etapas do
proprietário, a conta do portfólio (final 2327) foi atribuída e a leitura
de insights funcionou. A pedido dele, o acesso foi ampliado para "Gerenciar
campanhas" (DRAFT/ANALYZE/ADVERTISE), sem acesso total à conta. `meta.py`
ganhou rotas de anúncio, e `scripts/marketing/impulsionar.py` impulsiona
posts com teto obrigatório. Ativo desde 13/11, aprovado pelo proprietário
(teto R$300 com impostos): reel 28/09 (ambiente, R$140 até 21/11 0h, raio
20 km, site) e reel 14/10 (almoço, R$120 até 20/11 0h, seg–sex 7h–14h, raio
8 km, /almoco-executivo/). Conferir aprovação e entrega; resultado por UTM
`paid_social` e pelas reservas. Não trocar o token nem o fuso (Noronha). A API de dados
do GA4 respondeu 502 o dia todo; a interface funcionou.

## 2026-11-13 · Claude — Fotos de Luisa Dörr no site, Google, portal e proposta

Ensaio de 18/10/2026 (44 fotos; o proprietário confirmou a autorização das
pessoas e marcas). Análise foto a foto e mapa de lacunas:
https://claude.ai/artifact/WPvJeXVf2Cbd9uLLBk16uv. Crédito "Foto: Luisa
Dörr" em cada uso (Lei 9.610/98, art. 79) e nos metadados dos arquivos.

- Site `6c5f3ab`: nova imagem de compartilhamento
  (`og-sir-fisher-mesa-orla-fortaleza.jpg`) nas 8 páginas que usavam a
  antiga; capas de Como chegar (fachada), Sobre (varanda) e Guia (orla);
  fotos em Como chegar, Sobre, Reservas, Guia, Fish and chips PT/EN, Home
  PT/EN (fim de tarde no lugar do sol repetido), Pôr do sol e capa de
  Eventos; JSON-LD com a fachada. Verificadores, teste de navegador e
  capturas 390/1440 sem erro nem rolagem horizontal.
- Google: 14 fotos importadas por URL (`site/assets/img/perfil-google/
  luisa-dorr-*`), relidas pela API: capa 2000×1125 (substituiu a de
  640×360), 4 externas, 2 área de mesas, 4 comidas, 3 adicionais.
- Reservas `fcc5911`: capa do portal com a foto sob o degradê (opacidade
  0,7), crédito PT/EN; `style.css` e `i18n.js` com versão nova em todos os
  imports; 40 testes Deno ok. `eb2d8ae`: faixa "O cenário do seu evento"
  da proposta com a foto do grupo e crédito; `event-quote` reimplantada
  (versão 71, ACTIVE, `verify_jwt` false).
- Instagram: 4 carrosséis 4:5 e legendas em `OneDrive/Sir Fisher/Marketing/
  Fotos/Booking/Luisa Dorr - prontas para o Instagram/`. Não publicados: a
  fila exige aprovação do proprietário no painel e não aceita carrossel.

Pendente: postar os carrosséis (confirmar o @ da fotógrafa); logo da ficha
ainda com "Barra Sol"; drinks do cardápio sem foto (as taças do ensaio têm
marca de gin); `pricing_test.ts` com datas de exemplo vencidas (23 falhas,
anteriores a esta entrega).

## 2026-11-14 · Codex — Correção do atendimento Jotform

Pedido do proprietário aplicado ao agente ativo do Instagram. Localizadas
apresentações em saudação fixa, mensagem de boas-vindas gerada, persona e
fontes; saudação agora “Oi! Como posso ajudar?”. Identificação como IA
somente em pergunta explícita sobre quem atende ou sobre automação.
Réveillon direciona para a página com programação/instruções/pré-reserva;
reserva comum, inclusive aniversário, para o portal de 1 a 10 pessoas.
Quantidades confirmadas e casos que exigem equipe preservam os canais próprios.

Sete fontes lidas, seis corrigidas e salvas; catálogo preservado. Persona,
FAQ, política e matriz alinhadas. Ação específica de Réveillon e pedido de
pessoa salvas; ação de contato suspeito delimitada ao relato atual.
Resposta fixa experimental de reserva comum desabilitada após repetir o
portal para 15 pessoas; repetição pela persona/base passou. Ações antigas
de início de conversa, WhatsApp amplo e spam amplo permanecem desabilitadas.

Doze cenários sintéticos com repetições na prévia real: perguntas dos prints,
reserva genérica, 6/15/40 pessoas, saudação, identidade explícita, pessoa,
reserva após pessoa, contato suspeito e Réveillon após esse relato.
Fluxos finais descritos em docs/instagram-atendimento/REVISAO_2026-11-14.md.
Links públicos de Réveillon e portal retornaram HTTP 200. Direct pausado
durante ajustes, reativado e relido como Active em @sirfisherfc; comentários,
stories e menções continuam desligados. Sem envio a clientes ou alteração
de conversas antigas. Recibos sintéticos em tmp/instagram-atendimento/,
ignorados. Orientações da raiz e cópias versionadas idênticas.

## 2026-11-14 · Codex — Alertas repetidos e recuperação Stone de 09/11

O workflow concluía a rodada, mas retornava erro em cada retomada pelo mesmo
atraso. XML de 09/11 recebeu HTTP 400 e o controle impediu repetição; dez
baixas de 10/11 aguardavam suas capturas. Datas posteriores processavam e a
Pluggy continuava funcionando. Mensagem de HTTP 400 agora orienta revisão
manual de data/parâmetros, sem atribuir causa específica ao banco.

Proprietário autorizou nesta conversa uma única nova consulta do XML de 09/11
e o reprocessamento de 10/11. GET HTTP 200, cabeçalho e dry-runs de recebíveis
e vendas aprovados. Cache privado recuperado com registro do HTTP 400
original; recibo e logs em `tmp/stone-recuperacao-2026-11-14/`, ignorados.
Rotina somente pelo cache concluiu 09/11 e resolveu as dez baixas de 10/11.
Saúde sem atraso, fechamento contíguo até 12/11; extrato de 13/11 dentro do
prazo. Nenhum novo POST Pix ou consulta de outro dia à Stone.

Aquisição/retomada agendadas usam `--atraso-como-aviso`. Pendências continuam
no Status; saúde diária e execução manual mantêm falha por atraso. Erros que
interrompem a rodada preservam o código de saída. Testes do bloco Bash real
do workflow cobrem agenda/cache/aquisição/saúde/manual e saídas 0/1/3.
Suíte de fechamento com 17 testes aprovada, incluindo diagnóstico 400 e
saúde estrita mesmo com a flag de aviso. Quality gates e testes de APIs,
vendas, controle de pedidos/cache e Status aprovados. Sem migrations,
alteração de regra financeira, segredos ou dados brutos no commit.

## 2026-11-16 · Codex — Resultados ChatGPT Ads e Instagram/Meta

Revisão somente leitura em Ads Manager, Meta, GA4 e portal para 01–15/11.
Relatório em docs/RESULTADOS_CAMPANHAS_2026-11-16.md. ChatGPT Roteiros:
2.762 impressões, 40 cliques, R$95,40, CPC R$2,39; 36 sessões no GA4,
sem reserva paga vinculada no portal ou meta atribuída. Término autorizado
em 15/11 às 00h preservado; quatro campanhas ChatGPT sem elegibilidade
atual por status/datas. Conta aprovada/faturamento completo; limites da
conta indisponíveis. Total ChatGPT 01/10–15/11: R$895,43, não desde criação.

Meta: acesso existente de leitura funcionou sem configuração nova.
Ambiente tem R$50,59, alcance estimado 8.009 contas, 8.767 impressões e
679 cliques no link, CPC aproximadamente R$0,075; orçamento total R$140,
ativa até 21/11 às 00h Fortaleza. GA4 tem uma confirmação na sessão UTM;
portal tem uma reserva da campanha marcada como comparecida em 15/11,
grupo informado de duas pessoas, sem consumo/ticket. Consistência entre
agregados não comprova identidade individual nem crédito da Meta. Almoço
ativo até 20/11 às 00h, orçamento total R$120, mas sem linha de métricas
Meta no período; ausência não é zero. Nenhuma reserva com sua UTM exata.

Preservados os fusos: Meta America/Noronha, demais America/Fortaleza,
fronteiras diárias uma hora diferentes. Sem somar alcance ou sinais como
pessoas. Ticket R$80/conta e R$58/pessoa são referências legadas, sem
comprovar receita/lucro; cobertura PDV e contribuição continuam pendentes.
Previsões limitadas à aritmética de custo constante, sem nova autorização
de verba. Prioridades: preservar término ChatGPT, conferir entrega Almoço,
jornada/consentimento/atribuição e consumo efetivo antes de ampliar.

Validação documental: totais por grupo/dia/período reconciliados, fórmulas
CPC/CPM/CTR e cenários conferidos, referências locais e diff revisados.
Somente relatório e este registro; sem anúncio, código, banco, credencial,
automação, dado pessoal ou financeiro bruto alterado/incluído. Orientações
da raiz idênticas às cópias versionadas; três repositórios sincronizados.

## 2026-11-16 · Claude Code — Jotform: Fortal/Prime/Duo, parcerias e WhatsApp

Pedido do proprietário após respostas reais ruins no Direct (14–15/11).
Causas e testes em docs/instagram-atendimento/REVISAO_2026-11-16.md.
Na Jotform: duas ações Say exactly novas (Fortal em Dobro/Prime/Duo
Gourmet; proposta de parceria pedindo mídia kit e Insights pelo WhatsApp),
nome exibido "Sir Fisher", orientação positiva sem autoapresentação como
IA, regra de sempre escrever o link do WhatsApp, restrição "Inclua WhatsApp
somente quando…" limitada a reservas/Réveillon na persona e em cinco
fontes, fonte nova de perguntas sem confirmação e fila de pendentes zerada.
A ação de informação não confirmada foi reativada com condição genérica.

Aviso: quando a base não tem nada próximo da pergunta, a Jotform usa uma
resposta própria ("não tenho essa informação") que ignora persona e ações;
a fonte nova cobre esse caso por exemplos. Prévia: nove cenários aprovados,
inclusive regressões de reserva, horário e "é robô?". Contador do agente
36 → 45 por causa da prévia; nenhum cliente recebeu mensagem. Canal com
Reply to DMs ativo. Conversa da Larissa segue em atendimento humano.
Somente documentação no Git; sem código, banco, segredo ou dado bruto.

## 2026-11-16 · Codex — Seguidores atribuídos aos anúncios Instagram

Complementado docs/RESULTADOS_CAMPANHAS_2026-11-16.md com consulta Meta
às 13h22 Fortaleza/14h22 Noronha. Campos dedicados de seguimentos e
visitas ao perfil, ausentes no conjunto genérico de ações anterior.
Em 13–16/11, com dia 16 parcial: Ambiente 49 seguimentos, 454 visitas e
R$58,68; Almoço 15, 88 e R$27,52. Soma descritiva 64 seguimentos,
542 visitas e R$86,20; gasto por seguimento R$1,20/R$1,83 e R$1,35
no conjunto. Não equivale a pessoas únicas garantidas, crescimento
líquido, resultado somente de hoje, lucro ou efeito causal.

Preservado o snapshot inicial. Em 01–15, Ambiente retornou 41 seguimentos,
388 visitas e R$50,59; Almoço agora trouxe zeros explícitos somente para
gasto, seguimentos e visitas, sem preencher impressões/cliques/CPC/CPM
não reconsultados. Quatro linhas confirmaram atribuição de um dia após
visualização ou sete dias após clique. Cinco consultas somente leitura,
sem paginação/truncamento; nenhum cliente, anúncio ou orçamento alterado.
Validação de somas, divisões, unidades, sobreposição temporal e diff;
somente os dois documentos, sem segredo, dado pessoal ou bruto incluído.

## 2026-11-16 · Claude Code — Jotform: uma ação por cupom

O proprietário enviou as regras dos apps Fortal em Dobro, Prime Gourmet e
Duo Gourmet e pediu resposta só sobre o app perguntado. Criadas três ações
"Always talk about", uma por cupom; a ação única da manhã foi desativada.
Fonte "Regras dos Cupons Sir Fisher" como referência; três fontes antigas
apontam para ela; Q&A da manhã restrito ao Fortal. Orientações de cupom na
persona foram testadas, não aplicadas (fim da lista) e removidas: regra que
precisa valer sempre vai em ação. Prévia: Duo, Prime no sábado, Fortal hoje,
VR com Fortal e feriado de 20/11 corretos. Título automático da fonte "Regras
de Atendimento" aparece como "Please provide the text"; conteúdo conferido.
Página do Fortal mostra "Sir Fisher Praia", bairro Centro e horário até 23h;
nada alterado lá. Somente documentação no Git.

## 2026-11-16 · Codex — Próximos passos das campanhas

Complemento curto no relatório de resultados, leitura Meta 13h54 Fortaleza,
13–16/11 parcial: Ambiente R$59,32/803 links/49 seguimentos; Almoço
R$30,24/223/15, com entrega hoje comprovada. Total R$89,56/64, razão
descritiva R$1,40 por seguimento. Ambos ativos, orçamento/prazo preservados.

Plano recomendado, sem execução: manter R$260 mídia dentro de R$300 com
impostos; revisão manual sugerida 18/11 às 18h, comparando 16–17 completos
e separando dia 18 parcial; conferir consumo/margem das reservas na operação
antes de ampliar. ChatGPT encerrado em 15/11, zero metas em 12–15 completos.
Decisão até 19/11 sobre eventual outra rodada: o executivo é seg–sex,
10h–14h, exceto feriados; fim de Almoço em 20/11 às 00h é coerente com
a oferta. Ambiente cobre o dia 20 e termina 21/11 às 00h, sem o fim de
semana 21–22. Eventual divulgação desses dias deve avaliar ambiente e
cardápio regular, sem anunciar executivo indisponível.
Não houve renovação, realocação, anúncio novo, automação, contato externo,
integração ou coleta financeira. Só relatório/CANAL; aritmética e diff
validados, sem segredo, dado pessoal ou bruto incluído. Commits Claude
posteriores preservados.

## 2026-11-16 · Claude Code — Jotform: VR aceito também com cupom

Proprietário confirmou que a casa aceita VR para tudo, inclusive com Fortal
em Dobro, Prime Gourmet e Duo Gourmet, embora o app do Fortal proíba. Ações
dos três cupons e fonte "Regras dos Cupons" atualizadas; Q&A com a pergunta
exata do teste criado porque a Jotform repetia a resposta antiga em cache.
Página pública do agente: pergunta repetida e variação com Alelo responderam
"sim". Teste também mostrou que o agente sabe data e dia da semana, mas não
a hora. Somente documentação no Git.

## 2026-11-16 · Codex — Origem histórica das reservas de Réveillon

Pedido esclarecido como consulta das reservas já feitas. Auditoria somente
leitura: 15 registros com snapshot de atribuição. Entre 11 ativos, seis
públicos têm canal observado, um administrativo tem indício que pode ser
do cookie do operador e quatro seguem com origem não identificada.
Snapshot de cookie/localStorage não recupera UTMs/referrer ausentes nem
comprova crédito de anúncio ou origem declarada pelo cliente.

Identificadores GA4 em parte dos snapshots não permitiram recuperação
exata adicional pelas fontes disponíveis: não foi localizada exportação
individual nos guias/scripts nem ferramenta conectada para esse cruzamento.
Isso não prova inexistência de exportação externa privada. Preservar as
origens desconhecidas e a ressalva do cadastro administrativo; não reatribuir.
Sem alteração de captura, formulário, painel, tracking, banco ou dados
históricos. Somente este recado; nenhum dado pessoal, identificador opaco,
valor financeiro ou relatório bruto versionado. Diff documental revisado.

## 2026-11-16 · Claude Code — Jotform: autoapresentação como IA

Conversa real às 15h31 ainda abriu com "sou sua assistente de IA". Padrão:
só a primeira resposta no Instagram real, com o nome da pessoa; prévia não
reproduz. Removidas as sobras de 02/11: nome principal do agente era "Sir
Fisher — Assistente virtual" (agora "Sir Fisher"), títulos "ASSISTENTE
VIRTUAL" em duas fontes e menções "Identifique-se como IA…" em quatro.
Regra IDENTIDADE no início da primeira orientação da persona, conforme
recomendação do suporte Jotform. Confirmar na próxima conversa real.

## 2026-11-17 · Claude Code — Perfil do Google: botão de reserva

O botão "Reservar" não aparecia na Pesquisa nem no Maps: `url_reservations`
existe desde 30/09, mas nenhuma sessão ou reserva veio de `gbp_booking`.
Link do portal cadastrado no painel, em Agendamentos → "Links para suas
ferramentas de agendamento on-line". A Place Actions API está desativada no
projeto do OAuth. Conferir em alguns dias se o botão aparece e se surgem
reservas `google_maps/gbp_booking`. A métrica "Agendamentos" continua em 0
por definição. Detalhes em `docs/ROTINA_PERFIL_GOOGLE.md`.

## 2026-11-17 · Claude Code — Réveillon: Lote 2 no ar

A pedido do proprietário, Lote 2 ativo desde 11h07 (Fortaleza): lateral
R$ 3.200, central R$ 1.700, bistrô R$ 900, cadeira extra R$ 400, mesma
consumação (+R$ 50 por pessoa). Lote 1 inativo, com fim nessa hora; as 12
reservas dele mantêm os preços gravados. Troca feita no banco numa só
transação, conferida pelo acesso público (`rv_public_event`, `rv_simulate`).
Preços fixos atualizados em `site/reveillon/index.html` e
`reservas/reveillon.html`; seed e handoff do Réveillon registram os dois
lotes. Sugestão em aberto: Lote 3 em dezembro para as últimas 2 ou 3 mesas.

## 2026-11-17 · Claude Code — Jotform: apresentação como IA é do canal

A regra IDENTIDADE de 16/11 não resolveu: a conversa real das 18h57 abriu com
"Soy tu asistente de IA". Pelo histórico, 16 de 17 conversas reais no Direct
abrem com o nome da pessoa e a apresentação como IA, em todas as versões da
persona; a prévia nunca faz isso. É o aviso do canal Instagram da Jotform
(o suporte diz que não pode ser removido). Não mexer mais em persona, fontes
ou ações por isso; depende de decisão do proprietário. Detalhes em
`docs/instagram-atendimento/REVISAO_2026-11-16.md`. Nada alterado na Jotform.

## 2026-11-17 · Claude Code — Jotform: resposta bilíngue não funciona

Pedido: em outro idioma, responder no idioma da pessoa e repetir em
português. Testado com regra na persona e uma ação "Always talk about"
(condição livre de idioma). Na prévia, três respostas saíram só no idioma
da sessão, sem a parte em português. Persona restaurada ao texto original;
ação desativada, sem exclusão. Não reativar sem teste que mostre as duas
línguas. Apresentação como IA: o proprietário decidiu deixar como está.

## 2026-11-18 · Codex — API, token e MCP Instagram revalidados

Consulta do proprietário sobre o funcionamento do acesso. Entre 14h17 e
14h19 Fortaleza, identidade `@sirfisherfc` confirmada sem cache, quatro
permissões de leitura concedidas e insight `reach` disponível em consulta
nova. `debug_token`: `SYSTEM_USER`, válido, sem vencimento programado
informado. Sem renovação ou substituição da credencial canônica.

Servidor MCP stdio passou initialize, listagem das sete ferramentas e
`instagram_identity(refresh=true)`, com duas leituras HTTP novas. Usar o
Python privado analytics-mcp/0.8.0 (SDK 2.3.0); o Python padrão deste PC tem
SDK 1.28.1 sem MCPServer. Pendência constatada: `instagram_analytics` ausente
do cadastro Codex deste PC e das ferramentas desta sessão. O teste isolado
não comprova conexão na interface aberta. Configuração preservada.

Guia INTEGRACAO_INSTAGRAM_ANALYTICS atualizado com esse estado local.
Somente documentação; sem código, banco, anúncio, Direct, rotina ou segredo
alterado/incluído. Diff e pares de orientações da raiz conferidos; site e
reservas sem alterações da tarefa. Leituras reais substituem qualquer
suposição de falha baseada apenas no cadastro MCP.

## 2026-11-18 · Codex — Nova curadoria dos Destaques Instagram

Proprietário confirmou somente Destaques, com prioridade experiência e
identidade. Publicadas e relidas pela interface cinco coleções novas:
A Casa (3), Sabores (6), Drinks (4), Quem Veio (1), Visite (2), nessa ordem.
Reutilizados Stories de novembro já publicados; sem novos envios de Story,
alteração de feed, anúncio, Direct ou credencial. Quem Veio usa comentários
reais do Instagram, não avaliações Google ou depoimentos inventados.

Inventário anterior: 64 posições em quatro coleções; 53 quadros/datas dos
grupos Foods/Ambiente/Clientes conferidos. Há duplicações entre grupos.
Não houve reprodução integral de todos os vídeos nem ranking completo por
alcance. Duas amostras de insights históricos mostram audiência; não dizer
que todo conteúdo antigo teve pouco impacto. Benchmarks reais: Illa Mare,
Terra do Sol e Coco Bambu. Decisões editoriais e limites no relatório em
docs/marketing/DESTAQUES_INSTAGRAM_2026-11-18.md.

Pendência explícita de acabamento no celular: aplicar cinco capas novas,
como escolhido pelo proprietário, e retirar Influencers/Foods/Ambiente/
Clientes da vitrine preservando o arquivo. A web não apresentou upload de
capa nem exclusão da coleção inteira; as quatro antigas continuam online.
Não declarar limpeza concluída. Capas temporárias novas são fotográficas.
Visite ainda merece complemento específico de endereço/reservas.

Ícones PNG/SVG, gerador e QA versionados junto do relatório, sem fotos de
clientes. ZIP privado de entrega em output/instagram-destaques-2026-11-18/;
inventário, capturas e URLs temporárias fora do Git. Capas verificadas em
1080px/corte circular64px; quantidades novas relidas; diff documental e
pares de orientações da raiz conferidos. Nenhuma rotina nova criada.

## 2026-11-18 · Codex — Correção da seleção publicada nos Destaques

O proprietário apontou corretamente que Quem Veio só mostrava Big Ben
Fries. A seleção anterior estava errada e a conferência de datas/quantidades
não havia assegurado correspondência visual. Corrigido no mesmo Destaque:
agora contém o Story de 12/11 com dois comentários reais sobre o Fisher
Burger; a batata saiu dessa coleção, preservando o original.

Auditoria visual direta dos outros grupos encontrou erros adicionais:
retirado croquete de A Casa; retirados de Sabores varanda com horário
9h–23h e reel redundante de dadinho com abertura pouco informativa;
retirado dadinho de Visite e incluído o card dos executivos com link ao
site, selecionado e conferido na própria interface. Contagens corrigidas:
A Casa 2, Sabores 4, Drinks 4, Quem Veio 1, Visite 2. Drinks estava correto.
Reabertas as coleções para verificar cada posição visualmente. URLs de
mídia/miniaturas e contagem não bastam como validação editorial.

O perfil agora exibe somente os cinco grupos novos. Quatro ícones já estão
aplicados por ação fora desta execução do navegador; as quatro coleções
antigas não aparecem mais. Quem Veio recebeu capa fotográfica durante a
correção e precisa reaplicar o ícone pelo aplicativo. Ordem atual observada:
Visite, Quem Veio, A Casa, Sabores, Drinks. Não dizer que preservou a ordem
proposta inicialmente. Não presumir que editar capa reordene o perfil.

Relatório e roteiro do celular atualizados para o estado corrigido.
Capturas de QA e inventário anterior preservados fora do Git, em output.
Sem Stories novos, exclusão de originais, alteração de anúncios, Direct,
credencial, banco ou rotina. Capas vetoriais não foram modificadas.

## 2026-11-18 · Codex — A Casa ampliado; retirar Quem Veio no aplicativo

O proprietário pediu que A Casa apresentasse melhor o espaço e que Quem
Veio saísse se não houvesse mais material útil. Publicados quatro Stories
novos com fotos reais: chegada/fachada, mesas, vista da varanda e fim de
tarde. Três fotos de Luisa Dörr com crédito; uma do acervo Sir Fisher.
Fotos inteiras, sem retoque, geração de pessoas ou alegação de depoimento.
Site `5984a56` contém apenas os quatro JPEGs; URLs HTTP 200 e hashes iguais
aos arquivos locais; validação de imagens e Pages concluídos com sucesso.

Publicação pelo cliente Meta existente, separado do MCP somente leitura,
após confirmar @sirfisherfc, permissão e quota. As quatro mídias foram
relidas no destino. Uma trava do OneDrive no recibo interrompeu o lote
depois do primeiro envio; somente os três restantes foram publicados na
continuação, sem duplicar. Não reexecutar os scripts de envio. Fontes,
manifesto, recibos e verificação ficam privados em output/instagram-
destaques-2026-11-18/casa-revisada/, fora do Git e sem credenciais.

No Destaque A Casa, os dois itens anteriores foram substituídos pelos
quatro novos. Reaberto em página nova e percorrido visualmente de 1 a 4:
imagens, títulos, ordem 01/04 → 04/04 e capa de guarda-sol conferidos. Demais
grupos preservados. Quem Veio continua com um Story: não há mais relatos
úteis suficientes. A web não oferece exclusão de coleção e desabilita
Avançar com seleção vazia; tentativa cancelada sem excluir originais.
Retirada pendente pelo aplicativo, já comunicada ao proprietário.

Perfil final observado: A Casa 4, Visite 2, Quem Veio 1, Sabores 4, Drinks 4,
nessa ordem. Depois da retirada de Quem Veio: 14 posições em quatro grupos.
Relatório e roteiro do celular atualizados. Sem mudança em anúncios,
Direct, token, banco, agendamentos ou feed. Reservas sem alterações; pares
de orientações da raiz idênticos. Diff e conferência visual concluídos.
O gate local com --require-node não encontrou Node no PATH deste PC;
validação de JavaScript depende do Quality gates no GitHub Actions.

## 2026-11-18 · Codex — Encerramento e cores de A Casa corrigidos

Dois pedidos seguidos: evitar a fachada repetitiva no quarto Story e
aproximar brilho, contraste e vibração, pois a terceira foto destoava.
Acervo Luisa Dörr completo consultado; escolhida a foto 447, com pessoa
no parapeito, sol, mar e movimento na praia. Crédito preservado. Uma peça
intermediária foi publicada, mas o novo pedido de cor chegou antes de sua
inclusão no Destaque; asset e recibo preservados, sem apagar publicação.

Encontrada falha no renderer anterior: as fotos Luisa 1/2/4 tinham perfil
Adobe RGB (1998), descartado na montagem sem conversão. As três agora são
convertidas para sRGB antes de compor; não receberam filtro criativo nem
reconstrução generativa. A terceira foi suavizada pelo imagegen integrado,
reduzindo laranja, vibração, contraste e aparência de HDR, com as outras
como referência. QA independente aprovou cor e não identificou distorção
material de objetos/geometria/texto. Os quatro JPEGs finais incorporam sRGB.

Site `bad59f1` contém somente a peça intermediária 447; `e87a283` contém
somente os quatro novos assets -cor. Assets/Pages aprovados; URLs relidas
com HTTP 200, JPEG e SHA igual ao manifesto. Nenhum asset anterior foi
sobrescrito. Publicação dos quatro finais pelo cliente Meta existente,
com identidade fresca, Página, permissão, quota e diário exclusivo fsync.
Cada mídia relida; as quatro confirmadas em IG/stories. Não reexecutar os
scripts de publicação nem remover seus diários.

No mesmo Destaque A Casa, desmarcados os quatro anteriores e selecionados
os quatro finais depois de conferir as imagens reais na galeria. Reaberto
após salvar e percorrido 01/04 → 04/04: títulos, créditos, fotos e ordem
conferidos nas mídias efetivamente exibidas; quarto usa 447, terceiro é a
versão de cor suavizada. Capa de guarda-sol preservada. Outros grupos não
editados. Perfil final: A Casa 4, Visite 2, Sabores 4, Drinks 4 — 14 posições.
Quem Veio já não aparece: retirada fora desta execução, sem atribuí-la ao
Codex. A pendência anterior de acabamento no aplicativo está encerrada.

Relatório e roteiro do celular atualizados. Fontes, prompt, renderer,
manifesto, prévia, ZIP e evidências no diretório privado
`output/instagram-destaques-2026-11-18/casa-cor-unificada/`.
Somente três documentos em gestão; sem
segredos, banco, anúncio, Direct, feed, token ou rotina alterados. Reservas
sem mudanças. Diff, ZIP, QA visual e perfis/tamanhos dos JPEGs conferidos.

## 2026-11-18 · Codex — Jotform: Stories ativados e feed avaliado

Solicitação sem resposta era reply de Story, enquanto só DMs estavam
ativos. Painel confirmou conta/conexão corretas e Stories OFF; conversa
não localizada na busca do Jotform e pendente em Pedidos do Instagram.
Reply to Stories ativado, salvo e relido após reload: All Stories, All
Story Replies, base de conhecimento, mesma exclusão restrita de venda
artificial de seguidores/curtidas, sem fallback/horários/filtro de seguidores.

Prévia de Réveillon passou. Teste real pela conta do proprietário, 16h36
Fortaleza, recebeu resposta no Instagram e no histórico Jotform com marca
de Story e link correto. Story replies 0→1; DMs 36→37; cota 18→19/100.
Teste nomeava o evento em Story atual; não garante leitura de toda imagem
nem entrega a pedidos ainda não aceitos. Por pedido expresso posterior,
solicitação antiga aceita na Principal e respondida manualmente às 16h41,
com preços por mesa do lote 2 conferidos no site atual e link do evento.
Envio persistiu após reload; sem confirmação de leitura do destinatário.
Pausa automática de 12h após intervenção manual preservada.

Feed: 12 posts de 25/09–17/11, GET pelo cliente marketing existente, conta
e permissão conferidas, sem cortes de paginação informados. Treze comentários
de outras contas: duas perguntas comerciais, dez interações sociais e uma
reclamação de som vizinho. Uma pergunta já respondida pela casa. Nos seis
posts dos últimos 30 dias: nove comentários, duas perguntas e sete sociais.
Recomendação: atendimento pontual das dúvidas e revisão humana de reclamação;
comentários automáticos e menções seguem OFF, sem publicação de resposta
no feed. Palavras não garantem intenção nem consumo zero de cota.

Registro em docs/instagram-atendimento/REVISAO_2026-11-18.md; JOTFORM e
ATENDIMENTO_INSTAGRAM atualizados. Conteúdo individual do feed permanece
privado em tmp, fora do Git e da base do agente. Não houve nova credencial,
assinatura, piloto, cron, alteração de banco, anúncio ou feed. Site/reservas
sem mudanças; documentação revisada e pares das orientações da raiz idênticos.

## 2026-11-18 · Codex — Jotform: filtro de dúvidas no feed e Stories

Complemento solicitado pelo proprietário: exclusão nativa de interação
social sem pergunta/pedido de informação, sem fallback, nos dois canais.
Preserva dúvida sem interrogação, reclamação real e pedido de atendimento;
mantém a exclusão de venda artificial de seguidores. Cuidado: vírgulas no
texto viram categorias separadas ao salvar. Primeira redação foi dividida;
fragmentos corrigidos/removidos. Telas finais relidas após reload com
exatamente duas categorias, texto sem vírgulas no relatório de 18/11.

Feed agora ativo para posts/Reels, editando a automação antiga: resposta
somente por DM pela base; comentário público OFF, sem agradecimento
automático. Não foi criado comentário público de teste nem feita resposta
retroativa. Entrega a novo comentário continua sem ensaio; estado salvo não
é prova de entrega. Stories preservam base/todos os Stories com novo filtro.
Agente pausado na preparação e Enabled conferido após reativar/recarregar;
DMs comuns, menções OFF, memória, persona e base preservados.

Controle real pela conta do proprietário: reação só de emojis sem nova
resposta por pelo menos 64 s; dúvida sobre reserva para quatro pessoas sem
interrogação recebeu o portal, sem disponibilidade/confirmar reserva.
Cota consultada 20/100; também houve Direct real no intervalo. Teste usa
thread existente e não prova isenção de consumo para conversa excluída.
Não prometer economia exata: cota é de conversas, não mensagens.

JOTFORM, ATENDIMENTO_INSTAGRAM e relatório de 18/11 atualizados. Só
documentação no Git; sem segredo, banco, token, anúncio, plano ou rotina
alterados. Site/reservas sem mudanças; pares das orientações da raiz iguais.

## 2026-11-19 · Claude — Jotform: vinho inventado corrigido

O agente afirmou ter carta de vinhos num Direct real. Criados na Jotform a ação
"Always talk about" de vinho/rolha e o par de perguntas e respostas; os dois
testes na página pública saíram corretos. A cliente recebeu a correção manual
com desculpas às 11h40. Site `f8bdf5a`: o texto alternativo da foto da rolha
deixou de citar vinho. Detalhes no topo de
`docs/instagram-atendimento/JOTFORM.md`. Pendente: outros fatos do book que
não estão na base da Jotform podem gerar o mesmo erro.


## 2026-11-22 · Claude — Teknisa: pendências fiscais dos componentes

O caixa mostrou 16 componentes com pendência no cadastro de impostos.
Todos receberam NCM `21069090` em Impostos do Produto, PIS/COFINS
`0.00` onde estavam vazias, e Gênero 21, Tipo 04 e Origem 0 na aba
Fiscal. Tudo foi relido no painel. Os contratos estão no README do
Teknisa e os recibos em `tmp/teknisa/fiscal-componentes-2026-11-22/`.
Aviso: o cliente de componentes não preenche esses campos, então
complete-os ao criar um componente. Pendente: carga no caixa e venda de
teste.

Soda Italiana, a pedido do proprietário ("o que o imposto é menor"):
saiu de NCM `22089000` e CEST `02.002.00`, de bebida alcoólica, para
NCM `22021000` sem CEST, como Suco Copo e refrigerantes. O restante do
imposto já era igual. Relida por unidade e no cadastro global.

Aviso "notas pendentes/rejeitadas desde 06/08": são três NFC-e da
implantação (06/08 e 23/09, R$ 29 + R$ 10 + R$ 10). A SEFAZ confirmou
217 (não constam) para as três. O proprietário decidiu inutilizá-las,
mas a tela de inutilização do Teknisa só lista números pulados.
Detalhes e o registro de teste da nota 2/001 em
`docs/TEKNISA_ACESSOS_OPERACAO.md`. Pendente: suporte Teknisa.

## 2026-11-22 · Claude — Card de meta segue o gráfico diário

Na `index.html` e na `gerente.html`, a barra verde do card "Atingimento
da meta" agora soma o `venda_dia` do `painel_diario`. Antes ela usava o
`faturamento` total do mês. São os mesmos dias do gráfico de barras, que
param no `corte_venda` (Stone e sangria lançadas). O percentual e a
projeção já usavam esse corte via `tendencia_mes`. Assim, cartão ou Pix
de um dia sem sangria não adiantam mais a barra verde. Na `index.html`,
card e gráfico dividem a consulta (`diarioDoMes`). Se ela falhar, a
barra verde não aparece. Não houve mudança no banco nem nos KPIs. Nos
23 meses com venda, a soma das barras já era igual ao `faturamento`.
Testes em `test_desempenho_front.mjs` e `test_frontend_contracts.py`.

## 2026-11-22 · Claude — Réveillon: reativar reserva expirada

O proprietário recebeu o pagamento de RV-D30FC5 (mesa lateral 01) depois
que ela expirou e bloqueou a mesa para segurá-la. Nova migration
`20261122180000_reveillon_reativar_expirada.sql` cria
`rv_admin_reactivate`, só para administradores. Ela volta a reserva expirada
para pré-reserva na mesma mesa, com o preço original e um prazo novo.
Retira o bloqueio só com confirmação do painel. Recusa mesa ocupada e
limite de cadeiras estourado. Foi aplicada no `portal`, com a versão
registrada na mesma transação. Grants: `authenticated` sim, `anon` não. Não
alterou dados. No `reservas`: botão "Reativar reserva" na ficha, coluna Data
e ordenação por clique no título da lista de reservas. Testes:
`reveillon-reactivate-tests.sql` e `reveillon-deposit-tests.sql` passaram no
`portal` em ROLLBACK, e o novo teste de navegador passou em 390/1366px.
Pendente: o proprietário reativar RV-D30FC5 e registrar o pagamento.

## 2026-11-22 · Claude — Jotform: reserva, terça em dobro e quarta do camarão

Dois erros reais no Direct: "precisa fazer reserva?" recebeu "Sim", e duas
perguntas sobre a terça em dobro do almoço receberam o cupom Fortal em
Dobro. Na Jotform, a ação do Fortal só dispara com a palavra Fortal. Entraram
quatro ações (terça em dobro, quarta do camarão, promoções em geral e
"precisa reservar?"), uma seção de promoções da casa na fonte de cupons e
três pares de perguntas e respostas. A prévia passou nos 12 cenários,
incluindo os controles. A cliente recebeu a correção com desculpas pelo
Business Suite. Book, `CONHECIMENTO.md` e `JOTFORM.md` atualizados.
Pendências: horário, feriados e delivery da quarta do camarão; revisar as
datas da pausa da terça em dobro (dezembro e janeiro) quando ela voltar. O
site (home e almoço executivo) ainda descreve a terça em dobro sem a pausa.

## 2026-11-22 · Claude — Quarta do camarão e site da terça em dobro

Respostas do proprietário às pendências da entrada anterior. Quarta do
camarão: vale em qualquer horário, inclusive em feriado (leitura do "sim" na
resposta), e não vale para delivery. Ação e fonte da Jotform atualizadas e
testadas na prévia. Site `92bdd9a`: home e almoço executivo avisam que a terça
em dobro não acontece em dezembro de 2026 nem em janeiro de 2027. A conversa
de "Estão com vagas?" fica sem correção, por decisão do proprietário. Pendente
apenas revisar as datas quando a terça em dobro voltar.

## 2026-11-23 · Claude — Stone: recuperação de 16/11 e pedido antes das 4h

CSV de vendas/recebíveis vazios: o filtro no portal da Stone estava por CNPJ;
o histórico mensal veio completo. Os três arquivos (1.804 vendas, 1.468 e 831
recebíveis) foram comparados por identificador e estão inteiros no banco; 259
linhas novas, recálculo concluído. O aviso "sem importação confirmada" vinha
dos CSV vazios que continuavam na lista.
Falha diária da API desde 18/11: XML de 16/11 pedido às 00h41, antes da
liberação, recebeu HTTP 400 e ficou sem repetição. Com autorização do
proprietário, uma única consulta retornou 200; dia fechado pelo cache, 172
baixas conferidas, saúde sem atraso e fechamento contíguo até 21/11.
Correção: XML e Pix só são pedidos a partir das 5h do dia seguinte, sem gastar
a reserva antes disso (`HORA_LIBERACAO` em `api_stone_rotina.py`), com teste.
Detalhes em `docs/INTEGRACAO_API_BANCOS.md`. Sem migration. 22/11 aguarda a
aquisição de hoje, atrasada no GitHub; as vendas já entraram pelo CSV.

## 2026-11-24 · Codex — desempenho recente e campanhas

Revisão somente de leitura: GA4 e reservas comuns em 17–23/11 contra
10–16/11; Instagram em 16–22/11 contra 9–15/11; Search Console e Perfil
Google em 15–21/11 contra 8–14/11. Últimos dias do GA4 sujeitos à consolidação.
Site www: 2.441 sessões, 1.952 usuários ativos e 4.184 visualizações de
página. QR das mesas separado da descoberta externa. Portal: 13 reservas
públicas criadas contra sete; comparecimentos ainda exigem conferir quatro
reservas de datas passadas que permanecem confirmadas.

Meta: conta e 16 campanhas relidas, com término dos dois conjuntos novos
já vencido. ChatGPT: quatro campanhas conferidas, todas com término vencido;
sem linhas de entrega na semana atual. Google Ads aberto na sessão existente,
conta Sir Fisher Praia conferida: Performance Max finalizada, sem gasto ou
impressões nos dois períodos. As 12 ações de conversão ativadas não incluem
reserva confirmada; Store visits informa configuração incorreta. Vínculo
Ads/GA4 relido. Não atribuir visitas ou lucro a cliques, seguidores ou eventos
enviados; consumo das reservas continua sem vínculo com a mídia.

Evidências agregadas e scripts de leitura em `tmp/desempenho-2026-11-24/`,
ignorados pelo Git; sem nomes/contatos de clientes. Recomendações entregues
na conversa. Nenhum anúncio, verba, banco, site, credencial, mensagem ou
agendamento foi alterado. Única alteração versionada: este registro.

## 2026-11-24 · Codex — retomada de Ambiente na Meta

Após a revisão, o proprietário pediu escolher a melhor opção e ativar
novamente. Retomado o reel próprio de Ambiente de 28/09, que teve o menor
CPC do link e uma reserva identificada marcada como comparecida. Nova
rodada, com histórico separado: campanha `120255072476160120`, conjunto
`120255072476520120`, anúncio `120255072477670120`, conta Meta confirmada
`1004410887092327`. Nome: `SF | Ambiente | Retomada 24nov | Trafego`.

Teto desta rodada: R$150, sendo R$130 de orçamento total de mídia e R$20
reservados para impostos, conforme a proposta anterior de sete dias. Início
24/11/2026 às 02h25min01s; término 01/12/2026 às 02h25min01s, Fortaleza.
Meta exibe 03h25 em America/Noronha. Raio de 20 km do restaurante, 21–65
anos; Instagram feed, Stories e Reels. Objetivo tráfego, otimização para
cliques no link, cobrança por impressões. Destino: home oficial, com acesso
ao cardápio e às reservas. Não prometer otimização ou resultado em reservas.
UTM própria: `ambiente_retomada_20261124`, com ID do conteúdo e da campanha.

Criados pausados pela ferramenta validada `scripts/marketing/impulsionar.py`.
Conta, elegibilidade do reel, destino real do CTA, atribuição, orçamento,
público e datas relidos antes de ativar anúncio → conjunto → campanha.
Os três níveis foram relidos com status configurado ACTIVE; anúncio passou
de IN_PROCESS para PENDING_REVIEW. Aprovação e entrega efetiva dependem da
Meta. Não existe acompanhamento recorrente criado por esta tarefa. Revisão
manual recomendada no terceiro dia e no fechamento, com reservas e visitas
separadas de cliques/seguidores. Google, ChatGPT e testes anteriores preservados.

Sete testes do contrato de impulsionamento passaram. Home HTTP 200, links de
reserva e script de atribuição conferidos. Plano, prévia de configuração e
recibos antes/depois em `tmp/meta-ads/`, ignorados pelo Git. Sem alteração de
código, banco, credencial ou automação; somente este registro versionado.

## 2026-11-24 · Codex — acessos ao site nas últimas oito semanas

Consulta GA4 somente de leitura, propriedade oficial e host
`www.sirfisher.com.br`, oito blocos de sete dias de 29/09 a 23/11/2026,
no fuso de Fortaleza. Sessões, usuários ativos e páginas por semana; QR e
Instagram pago separados. Total consultado diretamente em 56 dias:
8.905 sessões, 6.923 usuários ativos e 15.973 visualizações de página.
Semana recente: 2.441 sessões, incluindo 847 por QR e 751 por Instagram
pago. Primeira semana: 415 sessões. Os últimos dias podem consolidar depois.

Contagens estimadas de sessões do GA4 diferem conforme a agregação:
soma dos oito recortes 8.824, consulta única 8.905 (0,9% de diferença).
Primeiro recorte conferido também em consulta independente; visualizações
somadas conciliam em 15.973. Preservados os retornos, sem ajustar números.
Documentação oficial de aproximação por HLL++ consultada. Usuários de
semanas diferentes não devem ser somados como pessoas únicas do período.
Evidências em `tmp/desempenho-2026-11-24/site-8-semanas.json`, ignorado pelo
Git. Sem mudanças no site, anúncios ou banco; apenas este registro versionado.

## 2026-11-24 · Codex — entrega da retomada confirmada

Consulta de acompanhamento às 02h51 de Fortaleza: campanha
`120255072476160120`, conjunto e anúncio agora com status efetivo ACTIVE.
Meta retornou 137 impressões, seis cliques no link e R$0,66 de mídia no dia
24/11 parcial. Confirma entrega após a análise; amostra inicial, sem avaliação
de eficiência. Reel reutilizado: Ambiente, publicação própria de 28/09,
`18113719193582226`, https://www.instagram.com/reel/Dd1jlNbBdIH/.
Mesma mídia da rodada anterior, nova rodada publicitária; não houve nova
publicação orgânica. Teto e datas preservados. Consulta somente de leitura;
comprovante em `tmp/meta-ads/retomada-20261124-status-consulta.json`.

## 2026-11-24 · Claude — trocar o nome na escala

`escalas.html`: o nome na tabela "Escala semanal" virou campo editável (Enter
salva, Esc desfaz). Usa a RPC existente `salvar_escala_funcionario` com os
demais dados iguais, então quem entra herda os turnos. Corrigidos no caminho:
salvar o cadastro em "Equipe" zerava a ordem manual para 100; adicionar pessoa
quebrava depois de gravar e não recarregava; erro ao salvar cadastro ou
horário usava variável inexistente e não mostrava a mensagem. Sem migration.
Testado em navegador com dados fictícios; nenhum nome real foi alterado.

## 2026-11-24 · Claude — escala destaca jornada não cumprida

`escalas.html`: qualquer diferença (a partir de 1 min) entre a semana e a
jornada pinta a linha, mostra "faltam/passa X", lista os nomes no topo e conta
na aba da equipe. Regras do proprietário em `JORNADAS`: 44h com intervalo de
1h; a partir de 16/12/2026, 42h com 1h15, pela data de Fortaleza. Vale o menor
entre a jornada do cadastro e o teto; horas e intervalo são recalculados no
navegador (turno gravado com 1h conta 1h15 após a virada). O seletor de 42h
antes da data é simulação sem edição, porque existe só uma escala gravada.
Views do banco continuam usando o intervalo e a jornada gravados. Sem
migration. Atenção: no 5x2, 1h15 leva 44h a 42h45; faltam 45min na semana.

## 2026-11-24 · Claude — 42h: intervalo de 1h12 e entrada 12min mais tarde

Decisão do proprietário, substitui o 1h15 do recado anterior: a partir de
16/12/2026 a escala usa intervalo de 1h12 e entrada +12min (24min x 5 dias =
2h). `ajustaTurno` aplica sobre turno gravado com o intervalo antigo; gravar
o turno salva o novo e ele não desloca de novo. O início do intervalo só move
para manter a margem de 90min (quatro turnos na escala de hoje). Simulação com
a escala real, em leitura: as 11 pessoas em 42h00. Única consequência: a
primeira entrada vai a 08:52 e a janela abre 08:40 (9h menos 20min), alerta
nos sete dias nas duas equipes; "Chega antes" não foi alterado.

## 2026-11-24 · Claude — 42h: 8min na entrada, 8 no intervalo e 8 na saída

Nova decisão do proprietário, substitui o 12/12: a partir de 16/12/2026,
entrada +8min, intervalo de 1h08 e saída -8min (24min x 5 dias = 2h).
Simulação com a escala real, em leitura: 11 pessoas em 42h00; os mesmos
quatro turnos movem o início do intervalo para manter 90min de margem.
Sobram 8min descobertos na abertura (08:40-08:48) e 8min no fim da janela de
fechamento, todo dia e nas duas equipes; a página mostra 10min porque amostra
em passos de 5. `escala_funcionamento` não foi alterado.

## 2026-11-24 · Claude — janela da escala reduzida

A pedido do proprietário, gravado pelo formulário da própria página:
`escala_funcionamento` com pré-abertura 12min e pós-fechamento 7min (seg a
qui) e 22min (sex a dom). Horários públicos iguais. Conferido no banco e na
produção: zero alertas na escala de hoje (44h) e na simulação de 42h.
O fechamento descoberto por 8min é aceito; se precisar, hora extra. Campos
de minutos passam a aceitar passo de 1.

## 2026-11-24 · Codex — análise do ritmo de vendas do Réveillon

Consultados reservas, pagamentos ativos, lotes, bloqueios e capacidade no
Supabase `portal`, pela rota Management API `database/query/read-only`, com
credencial existente verificada. Cruzamento com consultas reais do MCP
Google Analytics nas páginas do evento e do mapa. Comparação de coortes
pela criação da reserva com pagamento confirmado, em janelas iguais de sete
dias ao redor da virada de 17/11 às 11h07 de Fortaleza; atualização até a
tarde de 24/11 separada da janela fechada. Não confundir pagamento posterior
de reserva do lote anterior com nova venda do lote atual, nem somar sessões
dos dois domínios como pessoas únicas. Dados recentes do GA4 são provisórios.

Recomendação entregue na conversa: considerar vender a mesa da diretoria
no lote vigente e condicionar novo lote à redução do estoque e a novas
vendas com pagamento; cenário de reajuste mantém a consumação e repete o
incremento por pessoa da troca anterior. Conferidos desconto Pix real,
diferença entre contratado e recebido e limite global de cadeiras, incluindo
a necessidade de preservar lugares para o bloqueio do patrocinador.
Não pressupor a capacidade antiga das laterais da documentação: conferir
configuração vigente antes de prometer extras.

Somente este registro versionado. Totais agregados privados em
`reservas/tmp/reveillon-2026-11-24/`, ignorado pelo Git; nenhum dado pessoal,
valor financeiro bruto ou credencial incluído no commit. Sem migration,
mudança de interface, anúncio, preço, bloqueio, reserva ou pagamento.
Liberação da mesa e virada de lote permanecem como decisões do proprietário;
o pedido atual foi de análise.

## 2026-11-24 · Claude — análise da escala contra o movimento (só leitura)

Nada foi alterado na escala, na página ou no banco. Achados: contra os
lançamentos do Saipos (01/09 a 29/10, 59 dias) a defasagem pedido–pagamento
que melhor ajusta é ~45min (correlação 0,886; 75min dá 0,846), e os 75min
escondem a noite; a régua de 4,34 foi calibrada com essa curva e a média
esconde dias cheios (usar também o percentil 80). Com 42h, 8/8/8 alonga
intervalos encadeados de hora em hora e cria sobreposições de 8 a 10min.
Propostas de intervalo e turno entregues ao proprietário, aguardando decisão.

## 2026-11-24 · Codex — uso da consumação do Réveillon no caixa

Esclarecimento operacional, sem alteração dos sistemas: o portal já calcula
a consumação por reserva e a exibe na ficha e na confirmação. Ainda não há
procedimento validado para aplicar esse crédito no Teknisa. O histórico de
adiantamento POS/PC de 30/10 não comprova um recebimento específico para
consumação de evento já paga. Proposta apresentada como pendente de validação:
identificar mesa e reserva, lançar os produtos normalmente e abater o crédito
elegível no fechamento com identificação de valor recebido anteriormente,
cobrando apenas o excedente. Não presumir desconto comercial, novo ingresso
de Pix/dinheiro, transferência automática ou integração com vouchers de sócios.
Definir tratamento de serviço/couvert antes do evento. Nenhuma configuração,
comanda, venda ou recebimento criado. Catálogo local tentou executar, mas
`node` não está no PATH deste PC; manuais locais e manual oficial consultados.

## 2026-11-24 · Claude — escala ajustada ao movimento e régua em 45min

Aprovado pelo proprietário. 27 turnos regravados pela página (44h e folgas
iguais; conferidos 55 de 55 no banco). Cópia anterior e plano em
`tmp/escala-2026-11-24/`, ignorado pelo Git. Migration `20261124190000`
aplicada e registrada: defasagem 45min e capacidade 3,97 (pico 11,885 / 3).
Textos de reserva da página e `supabase_schema.md` acompanham. Correção do
recado anterior: a correlação 0,846 é de 70min, e 0,886 é de 50min.

## 2026-11-25 · Claude — Teknisa: perfil de administrador com menu reduzido

Pedido de acesso total para uma operadora não concluído. O login do
proprietário, no perfil Administrador de sistema, também está sem as telas de
Operador, Perfil e relatórios. Só leitura. Aguarda o suporte Teknisa restaurar
o perfil; detalhe em `docs/TEKNISA_ACESSOS_OPERACAO.md`. Aviso no login: sistema
perde a validade em 25 dias.

## 2026-11-25 · Codex — cliques e pedidos de eventos, últimos 30 dias

Auditoria somente de leitura de 26/10 a 24/11/2026, no fuso de Fortaleza.
GA4 oficial (353205396): `click_eventos` teve 19 eventos e 12 usuários no
período. Origens de sessão: ig/social 5 cliques; chatgpt/paid 4;
chatgpt.com/ai-assistant 3; google_maps/organic 3; qr_code/offline 2;
google/organic 1; site/organic 1. São cliques de saída para eventos, não
contagem de visitas à página ou atribuição dos pedidos.

No portal confirmado, a rota Management API `database/query/read-only`
retornou 1 pedido em 10/11 (approved) no período; histórico atual com 3
pedidos associados a 2 contatos: 2 em 30/09 e 1 em 10/11. Nenhum dado pessoal
foi exportado. A origem dos pedidos só distingue site/admin, sem UTM.

Lacuna confirmada no navegador em produção: `/eventos/` carrega somente
`eventos.js`, sem gtag/dataLayer nem SDK de Analytics. GA4 não retorna
pageviews desse caminho. A função `quote()` calcula sem persistir simulações;
o registro em `event_requests` acontece apenas no envio com contato.
Portanto, visitas diretas, simulações e abandonos históricos não podem ser
quantificados com essas fontes. Não interpretar ausência de medição como zero
nem calcular conversão dividindo pedidos por usuários de cliques.

Evidências agregadas em `tmp/eventos-auditoria-2026-11-25/`, ignorado pelo Git.
Alterado apenas este canal; sem migration, mudanças de site ou banco, envios
de formulário ou nova coleta. Pendente para acompanhamento futuro: medir
visita, etapas, simulação concluída, escolha e envio, preservando a origem.

## 2026-11-25 · Codex — medição do configurador de eventos publicada

Pedido de correção concluído no site, commit `4bf1d2d`. `/eventos/` agora
carrega GA4 e as preferências compartilhadas de publicidade/origem. Coleta
visita, início, etapas, impedimentos, tentativa/sucesso/erro de simulação,
escolha e tentativa/sucesso/erro de envio. Repetir a mesma escolha não duplica
o evento; chamadas simultâneas de cálculo/envio são impedidas. Sucesso de
envio depende da resposta da API. Eventos personalizados só vão para GA4,
sem contato, configuração, data do encontro, código ou texto de erro.
URLs estatísticas sem query/hash, com UTMs nos campos nativos de campanha.

Dia a dia e origem podem ser consultados por `date`, `eventName` e
`sessionSourceMedium`, com `eventCount`/`totalUsers`; usuários do período
não são a soma dos dias/etapas. Não houve alteração do banco, da Edge
Function, do painel nem cadastro de conversões de anúncios. A origem dos
pedidos no banco continua site/admin; a nova análise de canal ocorre no
Analytics. Histórico anterior à publicação não foi recuperado.

Validações: 134 testes Deno passaram; configurador em 390/1440 px passou
localmente e em produção (`eventos_browser_test.py --published`), com API
e SDKs simulados. Teste de CSP/consentimento com SDKs reais passou localmente
e no endereço público (coleta interceptada; GA 6, Ads 3, Meta 1, OpenAI 1).
Sem pedidos reais ou eventos de teste enviados. Capturas dos dois formatos
inspecionadas; limites, erros, recusa e falha do Analytics cobertos. Hashes,
CSP, FAQ e catálogo estático conferidos; CI de assets e GitHub Pages do
commit concluídos com sucesso. Evidências locais no tmp da auditoria.
Contrato e comandos em `site/tools/analytics/README.md`. Coleta nova desde
25/11/2026; bloqueadores/rede ainda podem causar diferenças frente ao banco.
