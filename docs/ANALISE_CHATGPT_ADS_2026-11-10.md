# ChatGPT Ads: análise do teste de novembro em andamento

## Ajuste aplicado em 10/11/2026

O proprietário autorizou a recomendação A. Pela interface do Ads Manager,
na sessão dele, foram gravados apenas estes campos:

| Nível e horário | Antes | Depois |
| --- | --- | --- |
| Grupo, 15h44 | Lance máximo de R$3,50 | R$5,00 |
| Grupo, 15h44 | Três contextos | Os cinco de outubro, com os mesmos fatos |
| Campanha, 15h49 | Sem metas de conversão | Reserva confirmada e Visita realizada |
| Campanha, 15h49 | Término em 16/11 às 00h | 18/11 às 00h |

Os contextos de outubro foram reescritos sem vírgulas internas, porque a
interface junta e separa as dicas por vírgula. Os fatos foram conferidos
antes: executivo de segunda a sexta, das 10h às 14h, exceto feriados, a
partir de R$31, e reservas online para até 10 pessoas. O histórico mostra
o texto corrido; não dá para ver se ficou em cinco itens ou em um.

O histórico de alterações registrou só essas duas entradas. Continuam iguais:
R$300 totais, os 14 setores, início em 09/11, todas as plataformas,
aprimoramento criativo desativado, texto, imagem e destino do anúncio, além
das outras campanhas. Depois de salvar, campanha, grupo e anúncio aparecem
"Em operação"; o aviso de lance baixo e a ação "Aumentar lance" sumiram. A
interface estima cerca de R$33,33 por dia. Isso não comprova entrega.

**Pendente:** conferir a entrega em 11/11, a partir das 15h45. Se ainda não
houver impressões, pausar e encerrar, sem subir mais o lance. Não foi criada
automação. O recibo privado está em `tmp/chatgpt-ads/ajuste-2026-11-10.json`.

## Leitura de 11/11/2026, 10h40

Cerca de 19 horas depois do ajuste e 59 horas depois do início: zero
impressões, cliques e gasto na campanha, no grupo e no anúncio. O aviso de
lance baixo não voltou; a Visão geral não tem tarefas nem dados. A única
ação exibida é o aviso geral de que lance máximo e CPC máximo saem em
01/01/2027, com migração para CPC desejado a partir de 09/11.

Como o lance deixou de ser apontado e conta, faturamento e aprovação estão
em ordem, a causa restante mais provável é o público elegível quase nulo
dos 14 setores postais. Em outubro, mesmo com Ceará, o GA4 registrou
sessões pagas de São Paulo, Curitiba e outras capitais, sinal de que a
localização da plataforma é aproximada; a precisão de CEP pode não existir
para a maioria dos usuários no Brasil. O suporte não respondeu sobre a cidade.

O GA4 tem duas sessões com a UTM da campanha (09/11 às 20h no portal e
10/11 às 9h em `/conheca/`), ambas em computador, Chrome e Fortaleza, sem
clique registrado pela plataforma: acessos diretos ao link, não entrega.

ChatGPT orgânico (`chatgpt.com`) trouxe 74 sessões de 01/11 a 11/11, só 18
do Ceará; 36 entraram em `/reveillon`. Quem chega pelo ChatGPT é, em grande
parte, quem planeja a viagem de fora, o público que o recorte por CEP exclui.

Acesso: a API pública (`api.ads.openai.com/v1`) exige chave de anunciante
criada em Configurações do Ads Manager; a sessão do navegador recebe 401 e
o token interno da interface não foi extraído. Não há MCP público de Ads;
o do Codex é conector exclusivo do ChatGPT. Nenhuma alteração foi feita.

## Análise que motivou o ajuste

Leitura em 10/11/2026 às 14h, America/Fortaleza, cerca de 38 horas após o
início programado (09/11 às 00h). Fontes: Ads Manager no navegador, GA4 pela
conta de serviço, portal pela rota de leitura da Management API e recibos
privados em `tmp/chatgpt-ads/`. Nada foi alterado na campanha, no site ou no
banco. Configuração analisada: [plano e ativação](PLANO_CHATGPT_ADS_2026-11-07.md)
e [geografia](GEOGRAFIA_CHATGPT_ADS_2026-11-08.md).

## Resumo

O teste não está veiculando. Campanha, grupo e anúncio estão ativos e o
anúncio está aprovado, mas os três níveis mostram zero gasto, zero impressões
e zero cliques desde o início. O status é "Em operação, Lance baixo". O aviso
da plataforma diz que os lances são superados com frequência, o que limita a
veiculação, e recomenda aumentar o lance do grupo. Os dados de 10/11 são
preliminares; 09/11 completo também ficou sem entrega. Sem mudança, o teste
termina em 16/11 sem gasto e sem dado para decidir.

