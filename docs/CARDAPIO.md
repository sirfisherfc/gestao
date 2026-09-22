# Cardápio — arquitetura, manutenção e migração

O cardápio do Sir Fisher passa a ter **uma fonte só**: as tabelas
`cardapio_*` no Supabase `portal`. O cliente lê pelo QR da mesa, em
`sirfisher.com.br/cardapio/`. A operação edita em **Gestão → Rotinas →
Cardápio**.

Antes existiam três fontes que discordavam entre si — um TXT, a página HTML
antiga e o Hubt. A lista do que cada uma dizia de diferente está em
[CARDAPIO_CONFERENCIA.md](CARDAPIO_CONFERENCIA.md).

---

## 1. As duas ideias que sustentam a estrutura

### Rascunho não é o que está no ar

`cardapio_produto` é o que a operação edita. O portal **nunca** lê essa tabela.
Ele lê `cardapio_publicacao`: uma fotografia imutável do catálogo, criada no
momento em que alguém apertou *Publicar*. Uma linha por versão, nunca alterada
depois.

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

## 4. Rotina do dia a dia

| Situação | O que fazer | Precisa publicar? |
|---|---|---|
| Acabou um item | **Marcar esgotado** na lista | Não. Vale na hora. |
| Voltou a ter | **Voltou a ter** na lista | Não. |
| Mudou preço | Editar → Salvar rascunho → **Publicar** | Sim. |
| Foto nova | Editar → enviar foto → **Publicar** | Sim. |
| Item novo | Editar/criar em rascunho → **Publicar** | Sim. |
| Errou e quer voltar | **Versões publicadas** → Restaurar | A restauração já publica. |

A tela mostra o tempo todo qual versão está no ar, quantos produtos foram
alterados desde a publicação e quantos têm campo a conferir. Antes de publicar,
aparece o resumo do que muda.

**Edição concorrente:** `cardapio_salvar_produto` recebe o `atualizado_em` que
a tela carregou. Se alguém salvou nesse meio-tempo, o salvamento é recusado com
`EDICAO_CONCORRENTE` e a tela manda recarregar, em vez de sobrescrever em
silêncio.

**Publicação que falha:** a transação não confirma e a versão ativa continua
intacta. Catálogo vazio também é recusado.

---

## 5. Como a mudança chega ao cliente

Três caminhos, do mais rápido ao mais lento:

1. **Ao vivo.** O portal consulta `cardapio_publico` pouco depois de abrir e
   quando a aba volta a ficar visível (a página esquecida aberta na mesa). Se
   houver versão mais nova, aparece um aviso discreto com um botão — **nada se
   move sozinho embaixo de quem está lendo**.
2. **Cópia embutida.** `site/cardapio/index.html` carrega o catálogo embutido,
   então a primeira pintura não espera requisição nenhuma. É gerada por
   `exportar_snapshot.py`, derivada da mesma publicação — nunca uma segunda
   base editada à mão.
3. **Rodapé honesto.** Sem rede, o portal usa a cópia embutida e o rodapé diz
   de quando ela é: *“Cardápio carregado da cópia salva em 22/09/2026.
   Confirme preços e disponibilidade com a equipe.”*

Para atualizar a cópia estática depois de publicar:

```bash
cd gestao/scripts/cardapio
SUPABASE_ANON_KEY=... python exportar_snapshot.py --do-banco
# escreve site/cardapio/dados/cardapio.json e o bloco embutido no index.html
# depois: commit e push no repositório do site
```

Isso é opcional — o portal já busca a versão nova sozinho. Vale a pena quando a
mudança é grande, para quem abrir sem rede também ver a versão certa.

---

## 6. Migração

### Já feito

- `/cardapio/` substituído pelo novo portal.
- **QR conferido, não presumido.** Os códigos impressos em
  `site/assets/qr/qr-cardapio-sirfisher.png` e `.svg` foram decodificados em
  22/09/2026: ambos codificam `https://www.sirfisher.com.br/qr/`. Como o
  destino fica do nosso lado, mudar `/qr/index.html` atualizou **todos** os
  códigos já impressos, sem reimprimir nada. A rota agora abre o cardápio
  direto, mantendo `utm_source=qr_code` para o acesso por QR seguir
  distinguível.
