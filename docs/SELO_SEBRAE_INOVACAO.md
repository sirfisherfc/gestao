# Sistemática de Melhoria Contínua e Desenvolvimento — Sir Fisher

Documento de referência para o item 6.4 (Gestão da Inovação) do checklist de auditoria.

| | |
|---|---|
| Empresa | Sir Fisher |
| Vigente desde | 14 de março de 2026 |
| Responsável | Direção, com execução pela gerência |
| Evidências do período | 14/03/2026 a 14/09/2026 |

---

## 1. Objetivo e abrangência

Garantir que toda ideia de melhoria, problema recorrente ou oportunidade identificada na
operação seja registrada, avaliada, decidida e tenha o resultado documentado — em vez de
se perder em conversa.

A sistemática abrange quatro frentes: **produto** (pratos, bebidas e portfólio),
**processo** (cozinha, salão, compras e estoque), **tecnologia** (sistemas próprios e de
terceiros) e **pessoas** (jornada e dimensionamento de equipe).

## 2. Onde fica o registro

O registro é feito no módulo **Melhoria e Inovação** do painel de gestão da empresa
(`admin.sirfisher.com.br/melhoria_inovacao.html`), desenvolvido internamente.

O acesso é nominal, por conta individual autenticada, e liberado por perfil (direção,
sócio e gerência). Todo registro fica vinculado à conta de quem o criou, com data e hora.
Nenhum registro pode ser apagado sem deixar rastro: o módulo mantém uma linha do tempo
automática de cada mudança de situação, com autor e data.

## 3. As cinco etapas

Toda ideia percorre a mesma sequência. A etapa em que cada uma está fica visível na lista.

| Etapa | O que significa | O que é exigido para avançar |
|---|---|---|
| **Recebida** | A ideia ou o problema foi registrado. | Apenas um título. O registro leva menos de 30 segundos, de propósito: a barreira de entrada precisa ser baixa para que a equipe use. |
| **Em avaliação** | A direção ou a gerência analisa viabilidade, custo, risco e impacto. | Uma decisão: seguir, descartar ou aguardar. |
| **Em andamento** | A ideia foi aprovada e está sendo executada ou testada. | Responsável nomeado, prazo definido e a próxima ação concreta escrita. |
| **Concluída** | Implantada, com efeito verificado. | **Obrigatório** registrar o resultado e o aprendizado. O sistema não permite concluir sem esse texto. Impacto financeiro e evidência em arquivo ou link são opcionais. |
| **Descartada** | Avaliada e não seguida. | **Obrigatório** registrar o motivo. O sistema não permite descartar sem justificativa. |

A obrigatoriedade do texto na conclusão e no descarte é a garantia de que a sistemática
produz aprendizado registrado, e não apenas movimentação de status.

## 4. Papéis

- **Qualquer pessoa com acesso** registra uma ideia ou um problema, a qualquer momento.
- **Gerência** avalia, executa e mantém a próxima ação atualizada.
- **Direção** decide sobre investimento, aprova testes e é quem descarta, sempre com motivo.

A origem de cada registro é classificada em Equipe, Cliente, Fornecedor, Auditoria, Gestão
ou Outra, o que permite verificar de onde a melhoria está de fato nascendo.

## 5. Indicadores acompanhados

Calculados automaticamente pelo módulo, sem digitação, e visíveis no topo da tela:

- total de ideias, e quantas estão abertas, em andamento, concluídas, descartadas e vencidas;
- **taxa de conclusão**;
- **prazo médio de conclusão**, em dias, da primeira manifestação até a conclusão;
- **percentual concluído dentro do prazo**;
- **impacto financeiro acumulado** das melhorias concluídas, quando mensurável.

### Posição em 14/09/2026

| Indicador | Valor |
|---|---|
| Ideias registradas | 26 |
| Concluídas | 8 |
| Descartadas, com motivo registrado | 3 |
| Em aberto | 15 |
| Taxa de conclusão | 31% |
| Prazo médio de conclusão | 40 dias |
| Pessoas distintas que registraram | 6 |
| Áreas alcançadas | 9 |

Origem dos registros: Gestão 12, Equipe 10, Cliente 2, Auditoria 1, Outra 1.
As 20 ideias do histórico têm responsável nomeado; as 6 ideias mais recentes aguardam quem as assuma.

## 6. Evidências disponíveis para auditoria

1. O próprio módulo, acessível em tela, com as 26 ideias do período de 14/03 a 14/09/2026.
2. A linha do tempo automática de cada ideia, com autor e data de cada mudança.
3. O texto de resultado e aprendizado das 8 concluídas e o motivo das 3 descartadas.
4. Evidências anexadas por ideia (arquivo em repositório privado ou link).
5. Os registros de desenvolvimento dos sistemas próprios, datados, no repositório da empresa.

---

# Caso demonstrativo — Dimensionamento da equipe pela curva de movimento

Registro correspondente no módulo: *"Ajustar a equipe à curva de movimento da casa"*.
Aberto em 22/04/2026, concluído em 18/08/2026. Ciclo de 118 dias.

### Situação

