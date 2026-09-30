-- Eventos v2: bebidas simplificadas (sem open bar), petiscos + lanche e principais definidos.
-- Espelha as constantes de reservas/supabase/functions/event-quote/pricing.ts.
-- A versão v1 fica aposentada, mas preservada para as propostas antigas.

alter table public.event_beverage_rules
  drop constraint if exists event_beverage_rules_mode_check;
alter table public.event_beverage_rules
  add constraint event_beverage_rules_mode_check
  check (mode in ('individual', 'sem_alcool', 'credito', 'fichas', 'chope', 'selecionado', 'open_bar', 'chope_coquetel'));

alter table public.event_beverage_rules
  add column if not exists retail_per_guest numeric(12,2) not null default 0 check (retail_per_guest >= 0);

comment on column public.event_beverage_rules.retail_per_guest is
  'Valor de cardápio por convidado (bebidas sem álcool, inclusive crianças).';
comment on column public.event_beverage_rules.composition is
  'v2: {"perGuest": {...}, "perAdult": {...}} em unidades por pessoa.';

update public.event_pricing_versions
   set status = 'retired'
 where status = 'active' and code <> 'eventos-2026-09-v2';

insert into public.event_pricing_versions
  (code, status, cmv_rate, service_rate, target_contribution_margin, freelancer_day, public_notes, internal_notes)
values
  ('eventos-2026-09-v2', 'active', 0.35, 0.10, 0.35, 100,
   'Valores com atendimento incluído, abaixo do cardápio. Duração base de 3 horas; cada hora adicional acrescenta 10%.',
   'v2: preço = cardápio menos desconto (antecipado, volume, horário, formato), limitado pelo piso de custo com margem mínima de 35% e pelo faturamento esperado do horário. CMV de 35% vale só sem CMV real no painel.')
on conflict (code) do update set
  status = 'active',
  cmv_rate = excluded.cmv_rate,
  service_rate = excluded.service_rate,
  target_contribution_margin = excluded.target_contribution_margin,
  freelancer_day = excluded.freelancer_day,
  public_notes = excluded.public_notes,
  internal_notes = excluded.internal_notes;

with version as (
  select id from public.event_pricing_versions where code = 'eventos-2026-09-v2'
), rules(food_style, profile, units, retail, labor, composition) as (
  values
    ('petiscos','essencial',7,28.32,0,'{"pasteizinhos":0.2,"bolinha_peixe":0.166667,"crocante_carne_sol":0.166667,"dadinho_tapioca":0.25}'::jsonb),
    ('petiscos','equilibrada',7,41.98,0,'{"pasteizinhos":0.2,"bolinha_peixe":0.166667,"crocantes":0.333333,"dadinho_tapioca":0.166667,"crispy_chicken":0.15,"isca_peixe":0.1}'::jsonb),
    ('petiscos','completa',7,56.98,0,'{"pasteizinhos":0.2,"bolinha_peixe":0.166667,"crocantes":0.333333,"dadinho_tapioca":0.166667,"crispy_chicken":0.15,"newcastle":0.25,"isca_peixe":0.1}'::jsonb),
    ('petiscos_principal','essencial',4,55.18,0,'{"pasteizinhos":0.15,"crocante_carne_sol":0.166667,"dadinho_tapioca":0.125,"lanche":1}'::jsonb),
    ('petiscos_principal','equilibrada',5.1,72.88,0,'{"pasteizinhos":0.16,"bolinha_peixe":0.166667,"crocantes":0.166667,"dadinho_tapioca":0.125,"lanche":1,"brownie":1}'::jsonb),
    ('petiscos_principal','completa',5.3,96.62,0,'{"pasteizinhos":0.18,"bolinha_peixe":0.166667,"crocantes":0.166667,"dadinho_tapioca":0.125,"newcastle":0.25,"lanche":1,"brownie_sorvete":1}'::jsonb),
    ('refeicao','essencial',2.5,47.33,0,'{"pasteizinhos":0.1,"dadinho_tapioca":0.125,"travessa_essencial":0.5}'::jsonb),
    ('refeicao','equilibrada',4,70.51,0,'{"pasteizinhos":0.15,"bolinha_peixe":0.166667,"dadinho_tapioca":0.125,"travessa_equilibrada":0.5,"brownie":1}'::jsonb),
    ('refeicao','completa',3.5,98.72,0,'{"pasteizinhos":0.15,"bolinha_peixe":0.166667,"crocantes":0.166667,"newcastle":0.2,"travessa_completa":0.5,"brownie_sorvete":1}'::jsonb)
)
insert into public.event_package_rules
  (pricing_version_id, food_style, profile, guest_min, guest_max, food_units_per_person, retail_per_person, kitchen_labor_per_person, composition)
select version.id, rules.food_style, rules.profile, band.min_guest, band.max_guest,
  rules.units, rules.retail, rules.labor, rules.composition
from version cross join rules cross join (values (1,40),(41,60),(61,80),(81,300)) band(min_guest,max_guest)
on conflict (pricing_version_id, food_style, profile, guest_min, guest_max) do update set
  food_units_per_person = excluded.food_units_per_person,
  retail_per_person = excluded.retail_per_person,
  kitchen_labor_per_person = excluded.kitchen_labor_per_person,
  composition = excluded.composition,
  active = true;

with version as (
  select id from public.event_pricing_versions where code = 'eventos-2026-09-v2'
), rules(mode, retail_adult, retail_guest, units, waste, validation, composition) as (
  values
    ('individual',0,0,0,0,false,'{"perGuest":{},"perAdult":{}}'::jsonb),
    ('sem_alcool',0,14.8,0,0.03,false,'{"perGuest":{"agua":0.8,"refrigerante":0.8,"suco":0.4},"perAdult":{}}'::jsonb),
    ('chope',32.7,7.7,3,0.05,true,'{"perGuest":{"agua":0.4,"refrigerante":0.3,"suco":0.3},"perAdult":{"chope":3}}'::jsonb),
    ('chope_coquetel',41.8,7.7,3,0.05,true,'{"perGuest":{"agua":0.4,"refrigerante":0.3,"suco":0.3},"perAdult":{"chope":2,"coquetel":1}}'::jsonb)
)
insert into public.event_beverage_rules
  (pricing_version_id, mode, retail_per_adult, retail_per_guest, units_per_adult, waste_risk, needs_validation, composition)
select version.id, rules.mode, rules.retail_adult, rules.retail_guest, rules.units, rules.waste, rules.validation, rules.composition
from version cross join rules
on conflict (pricing_version_id, mode) do update set
  retail_per_adult = excluded.retail_per_adult,
  retail_per_guest = excluded.retail_per_guest,
  units_per_adult = excluded.units_per_adult,
  waste_risk = excluded.waste_risk,
  needs_validation = excluded.needs_validation,
  composition = excluded.composition,
  active = true;
