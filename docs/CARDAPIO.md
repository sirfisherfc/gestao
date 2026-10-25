# Cardápio — arquitetura, manutenção e migração

Atualizado em 25/10/2026. A fonte editorial usada no site é o catálogo interno
versionado. O pipeline atual está em
[HANDOFF_CARDAPIO.md](HANDOFF_CARDAPIO.md), com as decisões mais recentes do
proprietário e as pendências de preços, porções e alérgenos.

```text
scripts/cardapio/catalogo_inicial.py
  → scripts/cardapio/catalogo_inicial.json
  → scripts/cardapio/exportar_snapshot.py
  → site/cardapio/dados/cardapio.json
  → bloco CARDAPIO-DADOS em site/cardapio/index.html
```

O cardápio próprio substituiu o Hubt. O cliente pode abri-lo pela home e pelas
páginas comerciais, em português e inglês. O QR das mesas continua levando à
home com origem `qr_code`; o cliente toca em “Cardápio”. O QR novo da entrada
leva ao cardápio com a campanha externa `cardapio_entrada`.

O painel mantém tabelas de rascunho e publicação no Supabase. O JavaScript do
site pode conferir a view de publicação ativa `cardapio_publico`, depois de
renderizar a cópia embutida. Essa capacidade não torna o rascunho fonte do
site. Nas revisões de 22 e 23/10, o rascunho foi realinhado ao catálogo sem
publicar uma nova versão pelo painel. Não trocar a fonte editorial ou exportar
`--do-banco` como rotina de produção sem reconciliar uma publicação ativa
com as decisões do catálogo versionado.

As seções abaixo descrevem o contrato do painel e os cuidados de manutenção.
A migração planejada em setembro foi superada pelo pipeline acima.
As divergências das fontes históricas estão em
[CARDAPIO_CONFERENCIA.md](CARDAPIO_CONFERENCIA.md).

---

## 1. As duas ideias que sustentam a estrutura

### Rascunho e publicação no painel

`cardapio_produto` guarda o que a operação edita no painel. O contrato de
leitura pública do banco usa `cardapio_publicacao`: uma fotografia do catálogo
criada ao apertar *Publicar*, com uma linha por versão. O site usa a cópia
embutida e só pode consultar essa publicação por `cardapio_publico`.

Isso resolve três coisas de uma vez: meia edição não vaza para a mesa;
publicação que falha não derruba o que está no ar; e dá para voltar atrás.

### Disponibilidade fica fora da fotografia

"Acabou a picanha" precisa valer na mesa em segundos, sem publicar nada — e
**não pode** ser desfeito por alguém restaurando uma versão editorial antiga.

Por isso `disponivel` mora em `cardapio_produto` e a view pública aplica o
valor de hoje por cima do que estava congelado na publicação:

```sql
jsonb_set(p.conteudo, '{produtos}', (
  select jsonb_agg(jsonb_set(item, '{disponivel}', to_jsonb(d.disponivel)) ...)
  from jsonb_array_elements(p.conteudo->'produtos') with ordinality as t(item, ord)
  left join public.cardapio_produto d on d.id = item->>'id'
))
```

Restaurar a versão 3 traz os textos da versão 3 e mantém esgotado o que está
esgotado hoje.

---

## 2. Objetos criados

Migration `20260922000000_cardapio_catalogo.sql`.

| Objeto | Para que serve |
|---|---|
| `cardapio_categoria` | Categorias, com `grupo` (`comer`/`beber`/`extras`) e subgrupos. |
| `cardapio_produto` | Rascunho do catálogo. Guarda também proveniência, pendências e notas internas. |
| `cardapio_variante` | Jeitos de pedir o mesmo produto, com preços próprios. Viram faixa de preço na lista. |
| `cardapio_adicional` | Acréscimo cobrado à parte. **Nunca** é preço do produto. |
| `cardapio_sinonimo` | Variantes de grafia e de região para a busca (macaxeira/mandioca/aipim). |
| `cardapio_aviso` | Avisos gerais. Ficam separados da matriz por prato. |
| `cardapio_estado` | Uma linha: `em_conferencia` ou `vigente`. |
| `cardapio_publicacao` | Fotografias publicadas. Índice parcial único garante uma ativa por vez. |
| `cardapio_disponibilidade_log` | Quem marcou o quê como esgotado, quando e por quê. |

### O campo `porcao`

Medidas separadas, porque não são a mesma coisa:

