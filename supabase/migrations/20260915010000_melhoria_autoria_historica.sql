-- Atribui autoria as 20 melhorias da carga historica.
--
-- Motivo: a carga entrou sem autor, o que enfraquece a evidencia de que a
-- melhoria continua nasce na operacao e nao so na direcao. Cada registro passa
-- a apontar para a conta de quem de fato levantou o tema no grupo de trabalho,
-- na data que consta em `referencia_origem`.
--
-- A correspondencia foi conferida mensagem a mensagem e aqui aparece apenas
-- como id de conta: nenhum nome, e-mail ou telefone e versionado. Quem precisar
-- auditar a correspondencia resolve o nome pela propria aplicacao, com
-- `private.nome_exibicao_usuario(uuid)`.
--
-- Uma ideia nasceu numa conversa de quem nao tem conta no painel; nesse caso o
-- autor e quem levou o tema ao grupo de gerencia, e a conversa de origem
-- continua citada em `referencia_origem`.
--
-- As 6 ideias novas (chave `ideia-%`) seguem sem autor de proposito: ainda nao
-- foram assumidas por ninguem.
--
-- Um statement so, sem tabela temporaria, para nao depender de como a transacao
-- e controlada por quem aplica. Idempotente: reatribui sempre o mesmo par
-- chave/conta, nao toca em quem ja esta certo e ignora conta que nao exista
-- neste ambiente (banco novo ou implantacao de outra empresa).

begin;

with autoria(chave_carga, user_id) as (values
    ('hist-2026-03-14-delivery-cardapio-mensagens', '5b74eab2-cf10-4211-9f24-119d5b435a68'::uuid),
    ('hist-2026-03-21-validade-no-recebimento',     '43324f35-c5b8-498f-ac97-37cb030eeec9'),
    ('hist-2026-04-01-alerta-antecipado-validade',  '2862abcf-8978-4299-b746-0bf13e2f9f5f'),
    ('hist-2026-04-07-evento-300-anos',             '94cddb35-4e5d-4dbe-be8e-2f3bc08348a3'),
    ('hist-2026-04-13-iluminacao',                  '5b74eab2-cf10-4211-9f24-119d5b435a68'),
    ('hist-2026-04-15-promocao-automatica',         '5b74eab2-cf10-4211-9f24-119d5b435a68'),
    ('hist-2026-04-22-equipe-por-movimento',        '43324f35-c5b8-498f-ac97-37cb030eeec9'),
    ('hist-2026-04-23-mudanca-imediata-quadro',     '58da3a66-5c40-4582-a2e6-d19dcb5cbc29'),
    ('hist-2026-05-19-politica-grupos-grandes',     '5b74eab2-cf10-4211-9f24-119d5b435a68'),
    ('hist-2026-05-29-substituir-sistema-vendas',   '5b74eab2-cf10-4211-9f24-119d5b435a68'),
    ('hist-2026-06-07-teste-novo-produto',          '94cddb35-4e5d-4dbe-be8e-2f3bc08348a3'),
    ('hist-2026-06-10-rotulos-fixos-cerveja',       '94cddb35-4e5d-4dbe-be8e-2f3bc08348a3'),
    ('hist-2026-07-08-equipamento-molho-bebida',    '43324f35-c5b8-498f-ac97-37cb030eeec9'),
    ('hist-2026-07-09-portal-reservas',             '43324f35-c5b8-498f-ac97-37cb030eeec9'),
    ('hist-2026-07-12-consumo-de-gas',              '2862abcf-8978-4299-b746-0bf13e2f9f5f'),
    ('hist-2026-08-10-anuncios-com-ia',             '43324f35-c5b8-498f-ac97-37cb030eeec9'),
    ('hist-2026-08-18-anuncio-ate-comparecimento',  '43324f35-c5b8-498f-ac97-37cb030eeec9'),
    ('hist-2026-08-18-manual-fotografico-pratos',   '94cddb35-4e5d-4dbe-be8e-2f3bc08348a3'),
    ('hist-2026-08-18-padrao-entre-turnos',         '2862abcf-8978-4299-b746-0bf13e2f9f5f'),
    ('hist-2026-09-12-validade-na-reetiquetagem',   '43324f35-c5b8-498f-ac97-37cb030eeec9')
),
-- O join com auth.users deixa a migration inofensiva onde essas contas nao
-- existem: nenhuma linha e tocada, em vez de violar a chave estrangeira.
alvo as (
  select m.id, a.user_id
    from public.melhorias m
    join autoria a on a.chave_carga = m.chave_carga
    join auth.users u on u.id = a.user_id
),
atualiza_melhoria as (
  update public.melhorias m
     set criado_por = alvo.user_id
    from alvo
   where m.id = alvo.id
     and m.criado_por is distinct from alvo.user_id
  returning m.id
)
-- A linha "Registro criado" da linha do tempo acompanha o autor.
update public.melhoria_historico h
   set usuario_id = alvo.user_id
  from alvo
 where h.melhoria_id = alvo.id
   and h.status_anterior is null
   and h.usuario_id is distinct from alvo.user_id;

commit;
