-- Configurador de eventos: modelo, segurança, regras iniciais e permissão da rotina.
-- Espelha o módulo isolado do repositório reservas e é a migration canônica
-- do banco compartilhado. Não altera tabelas existentes de reservas.

-- Configurador de eventos Sir Fisher - objetos isolados do módulo.
-- Aplicar depois do schema principal de reservas. Não altera tabelas existentes.

create table if not exists public.event_pricing_versions (
  id uuid primary key default gen_random_uuid(),
  code text not null unique,
  status text not null default 'draft' check (status in ('draft', 'active', 'retired')),
  cmv_rate numeric(6,5) not null default 0.35 check (cmv_rate between 0 and 1),
  service_rate numeric(6,5) not null default 0.10 check (service_rate between 0 and 1),
  target_contribution_margin numeric(6,5) not null default 0.52 check (target_contribution_margin between 0 and 0.90),
  freelancer_day numeric(12,2) not null default 100 check (freelancer_day >= 0),
  public_notes text,
  internal_notes text,
  effective_from timestamptz not null default now(),
  created_by_user_id uuid,
  created_at timestamptz not null default now()
);

create unique index if not exists event_pricing_versions_one_active
  on public.event_pricing_versions ((status)) where status = 'active';

create table if not exists public.event_package_rules (
  id uuid primary key default gen_random_uuid(),
  pricing_version_id uuid not null references public.event_pricing_versions(id) on delete restrict,
  food_style text not null check (food_style in ('petiscos', 'petiscos_principal', 'refeicao')),
  profile text not null check (profile in ('essencial', 'equilibrada', 'completa')),
  guest_min int not null check (guest_min >= 1),
  guest_max int not null check (guest_max >= guest_min),
  food_units_per_person numeric(8,3) not null check (food_units_per_person > 0),
  retail_per_person numeric(12,2) not null check (retail_per_person >= 0),
  kitchen_labor_per_person numeric(12,2) not null check (kitchen_labor_per_person >= 0),
  composition jsonb not null default '{}'::jsonb,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  unique (pricing_version_id, food_style, profile, guest_min, guest_max)
);

create table if not exists public.event_beverage_rules (
  id uuid primary key default gen_random_uuid(),
  pricing_version_id uuid not null references public.event_pricing_versions(id) on delete restrict,
  mode text not null check (mode in ('individual', 'sem_alcool', 'credito', 'fichas', 'chope', 'selecionado', 'open_bar')),
  retail_per_adult numeric(12,2) not null check (retail_per_adult >= 0),
  units_per_adult numeric(8,3) not null default 0 check (units_per_adult >= 0),
  waste_risk numeric(6,5) not null default 0 check (waste_risk between 0 and 1),
  needs_validation boolean not null default false,
  composition jsonb not null default '{}'::jsonb,
  active boolean not null default true,
  unique (pricing_version_id, mode)
);

create table if not exists public.event_product_rules (
  id uuid primary key default gen_random_uuid(),
  menu_version text not null,
  product_id text not null,
  classification text not null check (classification in ('recommended', 'limited', 'approval', 'not_recommended')),
  batch_friendly boolean not null default false,
  max_guests int,
  rationale text not null,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  unique (menu_version, product_id)
);

create table if not exists public.event_demand_baselines (
  id uuid primary key default gen_random_uuid(),
  month int not null check (month between 1 and 12),
  weekday int not null check (weekday between 0 and 6),
  start_hour int not null check (start_hour between 0 and 23),
  duration_hours numeric(5,2) not null default 3 check (duration_hours > 0),
  sample_size int not null default 0 check (sample_size >= 0),
  median_revenue numeric(14,2) not null,
  low_revenue numeric(14,2) not null,
  high_revenue numeric(14,2) not null,
  opportunity_cost numeric(14,2) not null,
  source_window daterange,
  calculated_at timestamptz not null default now(),
  unique (month, weekday, start_hour, duration_hours)
);

