"""Gera dados 100% fictícios para demonstrar o projeto.

Cria:
  - dados/clientes.xlsx   (planilha de clientes com e-mails @example.com)
  - arquivos/*.pdf        (relatórios de exemplo, um por cliente)
  - assets/assinatura_demo.png

Nenhuma empresa, CNPJ ou e-mail aqui é real. Os domínios .example/.example.com
são reservados (RFC 2606) e nunca recebem e-mail de verdade.
"""
import random
from pathlib import Path

from openpyxl import Workbook
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

RAIZ = Path(__file__).resolve().parent.parent
COMPETENCIA = ('Setembro', 9, 2026)
APURACAO = ('Outubro', 10, 2026)

# (razão social, e-mails). '-' = coluna vazia na planilha.
CLIENTES = [
    ('PADARIA PAO DOURADO LTDA', ['contato@paodourado.example.com', '-', '-']),
    ('MERCEARIA BOA VISTA LTDA', ['financeiro@boavista.example.com', 'dono@boavista.example.com', '-']),
    ('OFICINA VELOZ AUTOMOTIVA LTDA', ['oficina@veloz.example.com', '-', '-']),
    ('CLINICA SORRISO FELIZ LTDA', ['recepcao@sorrisofeliz.example.com', '-', '-']),
    ('CONSTRUTORA ALICERCE LTDA', ['obras@alicerce.example.com', 'adm@alicerce.example.com', '-']),
    ('CONSTRUTORA ALICERCE LTDA - FILIAL', ['obras@alicerce.example.com', 'adm@alicerce.example.com', '-']),
    ('PAPELARIA CANETA AZUL LTDA', ['vendas@canetaazul.example.com', '-', '-']),
    ('ACADEMIA CORPO EM FORMA LTDA', ['gerencia@corpoemforma.example.com', '-', '-']),
    ('AGENCIA PIXEL CRIATIVO LTDA', ['ola@pixelcriativo.example.com', 'fin@pixelcriativo.example.com', '-']),
    ('ESCOLA APRENDER MAIS LTDA', ['secretaria@aprendermais.example.com', '-', '-']),
    ('TRANSPORTES RODA LIVRE LTDA', ['logistica@rodalivre.example.com', '-', '-']),
    ('PET SHOP AMIGO FIEL LTDA', ['atendimento@amigofiel.example.com', '-', '-']),
    ('FLORICULTURA JARDIM DE CORES LTDA', ['pedidos@jardimdecores.example.com', '-', '-']),
    # Cadastrados na planilha, mas sem relatório no mês (cenário real: nem todo cliente tem PDF).
    ('LANCHONETE SABOR CASEIRO LTDA', ['lanches@saborcaseiro.example.com', '-', '-']),
    ('STUDIO LUZ DE FOTOGRAFIA LTDA', ['contato@studioluz.example.com', '-', '-']),
    # Sem e-mail cadastrado: o script deve acusar erro se houver PDF para ele.
    ('BARBEARIA NAVALHA DE OURO LTDA', ['', '-', '-']),
]
SEM_RELATORIO = {'LANCHONETE SABOR CASEIRO LTDA', 'STUDIO LUZ DE FOTOGRAFIA LTDA',
                 'BARBEARIA NAVALHA DE OURO LTDA'}


def cnpj_ficticio(i, filial=1):
    # Prefixo 00.000.xxx é inválido de propósito: não pertence a ninguém.
    return f'00.000.{i:03d}/{filial:04d}-00'


def brl(v):
    return 'R$ ' + f'{v:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def gerar_planilha():
    wb = Workbook()
    ws = wb.active
    ws.title = 'Clientes'
    ws.append(['RAZÃO SOCIAL', 'CPF/CNPJ', 'E-MAIL - 1', 'E-MAIL - 2', 'E-MAIL - 3'])
    for i, (nome, emails) in enumerate(CLIENTES, 1):
        filial = 2 if nome.endswith('FILIAL') else 1
        ws.append([nome, cnpj_ficticio(i, filial), *emails])
    for col, largura in zip('ABCDE', (46, 22, 38, 34, 12)):
        ws.column_dimensions[col].width = largura
    (RAIZ / 'dados').mkdir(exist_ok=True)
    wb.save(RAIZ / 'dados' / 'clientes.xlsx')


