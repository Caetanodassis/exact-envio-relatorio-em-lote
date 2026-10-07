"""Testa dois clientes fictícios usando os e-mails da demonstração."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'src'))
from enviar_relatorios import main, normalizar

DESTINOS_TESTE = {
    normalizar('ACADEMIA CORPO EM FORMA LTDA'): 'gerencia@corpoemforma.example.com',
    normalizar('CLINICA SORRISO FELIZ LTDA'): 'recepcao@sorrisofeliz.example.com',
}

if __name__ == '__main__':
    sys.exit(main(testes=DESTINOS_TESTE))