create table if not exists public.event_requests (
  id uuid primary key default gen_random_uuid(),
  public_code text not null unique,
  customer_name text not null check (char_length(customer_name) between 2 and 120),
  customer_phone text not null check (customer_phone ~ '^[0-9]{10,11}$'),
  event_date date not null,
  start_time time not null,
  duration_hours numeric(5,2) not null check (duration_hours between 2 and 8),
  guests int not null check (guests between 1 and 300),
  children int not null default 0 check (children >= 0 and children <= guests),
  configuration jsonb not null,
  selected_option_id text not null,
  public_snapshot jsonb not null,
  internal_snapshot jsonb not null,
  risk_level text not null check (risk_level in ('verde', 'amarelo', 'vermelho')),
  status text not null default 'pending' check (status in (
    'pending', 'approved', 'adjustment_requested', 'rejected',
    'information_requested', 'alternative_offered', 'final_proposal_ready'
  )),
  pricing_version text not null,
  menu_version text not null,
  accepted_privacy_at timestamptz not null,
  source text not null default 'site' check (source in ('site', 'admin')),
  reviewed_by_user_id uuid,
  discount_approved boolean not null default false,
  discount_reason text,
  discount_approved_by_user_id uuid,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint event_discount_approval_complete check (
    not discount_approved or (discount_reason is not null and discount_approved_by_user_id is not null)
  )
);

create index if not exists event_requests_queue_idx on public.event_requests(status, risk_level, created_at desc);
create index if not exists event_requests_date_idx on public.event_requests(event_date, start_time);
create index if not exists event_requests_phone_idx on public.event_requests(customer_phone, created_at desc);

create table if not exists public.event_request_audit (
  id bigint generated always as identity primary key,
  request_id uuid not null references public.event_requests(id) on delete restrict,
  action text not null,
  actor_type text not null check (actor_type in ('customer', 'admin', 'socio', 'gerente', 'system')),
  actor_user_id uuid,
  before_data jsonb,
  after_data jsonb,
  created_at timestamptz not null default now()
);

create index if not exists event_request_audit_request_idx on public.event_request_audit(request_id, created_at);

comment on table public.event_requests is 'Solicitações do configurador; snapshots público e interno preservam o cálculo auditável.';
comment on table public.event_demand_baselines is 'Agregados sem dados brutos para custo de oportunidade; deve ser alimentada por rotina interna read-only sobre as views financeiras.';



-- Segurança do módulo de eventos. A superfície pública é somente a Edge Function.

alter table public.event_pricing_versions enable row level security;
alter table public.event_package_rules enable row level security;
alter table public.event_beverage_rules enable row level security;
alter table public.event_product_rules enable row level security;
alter table public.event_demand_baselines enable row level security;
alter table public.event_requests enable row level security;
alter table public.event_request_audit enable row level security;

revoke all on public.event_pricing_versions, public.event_package_rules,
  public.event_beverage_rules, public.event_product_rules,
  public.event_demand_baselines, public.event_requests,
  public.event_request_audit from anon, authenticated;

-- O service_role da Edge Function ignora RLS. Nenhuma tabela recebe grant para anon.
-- O painel também passa pela Edge Function, que valida auth.users + app_users e grava auditoria.
grant all on public.event_pricing_versions, public.event_package_rules,
  public.event_beverage_rules, public.event_product_rules,
  public.event_demand_baselines, public.event_requests,
  public.event_request_audit to service_role;
grant usage, select on sequence public.event_request_audit_id_seq to service_role;

drop policy if exists event_requests_deny_anon on public.event_requests;
create policy event_requests_deny_anon on public.event_requests for all to anon using (false) with check (false);

drop policy if exists event_request_audit_deny_anon on public.event_request_audit;
create policy event_request_audit_deny_anon on public.event_request_audit for all to anon using (false) with check (false);




-- Parâmetros provisórios. Ativar uma nova versão é decisão explícita do proprietário.

insert into public.event_pricing_versions
  (code, status, cmv_rate, service_rate, target_contribution_margin, freelancer_day, public_notes, internal_notes)
values
  ('eventos-2026-09-mvp-1', 'active', 0.35, 0.10, 0.52, 100,
   'Valores com atendimento incluído.',
   'CMV provisório de 35%; substituir por custo real por produto quando disponível.')
