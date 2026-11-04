ADMIN = "admin"
ALMOXARIFE = "almoxarife"
CONSULTA = "consulta"

PERFIS = (ADMIN, ALMOXARIFE, CONSULTA)

# Matriz de permissões (resumo; aplicada por @requer_perfil nas rotas)
#   admin       -> tudo, incluindo gestão de usuários e exclusão de produtos
#   almoxarife  -> cadastrar/editar produtos e registrar entradas/saídas
#   consulta    -> somente leitura (produtos e movimentações)
