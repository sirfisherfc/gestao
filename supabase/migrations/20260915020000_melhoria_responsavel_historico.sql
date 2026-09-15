-- Preenche o responsavel das 20 melhorias da carga historica.
--
-- A migration anterior deu autoria, mas a lista continuava mostrando "Sem
-- responsavel" em tudo: autor e responsavel sao campos diferentes. Para a
-- carga, quem levantou o tema tambem foi quem o conduziu, entao o responsavel
-- recebe a mesma conta do autor. Quem estiver diferente disso e ajustado na
-- propria tela, que e onde esse campo deve mudar daqui pra frente.
--
-- Antes disso, uma correcao de autoria: a ideia sobre validade na
-- reetiquetagem nasceu numa conversa de quem nao tem conta no painel. A
-- migration anterior atribuiu a quem levou o tema ao grupo de gerencia; por
-- decisao da direcao ela passa para a gestora da area, que responde por quem
-- levantou o problema.
--
-- Idempotente: so escreve onde o valor esta diferente, e nada acontece onde a
-- conta nao existe (banco novo ou implantacao de outra empresa). As 6 ideias
-- novas seguem sem autor e sem responsavel de proposito: ainda nao foram
-- assumidas.

begin;

-- 1) Autoria da ideia que nasceu fora do painel.
update public.melhorias m
   set criado_por = u.id
  from auth.users u
 where u.id = '87cd8504-f4be-4128-81e5-bb9d55b88be4'::uuid
   and m.chave_carga = 'hist-2026-09-12-validade-na-reetiquetagem'
   and m.criado_por is distinct from u.id;

update public.melhoria_historico h
   set usuario_id = m.criado_por
  from public.melhorias m
 where h.melhoria_id = m.id
   and h.status_anterior is null
   and m.chave_carga = 'hist-2026-09-12-validade-na-reetiquetagem'
   and h.usuario_id is distinct from m.criado_por;

-- 2) Responsavel das 20 da carga.
update public.melhorias m
   set responsavel_id = m.criado_por,
       atualizado_em = now()
 where m.chave_carga like 'hist-%'
   and m.criado_por is not null
   and m.responsavel_id is distinct from m.criado_por;

commit;
