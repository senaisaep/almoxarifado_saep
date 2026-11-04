class ErroApi(Exception):
    """Erro previsto de negócio/validação, convertido em resposta JSON."""

    def __init__(self, mensagem, status=400, extra=None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.status = status
        self.extra = extra or {}


class EstoqueInsuficiente(ErroApi):
    def __init__(self, disponivel, solicitado):
        super().__init__(
            f"Saída não permitida: estoque insuficiente. "
            f"Disponível: {disponivel}, solicitado: {solicitado}.",
            status=422,
            extra={"disponivel": disponivel, "solicitado": solicitado},
        )
