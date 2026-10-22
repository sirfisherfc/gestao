begin;

-- Controle privado de pedidos e cache dos XMLs. Evita repetir uma chamada
-- mesmo quando o runner reinicia. Não altera vendas ou regras financeiras.
create table if not exists private.stone_api_controle (
  tipo text not null check (tipo in ('xml', 'pix')),
  identificador text not null,
  dia date not null,
  estado text not null check (estado in ('reservado', 'aceito', 'recebido', 'erro', 'resolvido')),
  criado_em timestamptz not null default now(),
  atualizado_em timestamptz not null default now(),
  resposta_http integer,
  conteudo text,
  erro text,
  primary key (tipo, identificador, dia)
);

alter table private.stone_api_controle enable row level security;
revoke all on private.stone_api_controle from public, anon, authenticated;
-- Somente scripts conectados como proprietário usam este controle. A Edge
-- Function continua gravando apenas stone_pix_arquivo, com seus grants atuais.
comment on table private.stone_api_controle is
  'Pedidos únicos Stone por tipo, identificador e dia; XMLs privados e recusas que suspendem novas consultas.';

commit;
