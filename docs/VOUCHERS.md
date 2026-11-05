# Vouchers de benefício Sir Fisher

Emissão: [Gestão / Vouchers](https://admin.sirfisher.com.br/vouchers.html),
também em Rotinas. Consulta e utilização:
[Reservas / Vouchers](https://reservas.sirfisher.com.br/admin/vouchers.html),
no menu e dashboard. Não são reservas de Réveillon e não geram lançamentos
financeiros ou operações no Teknisa.

## Regras confirmadas em 04/11/2026

- Uso único. Saldo não utilizado perdido. Não acumula com promoções nem
  com outro voucher na mesma conta.
- Valor fixo em reais ou percentual positivo até 100%, até duas casas
  decimais. Percentual sobre a conta inteira, taxa de serviço opcional,
  sem teto em reais. Aplicação do benefício e não cumulatividade são
  conferidas pela equipe no caixa; não há integração ao POS neste pedido.
- Uma unidade: Sir Fisher. Sem exclusões de dias/horários cadastradas.
- Validade sugerida de 30 dias, editável antes de emitir; aceita o mesmo
  dia, nunca data passada. Data inclusiva até o fim do dia em
  `America/Fortaleza`. A imagem exibe só a data. Não há prazo máximo de
  negócio imposto além do formato de data aceito pela interface.
- Motivo obrigatório: cliente insatisfeito, amigo, representação
  comercial/fornecedor, modelo em produção de fotos, aniversário de
  funcionário, fidelidade, ação promocional/sorteio, parceria com
  influenciador, premiação/atingimento de metas ou outro. Outro exige descrição livre; demais permitem
  complemento opcional. Não há motivo pré-selecionado.
- Nome, telefone, tipo/valor e validade obrigatórios. Nota interna opcional.
  Sócio/admin pode corrigir os campos pelo botão Editar enquanto o voucher
  estiver disponível. Código e emissor são preservados; alterações ficam no
  histórico com responsável, data e valores anteriores/novos. Usados,
  cancelados ou vencidos não são editáveis.

## Acesso, fluxo e privacidade

Sócio ou administrador ativo da gestão com permissão da página pode
emitir, listar, filtrar por situação/motivo, abrir detalhes, editar e cancelar.
Gerente da gestão não emite mesmo se liberarem a página na matriz.
Resgate exige cadastro ativo de `app_users` no reservas com papel
existente `admin` ou `operator`; ser sócio da gestão sozinho não concede
resgate. O servidor nunca aceita ator, instante ou situação do cliente.

Gerente consulta o código e confirma explicitamente o uso ao aplicar o
benefício na conta. Erro de rede dispara somente consulta; bloqueia nova
tentativa até reconsulta manual. Usado, vencido ou cancelado não é resgatável.
Telefone, motivo/complemento e nota interna ficam apenas na gestão.
Consulta do reservas, imagem e mensagem WhatsApp usam campos permitidos
explicitamente. Telefone prepara o destino somente ao acionar o link.
Não há consulta pública, QR público ou link que conceda resgate.

PNG horizontal 1600×1000 gerado localmente por Canvas, com foto autoral do deck,
emblema e Fraunces oficiais; sem API de imagens, serviço pago ou edição manual.
A foto `assets/vouchers/deck.webp` é cópia idêntica de
`site/assets/img/terraco-por-do-sol-sir-fisher-960.webp`; autoria do proprietário
registrada no guia de analytics do site. O enquadramento preserva mesas e
horizonte, sem deformar a foto. Os dados do voucher ficam sobre fundo liso.
O cartão sobre a foto mostra benefício, beneficiário, código de seis caracteres
e validade. Rodapé reduzido a uso único e não cumulatividade; as regras completas
continuam no cadastro e na consulta da equipe, sem repetições na imagem.
Ajusta fonte para nomes longos e valores elevados sem omitir o nome. Não gera nova
imagem de voucher indisponível. Imagem já enviada pode circular após
cancelamento: consulta ao servidor é obrigatória na utilização.

Vouchers já emitidos usam a nova arte ao reabrir seus detalhes; não é preciso
emitir novamente. A foto é desenhada no mesmo Canvas que gera o arquivo PNG
baixado/compartilhado, não apenas mostrada na interface. Carregamento da foto
é obrigatório e erro impede baixar silenciosamente a versão sem imagem.
Depois de editar, baixar/compartilhar a nova imagem; o arquivo enviado antes
não pode ser recolhido automaticamente. Gerente sempre consulta o servidor.

Compartilhamento nativo usa arquivo previamente preparado. Cancelar essa
janela não dispara download. Sem suporte ou com recusa do navegador,
oferece download e link WhatsApp com texto: anexar manualmente o PNG de
Downloads. O link não envia arquivo nem mensagem automaticamente.

## Banco e implantação

Migration canônica `supabase/migrations/20261104200024_benefit_vouchers.sql`.
Complemento `20261104202352_benefit_voucher_private_rpc.sql`: implementações
SECURITY DEFINER ficam no schema privado, wrappers públicos são INVOKER.
Complemento `20261104203828_benefit_voucher_award_reason.sql`: inclui a
categoria interna Premiação / atingimento de metas na emissão e no filtro.
Aplicado e relido no portal em 04/11/2026, com emissão/filtro verificados
pelos perfis reais em transação revertida.
Complementos aplicados em 05/11/2026: `20261104205451_benefit_voucher_edit.sql`
(edição, auditoria, revisão do benefício) e
`20261105130459_benefit_voucher_short_codes.sql` (código curto e aliases antigos).
Tabelas novas `private.benefit_vouchers`, `private.benefit_voucher_events`
e `private.benefit_voucher_rate_limits`, com RLS e privilégios diretos
revogados de PUBLIC, anon, authenticated e service_role. Não há Edge
Function consumidora. As RPCs públicas `benefit_voucher_*` (issue,
list, detail, edit, cancel, lookup, redeem) recebem só EXECUTE para authenticated,
com autorização interna e search_path fixo. Helpers privados sem EXECUTE
externo, exceto as implementações privadas correspondentes às RPCs,
que recebem EXECUTE de authenticated e repetem todos os gates de perfil.
O schema private já tem USAGE para authenticated; nenhum grant de schema
foi ampliado. Não altera perfis ou tabelas dos outros sistemas.

Listagem separa quantidade de percentuais do total disponível em reais,
com paginação. Emissão, utilização e cancelamento registram identidade,
nome no momento da ação e evento. Motivos de emissão/cancelamento são internos.

Códigos exibidos: seis caracteres Crockford, sem prefixo (30 bits aleatórios,
1.073.741.824 combinações), índice único e nova tentativa por colisão.
Vouchers existentes recebem código curto; seus códigos antigos de 12 caracteres
com SF continuam como aliases, sem invalidar imagens já enviadas.
Normalização tolera espaços, traços,
caixa e aliases O→0/I/L→1. Consulta autenticada: 30 tentativas/minuto por
usuário; emissão 10, listagem 60, resgate 20. Contador atômico retorna
recusa estruturada, persistindo consultas inválidas. `request_id` único
permite repetir emissão cuja resposta se perdeu sem duplicar voucher.

Edição, resgate e cancelamento disputam o mesmo FOR UPDATE. Validade conferida
pelo relógio capturado após lock; esse mesmo instante é registrado no uso.
Estado/evento na mesma transação e índice único adicional para evento de uso.
Edição incrementa `revision`, guarda snapshots privados antes/depois e recusa
sobrescrever edição concorrente. Resgate do reservas envia `p_expected_revision`;
se o sócio mudou os dados depois da consulta, o gerente precisa conferir a nova
versão e confirmar novamente. Cliente antigo só resgata voucher nunca editado.

`python scripts/implantacao/aplicar_benefit_vouchers.py` ensaia a migration
com rollback e verifica gates dos perfis reais sem exibir identidades;
`--aplicar` aplica só essas cinco versões e registra histórico na mesma transação.
Conexão valida portal. Não usar MCP somente leitura para escrever.
Publicar páginas depois do banco.

As migrations iniciais foram aplicadas e relidas no portal em 04/11/2026.
A verificação com perfis reais passou, com rollback das fixtures.
Security Advisor: nenhum WARN/ERROR dos objetos de vouchers após o
complemento; três INFO de RLS sem policy são intencionais, pois tabelas
privadas negam acesso direto e só as implementações autorizadas operam nelas.
Consulta HTTP anônima à RPC foi negada com 401/42501.

## Verificação

- `node --test scripts/ci/test_benefit_vouchers.mjs`: valores, datas,
  nomes, privacidade da imagem/texto, compartilhamento/fallback.
- `python scripts/ci/test_benefit_vouchers_sql.py`: PostgreSQL descartável
  local com PGDATABASE=sirfisher_vouchers_test e PGHOST local.
- `--portal-rollback`: migration reexecutada em schemas isolados; perfis
  sintéticos, grants, filtros, motivos, validade, repetição, NaN/Infinity,
  rate limit e colisões. Rollback obrigatório; nenhum registro real tocado.
- `--portal-concurrency`: só schemas sintéticos próprios commitados para
  disputas entre conexões: dois resgates, resgate versus cancelamento,
  emissão idempotente, duas edições e edição versus resgate.
  Limpeza exata em finally e ausência conferida. Inclui rollback após falha
  no histórico, revisão antiga, códigos curtos e aliases de vouchers antigos.
- `node scripts/ci/render_benefit_vouchers.mjs <módulo-canvas> <pasta>`:
  QA opcional com cinco PNGs sintéticos. @napi-rs/canvas é ferramenta local,
  não dependência do produto/deploy.
- Reservas: `node --test tools/benefit_vouchers_test.mjs` cobre a sessão e
  erros de rede antes/depois da gravação.

Na publicação Pages, `versionar_assets_pages.py` calcula os hashes dos JS/CSS
e reescreve as referências somente no artefato. A mudança de conteúdo gera
URL nova automaticamente; os arquivos originais usados nas outras páginas
continuam disponíveis. Testes em `scripts/ci/test_pages_assets.py`.

PNGs renderizados e inspecionados. Layout/responsividade da página,
autenticação interativa e WhatsApp real não foram exercitados: o Browser
integrado retornou indisponível. Testes de funções/estado não comprovam
esses fluxos visuais.

## Referências visuais

Estas páginas foram consultadas apenas para observar como cartões-presente
mostram o benefício e organizam textos curtos. Não há vínculo do Sir Fisher
com essas empresas nem uso das fotografias ou artes delas no voucher.

- [Belmond Gifts](https://gifts.belmond.com/gbp): apresentação do presente
  como uma visita ou experiência na casa.
- [The Dorchester Gifts](https://gifts.dorchestercollection.com/the-dorchester):
  destaque visual para o valor ou benefício oferecido.
- [Alain Ducasse](https://www.alainducasse-dorchester.com/gift-cards/):
  mensagem curta e pessoal.

Sem importar regras ou copiar artes/fotos. A imagem fornecida mostra o
processo anterior; por orientação do usuário não determina a composição.
Paleta e fonte vêm do site oficial Sir Fisher.
