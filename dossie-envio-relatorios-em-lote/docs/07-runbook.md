# 07 · Runbook de operação

Guia para quem executa o envio mensal. Linux e macOS usam `python3`; no Windows, use `python`.

## Pré-requisitos

- Ambiente preparado conforme o README (dependências instaladas e `.env` configurado).
- PDFs da competência salvos em `arquivos/`, no padrão de nome aceito.
- Planilha de clientes atualizada.

## Passo a passo mensal

1. **Salvar os PDFs** da competência na pasta de envio (`arquivos/`).
2. **Rodar a prévia** (não envia nada): `python src/enviar_relatorios.py`
3. **Ler a saída.**
   - Se aparecer `Prévia com pendências. Nenhum envio iniciado`, vá para a tabela de erros abaixo, corrija e **volte ao passo 2**.
   - Se terminar com `Prévia concluída: N mensagem(ns)`, siga.
4. **Conferir a prévia:** para cada arquivo, confira empresa, cadastro e e-mails de destino. Atenção a empresas com filial ou nomes parecidos.
5. **Enviar:** `python src/enviar_relatorios.py --enviar`
6. **Verificar o resultado:** cada envio mostra `Enviado: <arquivo> → <e-mails>`. Ao final, anote o `Tempo total da execução`.
7. **Conferir em Enviados** (webmail) se a cópia foi salva; se houve `AVISO` de cópia, confira manualmente.

**Regra de ouro:** nunca repita `--enviar` só porque a cópia em Enviados falhou. O e-mail já foi aceito pelo servidor.

## Erros mais comuns

| Mensagem | Causa provável | O que fazer |
| --- | --- | --- |
| `Nome de relatório não reconhecido: ...` | Nome do PDF fora dos padrões | Renomear o arquivo conforme o README |
| `Mês não reconhecido: ...` | Nome do mês escrito errado | Corrigir o mês no nome do arquivo |
| `... encontrados 0 cadastros; revise a razão social na tabela.` | Empresa não cadastrada ou escrita diferente | Corrigir o nome do arquivo ou incluir o cadastro |
| `... encontrados N cadastros; revise a razão social na tabela.` | Mais de um cadastro compatível (filiais, nomes parecidos) | Ajustar a razão social para ficar única |
| `... nenhum e-mail cadastrado.` | Cliente sem e-mail na planilha | Completar o cadastro |
| `E-mail inválido na linha N, coluna ...` | Endereço malformado na planilha | Corrigir a célula indicada |
| `A planilha deve ter RAZÃO SOCIAL e E-MAIL - 1, 2 e 3.` | Cabeçalho da planilha alterado | Restaurar os cabeçalhos |
| `Há várias planilhas em arquivos/. Escolha uma usando --planilha.` | Mais de um `.xlsx` na pasta | Deixar uma só ou usar `--planilha` |
| `Nenhum PDF encontrado.` / `Pasta não encontrada` | Pasta vazia ou caminho errado | Conferir a pasta ou usar `--pasta` |
| `Defina SMTP_PASSWORD antes do envio.` | Senha não configurada | Preencher o `.env` |
| `Destinatários recusados: ...` | Servidor recusou algum endereço | Conferir o e-mail; verificar em Enviados quem recebeu |
| `Pasta Enviados não identificada de forma única...` | IMAP sem pasta Enviados reconhecida | Definir `IMAP_SENT_FOLDER` no `.env` |

## Se o envio parar no meio do lote (falha de SMTP)

1. **Não rode `--enviar` de novo** com a pasta completa: isso duplicaria as mensagens já aceitas.
2. Abra **Enviados** e liste quais empresas já receberam.
3. Mova para outra pasta os PDFs já enviados (ou use `--pasta` com uma pasta só com os restantes) e rode a prévia e o envio apenas para eles.
4. Anote o ocorrido para melhorar o controle (ver backlog em [05](05-riscos-e-controles.md)).

## Boas práticas

- Rode sempre a prévia antes do envio real.
- Não envie com dados reais para o Mailpit nem com dados fictícios para clientes reais.
- Nunca versione o `.env`, a planilha real ou PDFs de clientes.
- Registre o tempo total de cada lote para acompanhar os KPIs de [03](03-baseline-e-kpis.md).

## Escalonamento

| Situação | Contato |
| --- | --- |
| Dúvida sobre cadastro de cliente | Responsável pela planilha (definir no escritório) |
| Erro técnico ou de configuração | Mantenedor da automação (definir no escritório) |