on conflict (code) do update set
  cmv_rate = excluded.cmv_rate,
  service_rate = excluded.service_rate,
  target_contribution_margin = excluded.target_contribution_margin,
  freelancer_day = excluded.freelancer_day;

with version as (
  select id from public.event_pricing_versions where code = 'eventos-2026-09-mvp-1'
), rules(food_style, profile, units, retail, labor, composition) as (
  values
    ('petiscos','essencial',5.0,23.0,7.0,'{"pasteizinhos":0.15,"bolinha_peixe":0.1667,"crocante_carne_sol":0.1667,"dadinho_tapioca":0.125}'::jsonb),
    ('petiscos','equilibrada',6.5,34.0,8.0,'{"pasteizinhos":0.18,"bolinha_peixe":0.2,"crocantes":0.2,"dadinho_tapioca":0.15,"crispy_chicken":0.12}'::jsonb),
    ('petiscos','completa',8.0,46.0,10.0,'{"pasteizinhos":0.2,"bolinha_peixe":0.22,"newcastle":0.16,"crocantes":0.2,"dadinho_tapioca":0.17,"isca_peixe":0.12}'::jsonb),
    ('petiscos_principal','essencial',4.5,56.0,9.0,'{"pasteizinhos":0.14,"crocante_carne_sol":0.17,"dadinho_tapioca":0.12,"principal":0.75}'::jsonb),
    ('petiscos_principal','equilibrada',6.0,66.0,10.0,'{"pasteizinhos":0.16,"bolinha_peixe":0.17,"crocantes":0.17,"dadinho_tapioca":0.14,"principal":0.85}'::jsonb),
    ('petiscos_principal','completa',7.5,81.0,12.0,'{"pasteizinhos":0.18,"bolinha_peixe":0.18,"newcastle":0.14,"crocantes":0.18,"dadinho_tapioca":0.15,"principal":1,"brownie":1}'::jsonb),
    ('refeicao','essencial',3.0,52.0,9.0,'{"dadinho_tapioca":0.1,"acompanhamento":0.12,"principal":0.8}'::jsonb),
    ('refeicao','equilibrada',4.0,66.0,10.0,'{"pasteizinhos":0.12,"dadinho_tapioca":0.12,"principal":1,"brownie":1}'::jsonb),
    ('refeicao','completa',5.0,86.0,13.0,'{"pasteizinhos":0.14,"bolinha_peixe":0.14,"dadinho_tapioca":0.12,"principal_premium":1,"sobremesa":1}'::jsonb)
)
insert into public.event_package_rules
  (pricing_version_id, food_style, profile, guest_min, guest_max, food_units_per_person, retail_per_person, kitchen_labor_per_person, composition)
select version.id, rules.food_style, rules.profile, band.min_guest, band.max_guest,
  rules.units, rules.retail, rules.labor, rules.composition
from version cross join rules cross join (values (30,40),(41,60),(61,80),(81,100)) band(min_guest,max_guest)
on conflict (pricing_version_id, food_style, profile, guest_min, guest_max) do update set
  food_units_per_person = excluded.food_units_per_person,
  retail_per_person = excluded.retail_per_person,
  kitchen_labor_per_person = excluded.kitchen_labor_per_person,
  composition = excluded.composition,
  active = true;

with version as (
  select id from public.event_pricing_versions where code = 'eventos-2026-09-mvp-1'
), rules(mode, retail, units, waste, validation, composition) as (
  values
    ('individual',0.0,0.0,0.0,false,'{}'::jsonb),
    ('sem_alcool',13.0,1.7,0.04,false,'{"agua":0.7,"refrigerante":0.7,"suco":0.3}'::jsonb),
    ('credito',22.0,0.0,0.0,false,'{"credito_reais":22}'::jsonb),
    ('fichas',20.0,2.0,0.03,false,'{"fichas":2}'::jsonb),
    ('chope',26.0,2.4,0.10,true,'{"chope":2.4}'::jsonb),
    ('selecionado',31.0,2.5,0.10,true,'{"agua_refrigerante":1,"cerveja_ou_chope":1.5}'::jsonb),
    ('open_bar',55.0,4.2,0.18,true,'{"agua_refrigerante":1.2,"alcoolicas_selecionadas":3}'::jsonb)
)
insert into public.event_beverage_rules
  (pricing_version_id, mode, retail_per_adult, units_per_adult, waste_risk, needs_validation, composition)
