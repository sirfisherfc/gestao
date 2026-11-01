# Integração do atendimento em nuvem

Implantação desligada em 01/11/2026. Migration canônica:
`supabase/migrations/20261101071634_instagram_support_durable_queue.sql`.
Foi criada com a CLI Supabase `2.122.0`, após ler a ajuda dos comandos.
**Aplicada ao portal e registrada na mesma transação**, após revisão. A
conferência de leitura confirmou dez tabelas com RLS, dez RPCs invoker,
nenhum acesso anon/authenticated e o cron inativo sob o owner esperado.
Modo off, pausa global, modelo/faturamento e alertas bloqueados, allowlist
vazia e gerente NULL foram preservados. Eventos, casos, outbox e reservas
de custo estavam zerados; os objetos protegidos dos outros sistemas
mantiveram o mesmo fingerprint de definição e grants. Nenhum segredo ou
destinatário foi configurado nesta aplicação.

Depois dessa aplicação, um lookup único de cadastro ativo/admin vinculou
a gerente em `settings`, sem criar usuário ou conceder papel novo.
A leitura confirmou `manager_configured=true`, com modo off, pausa global,
modelo/faturamento, avisos e cron ainda bloqueados. Nenhum caso ou alerta
foi criado. O identificador e o e-mail da gerente não foram versionados.

A Edge Function correspondente é
mantida no repositório `reservas`, em `supabase/functions/instagram-support/`.
O proprietário da tarefa revisa os dois projetos antes de implantar.

## Dados e acesso

O schema `instagram_support` fica fora da Data API. Ele contém dez tabelas:

| Tabela | Uso |
| --- | --- |
| `settings` | Modo, pausa global, allowlist de teste, limites e configuração sem segredos. |
| `threads` | Pausa humana, versão da conversa e lease do processamento. |
| `events` | MID único, data e estado do evento. O texto redigido existe só durante a fila/processamento. |
| `budget_months` e `budget_reservations` | Reserva atômica antes de chamar o modelo e contagem de gerações. |
| `outbox` | Intenção de envio e resultado verificável ou incerto. |
| `cases` | Pendência humana, motivo, resumo mínimo e responsável interno. |
| `control_audit` | Ação administrativa e identidade validada pelo backend. |
| `alert_months` e `alerts` | Controle e limite dos avisos por e-mail. |

As tabelas têm RLS e nenhum grant para PUBLIC, `anon` ou `authenticated`.
O servidor recebe grants explícitos para `service_role`. Todas as funções
novas usam `SECURITY INVOKER` e `search_path` fixo. As RPCs expostas em
`public` concedem EXECUTE somente ao servidor. A migration não altera
tabelas ou funções do sistema de reservas e do painel financeiro.

O painel humano autentica o JWT com `getUser` e consulta `fn_is_admin`
sob a identidade do usuário antes de chamar o controle com a chave de
servidor. `actor_id` é preenchido pelo backend a partir do usuário validado.
A chave `service_role` e os segredos permanecem fora do navegador.

A consulta somente de leitura ao portal encontrou um cadastro da gerente
com admin ativo, autenticação vinculada e e-mail presente. O servidor já
tem os grants de leitura necessários em `app_users`; nenhum grant foi
acrescentado ao cadastro. `settings.manager_auth_user_id` começa NULL.
O responsável pela implantação resolve o identificador no banco e o
configura sem gravar UUID ou e-mail real em arquivos versionados.
Esse vínculo foi concluído em 01/11/2026; ele não habilita envio de avisos.

## Fluxo e estados

1. O receptor verifica assinatura e ativos da Meta, redige o texto e
   classifica riscos objetivos antes de truncar. `ig_support_ingest` grava
   evento e roteamento na mesma transação, deduplicando o MID antes do ACK.
2. `safety_intent` em uma das categorias permitidas pausa a conversa e cria
   o caso imediatamente. Uma mensagem seguinte não apaga um pedido de
   pessoa ou uma alergia. Nessa rota conservadora, a equipe responde;
   não há ACK automático nem chamada de IA.
3. O worker obtém uma lease por conversa. Mensagem nova muda a versão e
   invalida resultado antigo. O worker reserva orçamento antes de Gemini.
4. A conclusão limpa o texto do cliente. Pergunta desconhecida permite
   uma tentativa de esclarecimento; a repetição cria caso e pausa humana.
