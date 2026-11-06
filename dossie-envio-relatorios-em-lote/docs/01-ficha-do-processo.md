# 01 · Ficha do processo

**Autor:** Vinícius Caetano de Assis · **Versão:** 1.0 · **Data:** 05/11/2026

## Identificação

| Campo | Descrição |
| --- | --- |
| Nome do processo | Envio de relatórios mensais aos clientes por e-mail |
| Tipo | Processo recorrente, operacional, executado por competência (mês de referência) |
| Área | Escritório de contabilidade (rotina fiscal e contábil) |
| Executor | Analista contábil |
| Dono do processo | Responsável pelo setor que emite os relatórios |
| Cliente do processo | Empresa cliente que recebe o relatório |
| Gatilho | Relatórios da competência gerados em PDF |
| Frequência | Mensal |
| Volume de referência | 13 relatórios por lote (cenário original e demonstração); 16 clientes cadastrados na demonstração |
| Fim do processo | Todas as mensagens enviadas e conferidas, ou lote interrompido e tratado manualmente |

## Objetivo

Entregar a cada cliente o relatório correto, no e-mail correto, com mensagem padronizada, reduzindo o trabalho repetitivo de localizar contatos, preparar mensagens e anexar arquivos, sem aumentar o risco de envio ao destinatário errado.

## Escopo

**Dentro do escopo**
- Identificar empresa e competência a partir do nome de cada PDF.
- Associar a empresa ao cadastro da planilha e obter até três e-mails.
- Validar o lote antes do envio (prévia) e bloquear em caso de pendência.
- Enviar uma mensagem por PDF, com assinatura e anexo, por uma única conexão SMTP.
- Copiar as mensagens para a pasta Enviados por IMAP (opcional).

**Fora do escopo**
- Geração dos relatórios.
- Leitura do conteúdo interno do PDF (a identificação usa só o nome do arquivo).
- Confirmação de entrega ou leitura pelo cliente.
- Histórico persistente de envios e retomada automática de lotes interrompidos (ver backlog em [05](05-riscos-e-controles.md)).

## Entradas, saídas e sistemas

| Entradas | Saídas | Sistemas |
| --- | --- | --- |
| PDFs no padrão de nome aceito (ver [04](04-regras-de-negocio-e-excecoes.md)) | E-mails com PDF anexo e assinatura | Python 3.10+ |
| Planilha `.xlsx` com `RAZÃO SOCIAL` e `E-MAIL - 1/2/3` | Cópias em Enviados (opcional) | Servidor SMTP e IMAP |
| Imagem de assinatura | Prévia, resumo e tempos no terminal | Excel (cadastro) |
| Configuração em `.env` (SMTP/IMAP) | Código de saída `0` (sucesso) ou `1` (erro) | Mailpit (somente na demonstração) |

## Papéis

| Papel | Responsabilidade |
| --- | --- |
| Analista contábil | Salvar os PDFs, rodar a prévia, corrigir pendências, conferir e autorizar o envio |
| Automação (script) | Identificar, associar, validar, montar e enviar as mensagens |
| Responsável pelo cadastro | Manter a planilha de clientes e e-mails atualizada |

## Premissas e restrições

- O nome do PDF segue um dos dois padrões aceitos; fora do padrão, o lote é bloqueado.
- A planilha de clientes é a fonte oficial de destinatários; erro no cadastro não é detectado pelo script.
- O envio real só ocorre com `--enviar`; sem ele, nenhuma conexão SMTP/IMAP é aberta.
- O servidor SMTP aceitar a mensagem não comprova entrega ou leitura.

## Glossário

| Termo | Significado |
| --- | --- |
| Competência | Mês e ano a que o relatório se refere |
| Lote | Conjunto de PDFs enviados em uma execução |
| Prévia | Execução sem `--enviar`, que mostra o plano de envio e as pendências |
| Pendência | Situação que impede o envio de um PDF (sem cadastro, sem e-mail, nome inválido, ambiguidade) |
