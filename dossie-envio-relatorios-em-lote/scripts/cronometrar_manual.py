"""Cronometra a simulação do processo MANUAL para gerar o baseline (ver docs/03).

Uso:
    python dossie-envio-relatorios-em-lote/scripts/cronometrar_manual.py
    python dossie-envio-relatorios-em-lote/scripts/cronometrar_manual.py --limite 5

Para cada relatório, execute a etapa de verdade (abrir pasta, localizar o PDF,
buscar o e-mail na planilha, redigir/anexar, enviar) e pressione Enter ao
terminar cada etapa. Ao final, os tempos são gravados em CSV e resumidos.
Faça 3 repetições e use a mediana. Declare no README que é uma SIMULAÇÃO.
"""
import argparse
import csv
import statistics
import time
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DOSSIE = RAIZ / 'dossie-envio-relatorios-em-lote'
ETAPAS = (
    'Localizar o PDF da empresa',
    'Buscar o e-mail na planilha',
    'Redigir a mensagem e anexar o PDF',
    'Enviar o e-mail',
)


def resumir(medicoes):
    """medicoes: lista de (relatorio, etapa, segundos). Devolve total e média por etapa."""
    total = sum(s for _, _, s in medicoes)
    por_etapa = {e: [s for _, et, s in medicoes if et == e] for e in ETAPAS}
    medias = {e: statistics.mean(v) for e, v in por_etapa.items() if v}
    return total, medias


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--pasta', type=Path, default=RAIZ / 'arquivos')
    parser.add_argument('--limite', type=int, help='Quantidade de relatórios a simular.')
    args = parser.parse_args()

    pdfs = sorted(args.pasta.glob('*.pdf'))[: args.limite]
    if not pdfs:
        raise SystemExit('Nenhum PDF encontrado para simular.')

    medicoes = []
    print(f'Simulação manual de {len(pdfs)} relatório(s). Enter conclui cada etapa.\n')
    for pdf in pdfs:
        print(f'--- {pdf.name}')
        for etapa in ETAPAS:
            input(f'  [Enter para INICIAR] {etapa}')
            inicio = time.perf_counter()
            input('  [Enter ao CONCLUIR]')
            medicoes.append((pdf.name, etapa, time.perf_counter() - inicio))

    total, medias = resumir(medicoes)
    destino = DOSSIE / 'docs' / 'medicoes'
    destino.mkdir(parents=True, exist_ok=True)
    arquivo = destino / f'manual_{datetime.now():%Y%m%d_%H%M%S}.csv'
    with arquivo.open('w', newline='', encoding='utf-8') as saida:
        escritor = csv.writer(saida)
        escritor.writerow(['relatorio', 'etapa', 'segundos'])
        escritor.writerows((r, e, f'{s:.1f}') for r, e, s in medicoes)

    print(f'\nTotal: {total / 60:.1f} min para {len(pdfs)} relatório(s) '
          f'({total / len(pdfs):.1f} s por relatório).')
    for etapa, media in medias.items():
        print(f'  {etapa}: média de {media:.1f} s')
    print(f'Medições gravadas em {arquivo}')


if __name__ == '__main__':
    main()
