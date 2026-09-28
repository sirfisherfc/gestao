# Handoff — experimento do ChatGPT Ads

Atualizado em 28/09/2026. Este documento permite que outra IA retome a análise sem depender do histórico da conversa.

## Acesso e segurança

- Usar o plugin **ChatGPT Ads Manager** e resolver a conta pelo nome **Sir Fisher**.
- O acesso conectado foi validado com papel de administrador.
- Nunca registrar IDs internos da conta, campanha, grupo ou anúncio neste documento.
- Nunca copiar nem exibir valores brutos de `oppref`; esse identificador deve ser tratado como opaco.
- Leituras de desempenho devem usar os recursos de insights/review. Qualquer alteração exige leitura atual, proposta de diferença mínima, confirmação e leitura posterior.

## Estado confirmado da campanha

- Campanha: **Sir Fisher campaign**.
- Status: ativa.
- Objetivo: alcance.
- Orçamento: R$40 por dia.
- Segmentação geográfica: Ceará.
- Grupo: **Turismo Fortaleza — Beira-Mar**.
- Um anúncio ativo.
- Término prorrogado de 30/09/2026 para **07/10/2026 às 17:17, horário de Fortaleza**.
- A prorrogação acrescenta no máximo aproximadamente R$280 ao período que já estava aprovado.
- Não foram alterados objetivo, orçamento diário, geografia, grupo, anúncio, texto ou imagem.

## Diagnóstico de referência

- Leitura mais recente antes do experimento: 6.169 impressões, 83 cliques, R$313,64 de gasto, CTR de 1,35% e CPC de R$3,78.
- Não havia conversões atribuídas no Ads Manager.
- GA4, 30 dias, `chatgpt / paid`: 117 sessões, 113 usuários e 120 visualizações.
- Entre esse tráfego, havia 13 eventos `click_menu` de 12 usuários e 1 `click_maps` de 1 usuário; não havia reserva nem WhatsApp registrados.
- Zero reservas não prova, sozinho, que o rastreamento está quebrado. O estado observado era `no_attribution_evidence`, sem alertas de qualidade.
- Meta econômica provisória: R$10 por visita efetiva, a validar. Com conta média aproximada de R$80, isso representa 12,5% do pagamento bruto, antes de margem e tamanho do grupo.

## Implementação publicada

Site publicado no commit `317ffc8` do repositório `site`.

- Os links de cardápio da home agora levam ao cardápio próprio em `/cardapio/`, não ao domínio externo anterior.
- A origem é preservada em `sf_attribution_v1` e compartilhada com o subdomínio de reservas por até 90 dias.
- Links para o portal de reservas recebem os parâmetros de atribuição armazenados.
- O Pixel do ChatGPT Ads foi centralizado e está presente nas páginas relevantes.
- O cardápio ganhou caminhos para reserva, WhatsApp e ligação.
- A política de privacidade foi atualizada para explicar os sinais de intenção.
- A versão em produção foi verificada após a publicação.

Eventos enviados ao ChatGPT Ads:

- `page_viewed`: visualização de página;
- `menu_opened`: abertura real do cardápio próprio;
- `directions_requested`: clique para obter rota/abrir Maps;
- `whatsapp_started`: início de contato pelo WhatsApp;
- `phone_call_started`: início de ligação;
- `reservation_started`: clique para iniciar uma reserva.

Esses eventos são sinais distintos. Nenhum deles deve ser contado automaticamente como `visit_realized`.

## Hierarquia de resultados

1. Engajamento: página vista e navegação.
2. Intenção média: `menu_opened`.
3. Intenção alta: rota, WhatsApp, ligação ou início de reserva.
4. Resultado comercial: reserva confirmada, visita realizada e receita/pagamento.

Os eventos comerciais já conhecidos na fonte são `appointment_scheduled` e `visit_realized`. Não substituir esses resultados por cliques.

## Janela e critérios do experimento

- Usar como janela principal os sete dias completos de **29/09 a 05/10/2026**.
- Fazer a revisão em **06/10/2026**; a campanha permanece ativa até 07/10 às 17:17 para permitir decisão e reação.
- Manter durante a janela: R$40/dia, objetivo de alcance, Ceará, grupo e criativo atuais.
- A principal mudança avaliada é a jornada mensurável pelo cardápio próprio.
- Não prometer significância estatística: no CPC anterior, a ordem de grandeza é de 70 a 75 cliques para cada R$280.

Critérios:

- **Continuar:** mensuração funcionando e custo dos sinais de intenção compatível com uma rota plausível até R$10 por visita.
- **Ajustar:** há abertura de cardápio, mas quase nenhuma ação de alta intenção; revisar página, chamada e oferta antes de elevar verba.
- **Interromper/reconstruir:** cerca de 70 cliques adicionais sem ação de alta intenção, ou custo por ação de alta intenção acima de R$10 sem evidência de boa conversão em visita.
- **Inconclusivo:** menos de 50 sessões atribuídas ou mensuração incompleta.

O custo máximo sustentável por ação de alta intenção depende da taxa real de comparecimento:

- 25% viram visita: até R$2,50 por ação;
- 50% viram visita: até R$5,00 por ação;
- 75% viram visita: até R$7,50 por ação.

## Lacunas que ainda exigem operação da casa

- Movimento médio de segunda a quinta por faixa de horário.
- Margem aproximada, não apenas conta média.
- Número médio de pessoas por pagamento.
- Registro de origem no caixa ou pergunta simples à mesa para estimar visitas sem reserva.
- Confirmação de quais diferenciais podem ser comprovados em anúncio.
- Horários exatos com maior capacidade ociosa.

Na próxima revisão, cruzar Ads Manager, GA4, reservas e dados da casa. Não aumentar orçamento antes desse cruzamento.
