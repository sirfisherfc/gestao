# Revisão dos alertas do Cloudflare

Conferência em 02/11/2026, no horário de Fortaleza, após o proprietário
acrescentar permissões de leitura ao token existente. Esta revisão consultou
a API e testou os serviços públicos. Nenhuma configuração foi alterada,
regra desativada ou ocorrência arquivada.

## Acesso confirmado

O token está ativo. As leituras de Security Insights e das regras WAF
passaram a retornar `success=true`; anteriormente retornavam HTTP 403.
O carregador `scripts/cloudflare/cf.py` reutiliza `CLOUDFLARE_API_TOKEN`
do ambiente ou de `gestao/.env`, ignorado pelo Git.

Permissões acrescentadas para a zona `sirfisher.com.br`:
`Zone Security Center Insights` e `Zone WAF Read`. Consultas reais aprovadas:

- `GET /zones/{zone_id}/security-center/insights?dismissed=false&per_page=1000`
- `GET /zones/{zone_id}/rulesets/phases/http_request_firewall_custom/entrypoint`
- `GET /zones/{zone_id}/security-center/insights/audit-log`

O comando `cf.py diagnostico` atual cobre DNS, algumas configurações,
certificados e regras de cache/redirecionamento/cabeçalhos. Ele ainda não
consulta Security Insights nem o conteúdo das regras WAF. Sua execução
isolada deixa essa parte da revisão pendente.

## Resultado

A API retornou **21 ocorrências ativas em 10 classes**: 17 Moderate e quatro
Low. A interface agrupa ocorrências da mesma classe. Cada item exige avaliar
a configuração correspondente antes de corrigir ou arquivar.

| Alerta | Quantidade | Evidência e encaminhamento |
| --- | ---: | --- |
| Dangling A | 4 | Os IPv4 são os oficiais do GitHub Pages. Todos responderam 200 para `www` e 301 do domínio sem `www` para `www`, com certificados validados. Preservar os registros e concluir a verificação de proteção do domínio no GitHub antes de arquivar como falso positivo. |
| Dangling AAAA | 4 | Os IPv6 coincidem com os oficiais do Pages. O vínculo do site foi confirmado pela API GitHub; conexão direta a cada IPv6 não foi testada. Concluir a verificação do domínio. |
| TLS antigo | 2 | `www` e `webmail` aceitaram TLS 1.0 e 1.1 em conexões reais. Também aceitaram 1.2 e 1.3. Correção de configuração pendente. |
| CNAME sem proxy | 5 | `admin` e `reservas` atendem via GitHub Pages, fora da borda HTTP Cloudflare. `autoconfig`, `autodiscover` e `webmail` apontam para a Hostinger. Avaliar o proxy por serviço; o e-mail tem requisitos próprios. |
| DMARC | 1 | O payload cita `p=none`. O TXT é `v=DMARC1; p=none`, válido, sem quarentena/rejeição e sem `rua` para solicitar relatórios agregados. Conferir autenticação/alinhamento dos remetentes Hostinger e Resend/SES antes de endurecer a política. |
| Muitas regras Skip | 1 | As duas regras customizadas ativas usam Skip somente na fase `http_request_sbfm`, com logs. O gatilho é mais de 30% das regras usarem Skip; ele não mede o percentual de tráfego com exceção. |
| Bot Fight Mode | 1 | `fight_mode=false`. O modo gratuito ignora as exceções Skip atuais; avaliar o efeito sobre rastreadores liberados antes de ativar. |
| AI Labyrinth | 1 | O insight informa o recurso desligado. Recurso opcional; avaliar junto da decisão de permitir leitura pública por robôs de IA. |
| security.txt | 1 | A configuração da API veio vazia. `/.well-known/security.txt` e `/security.txt` responderam 404 em `www`. Definir contato público e validade antes de publicar. |
| Lista de IPs | 1 | A única faixa nas regras customizadas atuais é `85.208.98.0/24`, para Semrush. Migrar para lista é uma opção de manutenção. |

## TLS e GitHub Pages

A zona usa `min_tls_version=1.0`, `tls_1_3=on` e `ssl=full`. A correção
candidata é elevar o mínimo para `1.2`, mantendo TLS 1.3 ligado. A mudança
atinge os hosts com proxy na zona, inclusive Workers. Conferir os fluxos
afetados e testar a rejeição de 1.0/1.1 e o funcionamento com 1.2/1.3.
`webmail` usa DNS-only: seu TLS depende da Hostinger, e a configuração da
borda Cloudflare não modifica esse serviço.

A API GitHub confirmou os três sites como `built`, com HTTPS obrigatório
e os domínios esperados (`www`, `admin`, `reservas`). Os quatro endereços
públicos, incluindo o domínio sem `www`, terminaram em HTTP 200.
`protected_domain_state` veio nulo, e os 27 registros DNS atuais não incluem
`_github-pages-challenge-*`. A verificação do domínio pela organização
continua sem comprovação. A consulta de saúde de DNS do Pages retornou 404
nos três repositórios e não forneceu essa comprovação.

Conferir `sirfisher.com.br` em Settings > Pages da organização `sirfisherfc`.
Se a verificação estiver pendente, usar o desafio fornecido pelo GitHub e
manter o TXT. O site em operação comprova a associação atual; a verificação
oferece proteção contra reivindicações após uma desvinculação.

## Exceções e histórico

As duas regras relidas coincidem com o escopo registrado em
`SEMRUSH_3_DIAS_2026-10-25.md`: host `www`, métodos GET/HEAD e 15 caminhos
públicos, incluindo robots/sitemap. Semrush exige ainda a faixa oficial
registrada, `SemrushBot-SI/` e consulta vazia. A regra de IA compara 31 textos
de user-agent; esse cabeçalho pode ser imitado e não autentica o rastreador.

Ambas pulam somente `http_request_sbfm`, preservando as outras fases.
Revisar necessidade/escopo e caminhos novos. O percentual de Skip, sozinho,
não justifica remover as exceções autorizadas em 25/10.

O histórico local registra ajustes pontuais em 13/10 e 25/10. As datas dos
insights registram detecção/atualização do serviço e não comprovam a data
de uma revisão humana. Esta leitura encerra a conferência dos alertas;
as correções e a comprovação do domínio listadas acima continuam pendentes.

## Fontes oficiais

- [Permissões dos tokens](https://developers.cloudflare.com/fundamentals/api/reference/permissions/)
- [Revisão dos Security Insights](https://developers.cloudflare.com/security/security-insights/review-insights/)
- [TLS mínimo na borda](https://developers.cloudflare.com/ssl/edge-certificates/additional-options/minimum-tls/)
- [Domínio e endereços do GitHub Pages](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)
- [Verificação do domínio no GitHub](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages)
- [Limites do Bot Fight Mode](https://developers.cloudflare.com/bots/get-started/bot-fight-mode/)
- [DMARC e autenticação de e-mail](https://developers.cloudflare.com/email-service/concepts/email-authentication/)
