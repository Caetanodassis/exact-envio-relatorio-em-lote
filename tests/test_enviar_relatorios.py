"""Testes: leitura de nomes/planilha e envio de ponta a ponta contra um SMTP local falso."""
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / 'src'))
import enviar_relatorios as er  # noqa: E402


def test_normalizar_remove_acentos_e_sufixos():
    assert er.normalizar('Padaria Pão Dourado & Cia ME') == 'PADARIA PAO DOURADO E CIA'


@pytest.mark.parametrize('nome, mes, ano, empresa', [
    ('Relatório SIMPLES NACIONAL 09 2026 - PADARIA X LTDA.pdf', 9, 2026, 'PADARIA X LTDA'),
    ('Relatório PADARIA X LTDA - Setembro 2026.pdf', 9, 2026, 'PADARIA X LTDA'),
    ('Relatório CONSTRUTORA Y LTDA - FILIAL - Setembro 2026.pdf', 9, 2026, 'CONSTRUTORA Y LTDA - FILIAL'),
])
def test_identificar(nome, mes, ano, empresa):
    r = er.identificar(Path(nome))
    assert (r.mes, r.ano, r.empresa) == (mes, ano, empresa)


def test_nome_invalido():
    with pytest.raises(ValueError):
        er.identificar(Path('qualquer coisa.pdf'))


def test_planilha_fictícia_carrega_e_relaciona():
    clientes = er.carregar_clientes(RAIZ / 'dados' / 'clientes.xlsx')
    cadastro, emails = er.relacionar('MERCEARIA BOA VISTA LTDA', clientes)
    assert cadastro == 'MERCEARIA BOA VISTA LTDA'
    assert emails == ['financeiro@boavista.example.com', 'dono@boavista.example.com']


def test_cliente_sem_email_gera_erro():
    clientes = er.carregar_clientes(RAIZ / 'dados' / 'clientes.xlsx')
    with pytest.raises(ValueError, match='nenhum e-mail'):
        er.relacionar('BARBEARIA NAVALHA DE OURO LTDA', clientes)


def test_envio_de_ponta_a_ponta(monkeypatch):
    """Sobe um SMTP local, envia os 13 relatórios por UMA conexão e confere o resultado."""
    from aiosmtpd.controller import Controller
    from aiosmtpd.smtp import AuthResult, LoginPassword

    recebidos = []

    class Coletor:
        async def handle_DATA(self, server, session, envelope):
            recebidos.append(envelope)
            return '250 OK'

    def autenticar(server, session, envelope, mechanism, auth_data):
        return AuthResult(success=True)

    import socket
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        porta = sock.getsockname()[1]
    ctrl = Controller(Coletor(), hostname='127.0.0.1', port=porta, authenticator=autenticar,
                      auth_require_tls=False)
    ctrl.start()
    try:
        monkeypatch.setenv('SMTP_HOST', '127.0.0.1')
        monkeypatch.setenv('SMTP_PORT', str(porta))
        monkeypatch.setenv('SMTP_STARTTLS', 'false')
        monkeypatch.setenv('SMTP_PASSWORD', 'qualquer')
        monkeypatch.setenv('SAVE_TO_SENT', 'false')
        monkeypatch.setattr(sys, 'argv', ['enviar_relatorios.py', '--enviar'])
        assert er.main() == 0
    finally:
        ctrl.stop()

    assert len(recebidos) == 13
    destinos = {d for e in recebidos for d in e.rcpt_tos}
    assert 'financeiro@boavista.example.com' in destinos
    assert all(b'application/pdf' in e.content or b'filename=' in e.content for e in recebidos)


def test_mes_desconhecido():
    with pytest.raises(ValueError, match='Mês não reconhecido'):
        er.identificar(Path('Relatório EMPRESA LTDA - Inexistente 2026.pdf'))


