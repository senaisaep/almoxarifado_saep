"""Cria o primeiro administrador.

Uso interativo:
    python -m src.scripts.criar_admin

Uso com argumentos (ou automação):
    python -m src.scripts.criar_admin --nome "Administrador" --email "admin@exemplo.com" --senha "SuaSenha123"
"""
import argparse
import getpass
import os
import sys
from pathlib import Path

# Garante que a raiz do projeto esteja no sys.path mesmo ao executar diretamente 'python src/scripts/criar_admin.py'
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.services import usuario_service
from src.utils.erros import ErroApi


def main():
    parser = argparse.ArgumentParser(description="Cria o administrador do sistema.")
    parser.add_argument("--nome", help="Nome do administrador")
    parser.add_argument("--email", help="E-mail do administrador")
    parser.add_argument("--senha", help="Senha (mínimo 8 caracteres com letras e números)")
    args = parser.parse_args()

    nome = (args.nome or os.getenv("ADMIN_NOME") or "").strip()
    email = (args.email or os.getenv("ADMIN_EMAIL") or "").strip()
    senha = args.senha or os.getenv("ADMIN_SENHA") or ""

    if not nome:
        nome = input("Nome: ").strip()
    if not email:
        email = input("E-mail: ").strip()
    if not senha:
        senha = getpass.getpass("Senha: ")
        confirma = getpass.getpass("Confirme a senha: ")
        if senha != confirma:
            print("As senhas não conferem.")
            return 1

    try:
        novo_id = usuario_service.criar(
            {"nome": nome, "email": email, "senha": senha, "perfil": "admin"}
        )
    except ErroApi as erro:
        print(f"Erro: {erro.mensagem}")
        return 1
    print(f"Administrador criado com sucesso (id {novo_id}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
