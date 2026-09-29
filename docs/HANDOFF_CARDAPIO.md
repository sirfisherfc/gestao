# Handoff — Cardápio próprio e conferência operacional

Atualizado em 29/09/2026. Este documento registra o estado real do cardápio em `https://www.sirfisher.com.br/cardapio/` e substitui o handoff anterior que tratava dados não confirmados como definitivamente validados.

## Estado atual

- O cardápio próprio está publicado e substitui a dependência do Hubt para consulta do cliente.
- O catálogo contém 81 produtos e usa como fontes o inventário interno, o HTML anterior e o cardápio impresso.
- Preços, porções e marcações alimentares ainda não receberam uma conferência formal e completa da cozinha/operação; por isso o estado editorial volta a ser `em_conferencia`.
- A interface deve deixar claro quando uma medida diverge ou quando uma informação alimentar foi apenas transcrita do impresso.
- Não se deve transformar ausência de símbolo no impresso em afirmação de ausência de alérgeno.

## Decisões preservadas

- A referência é o cardápio interno versionado; o Hubt não é fonte operacional nem participa dos cálculos de eventos.
- As abas horizontais, busca, modais, legenda de alérgenos, rodapé institucional e botão de voltar ao topo permanecem.
- Os pratos de “Pra Dividir” usam bases de imagem com o sufixo `-para-dividir-sir-fisher`, evitando colisão com as fotos do almoço executivo.
- O aviso geral orienta clientes com alergias ou restrições a consultar a equipe antes do pedido.
- Notas internas, fontes, pendências e divergências técnicas não podem vazar como campos brutos no JSON público.

## Pipeline

```text
scripts/cardapio/catalogo_inicial.py
  -> scripts/cardapio/catalogo_inicial.json
  -> scripts/cardapio/exportar_snapshot.py
  -> site/cardapio/dados/cardapio.json
  -> bloco CARDAPIO-DADOS em site/cardapio/index.html
```

`catalogo_inicial.py` é a origem auditável. Os arquivos JSON e o bloco embutido no HTML são derivados e devem ser regenerados, nunca corrigidos manualmente.

## Regras de publicação

1. Divergência entre fontes fica como `em_conferencia`; não escolher automaticamente um dos valores.
2. Porção divergente não exibe número ao cliente.
3. Porção sem texto fica como não informada, ou em conferência quando existir divergência registrada.
4. Declarações alimentares transcritas do impresso levam aviso de que não substituem ficha técnica.
5. Produto sem marcação no impresso não pode ser anunciado como livre de alérgenos.
6. Mudanças de foto devem manter a separação entre pratos individuais e pratos para compartilhar.

## Conferência necessária com a operação

- validar os 81 preços vigentes;
- confirmar medidas, unidades e rendimento dos pratos para compartilhar;
- revisar ingredientes e alérgenos com a cozinha;
- confirmar receitas divergentes, inclusive a marca do energético do Sherlock Holmes Gin;
- registrar a confirmação por versão, sem apagar a proveniência.

Depois dessa conferência, uma nova alteração pode promover o catálogo de `em_conferencia` para `vigente` e retirar apenas os avisos que deixarem de ser necessários.

## Qualidade e continuidade

- Rodar `catalogo_inicial.py` e depois `exportar_snapshot.py` sempre que a origem mudar.
- Conferir que os 81 produtos continuam presentes.
- Validar que não há campos internos no snapshot público.
- Rodar a suíte de aceitação do cardápio e conferir visualmente desktop e mobile antes de publicar.
- O book de atendimento relacionado fica em `docs/BOOK_QA_ATENDIMENTO.md`.
