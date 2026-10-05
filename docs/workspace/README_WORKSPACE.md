# Workspace Sir Fisher

Esta pasta e o ponto de entrada do ecossistema digital do restaurante. Ela nao
e um repositorio Git unico: contem tres projetos independentes, cada qual com
seu proprio historico, remoto e deploy.

| Projeto | Pasta local | Repositorio oficial | Branch principal | Finalidade |
| --- | --- | --- | --- | --- |
| Site institucional | `site/` | `sirfisherfc/site` | `main` | Site publico em `sirfisher.com.br` |
| Reservas | `reservas/` | `sirfisherfc/reservas` | `main` | Portal em `reservas.sirfisher.com.br` |
| Gestao financeira | `gestao/` | `sirfisherfc/gestao` | `main` | Painel em `admin.sirfisher.com.br` |

## Organizacao local

- `site/_materiais/`: fotos-fonte, diagnosticos e briefs locais do site. Sao
  ignorados pelo Git; os derivados publicados vivem no proprio site.
- `site/tools/analytics/`: scripts de Analytics, Google Business Profile e
  midia. Credenciais e ambiente virtual continuam ignorados pelo Git.
- `reservas/output/` e `reservas/tmp/`: artefatos locais gerados, ignorados
  pelo Git.
- `gestao/_Backups/`: bundles locais de recuperacao do painel financeiro,
  ignorados pelo Git.
- `.claude/`: configuracao local do workspace.

Os tres projetos compartilham o Supabase `portal` (ref
`lucpxoynpvogkvzepagi`), mas cada um deve ser alterado, testado e enviado no
seu proprio repositorio. O antigo banco Durth Vader nao e utilizado.