def gerar_pdf(destino, empresa, cnpj, rng):
    c = canvas.Canvas(str(destino), pagesize=A4)
    larg, alt = A4
    verde, lima = colors.HexColor('#0e3b43'), colors.HexColor('#b5cc18')

    def cabecalho(titulo, pagina):
        c.setFillColor(verde)
        c.rect(0, alt - 90, larg, 90, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 22)
        c.drawString(36, alt - 52, 'ALFA CONTÁBIL')
        c.setFont('Helvetica', 9)
        c.drawString(36, alt - 68, 'GESTÃO CONTÁBIL (DEMONSTRAÇÃO)')
        c.setFont('Helvetica-Bold', 16)
        c.drawRightString(larg - 36, alt - 48, titulo)
        c.setFont('Helvetica', 9)
        c.drawRightString(larg - 36, alt - 64, f'Competência: {COMPETENCIA[0]}/{COMPETENCIA[2]}  |  Página {pagina}')
        c.setFillColor(colors.HexColor('#999999'))
        c.setFont('Helvetica', 8)
        c.drawCentredString(larg / 2, 28, 'DOCUMENTO COM DADOS FICTÍCIOS — gerado para demonstração, sem valor fiscal')

    # Página 1 — capa
    c.setFillColor(verde)
    c.rect(0, 0, larg, alt, fill=1, stroke=0)
    c.setFillColor(lima)
    c.rect(36, alt - 140, 90, 6, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 30)
    c.drawString(36, alt - 190, 'RELATÓRIO EXECUTIVO')
    c.setFont('Helvetica', 20)
    c.drawString(36, alt - 220, 'SIMPLES NACIONAL')
    c.setFont('Helvetica', 11)
    c.drawString(36, alt - 290, 'COMPETÊNCIA')
    c.setFont('Helvetica-Bold', 18)
    c.drawString(36, alt - 312, f'{COMPETENCIA[0].upper()} • {COMPETENCIA[2]}')
    c.setFont('Helvetica', 11)
    c.drawString(36, alt - 350, 'EMPRESA')
    c.setFont('Helvetica-Bold', 16)
    c.drawString(36, alt - 372, empresa)
    c.setFont('Helvetica', 11)
    c.drawString(36, alt - 392, f'CNPJ: {cnpj} (fictício)')
    c.setFont('Helvetica-Oblique', 10)
    c.setFillColor(lima)
    c.drawString(36, 60, 'DADOS FICTÍCIOS — PROJETO DE DEMONSTRAÇÃO')
    c.showPage()

    # Página 2 — dashboard
    fat = rng.uniform(25_000, 180_000)
    aliq = rng.uniform(0.045, 0.115)
    das = fat * aliq
    ant = fat * rng.uniform(0.8, 1.2)
    cabecalho('DASHBOARD TRIBUTÁRIO', 1)
    c.setFillColor(verde)
    c.setFont('Helvetica-Bold', 20)
    c.drawString(36, alt - 135, empresa)
    c.setFillColor(colors.HexColor('#7a8a00'))
    c.setFont('Helvetica-Bold', 11)
    c.drawString(36, alt - 152, cnpj)
    cartoes = [
        ('FATURAMENTO SETEMBRO/26', brl(fat)),
        ('DAS APURADO SETEMBRO/26', brl(das)),
        ('ALÍQUOTA EFETIVA GLOBAL', f'{aliq * 100:.4f}%'.replace('.', ',')),
        ('FATURAMENTO AGOSTO/26', brl(ant)),
        ('VARIAÇÃO VS. AGOSTO/26', f'{(fat / ant - 1) * 100:+.2f}%'.replace('.', ',')),
        ('RBT12 PROJETADO', brl(fat * 11.4)),
    ]
    for k, (rotulo, valor) in enumerate(cartoes):
        x = 36 + (k % 3) * 178
        y = alt - 260 - (k // 3) * 95
        c.setFillColor(colors.HexColor('#f1f5f6'))
        c.roundRect(x, y, 168, 82, 6, fill=1, stroke=0)
        c.setFillColor(verde)
        c.setFont('Helvetica-Bold', 7.5)
        c.drawString(x + 10, y + 62, rotulo)
        c.setFont('Helvetica-Bold', 15)
        c.drawString(x + 10, y + 34, valor)
    c.setFillColor(colors.HexColor('#444444'))
    c.setFont('Helvetica', 9)
    c.drawString(36, alt - 470, 'Todos os valores deste relatório foram gerados aleatoriamente (semente fixa por empresa).')
    c.showPage()

    # Página 3 — composição
    cabecalho('COMPOSIÇÃO DO DAS', 2)
    partes = [('IRPJ', .055), ('CSLL', .035), ('COFINS', .127), ('PIS/PASEP', .028),
              ('CPP', .415), ('ICMS', .340)]
    c.setFillColor(verde)
    c.setFont('Helvetica-Bold', 13)
    c.drawString(36, alt - 135, 'Tributo')
    c.drawRightString(larg - 36, alt - 135, 'Valor (R$)')
    y = alt - 155
    for nome, pct in partes:
        c.setStrokeColor(colors.HexColor('#dddddd'))
        c.line(36, y - 6, larg - 36, y - 6)
        c.setFillColor(colors.black)
        c.setFont('Helvetica', 11)
        c.drawString(36, y, nome)
        c.drawRightString(larg - 36, y, brl(das * pct)[3:])
        y -= 24
    c.setFont('Helvetica-Bold', 11)
    c.drawString(36, y - 6, 'TOTAL DAS')
    c.drawRightString(larg - 36, y - 6, brl(das)[3:])
    c.showPage()
    c.save()


def gerar_pdfs():
    pasta = RAIZ / 'arquivos'
    pasta.mkdir(exist_ok=True)
    for antigo in pasta.glob('*.pdf'):
        antigo.unlink()
    n = 0
    for i, (nome, _) in enumerate(CLIENTES, 1):
        if nome in SEM_RELATORIO:
            continue
        filial = 2 if nome.endswith('FILIAL') else 1
        rng = random.Random(i)
        # Padrão de nome aceito pelo script: "Relatório <EMPRESA> - <Mês> <Ano>.pdf"
        arquivo = pasta / f'Relatório {nome} - {COMPETENCIA[0]} {COMPETENCIA[2]}.pdf'
        gerar_pdf(arquivo, nome, cnpj_ficticio(i, filial), rng)
        n += 1
    return n


def gerar_assinatura():
    img = Image.new('RGB', (900, 220), '#0e3b43')
    d = ImageDraw.Draw(img)
    try:
        fonte_g = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 54)
        fonte_p = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 24)
    except OSError:
        fonte_g = fonte_p = ImageFont.load_default()
    d.rectangle([40, 40, 52, 180], fill='#b5cc18')
    d.text((75, 38), 'ALFA CONTÁBIL', font=fonte_g, fill='white')
    d.text((75, 110), 'Maria Exemplo — Gerente (assinatura de demonstração)', font=fonte_p, fill='white')
    d.text((75, 148), 'relatorios@alfacontabil.example  |  (00) 0000-0000', font=fonte_p, fill='#b5cc18')
    (RAIZ / 'assets').mkdir(exist_ok=True)
    img.save(RAIZ / 'assets' / 'assinatura_demo.png')


if __name__ == '__main__':
    gerar_planilha()
    total = gerar_pdfs()
    gerar_assinatura()
    print(f'Planilha com {len(CLIENTES)} clientes, {total} PDFs e assinatura gerados em {RAIZ}')
