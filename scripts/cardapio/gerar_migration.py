# -*- coding: utf-8 -*-
"""
Gera a migration de carga inicial do cardapio a partir de catalogo_inicial.json.

A carga entra como RASCUNHO, nao como publicacao. Ninguem publica um catalogo
de 81 registros sem alguem da casa ter olhado: quem publica e uma pessoa, pelo
botao da rotina, depois de conferir. Por isso a migration popula as tabelas de
edicao e para por ai.

A carga e re-executavel: `on conflict do update` em tudo. Reaplicar a migration
num banco que ja tem o cardapio editado sobrescreveria a edicao, entao o update
so acontece quando a linha ainda esta como veio da carga -- marcada por
`fontes` contendo 'carga-inicial'. Assim a verificacao do Supabase Preview, que
reprocessa as migrations do zero, continua passando sem atropelar producao.
"""

import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
ORIGEM = os.path.join(AQUI, "catalogo_inicial.json")
DESTINO = os.path.join(
    AQUI, "..", "..", "supabase", "migrations",
    "20260922010000_cardapio_carga_inicial.sql")

MARCA = "carga-inicial"


def lit(valor):
    """Literal SQL para texto, com aspas escapadas."""
    if valor is None:
        return "null"
    return "'" + str(valor).replace("'", "''") + "'"


def arr(valores):
    if not valores:
        return "'{}'"
    return "array[" + ", ".join(lit(v) for v in valores) + "]::text[]"


def js(valor):
    return lit(json.dumps(valor, ensure_ascii=False)) + "::jsonb"


