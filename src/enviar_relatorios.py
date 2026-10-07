"""Relaciona relatórios à planilha de clientes. Sem --enviar, apenas exibe a prévia."""
import argparse
import imaplib
import os
import re
import smtplib
import ssl
import sys
import time
import unicodedata
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass
from html import escape
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.policy import SMTP as POLITICA_SMTP
from email.utils import formatdate, make_msgid
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ASSINATURA = RAIZ / 'assets' / 'assinatura_demo.png'


@dataclass(frozen=True)
class Relatorio:
    arquivo: Path
    tipo: str
    mes: int
    ano: int
    empresa: str


def normalizar(nome):
    nome = unicodedata.normalize('NFKD', str(nome)).encode('ascii', 'ignore').decode().upper()
    nome = re.sub(r'[^A-Z0-9]+', ' ', nome.replace('&', ' E ')).strip()
    return re.sub(r'\s+(ME|EPP)$', '', nome)


def identificar(arquivo):
    # Exemplo: RELATÓRIO SIMPLES NACIONAL 08 2026 - NOME DA EMPRESA.pdf
    padrao = r'^RELAT[ÓO]RIO\s+(.+?)\s+(0?[1-9]|1[0-2])[ _./-]+(20\d{2})\s*-\s*(.+)$'
    resultado = re.fullmatch(padrao, arquivo.stem, re.IGNORECASE)
    if resultado:
        tipo, mes, ano, empresa = resultado.groups()
        return Relatorio(arquivo, tipo.upper(), int(mes), int(ano), empresa.strip())

    padrao_mensal = (
        r'^RELAT[ÓO]RIO\s+(.+?)\s*-\s*'
        r'(0?[1-9]|1[0-2]|[A-ZÁÉÍÓÚÂÊÔÃÕÇ]+)\s+(20\d{2})$'
    )
    resultado = re.fullmatch(padrao_mensal, arquivo.stem, re.IGNORECASE)
    if resultado:
        empresa, mes, ano = resultado.groups()
        meses = ('JANEIRO', 'FEVEREIRO', 'MARCO', 'ABRIL', 'MAIO', 'JUNHO',
                 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO')
        if not mes.isdecimal() and normalizar(mes) not in meses:
            raise ValueError(f'Mês não reconhecido: {mes}')
        mes = int(mes) if mes.isdecimal() else meses.index(normalizar(mes)) + 1
        return Relatorio(arquivo, 'SIMPLES NACIONAL', mes, int(ano), empresa.strip())

    raise ValueError(f'Nome de relatório não reconhecido: {arquivo.name}')


def localizar_planilha(pasta):
    tabelas = sorted(pasta.glob('*.xlsx'))
    if len(tabelas) > 1:
        raise ValueError('Há várias planilhas em arquivos/. Escolha uma usando --planilha.')
    if tabelas:
        return tabelas[0]
    return RAIZ / 'dados' / 'clientes.xlsx'


def carregar_clientes(planilha):
    from openpyxl import load_workbook
    clientes = []
    with planilha.open('rb') as entrada:
        workbook = load_workbook(entrada, read_only=True, data_only=True)
        try:
            linhas = workbook.active.iter_rows(values_only=True)
            cabecalho = next(linhas, ())
            colunas = {normalizar(c): i for i, c in enumerate(cabecalho) if c}
            obrigatorias = ['RAZAO SOCIAL', 'E MAIL 1', 'E MAIL 2', 'E MAIL 3']
            if any(c not in colunas for c in obrigatorias):
                raise ValueError('A planilha deve ter RAZÃO SOCIAL e E-MAIL - 1, 2 e 3.')
            for numero, linha in enumerate(linhas, 2):
                empresa = linha[colunas['RAZAO SOCIAL']]
                if not empresa:
                    continue
                emails = []
                for coluna in obrigatorias[1:]:
                    valor = linha[colunas[coluna]]
                    if valor is None or str(valor).strip() in ('', '-'):
                        continue
                    for email in re.split(r'[;,\s]+', str(valor).strip()):
                        if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email):
                            raise ValueError(f'E-mail inválido na linha {numero}, coluna {coluna}.')
                        if email.lower() not in [e.lower() for e in emails]:
                            emails.append(email)
                clientes.append((str(empresa).strip(), emails))
        finally:
            workbook.close()
    return clientes


