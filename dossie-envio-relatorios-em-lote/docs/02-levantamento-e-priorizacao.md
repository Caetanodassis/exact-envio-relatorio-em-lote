# 02 · Levantamento e priorização

## Contexto

O escritório de contabilidade precisava entregar mensalmente um relatório a cada cliente. O trabalho consistia em localizar o PDF da empresa, descobrir o e-mail na planilha, redigir a mensagem padrão, anexar o arquivo e enviar, repetidamente, para cada cliente. O diagrama [AS-IS](bpmn/AS-IS.png) mostra esse fluxo.

## Como o processo manual funcionava

1. Abrir a pasta de documentos do período.
2. Localizar o documento da empresa.
3. Buscar o e-mail da empresa na planilha.
4. Se o e-mail não for encontrado, registrar a pendência em uma lista e seguir.
5. Redigir o e-mail com a mensagem padrão e anexar o documento.
6. Enviar o e-mail.
7. Repetir para a próxima empresa até acabar.

## Dores identificadas

| Dor | Consequência |
| --- | --- |
| Um e-mail manual por empresa | Tempo alto e repetitivo |
| Localização manual de documento e destinatário | Risco de anexo ou destinatário errado |
| Pendências em lista informal | Falhas descobertas tarde, sem padrão de tratamento |
| Nenhum registro automático dos envios | Difícil comprovar o que foi enviado e quando |

## Fontes do levantamento

- Relato de um colaborador sobre o tempo do processo manual (aproximadamente 15 minutos para 13 relatórios, valor relatado, não cronometrado).
- Conhecimento direto do fluxo pelo autor da automação.

**A preencher (para fortalecer o dossiê):** quem mais executa ou depende do processo, quantos envios errados ou atrasados já ocorreram e com que frequência as pendências aparecem. Roteiro de perguntas sugerido para a conversa com quem executa:

1. Mostre, na tela, como você faz isso do início ao fim.
2. Quanto tempo leva um lote completo? E em um mês corrido?
3. Que erros já aconteceram (anexo trocado, e-mail antigo, cliente esquecido)?
4. O que acontece quando o cliente não tem e-mail cadastrado ou o nome do arquivo está diferente da planilha?
5. Quem confere o resultado e como?

## Priorização

Avaliação retrospectiva do autor, de 1 (desfavorável) a 5 (favorável à automação):

| Critério | Evidência | Nota |
| --- | --- | :---: |
| Volume | 13 relatórios por lote, todo mês | 3 |
| Regra clara | Padrão de nome do arquivo, cadastro em planilha e mensagem única | 5 |
| Estabilidade | Dois padrões de nome aceitos e estrutura fixa da planilha | 4 |
| Dor | Tempo repetitivo e risco de envio ao destinatário errado | 4 |
| Esforço de automação | Biblioteca padrão do Python mais `openpyxl` | 4 |
| **Total** | | **20 de 25** |

**Decisão:** automatizar, mantendo uma etapa de conferência humana (prévia) antes do envio, porque o principal risco do processo é o envio ao destinatário errado, e esse risco não deve ser transferido para a máquina sem controle.

## Por que um script Python

- A normalização de nomes (acentos, pontuação, sufixos `ME/EPP`) e as validações são lógica própria, mais simples de escrever e testar em código.
- O resultado é testável (suíte `pytest`) e auditável (histórico no Git).
- Ferramentas low-code ou RPA seriam alternativas possíveis; a escolha por Python priorizou o controle sobre as regras e a capacidade de testar.
