@AGENTS.md

# Instruções específicas para Claude Code

- O `AGENTS.md` importado acima é a fonte canônica das regras do projeto.
- Quando necessário, use `/memory` para confirmar que este arquivo e o `AGENTS.md` foram carregados na sessão.

## Autorização permanente para commit e push

- A autorização permanente para todas as IAs, incluindo Claude Code, está no `AGENTS.md` e no `../AGENTS.md`: validar, commitar, dar push para `main`, publicar e sincronizar os três repositórios e as orientações da raiz, sem nova confirmação rotineira. A configuração local do Claude em `.claude/settings.local.json` continua específica desse cliente; uma instrução em Markdown não modifica permissões técnicas do ambiente.
- Isso não dispensa nenhuma outra regra do `AGENTS.md`: revisar `git status`/`git diff` antes de commitar, incluir apenas arquivos relacionados à tarefa, nunca commitar segredos/dados sensíveis/CSVs/XLSX, mensagens de commit claras, e relatar o `git status` final.
- Ações destrutivas (reset --hard, force push, descartar alterações, editar migrations antigas, etc.) continuam exigindo autorização explícita a cada vez.