def relacionar(empresa, clientes):
    nome = normalizar(empresa)
    candidatos = [c for c in clientes if normalizar(c[0]) == nome]
    unicos = {}
    for cadastro, emails in candidatos:
        chave = (normalizar(cadastro), frozenset(email.lower() for email in emails))
        unicos.setdefault(chave, (cadastro, emails))
    candidatos = list(unicos.values())
    if not candidatos:
        # Aceita cadastro abreviado com ao menos três palavras completas.
        candidatos = [c for c in clientes if len(normalizar(c[0]).split()) >= 3
                      and nome.startswith(normalizar(c[0]) + ' ')]
        unicos = {}
        for cadastro, emails in candidatos:
            chave = (normalizar(cadastro), frozenset(email.lower() for email in emails))
            unicos.setdefault(chave, (cadastro, emails))
        candidatos = list(unicos.values())
    if len(candidatos) != 1:
        raise ValueError(f'{empresa}: encontrados {len(candidatos)} cadastros; revise a razão social na tabela.')
    cadastro, emails = candidatos[0]
    if not emails:
        raise ValueError(f'{cadastro}: nenhum e-mail cadastrado.')
    return cadastro, emails


def salvar_em_enviados(conteudo, remetente, senha, host_smtp):
    """Salva a mensagem já enviada; nunca inicia outro envio SMTP."""
    host = os.getenv('IMAP_HOST', host_smtp)
    porta = int(os.getenv('IMAP_PORT', '993'))
    usuario = os.getenv('IMAP_USER', remetente)
    senha_imap = os.getenv('IMAP_PASSWORD', senha)
    with imaplib.IMAP4_SSL(host, porta, ssl_context=ssl.create_default_context(), timeout=30) as servidor:
        servidor.login(usuario, senha_imap)
        pasta = os.getenv('IMAP_SENT_FOLDER')
        if pasta:
            pasta = '"' + pasta.replace('\\', '\\\\').replace('"', '\\"') + '"'
        else:
            status, lista = servidor.list()
            if status != 'OK':
                raise ValueError('Não foi possível consultar as pastas IMAP.')
            especiais, alternativas = [], []
            for linha in lista or []:
                if not isinstance(linha, bytes):
                    continue
                partes = re.fullmatch(rb'\(([^)]*)\)\s+(?:"[^"\\]*(?:\\.[^"\\]*)*"|NIL)\s+(.+)', linha)
                if not partes:
                    continue
                flags, nome = partes.groups()
                # Mantém o nome codificado pelo servidor, incluindo aspas.
                nome_pasta = nome.decode('ascii')
                if b'\\sent' in flags.lower().split():
                    especiais.append(nome_pasta)
                elif nome.strip(b'"').lower() in (
                    b'sent', b'sent items', b'sent messages', b'enviados',
                    b'inbox.sent', b'inbox.enviados', b'inbox.sent items',
                ):
                    alternativas.append(nome_pasta)
            candidatas = especiais or alternativas
            if len(candidatas) != 1:
                raise ValueError('Pasta Enviados não identificada de forma única. Defina IMAP_SENT_FOLDER no .env.')
            pasta = candidatas[0]
        status, _ = servidor.append(pasta, r'\Seen', imaplib.Time2Internaldate(time.time()), conteudo)
        if status != 'OK':
            raise ValueError('O servidor IMAP recusou o salvamento da cópia.')
        print(f'Cópia salva no webmail, pasta {pasta}.')


@contextmanager
def conectar_smtp():
    host = os.getenv('SMTP_HOST', 'localhost')
    porta = int(os.getenv('SMTP_PORT', '1025'))
    remetente = os.getenv('SMTP_USER', 'relatorios@alfacontabil.example')
    senha = os.getenv('SMTP_PASSWORD')
    if not senha:
        raise ValueError('Defina SMTP_PASSWORD antes do envio.')
    contexto = ssl.create_default_context()
    usar_starttls = os.getenv('SMTP_STARTTLS', 'true').lower() not in ('0', 'false', 'no')
    if porta == 465:
        servidor = smtplib.SMTP_SSL(host, porta, context=contexto, timeout=30)
    else:
        servidor = smtplib.SMTP(host, porta, timeout=30)
    with servidor:
        if porta != 465 and usar_starttls:
            servidor.ehlo()
            servidor.starttls(context=contexto)
            servidor.ehlo()
        servidor.login(remetente, senha)
        yield servidor