```json
{ "texto": "6 unidades / 360 g",
  "principal": { "valor": 300, "unidade": "g", "alcance": "proteina" },
  "total":     { "valor": 360, "unidade": "g" },
  "unidades":  { "quantidade": 6, "rotulo": "bolinhos" },
  "rende_pessoas": null,
  "estado": "declarado", "divergencia": null, "nota": "peso in natura…" }
```

`rende_pessoas` só é preenchido se a cozinha confirmar. **Peso nunca vira
número de pessoas**: os seis pratos para compartilhar declaram 300 g de
proteína e nenhuma fonte diz para quantos serve.

`estado` decide o que o cliente lê:

| `estado` | O portal mostra |
|---|---|
| `declarado` / `parcial` | o número |
| `divergente` | “Porção em conferência” |
| `ausente` | nada sobre porção |

### O campo `alimentar`

Camadas separadas por grau de confiança:

```json
{ "declarados": ["GLÚTEN", "LACTOSE"],
  "estado": "declarado_no_impresso",
  "divergencias": ["O nome cita caranguejo, mas não há símbolo de CRUSTÁCEOS."],
  "alegacoes": [],
  "confirmado_cozinha": [],
  "contato_cruzado": [] }
```

**Lista vazia significa “não revisado”, nunca “não contém”.** Enquanto
`confirmado_cozinha` estiver vazio, o portal mostra a ressalva e manda falar
com a equipe — e a busca por “glúten”, “vegano” ou “sem lactose” devolve essa
orientação em vez de uma lista que pareceria uma classificação segura.

Os dez rótulos do impresso são preservados como estão. LACTOSE e LEITE são
rótulos distintos lá e continuam distintos aqui.

---

## 3. Contrato de leitura pública

**Um único objeto do cardápio tem `grant` para `anon`:**

```sql
grant select on public.cardapio_publico to anon, authenticated;
```

`cardapio_publico` devolve só `versao`, `publicado_em` e `conteudo` da
publicação ativa. O `conteudo` é montado por
`private.cardapio_montar_publicacao()`, que é **o único lugar que decide o que
o cliente enxerga**. O que não for montado lá não existe para o portal:
rascunho, nota interna, pendência, fonte, alegação a conferir, custo, margem e
usuário não passam.

Todas as tabelas ficam com RLS ligado e `revoke all` para `anon` e
`authenticated`. O painel lê pelas views `app_cardapio_*`, com o mesmo portão
`usuario_pode_acessar_pagina('cardapio.html')` das outras rotinas, e escreve
pelas RPCs `security definer`. Nenhuma view toca `auth.users`: o nome de quem
editou sai de `private.nome_exibicao_usuario(uuid)`.

O navegador recebe apenas a chave anônima, que já é pública no painel.

### Testes de segurança a rodar depois de aplicar a migration

```sql
-- 1. Leitura anônima do catálogo publicado: DEVE funcionar
set role anon;  select versao from public.cardapio_publico;

-- 2. Leitura anônima do rascunho: DEVE falhar
set role anon;  select * from public.cardapio_produto;              -- permission denied
set role anon;  select * from public.app_cardapio_produtos;         -- permission denied

-- 3. Escrita anônima: DEVE falhar
set role anon;  select public.cardapio_publicar(null);              -- permission denied
set role anon;  update public.cardapio_produto set preco_centavos = 1;

-- 4. Usuário logado sem o papel da página: DEVE ver zero linhas nas views
--    app_cardapio_* e receber "Sem permissão" nas RPCs.
```

---

## 4. Operações do painel

| Situação | O que fazer | Precisa publicar? |
|---|---|---|
| Acabou um item | **Marcar esgotado** na lista | Atualiza a disponibilidade do banco; conferir uma publicação ativa e o efeito no site. |
| Voltou a ter | **Voltou a ter** na lista | Não. |
| Mudou preço | Editar → Salvar rascunho → **Publicar** | Sim. |
| Foto nova | Editar → enviar foto → **Publicar** | Sim. |
| Item novo | Editar/criar em rascunho → **Publicar** | Sim. |
| Errou e quer voltar | **Versões publicadas** → Restaurar | A restauração já publica. |

As operações acima alteram o banco. Para atualizar a cópia estática usada no
site, seguir o pipeline do início deste documento e o handoff; o botão do
painel, isoladamente, não atualiza os arquivos publicados no GitHub Pages.

A tela mostra qual versão do banco está ativa, quantos produtos foram
alterados desde a publicação e quantos têm campo a conferir. Antes de publicar,
aparece o resumo do que muda.