- 10 links para o Hubt trocados pelo portal próprio em `index.html`,
  `en/index.html`, `fish-and-chips/` e `en/fish-and-chips/`, incluindo o
  `hasMenu` dos dados estruturados.
- Política de privacidade: o Hubt deixou de ser o terceiro que recebe o cliente.
- Dados estruturados `schema.org/Menu` gerados da própria publicação — variante
  vira oferta com nome, adicional **não** vira oferta, item esgotado sai como
  `SoldOut`.

### Falta

- **`almoco-executivo/index.html` ainda aponta para o Hubt**, para
  `sir-fisher-praia--almoco`, que é **outro cardápio**: o almoço executivo não
  está entre os 81 registros. Redirecioná-lo para `/cardapio/` mostraria o
  cardápio errado. Duas saídas: cadastrar o almoço executivo como uma categoria
  com horário próprio, ou manter o link até essa decisão. **Enquanto isso, a
  dependência do Hubt não está 100% encerrada.**
- Conferir preços, variantes e disponibilidade **antes** de usar o portal no
  atendimento (ver [CARDAPIO_CONFERENCIA.md](CARDAPIO_CONFERENCIA.md)).
- Aplicar as duas migrations e rodar os testes de segurança da seção 3.

### Ordem de aplicação

1. `20260922000000_cardapio_catalogo.sql` — estrutura, segurança e RPCs.
2. `20260922010000_cardapio_carga_inicial.sql` — os 81 registros, **como
   rascunho**. A carga não publica nada: publicar é ato humano, depois de
   alguém da casa olhar.
3. Abrir Gestão → Rotinas → Cardápio, conferir e **Publicar**.
4. Enquanto o estado for `em_conferencia`, o portal avisa o cliente.

Reaplicar a carga é seguro: cada linha só é sobrescrita enquanto continuar
marcada como `carga-inicial` em `fontes`. Depois que alguém editar, a carga
respeita a edição.

---

## 7. Scripts

Em `scripts/cardapio/`:

| Script | O que faz |
|---|---|
| `catalogo_inicial.py` | A reconciliação das três fontes, com proveniência e estado de revisão por campo. Gera `catalogo_inicial.json`. Valida: 81 publicáveis, nenhum adicional mais caro que o produto, porção divergente sem texto, declaração alimentar sem fonte. |
| `gerar_migration.py` | `catalogo_inicial.json` → migration de carga. |
| `exportar_snapshot.py` | Publicação → cópia pública. `--do-banco` em produção; sem argumento, usa a semente (modo bootstrap). Recusa a exportação se algum campo interno vazar. |
| `gerar_conferencia.py` | Gera `docs/CARDAPIO_CONFERENCIA.md`. |

Quando o banco estiver populado, **a montagem autoritativa é a do SQL**
(`private.cardapio_montar_publicacao`). O `montar()` do Python só existe para o
bootstrap, antes da primeira publicação. As duas aplicam as mesmas regras; se
divergirem, o SQL vence.

---

## 8. Teste do portal

`site/tools/cardapio/teste-aceitacao.html` roda 37 verificações no navegador
contra `/cardapio/`:

```bash
cd site && python -m http.server 8777
# abrir http://127.0.0.1:8777/tools/cardapio/teste-aceitacao.html
```

Cobre o que não pode regredir: os 81 registros na página; nome, preço, porção e
descrição na própria listagem; adicional nunca como preço; faixa de preço nas
variantes; porção divergente sem número; nenhuma etiqueta “sem glúten” ou
“vegano” publicada; nenhum “serve N pessoas”; atalhos de categoria; busca sem
acento e por sinônimo; termo de restrição alimentar mandando falar com a
equipe; detalhe com endereço próprio, Voltar do navegador e volta na mesma
posição; ausência de carrinho, seleção, subtotal e finalizar.
