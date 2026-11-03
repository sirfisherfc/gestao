# Correções dos alertas do Cloudflare

Estado atualizado em 03/11/2026, no horário de Fortaleza, após autorização
do proprietário para corrigir os itens necessários. A primeira leitura
retornou 21 ocorrências em dez classes: 17 Moderate e quatro Low.

## Aplicado e conferido

| Item | Resultado |
| --- | --- |
| TLS antigo | Mínimo da zona elevado de 1.0 para 1.2, com TLS 1.3 mantido. Conexões reais em www, domínio sem www, admin, reservas, webmail, ativacao e reparos recusaram TLS 1.0/1.1 e aceitaram 1.2/1.3. |
| Admin e reservas | Proxy Cloudflare ligado nos dois CNAME, mantendo destino GitHub Pages. Os HTMLs e cinco arquivos JS/CSS responderam 200 e coincidiram com os repositórios. |
| Webmail | Proxy ligado e regra 302 para `https://mail.hostinger.com/auth/login`, sem repassar consulta. O endereço próprio funciona como atalho para o login oficial da Hostinger, com TLS atualizado na nossa zona. |
| security.txt | Publicado pelo Cloudflare em `/.well-known/security.txt`, com `mailto:contato@sirfisher.com.br`, contato já público no site. Validade até 31/10/2027 às 23:59:59 UTC, idiomas pt-BR/en. Apex e www responderam 200/text/plain. Renovar antes do vencimento. |
| DNS do GitHub Pages | Oito A/AAAA classificados como `false_positive`, com justificativa e confirmação no histórico da API. Os quatro IPv4 servem www e redirecionam apex com certificados válidos; os IPv6 coincidem com a documentação oficial e não foram testados por conexão direta. Registros preservados. |
| Proteção do domínio no GitHub | O proprietário concluiu Verify na conta sirfisherfc após a publicação do TXT. API confirmou `protected_domain_state=verified`, Pages `built` e HTTPS obrigatório nos três repositórios. www/admin/reservas responderam 200 após a verificação. |
| DMARC | Em 03/11, teste atual da Hostinger passou SPF, DKIM e DMARC no Gmail. Publicado `v=DMARC1; p=quarantine; sp=none; rua=mailto:contato@sirfisher.com.br`, confirmado na API e no DNS público Google/Cloudflare. Quarentena para o domínio principal, subdomínios em monitoramento e relatórios preservados. Rejeição e política dos subdomínios dependem da análise posterior dos envios/relatórios. |

Na primeira rodada, dos 27 registros DNS, mudaram somente `proxied` em
admin/reservas/webmail e o TXT DMARC. Depois foi acrescentado o desafio TXT
do GitHub Pages, totalizando 28 registros. MX, SPF, DKIM e descoberta de
e-mail permaneceram iguais.
As duas regras WAF e o objeto Bot Management foram comparados antes/depois
e permaneceram iguais. A regra apex para www foi preservada junto do novo
atalho do webmail.

## Alertas que ainda podem aparecer

A releitura de 02/11 retornou **13 ocorrências não classificadas**. Os oito falsos
positivos deixaram essa lista; o endpoint de arquivamento não foi executado.
A lista ainda trazia seis ocorrências de TLS, security.txt e CNAME já
corrigidas e conferidas no serviço real. O scanner precisa atualizar essas
detecções; não há prazo de atualização confirmado. Essa contagem não mede
quantas falhas continuam confirmadas.

| Item restante | Tratamento |
| --- | --- |
| autoconfig/autodiscover sem proxy | Mantidos DNS-only na Hostinger. Configuram clientes de e-mail; avaliar o suporte do provedor antes de usar proxy HTTP. |
| Duas regras Skip | Mantidas conforme autorização de 25/10: www, GET/HEAD e 15 caminhos públicos. Pulam somente `http_request_sbfm`, com logs; outras fases preservadas. Semrush exige faixa oficial, agente e consulta vazia. A regra de IA usa user-agent, que pode ser imitado. O percentual de regras Skip não mede o tráfego com exceção. |
| Bot Fight Mode | Mantido desligado. O modo gratuito ignora as exceções Skip e pode afetar os rastreadores autorizados. |
| AI Labyrinth | Recurso opcional mantido desligado; a decisão vigente permite leitura pública por robôs de IA. |
| Lista de IPs | Manutenção opcional para a única faixa atual, `85.208.98.0/24`; regras preservadas. |

## Teste da Hostinger aprovado e quarentena DMARC ativa

O proprietário enviou pelo webmail uma mensagem de teste de
`contato@sirfisher.com.br`, recebida no Gmail em 03/11/2026. A leitura dos
cabeçalhos adicionados por `mx.google.com` confirmou SPF, DKIM e DMARC com
resultado `pass`, entrega na caixa de entrada e assinatura do domínio
`sirfisher.com.br`, seletor `hostingermail-a`. O Return-Path também usa
`sirfisher.com.br`. O teste ocorreu sob a política anterior de monitoramento.

O outro serviço conhecido é Resend/Amazon SES. Oito mensagens automáticas
recebidas de 06/09 a 30/09/2026 passaram SPF, DKIM e DMARC com alinhamento
do domínio. Essa amostra é histórica e não comprova todos os fluxos atuais.

Com as fontes conhecidas aprovadas, aplicada a etapa de quarentena no
domínio principal dentro da autorização de corrigir os alertas necessários:

```text
v=DMARC1; p=quarantine; sp=none; rua=mailto:contato@sirfisher.com.br
```