def enviar(relatorio, destinatarios, teste=False, servidor_smtp=None):
    if isinstance(destinatarios, str):
        destinatarios = [destinatarios]
    if not relatorio.arquivo.is_file():
        raise ValueError(f'Envio cancelado: anexo não encontrado: {relatorio.arquivo}')
    if not ASSINATURA.is_file():
        raise ValueError(f'Envio cancelado: assinatura não encontrada: {ASSINATURA}')
    senha = os.getenv('SMTP_PASSWORD')
    if not senha:
        raise ValueError('Defina SMTP_PASSWORD antes do envio.')
    host = os.getenv('SMTP_HOST', 'localhost')
    remetente = os.getenv('SMTP_USER', 'relatorios@alfacontabil.example')
    competencia = f'{relatorio.mes:02d}/{relatorio.ano}'
    mensagem = MIMEMultipart()
    mensagem['From'] = remetente
    mensagem['To'] = ', '.join(destinatarios)
    mensagem['Date'] = formatdate(localtime=True)
    mensagem['Message-ID'] = make_msgid(domain=remetente.split('@')[-1])
    mensagem['Subject'] = f'{"[TESTE] " if teste else ""}{relatorio.tipo} {competencia} - {relatorio.empresa}'
    corpo = (
        'Olá!\n\n'
        f'Segue em anexo o relatório {relatorio.tipo} da empresa {relatorio.empresa}, '
        f'referente à competência {competencia}.\n\n'
        'Este documento contém dados fictícios, sem valor fiscal, e foi gerado '
        'para demonstrar a automação de envio de relatórios.\n\n'
        'Confira o PDF anexo.\n'
    )
    alternativas = MIMEMultipart('alternative')
    alternativas.attach(MIMEText(corpo + '\nAlfa Contábil (demo) — Maria Exemplo, Gerente\n'
                                 'relatorios@alfacontabil.example | (00) 0000-0000\n', 'plain', 'utf-8'))
    relacionado = MIMEMultipart('related')
    cid_assinatura = make_msgid(domain=remetente.split('@')[-1])
    paragrafos = ''.join(f'<p>{escape(p).replace(chr(10), "<br>")}</p>'
                        for p in corpo.strip().split('\n\n'))
    html = ('<!DOCTYPE html><html><body style="font-family:Arial,sans-serif;font-size:14px;">'
            + paragrafos
            + f'<img src="cid:{cid_assinatura[1:-1]}" width="600" '
              'style="display:block;width:600px;max-width:100%;height:auto;margin-top:20px;" '
              'alt="Alfa Contábil (demo) — Maria Exemplo, Gerente. '
              'relatorios@alfacontabil.example | (00) 0000-0000">'
              '</body></html>')
    relacionado.attach(MIMEText(html, 'html', 'utf-8'))
    imagem = MIMEImage(ASSINATURA.read_bytes(), _subtype='png')
    imagem.add_header('Content-ID', cid_assinatura)
    imagem.add_header('Content-Disposition', 'inline', filename=ASSINATURA.name)
    relacionado.attach(imagem)
    alternativas.attach(relacionado)
    mensagem.attach(alternativas)
    anexo = MIMEApplication(relatorio.arquivo.read_bytes())
    anexo.add_header('Content-Disposition', 'attachment', filename=relatorio.arquivo.name)
    mensagem.attach(anexo)
    # Usa a mesma mensagem para SMTP e para a cópia no webmail.
    conteudo = mensagem.as_bytes(policy=POLITICA_SMTP)
    conexao = nullcontext(servidor_smtp) if servidor_smtp is not None else conectar_smtp()
    with conexao as servidor:
        # Mesmo formato e método de envio do enviar_emails2_copy.py.
        recusados = servidor.sendmail(remetente, destinatarios, conteudo)
        if recusados:
            raise ValueError(f'Destinatários recusados: {", ".join(recusados)}. Outros podem ter recebido.')
        # Uma falha ao salvar não deve transformar um envio aceito em tentativa de reenvio.
        try:
            if os.getenv('SAVE_TO_SENT', 'true').lower() not in ('0', 'false', 'no'):
                salvar_em_enviados(conteudo, remetente, senha, host)
        except (imaplib.IMAP4.error, OSError, ValueError, UnicodeError) as erro:
            print(f'AVISO: SMTP aceitou o e-mail para {", ".join(destinatarios)}, '
                  f'mas a cópia em Enviados falhou: {erro}. '
                  'Não repita --enviar apenas para salvar a cópia.', file=sys.stderr)


