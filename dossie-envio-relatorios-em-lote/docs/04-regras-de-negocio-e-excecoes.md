# 04 · Regras de negócio e exceções

## Regras de negócio

| ID | Regra |
| --- | --- |
| RN01 | Somente arquivos `.pdf` da pasta de envio são considerados. |
| RN02 | O nome do arquivo segue um de dois padrões: `Relatório <TIPO> <MM> <AAAA> - <EMPRESA>.pdf` ou `Relatório <EMPRESA> - <Mês> <AAAA>.pdf`. No segundo, o tipo é `SIMPLES NACIONAL`. |
| RN03 | O mês pode ser número (1 a 12) ou nome por extenso; mês desconhecido gera erro. |
| RN04 | A empresa é associada ao cadastro por **razão social normalizada**: maiúsculas, sem acentos, pontuação convertida em espaço, `&` convertido em `E`, sufixo `ME`/`EPP` removido. |
| RN05 | Cadastro abreviado é aceito somente se for prefixo de **pelo menos três palavras completas** e houver **uma única** correspondência. |
| RN06 | Cadastros idênticos com os mesmos destinatários são consolidados; correspondências conflitantes bloqueiam o lote. |
| RN07 | Cada cliente tem até três colunas de e-mail; células vazias ou `-` são ignoradas; múltiplos endereços na célula (separados por `;`, `,` ou espaço) são lidos; repetidos são removidos; e-mail com formato inválido bloqueia, indicando linha e coluna. |
| RN08 | Cliente sem nenhum e-mail cadastrado, com PDF no lote, gera erro. |
| RN09 | Cliente cadastrado **sem** PDF no mês não recebe mensagem e não é pendência. |
| RN10 | **Qualquer pendência bloqueia o lote inteiro**: nenhum envio é iniciado. |
| RN11 | Sem `--enviar`, o programa só mostra a prévia e nunca abre conexão SMTP ou IMAP. |
| RN12 | O lote usa **uma** conexão SMTP autenticada; STARTTLS por padrão, exceto na porta 465, que usa SSL. |
| RN13 | Cada PDF gera uma mensagem com texto e HTML, assinatura incorporada e o PDF anexado; destinatário recusado pelo servidor gera erro. |
| RN14 | A cópia em Enviados por IMAP é opcional (`SAVE_TO_SENT`); falha na cópia gera aviso e **não** reenvia a mensagem. |
| RN15 | Falha de SMTP durante o lote interrompe a execução. |
| RN16 | Sem `SMTP_PASSWORD`, nenhum envio é feito. |
| RN17 | A planilha é a única `.xlsx` de `arquivos/`; se houver várias, é preciso escolher com `--planilha`; sem nenhuma, usa `dados/clientes.xlsx`. |

## Catálogo de exceções

| ID | Situação | Comportamento do sistema | Quem age | Evidência |
| --- | --- | --- | --- | --- |
| EX01 | Nome de arquivo fora dos padrões | Erro `Nome de relatório não reconhecido`; lote bloqueado | Analista renomeia o arquivo | `test_nome_invalido` |
| EX02 | Mês desconhecido no nome | Erro `Mês não reconhecido`; lote bloqueado | Analista corrige o nome | `test_mes_desconhecido` |
| EX03 | Empresa sem cadastro na planilha | Erro `encontrados 0 cadastros`; lote bloqueado | Analista inclui o cadastro ou corrige o nome | `test_empresa_sem_cadastro_gera_erro` |
| EX04 | Cliente cadastrado sem e-mail | Erro `nenhum e-mail cadastrado`; lote bloqueado | Analista completa o cadastro | `test_cliente_sem_email_gera_erro` |
| EX05 | Nome corresponde a mais de um cadastro | Erro `encontrados N cadastros`; lote bloqueado | Analista ajusta a razão social | `test_cadastro_ambiguo_bloqueia` |
| EX06 | Matriz e filial com nomes parecidos | Correspondência exata; cada uma recebe o seu | Nenhum (tratado) | `test_filial_nao_se_confunde_com_matriz` |
| EX07 | E-mail com formato inválido na planilha | Erro com linha e coluna; lote bloqueado | Analista corrige a célula | `test_email_invalido_na_planilha` |
| EX08 | Pendência em um PDF e os demais válidos | Nenhum envio é iniciado | Analista corrige e roda a prévia de novo | `test_pendencia_bloqueia_o_lote_inteiro` |
| EX09 | Planilha sem as colunas obrigatórias | Erro de estrutura; execução interrompida | Analista corrige a planilha | Sem teste automatizado |
| EX10 | Várias planilhas em `arquivos/` | Erro; exige `--planilha` | Analista escolhe a planilha | Sem teste automatizado |
| EX11 | Pasta sem PDFs | Erro `Nenhum PDF encontrado` | Analista confere a pasta | Sem teste automatizado |
| EX12 | Anexo ou assinatura ausente | Envio cancelado | Analista restaura o arquivo | Sem teste automatizado |
| EX13 | `SMTP_PASSWORD` ausente | Erro antes de qualquer envio | Analista configura o `.env` | Sem teste automatizado |
| EX14 | Destinatário recusado pelo servidor | Erro; outros destinatários da mensagem podem ter recebido | Analista confere em Enviados | Sem teste automatizado |
| EX15 | Falha de SMTP no meio do lote | Execução interrompida; mensagens anteriores podem ter sido aceitas | Analista confere Enviados e envia o restante | Sem teste automatizado |
| EX16 | Falha ao copiar para Enviados (IMAP) | Aviso; mensagem **não** é reenviada | Analista não repete o envio | Sem teste automatizado |
| EX17 | Reexecução de `--enviar` | Reenvia tudo (sem histórico contra duplicidade) | Analista evita repetir | Limitação conhecida (backlog) |