5. Antes de enviar, o banco confere versão, modo, allowlist, pausa e janela
   de 24h, e cria uma única outbox em `sending`. A função só registra
   `sent` com MID devolvido pelo provedor.
6. Timeout ou interrupção após iniciar o POST produz `uncertain` e caso
   humano. Esse estado não recebe reenvio automático. A equipe confere
   a conversa original antes de retomar.

Um echo só é reconhecido como bot quando seu MID já consta de envio
confirmado. Echo desconhecido pausa a conversa, inclusive se chegar antes
da resposta HTTP do próprio envio. Essa escolha pode exigir uma revisão
humana adicional; ela evita responder sobre atendimento já assumido.

A pausa por conversa não tem prazo automático. Fechar o caso mantém a
pausa e o registro continua visível no painel. Retomar exige ação explícita,
sem envio em andamento. A retomada descarta tarefas antigas e aguarda nova
mensagem; ela não dispara respostas retroativas.

## Modos e custo

A instalação começa com `mode=off`, `paused=true`, allowlist vazia,
`model_usage_allowed=false`, `billing_verified=false` e alertas desligados.
O modo da Edge Function e o do banco precisam autorizar o mesmo estágio.
`test` só aceita os remetentes expressamente listados. O painel não pode
mudar modo, limites de gasto ou autorização de uso do modelo.

O teto desta integração é R$45/mês em IA, com R$5 de margem dentro do
orçamento autorizado. O banco reserva dois centavos antes de cada geração,
no máximo 2.000 gerações/mês, dez por minuto globalmente e três por conversa
em dez minutos. A entrada completa é limitada por um limite superior de
tokens até 4.096 e a saída a 96 tokens. Com as tarifas conferidas para
Gemini 3.5 Flash-Lite (US$0,30/M de entrada e US$2,50/M de saída), câmbio
conservador de R$10/US$1 dá custo calculado de até dois centavos por chamada.

No caminho normal, o worker conserva os dois centavos reservados como custo
conservador. Os 2.000 pedidos limitam esse total a R$40. Mesmo que outro
cliente do servidor informe uso verificado menor, o limite mensal adicional
de R$45 continua sendo aplicado antes de reservar. Metadata ausente, erro
ou timeout conserva a reserva inteira. Um excesso de uso/custo informado
pausa globalmente e exige rever tarifa e configuração. O prazo de validade
da tarifa é obrigatório. Sem ele, sem aprovação de uso ou sem confirmação
de faturamento, o banco recusa nova chamada.

Esse controle cobre as chamadas do agente. Outros usos da mesma chave do
provedor têm faturamento próprio e precisam de acompanhamento separado.
Os modos de envio e de alertas permanecem desligados antes dos testes
de ponta a ponta, da conferência de privacidade e da análise da Meta.

## Aviso à gerente

O aviso usa uma outbox própria, com um alerta por caso novo. O destino é
resolvido no servidor em `app_users`, exigindo admin ativo e identidade
vinculada. O e-mail não aparece no painel, em logs ou em configurações
versionadas. O conteúdo deve conter apenas assunto por categoria e link
do painel, sem texto, nome, telefone ou identificador de cliente.

Os alertas começam desligados. Casos criados antes da ativação ficam
`suppressed`; habilitar depois não dispara o acervo. A reserva de envio
conta no máximo 60 tentativas/mês e duas por alerta. O backend inicial
não retenta automaticamente falha ou timeout. `uncertain` exige revisão;
uma extensão futura só pode retentar recusa comprovada, com a mesma chave
de idempotência e dentro do prazo do provedor. `sent` significa aceitação
pelo provedor de e-mail e exige ID retornado; não comprova leitura.

## Contrato das RPCs

Todas retornam JSONB e exigem `service_role`:

