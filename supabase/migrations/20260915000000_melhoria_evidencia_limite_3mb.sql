-- Baixa o teto por arquivo das evidencias de 10 MB para 3 MB.
--
-- Motivo: o Storage do Supabase consome a cota do projeto, que e apertada. Tres
-- megabytes cobrem com folga o caso real desta rotina — um print de tela, uma
-- foto de prato ou um PDF curto. Arquivo maior que isso continua cabendo na
-- rotina como link (Drive, OneDrive), que nao ocupa cota nenhuma.
--
-- O limite e POR ARQUIVO, nao por ideia nem por bucket: quem precisa segurar o
-- total acompanha o uso pelo painel do Supabase.
--
-- Idempotente: so ajusta a coluna do bucket, e o bloco e condicional porque o
-- schema storage nao existe em Postgres puro.

begin;

do $migration$
begin
  if to_regclass('storage.buckets') is null then
    raise notice 'Schema storage ausente: limite do bucket nao ajustado.';
    return;
  end if;

  update storage.buckets
     set file_size_limit = 3145728
   where id = 'melhoria-evidencias';
end;
$migration$;

commit;