def test_lote_reutiliza_smtp_e_preserva_assinatura(monkeypatch):
    from email import message_from_bytes
    from unittest.mock import MagicMock

    smtp = MagicMock()
    smtp.return_value.sendmail.return_value = {}
    monkeypatch.setattr(er.smtplib, 'SMTP', smtp)
    monkeypatch.setenv('SMTP_HOST', 'localhost')
    monkeypatch.setenv('SMTP_PORT', '1025')
    monkeypatch.setenv('SMTP_USER', 'relatorios@alfacontabil.example')
    monkeypatch.setenv('SMTP_PASSWORD', 'ficticia')
    monkeypatch.setenv('SMTP_STARTTLS', 'false')
    monkeypatch.setenv('SAVE_TO_SENT', 'false')
    monkeypatch.setattr(sys, 'argv', ['enviar_relatorios.py', '--enviar'])
    assert er.main() == 0
    assert smtp.call_count == 1
    smtp.return_value.login.assert_called_once()
    smtp.return_value.starttls.assert_not_called()
    assert smtp.return_value.sendmail.call_count == 13
    for chamada in smtp.return_value.sendmail.call_args_list:
        msg = message_from_bytes(chamada.args[2])
        partes = list(msg.walk())
        imagem = next(p for p in partes if p.get_content_type() == 'image/png')
        html = next(p for p in partes if p.get_content_type() == 'text/html')
        assert ('cid:' + imagem['Content-ID'][1:-1]) in html.get_payload(decode=True).decode('utf-8')
        assert imagem.get_payload(decode=True) == er.ASSINATURA.read_bytes()
        anexos = [p for p in partes if p.get_content_disposition() == 'attachment']
        assert len(anexos) == 1
        assert anexos[0].get_filename().endswith('.pdf')


def test_previa_nao_abre_conexoes(monkeypatch):
    from unittest.mock import MagicMock
    smtp, imap = MagicMock(), MagicMock()
    monkeypatch.setattr(er.smtplib, 'SMTP', smtp)
    monkeypatch.setattr(er.imaplib, 'IMAP4_SSL', imap)
    monkeypatch.setattr(sys, 'argv', ['enviar_relatorios.py'])
    assert er.main() == 0
    smtp.assert_not_called()
    imap.assert_not_called()


def test_pendencia_bloqueia_o_lote_inteiro(monkeypatch, tmp_path):
    """Um PDF sem e-mail cadastrado impede o envio de todos os outros."""
    from unittest.mock import MagicMock

    (tmp_path / 'Relatório PADARIA PAO DOURADO LTDA - Setembro 2026.pdf').write_bytes(b'%PDF')
    (tmp_path / 'Relatório BARBEARIA NAVALHA DE OURO LTDA - Setembro 2026.pdf').write_bytes(b'%PDF')
    smtp = MagicMock()
    monkeypatch.setattr(er.smtplib, 'SMTP', smtp)
    monkeypatch.setenv('SMTP_PASSWORD', 'ficticia')
    monkeypatch.setenv('SAVE_TO_SENT', 'false')
    monkeypatch.setattr(sys, 'argv', ['enviar_relatorios.py', '--pasta', str(tmp_path), '--enviar'])
    assert er.main() == 1
    smtp.assert_not_called()


def test_empresa_sem_cadastro_gera_erro():
    clientes = er.carregar_clientes(RAIZ / 'dados' / 'clientes.xlsx')
    with pytest.raises(ValueError, match='encontrados 0 cadastros'):
        er.relacionar('EMPRESA QUE NAO EXISTE LTDA', clientes)


def test_cadastro_ambiguo_bloqueia():
    clientes = [
        ('EMPRESA ALFA COMERCIO', ['a@exemplo.example.com']),
        ('EMPRESA ALFA COMERCIO SUL', ['b@exemplo.example.com']),
    ]
    with pytest.raises(ValueError, match='encontrados 2 cadastros'):
        er.relacionar('EMPRESA ALFA COMERCIO SUL FILIAL', clientes)


def test_filial_nao_se_confunde_com_matriz():
    clientes = er.carregar_clientes(RAIZ / 'dados' / 'clientes.xlsx')
    assert er.relacionar('CONSTRUTORA ALICERCE LTDA', clientes)[0] == 'CONSTRUTORA ALICERCE LTDA'
    assert er.relacionar('CONSTRUTORA ALICERCE LTDA - FILIAL', clientes)[0] == (
        'CONSTRUTORA ALICERCE LTDA - FILIAL'
    )


def test_email_invalido_na_planilha(tmp_path):
    from openpyxl import Workbook

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(['RAZÃO SOCIAL', 'E-MAIL - 1', 'E-MAIL - 2', 'E-MAIL - 3'])
    worksheet.append(['EMPRESA TESTE LTDA', 'isto-nao-e-um-email', '-', '-'])
    caminho = tmp_path / 'clientes.xlsx'
    workbook.save(caminho)
    with pytest.raises(ValueError, match='E-mail inválido na linha 2'):
        er.carregar_clientes(caminho)