| RPC | Contrato |
| --- | --- |
| `ig_support_settings()` | Configuração sem segredos para o servidor. |
| `ig_support_ingest(p_event)` | `mid`, `sender_id`, `recipient_id`, `timestamp_ms`, `kind`, `text` redigido e `safety_intent` opcional. |
| `ig_support_claim(p_worker,p_limit)` | Array de eventos com lease, versão, remetente, texto e `first_reply`. |
| `ig_support_reserve_budget(p_event_id,p_lease,p_max_cost_cents)` | Autoriza uma única chamada; repetição retorna `already_started`. |
| `ig_support_complete(p_event_id,p_lease,p_result)` | Conclui processamento, limpa texto, cobra reserva e cria caso quando necessário. |
| `ig_support_prepare_send(p_event_id,p_lease,p_text,p_expected_version)` | Revalida e registra `sending` irreversível antes do POST. |
| `ig_support_finish_send(p_outbox_id,p_lease,p_status,p_provider_message_id)` | Confirma MID ou registra falha/resultado incerto. |
| `ig_support_control(p_action,p_thread_id,p_args)` | `status`, `cases`, `assume`, `close`, `resume`, `pause_global`; backend exige admin. |
| `ig_support_claim_alerts(p_worker,p_limit)` | Array privado com destino resolvido, lease, caso, revisão e categoria. |
| `ig_support_finish_alert(p_alert_id,p_lease,p_status,p_provider_id,p_retryable)` | Registra aceitação/falha/incerteza, sem duplicar resultado final. |

## Recuperação contínua

O ACK não depende de uma chamada ao modelo. `waitUntil` pode acelerar o
worker, mas a fila permanece no PostgreSQL. Um cron de segurança está
preparado com nome estável `sirfisher-instagram-support-drain` e começa
inativo. Ele recupera leases vencidas e chama `/instagram-support/drain`
somente se houver tarefa elegível.

O segredo do drain fica em Vault como `instagram_support_drain_secret` e
é enviado no header `x-instagram-drain-secret`. A função privada de nudge
executa como o owner do cron; o servidor não recebeu acesso ao Vault.
O endpoint é fixo no projeto portal. Uma chave anônima não autoriza drain.
Falhas registram só SQLSTATE, sem payload ou segredo. A pausa global do
bot preserva avisos humanos habilitados; `mode=off` bloqueia os provedores.

## Validação e ativação pendente

Os testes usam PostgreSQL real local e dados fictícios, sem chamar Meta,
Gemini ou Resend. O runner exige flag explícita, host loopback e banco
`sirfisher_ig_support_test` e confere novamente o destino no servidor.
Reaplica a migration para testar idempotência. Exercita RLS/grants,
concorrência entre conexões, reserva e limites, pausa humana, mensagens em
rajada, echo antecipado, timeout e alertas sem retroativos.

Exemplo em um banco local descartável já criado:

```powershell
$env:IG_SUPPORT_SQL_DISPOSABLE='1'
$env:PGHOST='127.0.0.1'
$env:PGPORT='65437'
$env:PGUSER='postgres'
$env:PGDATABASE='sirfisher_ig_support_test'
python -B scripts/ci/test_instagram_support_sql.py
```

O workflow Quality também usa banco dedicado no serviço PostgreSQL 15.
A execução local em PostgreSQL 18 aprovou 17 testes; a checagem estática e
o catálogo de 224 migrations também passaram. O servidor local descartável
foi encerrado após os testes. A aplicação ao portal conferiu apenas os
objetos e os modos seguros; o backend e os provedores ainda exigem os
testes descritos a seguir.
A execução local não comprova compatibilidade da implantação, entrega de
webhook, envio de Direct ou leitura do aviso pela gerente. Antes de ativar:
revisar os dois repositórios, conferir grants e advisors, implantar a Edge
Function desligada, configurar segredos e
identidade da gerente e testar com remetente controlado. Só depois tratar
permissões/review e ativação na Meta. Não usar clientes como conta de teste.

### Aplicação restrita desta migration

Usar o carregador existente `site/tools/analytics/supabase_credentials.py`
e executar `verify_portal()` antes de escrever. Para a aplicação autorizada,
usar a rota Management API `POST /v1/projects/lucpxoynpvogkvzepagi/database/query`;
a rota `/query/read-only` e o MCP de leitura continuam sem escrita.

Ler o arquivo canônico em memória, conferir sua versão e preparar uma única
transação. Antes do último `COMMIT`, acrescentar a inserção no histórico:

```sql
insert into supabase_migrations.schema_migrations(version,name,statements)
values ('20261101071634','instagram_support_durable_queue',array[/* corpo SQL como literal seguro */]);
```

