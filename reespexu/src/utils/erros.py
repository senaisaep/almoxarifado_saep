class ErroAPI(Exception):
    # Erro que vira resposta JSON. Ex.: raise ErroAPI("Produto não encontrado.", 404)
    def __init__(self, mensagem, status=400, detalhes=None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.status = status
        self.detalhes = detalhes
