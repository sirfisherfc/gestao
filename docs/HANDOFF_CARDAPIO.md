# Handoff — Cardápio próprio e conferência operacional

Atualizado em 22/10/2026. Este documento registra o estado real do cardápio em `https://www.sirfisher.com.br/cardapio/` e substitui o handoff anterior que tratava dados não confirmados como definitivamente validados.

## Estado atual

- O cardápio próprio está publicado e substitui a dependência do Hubt para consulta do cliente.
- O catálogo contém 78 produtos e usa como fontes o inventário interno, o HTML anterior e o cardápio impresso.
- Revisão do impresso (Canva "Sir Fisher Praia") com o proprietário em 22/10/2026: saíram Crispy Spicy Chicken, Marine Sandwich, Budweiser 600, Cachaça Premium e Smirnoff Ice; entraram Corona 600 (R$ 23,90) e Adicional Salada (R$ 19,00). Ficaram confirmados Spaten Longneck 355 mL e Bolinha de Peixe 300 g. Nos empanados, o proprietário decidiu publicar o mesmo número em todos os canais: 150 g nos dois Fish & Chips (peso do peixe; empanado chega a 200 g) e 120 g no Fisher Burger (peixe empanado; são 100 g de peixe). O alerta de alergia (impresso e site) passou a dizer que todos os fritos usam o mesmo óleo e que a cozinha frita em panela separada a pedido; o rodapé do impresso troca "peso in natura" por "pesos aproximados" e corrige o contato do consumidor (DECON-CE 0800 275 8001; PROCON Fortaleza 151). Patinha de Caranguejo ganhou CRUSTÁCEOS e a Bolinha, PEIXE. “Farota” era erro de digitação de “farofa”.
- O rascunho do banco (`cardapio_produto`) foi realinhado ao catálogo em 22/10/2026 pela migration `20261022200000_cardapio_realinha_rascunho.sql`: 78 publicáveis, os 5 retirados arquivados (não apagados), foto enviada pelo painel preservada e estado `vigente` mantido; a `20261022230000_cardapio_pesos_e_alerta.sql` levou os pesos e o alerta acima. Nenhuma publicação foi feita; o site segue lendo a cópia embutida. A cada mudança futura: `gerar_migration.py --realinhar <AAAAMMDDHHMMSS>_cardapio_....sql` e `supabase db push` (com `--dry-run` antes).
- Toda mudança de cardápio também vai para o Google: `python scripts/gbp/gbp.py cardapio` (simula) e `--publicar`, depois do push do site. Decisão do proprietário em 22/10/2026.
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

- validar os 78 preços vigentes;
- confirmar medidas, unidades e rendimento dos pratos para compartilhar;
- revisar ingredientes e alérgenos com a cozinha;
- confirmar receitas divergentes, inclusive a marca do energético do Sherlock Holmes Gin;
- registrar a confirmação por versão, sem apagar a proveniência.

Depois dessa conferência, uma nova alteração pode promover o catálogo de `em_conferencia` para `vigente` e retirar apenas os avisos que deixarem de ser necessários.

## Qualidade e continuidade

- Rodar `catalogo_inicial.py` e depois `exportar_snapshot.py` sempre que a origem mudar.
- Conferir que os 78 produtos continuam presentes.
- Validar que não há campos internos no snapshot público.
- Rodar a suíte de aceitação do cardápio e conferir visualmente desktop e mobile antes de publicar.
- O book de atendimento relacionado fica em `docs/BOOK_QA_ATENDIMENTO.md`.
