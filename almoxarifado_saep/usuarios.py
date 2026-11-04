CREATE TABLE usuarios (
    from conexao import conectar
    from werkzeug.security import generate_password_hash, check_password_hash
    def cadastrar_usuario(nome,email,senha,perfil):
        if perfil not in ("administrador", "Operador"): 
            raise valueError("Perfil inválido.")

            banco = conectar()
            cursor = banco.cursor(dictionary=true)
            try:
                senha_hash = generate_password_hash(senha)

                cursor.execute("""
                INSERT INTO usuarios
                (nome, email, senha_hash, perfil)
                VALUES(%S, %S, %S,%S)
                """, (nome, email,senha_hash, perfil))
                banco.commit()
                
                finally: 
                    cursor.close()
                    banco.close()
    def autenticar_usuario(email, senha):
        banco = conectar()
        cursor = banco.cursor(dictionary=True)

        try:
            cursoe.execute("""
            SELECT * FROM usuarios
            WHERE email = %s AND ativo = TRUE
            """, (email,))

            usuario = cursor.fetchone()

            if usuario and check_password_hash(
                usuario["senha_hash"], senha 
            ):
                return usuario 
            return None 
         finally:
            cursor.close()
            banco.close()        
); 



















































anco.start_transaction()
                cursor.execute(""" 
                SELECT quantidade_estoque
                FROM produtos 
                WHERE id = %s
                FOR UPDATE
                """, (produto_id,))
                produto = cursor.fetchone()
                if produto is None: 
                    raise valueError ("Produto não encontrado.")

                    saldo = produto["quantidade_estoque"]
                    