select version.id, rules.mode, rules.retail, rules.units, rules.waste, rules.validation, rules.composition
from version cross join rules
on conflict (pricing_version_id, mode) do update set
  retail_per_adult = excluded.retail_per_adult,
  units_per_adult = excluded.units_per_adult,
  waste_risk = excluded.waste_risk,
  needs_validation = excluded.needs_validation,
  composition = excluded.composition,
  active = true;

with classified(classification, batch_friendly, max_guests, rationale, ids) as (
  values
    ('recommended', true, 100, 'Produção padronizada ou bebida estável, adequada a volume.', array[
      'bolinha-de-peixe-cremosa','newcastle','crocante-carne-de-sol','crocante-calabresa','pasteizinhos','crispy-spicy-chicken','dadinho-de-tapioca','isca-de-peixe','brownie-de-chocolate',
      'spaten-longneck','stella-artois-longneck','corona-longneck','corona-zero-longneck','spaten-600','original-600','budweiser-600','stella-artois-600','stella-pure-gold-600',
      'agua-sem-gas','agua-com-gas','agua-de-coco-copo','agua-tonica','refrigerante-lata','suco-copo','soda-italiana'
    ]::text[]),
    ('limited', false, 60, 'Viável com limite de volume ou janela de serviço para preservar qualidade.', array[
      'sir-fisher-fish-n-chips','london-fish-n-chips','big-ben-fries','caldo-de-peixe','camarao-alho-e-oleo','calabresa-acebolada-com-fritas','macaxeira-ou-batata-frita',
      'fisher-burger','edimburger','marine-sandwich','peito-de-frango-com-ervas','picanha-suina','brownie-com-sorvete','chope-brahma','smirnoff-ice','energetico-red-bull',
      'caipirinha','caipiroska','caipifruta','gin-tonica','melancita','sherlock-holmes-gin','tropicall','margarita','fitzgerald','moscow-mule'
    ]::text[]),
    ('approval', false, null, 'Maior custo, complexidade, perecibilidade ou risco de serviço; requer validação.', array[
      'patinha-de-caranguejo','file-mignon-trinchado','file-mignon-dividir','picanha-importada','file-de-peixe-grelhado','carne-de-sol-acebolada',
      'teachers','black-white','red-label','black-label','rum','campari','martini','vodka-nacional','vodka-sky','vodka-absolut','gin-nacional','gin-gordons','aperol','conhaque','cachaca-nacional','cachaca-ypioca-150','cachaca-premium','rolha'
    ]::text[]),
    ('not_recommended', false, null, 'Não compõe pacote padrão; uso avulso, apoio operacional ou baixa adequação ao serviço volante.', array[
      'cafe-expresso','sumo-de-limao','molho-extra','arroz-extra','pacote-gelo','embalagem-viagem'
    ]::text[])
), expanded as (
  select classification, batch_friendly, max_guests, rationale, unnest(ids) as product_id from classified
)
insert into public.event_product_rules(menu_version, product_id, classification, batch_friendly, max_guests, rationale)
select 'cardapio-1-2026-09-22', product_id, classification, batch_friendly, max_guests, rationale from expanded
on conflict (menu_version, product_id) do update set
  classification = excluded.classification,
  batch_friendly = excluded.batch_friendly,
  max_guests = excluded.max_guests,
  rationale = excluded.rationale,
  active = true;

do $$
declare v_count int;
begin
  select count(*) into v_count from public.event_product_rules where menu_version = 'cardapio-1-2026-09-22';
  if v_count <> 81 then
    raise exception 'Classificação de cardápio incompleta: esperado 81, encontrado %', v_count;
  end if;
end $$;



-- A rotina começa exclusiva do admin. O proprietário pode liberar socio e/ou
-- gerente depois em permissoes.html, sem nova migration.
insert into public.pagina_permissao (pagina, papeis)
values ('eventos.html', '{}'::text[])
on conflict (pagina) do nothing;