O cliente deve construir o literal com um delimitador dollar-quote que não
exista no arquivo e enviar o JSON por argumento estruturado. Não interpolar
SQL, segredo ou credencial em comando do shell. Não usar ON CONFLICT: uma
versão já registrada deve impedir a aplicação e provocar rollback, até que
o conteúdo existente seja conferido. A migration já contém BEGIN/COMMIT e
NOTIFY para recarregar o schema do PostgREST; não a envolver em outra
transação incompleta. Confirmar a versão, os objetos, grants e modos depois.

Para vincular a gerente sem imprimir identidade ou e-mail, executar depois
da implantação e revisar somente a contagem e os flags retornados:

```sql
do $manager$
declare v_ids uuid[];
begin
  select array_agg(auth_user_id) into v_ids
  from public.app_users
  where active and role='admin' and auth_user_id is not null
    and translate(lower(coalesce(name,'')),'êéèë','eeee') like '%hemile%';
  if coalesce(array_length(v_ids,1),0)<>1 then
    raise exception 'Cadastro da gerente ausente ou ambiguo; revisar.';
  end if;
  update instagram_support.settings
    set manager_auth_user_id=v_ids[1],alerts_enabled=false,updated_at=now()
    where singleton;
end;
$manager$;
```

Esse lookup não concede acesso nem altera `app_users`. Ainda não habilita
modelo, aviso ou Direct. O responsável pela implantação confere a modalidade
de faturamento/privacidade do Gemini antes de preencher os flags de aprovação
e `pricing_valid_until`; o painel não possui esse comando.

O segredo de drain deve ser criado em armazenamento privado e configurado
com o mesmo valor no ambiente da Edge Function e em um único registro Vault
chamado `instagram_support_drain_secret`. Transferir o valor apenas em
memória por HTTPS oficial; não colocar em chat, arquivo versionado ou
argumento visível de processo. Conferir só existência e comprimento.
Com segredo ausente ou nome duplicado, o nudge não chama o worker.

O cron começa inativo. Após teste controlado, o responsável pode habilitar
`settings.cron_enabled` e o job pelo nome estável, conferindo `active` e o
owner. Até essa etapa, manter ambos desligados. Alertas exigem habilitação
separada e `alerts_activation_after` preenchido no instante da ativação;
os casos anteriores permanecem suprimidos. Antes de ativar o agente, testar
também as FAQs nativas existentes e deixar uma aplicação responsável por
responder a cada evento, evitando duplicidade entre fornecedores.

## Referências consultadas em 01/11/2026

- [Supabase: funções de banco](https://supabase.com/docs/guides/database/functions),
  [API e grants](https://supabase.com/docs/guides/api/securing-your-api).
- [Supabase: agendamento de Edge Functions](https://supabase.com/docs/guides/functions/schedule-functions),
  [pg_net](https://supabase.com/docs/guides/database/extensions/pg_net).
- [Supabase changelog](https://supabase.com/changelog.md): verificadas as
  mudanças relevantes de TLS e segurança; nenhuma alteração desses
  componentes foi feita nesta preparação.
- [Google: preço do modelo](https://ai.google.dev/gemini-api/docs/pricing).

## Advisors dos objetos novos

Os comandos MCP de security/performance para o portal foram negados por
permissão do conector. A mesma leitura oficial foi concluída com HTTP 200
pela Management API e o PAT já existente, sem reconexão nem mudança de
escopo. Foram apresentados somente os achados de `instagram_support`
e das RPCs novas; os avisos dos outros sistemas não foram alterados.

- Segurança: dez INFO de [RLS sem policy](https://supabase.com/docs/guides/database/database-linter?lint=0008_rls_enabled_no_policy).
  Esse estado é intencional no schema privado: os clientes não têm USAGE,
  grants ou EXECUTE, e somente service_role com BYPASSRLS usa o componente.
- Desempenho: quatro INFO de [FK sem índice](https://supabase.com/docs/guides/database/database-linter?lint=0001_unindexed_foreign_keys)
  (`budget_reservations.month`, `cases.event_id`, `control_audit.thread_id`
  e `outbox.thread_id`) e sete INFO de
  [índice ainda sem uso](https://supabase.com/docs/guides/database/database-linter?lint=0005_unused_index),
  em tabelas recém-criadas e sem eventos. Nenhum índice foi retirado.

Não apareceram WARN ou ERROR para os objetos novos. Os INFO de desempenho
ficam registrados para revisão quando houver carga medida; essa consulta
não comprova desempenho de atendimento em produção.