**Edição concorrente:** `cardapio_salvar_produto` recebe o `atualizado_em` que
a tela carregou. Se alguém salvou nesse meio-tempo, o salvamento é recusado com
`EDICAO_CONCORRENTE` e a tela manda recarregar, em vez de sobrescrever em
silêncio.

**Publicação que falha:** a transação não confirma e a versão ativa continua
intacta. Catálogo vazio também é recusado.

---

## 5. Publicação usada no site

Depois de uma alteração confirmada no catálogo:

1. Rodar `catalogo_inicial.py` e `exportar_snapshot.py` pelo fluxo de arquivo.
2. Conferir os 78 produtos e a ausência de campos internos nos derivados.
3. Executar as verificações do cardápio, revisar a interface e publicar o site.
4. Conferir os arquivos públicos e, pela decisão de 22/10/2026, simular e
   publicar o FoodMenus com `scripts/gbp/gbp.py cardapio` e `--publicar`.

Para realinhar o rascunho no banco, usar uma migration nova gerada por
`gerar_migration.py --realinhar`, conforme o handoff, preservando fotos enviadas
pelo painel e itens arquivados. Isso não publica o rascunho no site.

O site renderiza primeiro o catálogo embutido. A leitura opcional de uma
publicação ativa mais recente no banco pode oferecer um aviso de atualização;
sem ela, o cliente continua com a cópia estática. Uma troca de fonte exige
verificar versão, conteúdo e regras editoriais nas duas bases.

## 6. Percurso do QR e atribuição

O QR das mesas segue este caminho, por decisão do proprietário de 22/09/2026:

```text
QR das mesas → /qr/ → home com origem qr_code → botão Cardápio → /cardapio/
```

A publicação do cardápio próprio mudou o destino do botão. O redirecionamento
continua abrindo a home. O QR novo da entrada usa
`/cardapio/?utm_source=qr_code&utm_medium=offline&utm_campaign=cardapio_entrada`.
As campanhas dos dois materiais devem continuar separadas no Analytics.

Atribuição real de anúncio, Maps e QR precisa ser preservada no percurso.
Usar `sf_origin` como contexto de navegação e `sf_cta` para a posição do botão.
As UTMs artificiais de navegação interna foram removidas em 06/10; não criar
`utm_source=site` e `utm_medium=organic` nos links internos.

O plano antigo de setembro que mantinha o Hubt e previa uma futura virada
fica no histórico Git. O almoço executivo também deve seguir o inventário e
os links atuais do site; o plano antigo não comprova uma dependência atual
do Hubt.

---

## 7. Scripts

Em `scripts/cardapio/`:

| Script | O que faz |
|---|---|
| `catalogo_inicial.py` | A reconciliação das três fontes, com proveniência e estado de revisão por campo. Gera `catalogo_inicial.json`. Valida: 78 publicáveis (81 até 22/10/2026), nenhum adicional mais caro que o produto, porção divergente sem texto, declaração alimentar sem fonte. |
| `gerar_migration.py` | `catalogo_inicial.json` → migration de carga. Com `--realinhar ARQUIVO`, gera uma migration nova que realinha o rascunho do banco, preserva foto enviada pelo painel e arquiva os produtos de `RETIRADOS`, sem mexer no estado nem publicar. |
| `exportar_snapshot.py` | Catálogo de arquivo → cópia pública no pipeline atual. `--do-banco` é uma opção para uma publicação ativa reconciliada; não é a rotina adotada nesta revisão. Recusa campos internos no resultado. |
| `gerar_conferencia.py` | Gera `docs/CARDAPIO_CONFERENCIA.md`. |

A montagem do SQL define o conteúdo da publicação do banco. O `montar()`
Python define os derivados da fonte versionada usada no site. Antes de mudar
para uma publicação do banco, comparar os resultados e resolver divergências
conforme as decisões registradas no handoff.

---

## 8. Teste do portal

`site/tools/cardapio/teste-aceitacao.html` roda 37 verificações no navegador
contra `/cardapio/`:

```bash
cd site && python -m http.server 8777
# abrir http://127.0.0.1:8777/tools/cardapio/teste-aceitacao.html
```

Cobre o que não pode regredir: os 78 registros na página; nome, preço, porção e
descrição na própria listagem; adicional nunca como preço; faixa de preço nas
variantes; porção divergente sem número; nenhuma etiqueta “sem glúten” ou
“vegano” publicada; nenhum “serve N pessoas”; atalhos de categoria; busca sem
acento e por sinônimo; termo de restrição alimentar mandando falar com a
equipe; detalhe com endereço próprio, Voltar do navegador e volta na mesma
posição; ausência de carrinho, seleção, subtotal e finalizar.
