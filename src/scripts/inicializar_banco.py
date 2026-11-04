"""Script para inicializar e verificar o banco de dados do Almoxarifado.

Uso:
    python -m src.scripts.inicializar_banco
"""
import sys
from pathlib import Path

# Garante que a raiz do projeto esteja no sys.path
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.config.db import conectar, inicializar_banco, obter_configuracao, testar_conexao


def main():
    cfg = obter_configuracao()
    print(f"[*] Verificando conexão com MySQL em {cfg['host']}:{cfg['port']}...")

    ok, msg = testar_conexao()
    if ok:
        print(f"[+] Conexão bem-sucedida! Banco de dados '{cfg['database']}' operacional.")
        return 0

    print(f"[-] Conexão falhou: {msg}")
    print("[*] Tentando inicializar o banco e tabelas a partir de infra/bd.sql...")
    try:
        sucesso, mensagem = inicializar_banco()
        print(f"[+] {mensagem}")
        return 0
    except Exception as e:
        print(f"[!] Erro ao inicializar o banco: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