O GA4 confirma: nenhuma sessão começou em `/conheca/` em 09/11, por nenhuma
origem. Houve uma sessão `chatgpt / paid` com a UTM da campanha, iniciada
direto no portal de reservas, em computador, com três segundos. Isso não é
compatível com zero cliques e não deve ser contado como resultado. O portal
não tem reserva com origem ChatGPT desde 09/11.

## O que mudou em relação a outubro

| Item | Outubro, 06 a 19/10 | Novembro, desde 09/11 |
| --- | --- | --- |
| Localização | Ceará | 14 setores postais de Fortaleza |
| Lance | Máximo manual de R$3,50 | Máximo manual de R$3,50 |
| Contextos do grupo | Cinco, com endereço, pratos, executivo, fim de tarde e reservas | Três, mais genéricos |
| Metas de conversão | Reserva confirmada e Visita realizada associadas | Nenhuma; a coluna mostra "Configurar" |
| Pixel no site | Carregava para todos os visitantes | Só com aceite de publicidade, desde 03/11 |
| Entrega | 20.634 impressões e 210 cliques, já com aviso de lance baixo | Zero |

O mesmo lance que entregava no Ceará não entrega nos 14 setores. A causa
mais provável é o conjunto menor de pessoas e conversas elegíveis na área,
somado a um lance que já perdia leilões em outubro. A plataforma não mostra
tamanho de público por setor; não é possível separar o peso de cada fator.
Não há indício de bloqueio de conta, faturamento ou reprovação.

## Problemas

1. **Entrega zero, crítico.** Cerca de 23% do período já passou sem dados.
   O ponto de revisão de 12/11 do plano perde o sentido sem entrega.
2. **Campanha sem metas de conversão, importante.** O recibo da criação tem
   `conversion_event_setting_ids` vazio e a ativação só gravou status. Em
   outubro essa associação foi uma das correções feitas antes do teste. Sem
   ela, o Ads Manager não relata reserva confirmada nem visita da campanha.
3. **Pixel condicionado ao aceite, atenção na leitura.** Desde o site
   `5eeb6f2`, sem aceite de publicidade o Pixel da OpenAI não carrega e o
   `oppref` é descartado no site e no portal. A reserva guarda só as UTMs e
   não gera conversão para a OpenAI. Entre as reservas públicas de 03 a
   10/11, 9 de 11 tinham aceite; entre visitantes em geral, a taxa é
   desconhecida. Os sinais de cardápio e rota no Ads Manager não serão
   comparáveis aos de outubro. Usar como fonte comparável o GA4 por
   `chatgpt / paid` e as UTMs das reservas.
4. **Peça, secundário.** Título e descrição cumprem os limites, mas são
   genéricos. A imagem é do almoço executivo, com pessoa, prato e
   refrigerante, sem o mar. O mar é o diferencial principal e a abertura da
   própria `/conheca/`. Trocar a peça agora reinicia a análise da OpenAI;
   fica para o próximo ciclo.

## Referência econômica

Em outubro, cerca de 210 cliques no teto acumulado de R$577,05 geraram seis
pedidos de rota e quatro inícios de reserva atribuídos, com janela de 30
dias pelo clique, e nenhuma reserva confirmada ou visita. Se o teto foi
consumido, isso dá cerca de R$58 por ação de alta intenção. O handoff
calculou R$2,50 a R$7,50 como limite sustentável, conforme o comparecimento.
Clientes sem reserva continuam sem medição, por decisão de 25/10. O número
não prova ausência de retorno, mas mostra que o público local precisa
converter muito melhor que o de outubro para o canal se pagar.

## Recomendação

Cada item é alteração na campanha e depende de autorização do proprietário.

**A, recomendada: tornar o teste veiculável sem mudar a área.**

- Lance máximo do grupo de R$3,50 para R$5,00.
- Restaurar os cinco contextos do grupo de outubro, já aprovados.
- Associar Reserva confirmada e Visita realizada à campanha.
- Mover o término para 18/11 às 00h, mantendo R$300 totais.
- Conferir 24 horas depois. Se continuar sem impressões, a área é pequena
  demais para o canal: pausar e encerrar, sem subir mais o lance.

A exposição continua limitada a R$300 pelo orçamento total. Com máximo de
R$5,00, o pior caso é de cerca de 60 cliques. O orçamento total não distribui
o gasto pelos dias; em outubro o teto acabou em três dias.

**B: encerrar agora.** Pausar e registrar que os 14 setores com R$3,50 não
entregam. Preserva os R$300, sem aprendizado sobre clientes.

Fora desta rodada: Ceará, recusado em 08/11; Target CPC, que muda o tipo de
controle, enquanto o máximo manual continua válido até 01/01/2027; troca de
peça, que reinicia a análise.
