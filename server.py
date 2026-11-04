import logging
import os
import sys
from pathlib import Path

# Garante que a raiz do projeto esteja no sys.path
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.server import app, create_app

__all__ = ["app", "create_app"]

if __name__ == "__main__":
    from src.config.db import testar_conexao
    logger = logging.getLogger("almoxarifado")
    ok, msg = testar_conexao()
    if ok:
        logger.info("Banco de dados MySQL conectado com sucesso.")
    else:
        logger.warning("Aviso de banco: %s", msg)

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    logger.info("Iniciando servidor em http://%s:%d (debug=%s)", host, port, debug)

    app.run(
        host=host,
        port=port,
        debug=debug,
    )