`p=quarantine` pede ao destinatário que envie ao spam mensagens do domínio
principal que falhem no DMARC. O alinhamento permanece relaxado, como antes.
`sp=none` mantém os subdomínios em monitoramento enquanto seus possíveis
endereços From são conferidos; o teste atual cobre o domínio principal.
O Return-Path de Resend em `send.sirfisher.com.br` não transforma o From
principal em um remetente de subdomínio. A mudança não alterou MX, SPF,
DKIM ou qualquer outro registro DNS; os 28 registros foram preservados.

API e resolvedores públicos Google/Cloudflare confirmaram a política exata.
A revisão independente confirmou Pages verified/built/HTTPS e HTTP 200
nos três sites. Recibos do teste e da alteração ficam em
`tmp/cloudflare-seguranca-2026-11-03/`, ignorado pelo Git, sem corpo da mensagem
ou endereço do destinatário. O carregador existente reutilizou o token;
nenhuma credencial nova foi necessária.

Próxima etapa: analisar os relatórios solicitados para
`contato@sirfisher.com.br`, corrigir eventuais fontes legítimas que falhem e
avaliar `p=reject` e a política de subdomínios conforme a cobertura observada.
O teste atual não garante entrega de fluxos sem amostra. Não foi criada
rotina agendada nem prometida revisão automática. O teste foi enviado pelo
proprietário; no Gmail, o assistente fez somente a leitura.

## Domínio verificado na conta sirfisherfc

A API confirmou que **sirfisherfc é uma conta pessoal (`User`)**, dona dos
três repositórios. O encaminhamento inicial que a chamou de organização
foi corrigido. O `gh` local usa durthvader, colaborador com push, sem admin
no repositório consultado. A verificação Pages acontece no perfil do dono.

A API confirmou `protected_domain_state=verified` nos três Pages após o
proprietário concluir Verify no perfil sirfisherfc. Os três continuaram
`built`, com HTTPS obrigatório e os domínios esperados. A conferência HTTP
posterior retornou 200 em www, admin e reservas, cada um no próprio host.

O navegador ficou indisponível para controle. O proprietário forneceu duas
vezes um desafio com prefixo `_github-pages-challenge-durthvader`. Esse TXT
ficou sem publicação: verificar em outra conta pode desvincular o domínio
dos sites do proprietário atual, conforme a documentação do GitHub.

Depois, o proprietário forneceu o desafio correto de sirfisherfc. O TXT
`_github-pages-challenge-sirfisherfc.sirfisher.com.br` foi criado no Cloudflare
com o valor recebido, TTL 300 e DNS-only. A releitura da API e os resolvedores
públicos Google e Cloudflare confirmaram o valor exato. Os outros 27 registros
permaneceram iguais. Recibos ficam em `tmp/cloudflare-seguranca-2026-11-02/`.

O proprietário concluiu o clique manual e forneceu a tela de sucesso, com a
conta sirfisherfc identificada. A leitura posterior da API confirmou a
conclusão. **Manter o TXT**: o domínio principal verificado também protege
seus subdomínios imediatos, incluindo www, admin e reservas. Para consultar
o estado no painel, usar `https://github.com/settings/pages` em sirfisherfc.

## Ferramenta e validações

`scripts/cloudflare/cf.py` usa `CLOUDFLARE_API_TOKEN` do ambiente ou de
`gestao/.env`, ignorado pelo Git. As leituras de Insights e WAF e as
alterações autorizadas de configuração, DNS e classificação passaram na API.

`cf.py diagnostico` agora lê TLS mínimo, regras WAF e Insights, distinguindo
acesso indisponível de lista vazia. O comando `site` atualiza cada regra
por identificação e preserva as regras dos outros serviços, incluindo
webmail. POST de criação incerto exige releitura do destino antes de repetir.
TLS mínimo 1.2 foi incluído na configuração aplicada pelo comando `site`.

Passaram 17 testes Cloudflare, seis novos, e o check do projeto com 123
contratos e 31 de segurança. A validação real cobriu API, DNS, HTTP/arquivos
e TLS. O login autenticado não foi conferido visualmente: o navegador
estava indisponível. Planos e recibos privados ficam em
`tmp/cloudflare-seguranca-2026-11-02/`, ignorado pelo Git. Esta documentação
não contém credencial ou corpo das mensagens.

## Fontes oficiais

- [TLS mínimo](https://developers.cloudflare.com/ssl/edge-certificates/additional-options/minimum-tls/)
- [Revisão dos insights](https://developers.cloudflare.com/security/security-insights/review-insights/)
- [Classificação de insight](https://developers.cloudflare.com/api/resources/security_center/subresources/insights/subresources/classification/methods/update/)
- [Limites do Bot Fight Mode](https://developers.cloudflare.com/bots/get-started/bot-fight-mode/)
- [Webmail oficial Hostinger](https://www.hostinger.com/support/1583218-how-to-access-webmail-of-hostinger-email/)
- [DMARC Hostinger](https://www.hostinger.com/support/8412851-how-to-add-a-dmarc-record-for-hostinger-email/)
- [DMARC e SES](https://docs.aws.amazon.com/ses/latest/dg/send-email-authentication-dmarc.html)
- [Etapas de DMARC no Resend](https://resend.com/docs/dashboard/domains/dmarc)
- [Política DMARC de subdomínios](https://resend.com/blog/how-dmarc-applies-to-subdomains)
- [Endereços GitHub Pages](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)
- [Verificação do domínio GitHub](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages)
