# 05 · Riscos e controles

Princípios do desenho: **falhar de forma segura** (na dúvida, bloquear em vez de enviar) e **manter uma pessoa no circuito** antes do envio real (prévia obrigatória, `--enviar` explícito).

Classificação de probabilidade e impacto: avaliação qualitativa do autor (Baixa, Média, Alta).

| ID | Risco | Prob. | Impacto | Controle existente | Risco residual / ação |
| --- | --- | :---: | :---: | --- | --- |
| R01 | Envio ao destinatário errado | Média | Alta | Prévia mostra empresa, cadastro e e-mails; associação exata; ambiguidade bloqueia; conferência humana antes de `--enviar` | Erro no cadastro da planilha não é detectado; manter a planilha sob responsável definido |
| R02 | Anexo errado (PDF trocado) | Baixa | Alta | Associação pelo nome do arquivo; prévia lista arquivo e empresa | O conteúdo do PDF não é lido; backlog: validar razão social ou CNPJ dentro do PDF |
| R03 | Envio duplicado | Média | Média | Nenhum (limitação documentada) | Backlog: histórico persistente de envios |
| R04 | Falha no meio do lote | Média | Média | A execução para e informa o erro; cópia em Enviados ajuda a conferir | Retomada é manual; backlog: retomar só as mensagens que falharam |
| R05 | Vazamento de credenciais | Baixa | Alta | `.env` ignorado pelo Git; `.env.example` sem segredos; senha só por variável de ambiente | Usar conta de serviço ou senha de aplicativo; ativar varredura de segredos no repositório |
| R06 | Exposição de dados de clientes (LGPD) | Baixa | Alta | Versão pública usa só dados fictícios (domínios `.example`, CNPJs inválidos); TLS (STARTTLS ou SSL) no SMTP e IMAP | Em produção: restringir acesso à pasta e à planilha, não publicar dados reais |
| R07 | Mudança no padrão de nome dos arquivos | Média | Baixa | Nome fora do padrão bloqueia o lote com erro claro, em vez de enviar errado | Comunicar o padrão aos geradores dos relatórios |
| R08 | Falha ao copiar para Enviados | Média | Baixa | Aviso separado; a mensagem não é reenviada | Conferir Enviados manualmente quando houver aviso |
| R09 | Dependência de uma só pessoa | Média | Média | README, dossiê, runbook e testes automatizados | Treinar um segundo executor com o runbook |
| R10 | Confundir "enviado" com "entregue ou lido" | Média | Baixa | Limitação declarada no README | Se necessário, adotar confirmação de leitura ou canal de resposta |

## Controles preventivos, detectivos e corretivos

| Tipo | Controle |
| --- | --- |
| Preventivo | Prévia obrigatória; bloqueio do lote por pendência; validação de formato de e-mail; associação exata |
| Detectivo | Cópia em Enviados; tempos e mensagem por envio no terminal; avisos de falha de IMAP |
| Corretivo | Runbook com ação para cada erro; reenvio manual do restante após falha de SMTP |

## Backlog priorizado

1. Histórico persistente de envios com prevenção de duplicidade (R03).
2. Retomada de lotes interrompidos (R04).
3. Validação cruzada com o conteúdo do PDF (R02).
4. Exportação dos resultados e tempos para CSV (apoia os KPIs de [03](03-baseline-e-kpis.md)).