A escala era montada por hábito e por disponibilidade, não por demanda. O efeito era duplo:
mão de obra ociosa de segunda a quarta e equipe curta no pico de sexta a domingo. O banco de
horas estava negativo — a empresa pagava mais hora do que usava.

### Pesquisa

Em vez de estimar, a demanda foi medida a partir das transações reais de venda dos 12 meses
anteriores. Duas decisões metodológicas foram necessárias:

- **Deslocamento pedido–pagamento.** O pagamento acontece no fim da refeição; o trabalho de
  salão e cozinha aconteceu antes. Cruzando a curva de lançamento do sistema de vendas com a
  curva de pagamento, estimou-se uma defasagem de **75 minutos**. Cada transação é deslocada
  individualmente, e não a curva já agregada, para o resultado não depender de a defasagem
  ser múltipla de uma hora.
- **Capacidade por pessoa.** Definida como a carga do pico efetivamente atendido — domingo às
  17h, com 3 pessoas e 13,00 vendas/hora — resultando em **4,34 vendas/hora por pessoa**.

Os dois valores são parâmetros configuráveis e recalibráveis, não constantes no código.

### Hipótese

Migrar a escala de 6×1 para 5×2 permitiria concentrar até 6 pessoas no pico, abrir mais tarde
nos dias de baixo movimento, reduzir o custo de transporte e alimentação em um dia por semana
por pessoa e conceder duas folgas semanais — sem perda de atendimento.

### Alternativa avaliada e rejeitada

Em 23/04/2026 foi proposta a ampliação imediata do quadro. A proposta foi registrada, avaliada
e **descartada**, com o motivo documentado: testar primeiro a mudança de escala e medir o
resultado antes de assumir custo fixo adicional. O registro da recusa está no módulo, junto
com as ideias aprovadas.

### Desenvolvimento

Foi desenvolvida internamente uma rotina de escalas no painel de gestão, que sobrepõe a
jornada de cada pessoa à curva de demanda hora a hora e sinaliza os desvios de jornada,
intervalo e interjornada. A ferramenta foi publicada em 18/08/2026.

### Implantação e calibração

A cozinha migrou para 5×2 e o salão iniciou a migração. Após o uso real, dois parâmetros
foram recalibrados contra a operação: a janela de pré-abertura passou de 30–40 para 20
minutos, e a capacidade por pessoa de 4,18 para 4,34 — o valor anterior vinha de um cálculo
externo que tornava a régua circular. A correção está documentada e datada.

### Resultado registrado

- Régua objetiva de dimensionamento publicada e em uso, substituindo a decisão por hábito.
- Cozinha em 5×2; salão em migração.
- Economia de transporte e alimentação de um dia por semana por pessoa, redistribuída como
  aumento do benefício para toda a equipe.
- Duas folgas semanais por pessoa.

### Aprendizado

Medir antes de decidir mudou a decisão: a leitura inicial pedia mais gente, e o dado mostrou
que o problema era distribuição, não quantidade. O parâmetro que sustenta a régua é revisto
contra a operação real, e não tratado como número fixo.

---

## Outros casos do período

| Caso | Tipo | Situação | Resultado |
|---|---|---|---|
| Teste de dois pratos novos de entrada (07/06/2026) | Produto | Concluída | Entraram no cardápio com preço e CMV calculados; divergência de gramatura corrigida contra a ficha técnica antes da venda. |
| Mix de cervejas 600 ml (10/06/2026) | Produto / portfólio | Descartada | Manter seis rótulos fixos foi recusado após análise de custo por mililitro e risco de um rótulo canibalizar a venda do outro. Substituído por mix menor com teste controlado de 30 dias. |
| Portal de reservas próprio (09/07/2026) | Tecnologia | Concluída | Sistema próprio em domínio da empresa, com painel, confirmação e lembrete automáticos, substituindo ferramenta contratada. Testado de ponta a ponta pela equipe antes da virada. |
| Medição do anúncio até o comparecimento (18/08/2026) | Tecnologia / marketing | Concluída | A origem do anúncio é preservada da visita ao site até a reserva e o comparecimento, permitindo avaliar retorno real de mídia. |
| Alerta antecipado de validade e estoque (01/04/2026) | Processo | Concluída | Contagem semanal separada do fechamento mensal, com registro de revisões, após episódio de lote próximo do vencimento detectado tarde. |

---

## Correspondência com o checklist

| Item | Onde está a evidência |
|---|---|
| 6.4.1 — iniciativas de inovação alinhadas ao planejamento | Módulo Melhoria e Inovação; sistemas próprios de gestão, reservas e análise. |
| 6.4.2 — cultura de inovação estabelecida e disseminada | 26 registros de 6 pessoas distintas, em 9 áreas, com 10 de 26 originados pela equipe e 2 por clientes. Acesso nominal liberado à gerência. |
| 6.4.3 — sistemática estabelecida e implementada para P&D | Seções 1 a 6 deste documento, com o caso demonstrativo e os cinco casos adicionais do período. |
| 6.4.4 — gestão de indicadores de inovação e ações de melhoria | Indicadores da seção 5, calculados automaticamente, com responsável, prazo e próxima ação por ação de melhoria. |
