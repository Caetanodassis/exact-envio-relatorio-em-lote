# 06 · Critérios de aceite

Cada critério tem evidência rastreável: um teste automatizado ou uma verificação manual (UAT). Execute os testes com `python -m pytest -q`.

## Critérios verificados por testes automatizados

| ID | Dado / Quando / Então | Evidência |
| --- | --- | --- |
| CA01 | **Dado** nomes nos dois padrões aceitos, **quando** o arquivo é lido, **então** empresa, mês e ano são extraídos corretamente | `test_identificar` |
| CA02 | **Dado** nome fora do padrão ou mês inexistente, **quando** lido, **então** gera erro explícito | `test_nome_invalido`, `test_mes_desconhecido` |
| CA03 | **Dado** razão social com acentos, `&` e sufixo `ME/EPP`, **quando** normalizada, **então** compara de forma consistente | `test_normalizar_remove_acentos_e_sufixos` |
| CA04 | **Dado** a planilha fictícia, **quando** associada a uma empresa, **então** devolve o cadastro e os e-mails corretos | `test_planilha_fictícia_carrega_e_relaciona` |
| CA05 | **Dado** matriz e filial, **quando** associadas, **então** cada uma recebe o seu cadastro | `test_filial_nao_se_confunde_com_matriz` |
| CA06 | **Dado** cliente sem e-mail, empresa sem cadastro, cadastro ambíguo ou e-mail inválido, **quando** associado, **então** gera erro | `test_cliente_sem_email_gera_erro`, `test_empresa_sem_cadastro_gera_erro`, `test_cadastro_ambiguo_bloqueia`, `test_email_invalido_na_planilha` |
| CA07 | **Dado** um lote com um PDF válido e outro com pendência, **quando** executado com `--enviar`, **então** retorna erro e **nenhuma** conexão SMTP é aberta | `test_pendencia_bloqueia_o_lote_inteiro` |
| CA08 | **Dado** a execução sem `--enviar`, **quando** concluída, **então** nenhuma conexão SMTP ou IMAP foi aberta | `test_previa_nao_abre_conexoes` |
| CA09 | **Dado** o lote completo, **quando** enviado, **então** usa uma única conexão e autenticação SMTP e faz 13 envios | `test_lote_reutiliza_smtp_e_preserva_assinatura` |
| CA10 | **Dado** cada mensagem do lote, **quando** montada, **então** tem texto e HTML, assinatura incorporada por CID e exatamente um anexo PDF | `test_lote_reutiliza_smtp_e_preserva_assinatura` |
| CA11 | **Dado** um servidor SMTP local, **quando** o lote é enviado, **então** os 13 relatórios chegam aos destinatários corretos com anexo | `test_envio_de_ponta_a_ponta` |

## Verificação manual (UAT) com o Mailpit

Marque cada item ao executar o roteiro da demonstração.

| Item | Resultado |
| --- | --- |
| Prévia lista 13 mensagens com empresa, competência, cadastro e destinatários | A preencher |
| Copiar um PDF renomeado para `Relatório BARBEARIA NAVALHA DE OURO LTDA - Setembro 2026.pdf` (cliente sem e-mail) bloqueia o lote inteiro na prévia | A preencher |
| Após `--enviar`, o Mailpit (`http://localhost:8025`) mostra 13 mensagens | A preencher |
| Cada mensagem tem o PDF correto da empresa e a assinatura visível | A preencher |
| Mensagens para clientes com dois e-mails chegam aos dois endereços | A preencher |
| Cliente cadastrado sem relatório (Lanchonete, Studio Luz) não recebe mensagem | A preencher |