def main():
    with open(ORIGEM, encoding="utf-8") as arq:
        cat = json.load(arq)

    linhas = []
    w = linhas.append

    w("-- Carga inicial do cardapio: os 81 registros do cadastro, reconciliados")
    w("-- com o cardapio HTML e com o cardapio impresso em %s." % cat["gerado_em"])
    w("--")
    w("-- Gerado por scripts/cardapio/gerar_migration.py a partir de")
    w("-- catalogo_inicial.json. Nao editar a mao: edite o catalogo e gere de novo.")
    w("--")
    w("-- Entra como RASCUNHO. Nada aqui foi validado pela cozinha ou pela")
    w("-- operacao: precos, porcoes e declaracoes alimentares carregam a fonte e")
    w("-- o estado de revisao, e as pendencias ficam visiveis para quem edita.")
    w("-- A publicacao e um ato humano, na rotina Gestao -> Rotinas -> Cardapio.")
    w("--")
    w("-- Re-execucao: cada linha so e sobrescrita enquanto continuar marcada")
    w("-- como '%s' em fontes. Depois que alguem da casa editar o" % MARCA)
    w("-- produto, a carga passa a respeitar a edicao.")
    w("")
    w("begin;")
    w("")

    w("-- Categorias -----------------------------------------------------------")
    w("insert into public.cardapio_categoria (id, nome, resumo, grupo, subgrupos, ordem)")
    w("values")
    partes = []
    for i, c in enumerate(cat["categorias"]):
        partes.append("  (%s, %s, %s, %s, %s, %d)" % (
            lit(c["id"]), lit(c["nome"]), lit(c["resumo"]), lit(c["grupo"]),
            js(c["subgrupos"]), i))
    w(",\n".join(partes))
    w("on conflict (id) do update set")
    w("  nome = excluded.nome, resumo = excluded.resumo, grupo = excluded.grupo,")
    w("  subgrupos = excluded.subgrupos, ordem = excluded.ordem")
    w("where public.cardapio_categoria.atualizado_por is null;")
    w("")

    w("-- Sinonimos de busca ---------------------------------------------------")
    w("-- Variantes de grafia e de regiao, nao sinonimos inventados sobre receitas.")
    w("insert into public.cardapio_sinonimo (termo, alternativas) values")
    partes = ["  (%s, %s)" % (lit(t), arr(a))
              for t, a in sorted(cat["sinonimos"].items())]
    w(",\n".join(partes))
    w("on conflict (termo) do update set alternativas = excluded.alternativas;")
    w("")

    w("-- Avisos gerais --------------------------------------------------------")
    w("-- O aviso geral do impresso fica aqui, separado da matriz por prato: ele")
    w("-- nao vira presenca confirmada nem contato cruzado de item nenhum.")
    w("insert into public.cardapio_aviso (id, titulo, texto, fonte, citacao, estado, ordem) values")
    partes = []
    for i, a in enumerate(cat["avisos"]):
        partes.append("  (%s, %s, %s, %s, %s, %s, %d)" % (
            lit(a["id"]), lit(a["titulo"]), lit(a["texto"]), lit(a.get("fonte")),
            lit(a.get("citacao")), lit(a["estado"]), i))
    w(",\n".join(partes))
    w("on conflict (id) do update set")
    w("  titulo = excluded.titulo, texto = excluded.texto, fonte = excluded.fonte,")
    w("  citacao = excluded.citacao, estado = excluded.estado;")
    w("")

    w("-- Produtos -------------------------------------------------------------")
    for prod in cat["produtos"]:
        fontes = list(prod["fontes"]) + [MARCA]
        notas = list(prod["notas_internas"])
        # A proveniencia acompanha o registro: sem ela, daqui a um mes ninguem
        # sabe de onde veio o 300 g nem por que dois nomes divergem.
        if prod["porcao"].get("divergencia"):
            notas.append("Porção: " + prod["porcao"]["divergencia"])
        for d in prod["alimentar"].get("divergencias", []):
            notas.append("Alimentar: " + d)
        for al in prod["alimentar"].get("alegacoes", []):
            notas.append("Alegação do impresso, não publicada: “%s” — %s"
                         % (al["texto"], al["nota"]))

        w("")
        w("-- %s (%s)" % (prod["nome"], ", ".join(prod["fontes"])))
        w("insert into public.cardapio_produto (")
        w("  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,")
        w("  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,")
        w("  termos, etiquetas, publicar, pendencias, fontes, notas_internas")
        w(") values (")
        w("  %s, %s, %s, %s," % (lit(prod["id"]), lit(prod["categoria"]),
                                 lit(prod["subgrupo"]), lit(prod["nome"])))
        w("  %s, %s," % (lit(prod["nome_original"]), lit(prod["descritor"])))
        w("  %s," % lit(prod["descricao"]))
        w("  %s," % lit(prod["detalhe"]))
        w("  %s, %d," % ("null" if prod["preco_centavos"] is None
                         else str(prod["preco_centavos"]), prod["ordem"]))
        w("  %s," % arr(prod["inclui"]))
        w("  %s," % js(prod["opcoes"]))
        w("  %s," % js(prod["porcao"]))
        w("  %s," % js(prod["alimentar"]))
        w("  %s," % (js(prod["foto"]) if prod["foto"] else "null"))
        w("  %s," % arr(prod["termos"]))
        w("  %s," % arr(prod["etiquetas"]))
        w("  %s," % ("true" if prod["publicar"] else "false"))
        w("  %s," % arr(prod["pendencias"]))
        w("  %s," % arr(fontes))
        w("  %s" % arr(notas))
        w(")")
        w("on conflict (id) do update set")
        for campo in ("categoria_id", "subgrupo", "nome", "nome_original",
                      "descritor", "descricao", "detalhe", "preco_centavos",
                      "ordem", "inclui", "opcoes", "porcao", "alimentar",
                      "foto", "termos", "etiquetas", "publicar", "pendencias",
                      "fontes", "notas_internas"):
            w("  %s = excluded.%s," % (campo, campo))
        w("  atualizado_em = now()")
        w("where %s = any(public.cardapio_produto.fontes);" % lit(MARCA))

        if prod["variantes"]:
            w("delete from public.cardapio_variante where produto_id = %s"
              % lit(prod["id"]))
            w("  and exists (select 1 from public.cardapio_produto p")
            w("               where p.id = %s and %s = any(p.fontes));"
              % (lit(prod["id"]), lit(MARCA)))
            w("insert into public.cardapio_variante (produto_id, nome, preco_centavos, ordem)")
            w("select * from (values")
            partes = ["  (%s, %s, %d, %d)" % (lit(prod["id"]), lit(v["nome"]),
                                              v["preco_centavos"], i)
                      for i, v in enumerate(prod["variantes"])]
            w(",\n".join(partes))
            w(") as v(produto_id, nome, preco_centavos, ordem)")
            w("where exists (select 1 from public.cardapio_produto p")
            w("              where p.id = %s and %s = any(p.fontes))"
              % (lit(prod["id"]), lit(MARCA)))
            w("on conflict (produto_id, nome) do update set")
            w("  preco_centavos = excluded.preco_centavos, ordem = excluded.ordem;")

        if prod["adicionais"]:
            w("-- Adicional, nunca preco do produto.")
            w("insert into public.cardapio_adicional (produto_id, nome, preco_centavos, ordem)")
            w("select * from (values")
            partes = ["  (%s, %s, %d, %d)" % (lit(prod["id"]), lit(a["nome"]),
                                              a["preco_centavos"], i)
                      for i, a in enumerate(prod["adicionais"])]
            w(",\n".join(partes))
            w(") as a(produto_id, nome, preco_centavos, ordem)")
            w("where exists (select 1 from public.cardapio_produto p")
            w("              where p.id = %s and %s = any(p.fontes))"
              % (lit(prod["id"]), lit(MARCA)))
            w("on conflict (produto_id, nome) do update set")
            w("  preco_centavos = excluded.preco_centavos, ordem = excluded.ordem;")

    w("")
    w("-- O catalogo nasce em conferencia. O portal avisa o cliente enquanto")
    w("-- precos, porcoes e informacao alimentar nao forem confirmados pela casa.")
    w("update public.cardapio_estado set valor = 'em_conferencia' where id;")
    w("")
    w("commit;")
    w("")

    destino = os.path.abspath(DESTINO)
    with open(destino, "w", encoding="utf-8", newline="\n") as arq:
        arq.write("\n".join(linhas))

    publicaveis = [p for p in cat["produtos"] if p["publicar"]]
    print("Migration: %s" % destino)
    print("%d produtos (%d publicáveis, %d em rascunho), %d categorias, %d KB"
          % (len(cat["produtos"]), len(publicaveis),
             len(cat["produtos"]) - len(publicaveis), len(cat["categorias"]),
             os.path.getsize(destino) // 1024))


if __name__ == "__main__":
    main()
