# 03 · Baseline e KPIs

## Indicadores

| KPI | Definição | Como medir | Meta |
| --- | --- | --- | --- |
| Tempo por lote | Minutos do início ao fim da execução | `Tempo total da execução` impresso pelo script | Menor que o manual |
| Tempo por relatório | Tempo do lote ÷ número de relatórios | Cálculo | Acompanhar tendência |
| Redução de tempo | `(manual − automático) ÷ manual × 100` | Cálculo | Maior que 50% |
| Pendências na prévia | Pendências ÷ PDFs do lote | Saída da prévia | Tende a zero ao longo do tempo |
| Envios incorretos | Mensagens com destinatário ou anexo errado por lote | Conferência em Enviados | 0 |
| Cobertura de registro | Mensagens com cópia em Enviados ÷ enviadas | Contagem em Enviados | 100% |
| Horas economizadas por mês | `(manual − automático) × lotes por mês` | Cálculo | Acompanhar |

## Dados disponíveis (cenário original)

| Indicador | Valor | Natureza |
| --- | ---: | --- |
| Envio automático de 13 relatórios | 4 min 16 s (256 s) | Medição informada pelo autor da versão original |
| Envio manual de 13 relatórios | ~15 min (900 s) | **Relatado** por um colaborador, não cronometrado |
| Economia por lote | 10 min 44 s | Cálculo |
| Redução do tempo | 71,6% (~72%) | Estimativa |
| Fator de velocidade | 3,5x | Estimativa |
| Teste real com 2 relatórios | 53,3 s | Medição, inclui processamento, SMTP e IMAP |

Por relatório: manual ≈ 69,2 s; automático ≈ 19,7 s.

## Leitura honesta do ganho

- Em **um** lote de 13 relatórios por mês, o ganho bruto de tempo é de cerca de **11 minutos por mês**. Isso é pouco, se olhado isoladamente.
- O valor da automação está em três frentes: **escala** (o ganho cresce com o número de clientes), **redução de risco** (a prévia e as validações previnem envio ao destinatário errado) e **padronização e rastreabilidade** (mensagem única e cópia em Enviados).
- Qualquer apresentação do resultado deve citar o tempo **e** o controle de erros, nunca só a porcentagem.

## Projeção por volume (extrapolação, não medição)

Premissas: o tempo manual é proporcional ao volume (69,2 s por relatório); o tempo automático segue um modelo linear ajustado às duas medições disponíveis (2 relatórios em 53,3 s e 13 em 256 s), com custo fixo de cerca de 16,4 s e cerca de 18,4 s por relatório.

| Relatórios por lote | Manual (min) | Automático (min) | Economia (min) | Redução |
| ---: | ---: | ---: | ---: | ---: |
| 13 | 15,0 | 4,3 | 10,7 | 71,6% |
| 30 | 34,6 | 9,5 | 25,1 | 72,6% |
| 60 | 69,2 | 18,7 | 50,5 | 73,0% |
| 100 | 115,4 | 31,0 | 84,4 | 73,1% |

Limites: as duas medições automáticas podem ter sido feitas em condições diferentes (rede, tamanho dos anexos, servidor), e o tempo manual de um volume maior pode crescer por cansaço e interrupções. Use a tabela para ordem de grandeza, não como promessa.

## Protocolo para medir o baseline manual (simulação)

Como o cenário original talvez não possa mais ser medido, o baseline deve ser **simulado** com os dados fictícios e declarado como tal.

1. Gere os dados: `python scripts/gerar_dados_ficticios.py`.
2. Na raiz do repositório, rode `python dossie-envio-relatorios-em-lote/scripts/cronometrar_manual.py` e execute de verdade cada etapa (localizar o PDF, buscar o e-mail na planilha, redigir e anexar, enviar), pressionando Enter ao iniciar e ao concluir cada uma.
3. Repita **3 vezes** (o script grava um CSV por execução em `dossie-envio-relatorios-em-lote/docs/medicoes/`).
4. Use a **mediana** das repetições e preencha a tabela abaixo.
5. Registre no README que a medição é uma simulação com dados fictícios.

| Etapa | Repetição 1 | Repetição 2 | Repetição 3 | Mediana |
| --- | --- | --- | --- | --- |
| Localizar o PDF da empresa | A preencher | A preencher | A preencher | A preencher |
| Buscar o e-mail na planilha | A preencher | A preencher | A preencher | A preencher |
| Redigir a mensagem e anexar o PDF | A preencher | A preencher | A preencher | A preencher |
| Enviar o e-mail | A preencher | A preencher | A preencher | A preencher |
| **Total do lote** | A preencher | A preencher | A preencher | A preencher |

## Protocolo para medir o automático

1. Suba o Mailpit: `docker compose up -d`.
2. Execute `python src/enviar_relatorios.py --enviar` 3 vezes e anote o `Tempo total da execução` de cada uma.
3. Use a mediana. Declare que o Mailpit local **não tem latência de rede**, então o tempo não é comparável ao de um servidor real.

| Execução | Tempo total (s) |
| --- | --- |
| 1 | A preencher |
| 2 | A preencher |
| 3 | A preencher |
| **Mediana** | A preencher |

## Como relatar o resultado

Modelo de frase: *"Na simulação com 13 relatórios fictícios, o envio manual levou X min (mediana de 3 execuções) e o automático Y min; a prévia obrigatória bloqueou 100% dos casos de PDF sem e-mail ou sem cadastro nos testes."*
