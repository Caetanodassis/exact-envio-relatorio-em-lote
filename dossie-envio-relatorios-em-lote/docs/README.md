# Dossiê do processo

Este diretório documenta o **processo** que a automação resolve, não apenas o código. A ordem de leitura abaixo vai do problema ao resultado.

| Documento | Pergunta que responde |
| --- | --- |
| [01 · Ficha do processo](01-ficha-do-processo.md) | O que é o processo, quando acontece, quem executa, o que entra e o que sai? |
| [02 · Levantamento e priorização](02-levantamento-e-priorizacao.md) | Qual era o problema e por que valeu automatizar este processo? |
| [03 · Baseline e KPIs](03-baseline-e-kpis.md) | Como o ganho é medido, o que foi medido e o que ainda é estimativa? |
| [04 · Regras de negócio e exceções](04-regras-de-negocio-e-excecoes.md) | Que regras o processo segue e o que acontece quando algo foge do padrão? |
| [05 · Riscos e controles](05-riscos-e-controles.md) | O que pode dar errado e como o processo se protege? |
| [06 · Critérios de aceite](06-criterios-de-aceite.md) | Como saber que a solução cumpre o combinado? |
| [07 · Runbook de operação](07-runbook.md) | Como o analista executa o processo no dia a dia e o que fazer em cada erro? |

## Diagramas BPMN

| Diagrama | Imagem | Arquivo editável |
| --- | --- | --- |
| Processo manual (AS-IS) | [AS-IS.png](bpmn/AS-IS.png) | [AS-IS.bpmn](bpmn/AS-IS.bpmn) |
| Processo automatizado (TO-BE) | [TO-BE.png](bpmn/TO-BE.png) | [TO-BE.bpmn](bpmn/TO-BE.bpmn) |

Os arquivos `.bpmn` abrem em [bpmn.io](https://demo.bpmn.io) ou no Camunda Modeler. O TO-BE descreve o comportamento real do código: prévia obrigatória, bloqueio do lote inteiro quando há pendência e falha de SMTP interrompendo o lote.

## Convenções

- Todos os dados são fictícios (domínios `.example`, CNPJs inválidos de propósito).
- Números do cenário original são tratados como **relatados** ou **estimados**, nunca como medições reproduzidas neste repositório.
- Itens marcados como **A preencher** dependem de uma medição que só pode ser feita por quem executa o processo (ver [03](03-baseline-e-kpis.md)).
