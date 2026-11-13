# Execução do parecer jurídico do cardápio

Parecer de Pinho & Albuquerque, 12/11/2026, recebido em 13/11/2026.
Documento original privado em Downloads. Esta entrega não certifica a
composição das receitas nem a conformidade integral do estabelecimento.
Texto oficial conferido: [Lei 17.899/2022, art. 1º e anexo](https://www2.al.ce.gov.br/legislativo/legislacao5/leis2022/17899.htm).

## Ajustes executados

**Decisão posterior:** em 13/11/2026 o proprietário pediu retirar o ícone
GLÚTEN do Chope Brahma. Essa decisão substitui a marcação do chope descrita
no histórico abaixo; não equivale a certificação de ausência de glúten.
Catálogo, banco e Google sincronizados pela migration pontual
`20261113160000_cardapio_chope_sem_icone.sql`, sem mudar preços ou outros itens.

- Brownies: cinco ícones já publicados em 12/11, por receita padrão autorizada
  pelo proprietário; ficha técnica real ainda pendente.
- LEITE acrescentado à Patinha, Bolinha, Crocantes de Carne de Sol e Calabresa,
  Pasteizinhos, Dadinho, Isca de Peixe, Fisher Burger e Edimburger. LACTOSE
  preservada. Base: derivados/lactose já declarados no cadastro e item 2 do parecer.
- Big Ben Fries: LEITE e LACTOSE pelo cheddar declarado; demais ícones mantidos.
- Chope Brahma: GLÚTEN, conforme recomendação expressa do parecer.
- Pasteizinhos: recheios já cadastrados (2 queijos, carne e camarão) expostos
  na descrição da lista e traduzidos. Aviso explica que o conjunto de ícones
  reúne os sabores e o molho; não anuncia um recheio como seguro.
- Legenda SOJA/CORANTES corrigida em PT/EN para explicar o símbolo sem afirmar
  composição desconhecida de molhos, óleos, bebidas ou xaropes.
- Inglês usa os mesmos dados alimentares do português. Google FoodMenus passa
  a receber `Contém: ...` e alerta de contaminação cruzada, inclusive nas opções.
- Placa A3 gerada com os dez pictogramas oficiais existentes, nomes legíveis,
  distinção leite/lactose e alerta. Gerador: `scripts/cardapio/gerar_placa_alergenos.py`.
  PDF local: `../output/pdf/Sir-Fisher-Placa-Alergenicos-A3.pdf`.

## Conferência necessária da cozinha

O proprietário informou em 13/11 que não tem as composições/rótulos.
Não substituir essa ausência por receita típica ou afirmação de ausência.

| Ponto | O que obter antes de concluir |
| --- | --- |
| Brownies e charlotes | Receita/rótulo real, chocolate e sorvete; verificar soja, castanhas e amêndoas |
| Todos os molhos e óleo | Marca, fornecedor, lista completa e declaração de alérgenos; mapear pratos que usam cada insumo |
| Melancita, Sherlock e Tropicall | Rótulos dos energéticos, versões e sabores; verificar corantes |
| Caipifruta, Margarita e Fitzgerald | Rótulos das polpas/triple sec e receita/rótulo do bitter |
| Moscow Mule | Receita da espuma e demais insumos; confirmar se há clara de ovo |
| Patinha e Bolinha | Ficha do empanamento e ovo; ícones existentes preservados, sem confirmação por inferência |
| Pasteizinhos | Massa, recheio de cada sabor e molho; separar ícones só após conferir cada composição |
| Camarão alho e óleo | Justificativa do GLÚTEN; manter até esclarecimento, como orienta o parecer |
| Caldo de Peixe | Justificativa de GLÚTEN/OVO; manter até esclarecimento |
| Dadinho e Calabresa Acebolada | Receita/ficha do fornecedor, molho e preparo; Dadinho teve LEITE acrescentado |
| Pratos para compartilhar | Farofa, manteiga, demais acompanhamentos e molho; confirmar LEITE/LACTOSE e SOJA |
| Pesos | Fase da pesagem por produto; empanados têm decisão específica anterior, não aplicar nota genérica |

## Ações físicas e canais externos

Imprimir a placa em cores, em A3 e escala 100%, e afixar em local visível no
caixa/balcão e na área de mesas; conferir legibilidade e registrar foto/data.
A geração do arquivo não comprova afixação.

Impresso/Canva: atualizar a proposta de mesa `DAHYx8a8mAI` e o A3 em uso
`DAHY1RSheg4` com as mesmas marcações; reimpressão depende do responsável.
Canva não tem ferramenta conectada nesta sessão. Não presumir atualização.
Delivery: identificar se há canais ativos, comparar cada item com o catálogo
e incluir `Contém: ...` quando não houver pictogramas. Não há conta de delivery
identificada/conectada nesta sessão. Google não é plataforma de delivery.

## Rotina de revisão e publicação

Cada inclusão, mudança de receita, acompanhamento, molho, insumo ou fornecedor
exige conferir os dez insumos do Anexo I, registrar a ficha/versão e rótulos no
campo de referência alimentar e marcar a conferência explícita no painel.
Uma lista vazia de alérgenos exige a mesma conferência; nunca significa dispensa.
Sem evidência, salvar rascunho e manter a pendência.

Migration `20261113150000_cardapio_parecer_juridico.sql`: atualiza somente os
campos alimentares dos onze produtos e a descrição dos Pasteizinhos, com
guardas de igualdade. Não altera preços, porções, fotos ou estoque.
Funções privadas verificam referência/data/atestado; trigger invalida revisão
antiga se nome/composição/opções/ícones mudarem sem novo atestado. Preço e
disponibilidade preservam a revisão. `cardapio_publicar` mantém autorização
e bloqueia receitas sem revisão, preservando a versão anterior.
Revisão é atestado do operador, não validação automática de receita.
Restauração também exige revisão e recusa receitas históricas diferentes da
prévia atual revisada; o operador deve conferir o rascunho e publicar nova versão.

Sem tabelas/views novas nem ampliação de acesso. Funções privadas com EXECUTE
revogado de public/anon/authenticated; RPC existente mantém seus grants.
Nova publicação integral pelo painel ficará bloqueada até concluir a revisão
dos itens de fabricação própria. O site continua servindo o snapshot existente,
com os ajustes pontuais desta entrega, sem criar publicação integral no banco.
No início da tarefa não havia publicações no banco nem histórico a restaurar.

Não usar uma exportação local para publicar receitas novas sem revisão.
O pipeline estático exige conferência editorial humana; a trava descrita
protege o botão de publicação do painel. Preços e porções de decisões anteriores
foram preservados. Parecer e fichas devem ser revalidados pela operação.

## Validação da entrega

Migration ensaiada duas vezes na mesma transação, com rollback; exercitados
bloqueio sem referência, aceite com atestado fictício, invalidação por troca de
receita e preservação por preço/estoque. Após aplicação, conferidos 80 registros
contra a fonte e hash dos demais campos; zero atestados fictícios persistidos.
Ensaio reexecutável: `scripts/cardapio/test_conformidade.sql` (sempre rollback).

Site: 47 testes de aceitação; igualdade dos ícones dos 80 produtos em PT/EN,
390px/1366px, sem overflow nem erro JavaScript; formulário administrativo com
cliente simulado, sem autenticação nem escrita externa. Navegador integrado
indisponível; usado Edge local. QA visual de placa A3 e quatro páginas do
checklist. Testes relevantes: oito de perfil QR, três de Google FoodMenus,
dois de assets Pages; cadeia de 243 migrations, quality gates, assets, CSP,
FAQ e pré-renderização aprovados. Uma varredura ampla de Analytics no Python
geral não carregou módulos Google Analytics ausentes nesse interpretador;
não faz parte do fluxo alterado. As suítes aplicáveis passaram separadamente.

Google sincronizado pela rotina existente e relido, mantendo 83 itens/opções
e os preços; 29 com `Contém: ...`, descrições comparadas integralmente com a
exportação esperada. Site `9547c86`, Pages built; HTTP 200 e igualdade de HTML,
JSON e scripts PT/EN no domínio público. Sem mensagem enviada, nova rotina
ou publicação em delivery.