def main(testes=None):
    inicio_total = time.perf_counter()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pasta', type=Path, default=RAIZ / 'arquivos')
    parser.add_argument('--planilha', type=Path, help='Tabela de referência .xlsx')
    parser.add_argument('--enviar', action='store_true', help='Executa o envio real; padrão é prévia.')
    args = parser.parse_args()
    try:
        if (RAIZ / '.env').is_file():
            try:
                from dotenv import load_dotenv
            except ImportError as erro:
                raise ValueError('Para ler o .env, instale as dependências: python3 -m pip install -r requirements.txt') from erro
            load_dotenv(RAIZ / '.env', override=False)
        if not args.pasta.is_dir():
            raise ValueError(f'Pasta não encontrada: {args.pasta}')
        if not ASSINATURA.is_file():
            raise ValueError(f'Assinatura não encontrada: {ASSINATURA}')
        planilha = args.planilha or localizar_planilha(args.pasta)
        clientes = carregar_clientes(planilha)
        arquivos = sorted(p for p in args.pasta.iterdir() if p.is_file() and p.suffix.lower() == '.pdf')
        if not arquivos:
            raise ValueError('Nenhum PDF encontrado.')
        print(f'Tabela: {planilha}\nModo: {"ENVIO REAL" if args.enviar else "PRÉVIA — sem envio"}')
        plano, erros = [], []
        encontrados = set()
        for arquivo in arquivos:
            try:
                relatorio = identificar(arquivo)
                if testes is not None and normalizar(relatorio.empresa) not in testes:
                    continue
                cadastro, emails = relacionar(relatorio.empresa, clientes)
                destino = emails if testes is None else [testes[normalizar(relatorio.empresa)]]
                encontrados.add(normalizar(relatorio.empresa))
                plano.append((relatorio, destino))
                print(f'\nArquivo: {arquivo.name}\nRelatório: {relatorio.tipo} | Competência: {relatorio.mes:02d}/{relatorio.ano}'
                      f'\nEmpresa: {relatorio.empresa}\nCadastro: {cadastro}\nE-mails na tabela: {", ".join(emails)}'
                      f'\nDestino do envio: {", ".join(destino)}')
            except ValueError as erro:
                erros.append(str(erro))
        if testes is not None:
            for nome in testes.keys() - encontrados:
                erros.append(f'Relatório de teste não encontrado ou cadastro inválido: {nome}')
        if erros:
            raise ValueError('Prévia com pendências. Nenhum envio iniciado:\n' + '\n'.join(erros))
        if not args.enviar:
            print(f'\nPrévia concluída: {len(plano)} mensagem(ns). Use --enviar para enviar.')
            return 0
        if not os.getenv('SMTP_PASSWORD'):
            raise ValueError('Defina SMTP_PASSWORD antes do envio.')
        inicio_conexao = time.perf_counter()
        with conectar_smtp() as servidor:
            print(f'Conexão e autenticação SMTP: {time.perf_counter() - inicio_conexao:.2f} s')
            for relatorio, destino in plano:
                inicio_mensagem = time.perf_counter()
                try:
                    enviar(relatorio, destino, teste=testes is not None, servidor_smtp=servidor)
                    print(f'Enviado: {relatorio.arquivo.name} → {", ".join(destino)}')
                finally:
                    print(f'Tempo da mensagem (montagem, SMTP e registro IMAP): '
                          f'{time.perf_counter() - inicio_mensagem:.2f} s')
        return 0
    except (ValueError, OSError, smtplib.SMTPException, ImportError) as erro:
        print(f'Erro: {erro}', file=sys.stderr)
        return 1
    finally:
        print(f'Tempo total da execução: {time.perf_counter() - inicio_total:.2f} s')


if __name__ == '__main__':
    sys.exit(main())
