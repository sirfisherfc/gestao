# Correções dos alertas do Cloudflare

Estado conferido em 02/11/2026, no horário de Fortaleza, após autorização
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
| DMARC | Adicionado pedido de relatórios para o contato público. API e DNS público confirmaram `v=DMARC1; p=none; rua=mailto:contato@sirfisher.com.br`. Quarentena/rejeição continuam pendentes da conferência de remetentes. |

Na primeira rodada, dos 27 registros DNS, mudaram somente `proxied` em
admin/reservas/webmail e o TXT DMARC. Depois foi acrescentado o desafio TXT
do GitHub Pages, totalizando 28 registros. MX, SPF, DKIM e descoberta de
e-mail permaneceram iguais.
As duas regras WAF e o objeto Bot Management foram comparados antes/depois
e permaneceram iguais. A regra apex para www foi preservada junto do novo
atalho do webmail.

## Alertas que ainda podem aparecer

A releitura retornou **13 ocorrências não classificadas**. Os oito falsos
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

## Pendência: autenticação dos envios da Hostinger

O proprietário acredita que os envios saem pela Hostinger, sem confirmação
dos serviços usados. O código dos sistemas usa Resend. Oito mensagens
automáticas recebidas no Gmail, de 06/09 a 30/09/2026, passaram SPF, DKIM
e DMARC via Resend/Amazon SES, com alinhamento do domínio. Essa amostra
comprova os envios examinados. A busca não encontrou mensagem de contato
nem outro remetente do domínio fora de reservas para conferir a Hostinger.

Conferir um envio legítimo da Hostinger ou relatórios DMARC antes de trocar
`p=none` por `quarantine` e depois `reject`. Hostinger Mail foi oferecido;
a conexão ainda não foi confirmada. Nenhum e-mail ou chamado foi enviado,
e nenhuma outra rotina agendada foi criada nesta tarefa.

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
não contém credencial ou conteúdo de e-mail.

## Fontes oficiais

- [TLS mínimo](https://developers.cloudflare.com/ssl/edge-certificates/additional-options/minimum-tls/)
- [Revisão dos insights](https://developers.cloudflare.com/security/security-insights/review-insights/)
- [Classificação de insight](https://developers.cloudflare.com/api/resources/security_center/subresources/insights/subresources/classification/methods/update/)
- [Limites do Bot Fight Mode](https://developers.cloudflare.com/bots/get-started/bot-fight-mode/)
- [Webmail oficial Hostinger](https://www.hostinger.com/support/1583218-how-to-access-webmail-of-hostinger-email/)
- [DMARC Hostinger](https://www.hostinger.com/support/8412851-how-to-add-a-dmarc-record-for-hostinger-email/)
- [DMARC e SES](https://docs.aws.amazon.com/ses/latest/dg/send-email-authentication-dmarc.html)
- [Endereços GitHub Pages](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)
- [Verificação do domínio GitHub](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages)
