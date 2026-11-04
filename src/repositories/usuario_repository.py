_PUBLICO = "id, nome, email, perfil, ativo, data_cadastro"


def buscar_por_id(cur, usuario_id):
    cur.execute(f"SELECT {_PUBLICO} FROM usuarios WHERE id = %s", (usuario_id,))
    return cur.fetchone()


def buscar_por_email(cur, email):
    cur.execute(
        f"""SELECT {_PUBLICO}, senha_hash, tentativas_login, bloqueado_ate,
                   (bloqueado_ate IS NOT NULL AND bloqueado_ate > NOW()) AS bloqueado
            FROM usuarios WHERE email = %s""",
        (email,),
    )
    return cur.fetchone()


def listar(cur):
    cur.execute(f"SELECT {_PUBLICO} FROM usuarios ORDER BY nome")
    return cur.fetchall()


def inserir(cur, nome, email, senha_hash, perfil):
    cur.execute(
        "INSERT INTO usuarios (nome, email, senha_hash, perfil) VALUES (%s, %s, %s, %s)",
        (nome, email, senha_hash, perfil),
    )
    return cur.lastrowid


def atualizar(cur, usuario_id, nome, perfil, ativo):
    cur.execute(
        "UPDATE usuarios SET nome=%s, perfil=%s, ativo=%s WHERE id=%s",
        (nome, perfil, 1 if ativo else 0, usuario_id),
    )


def atualizar_senha(cur, usuario_id, senha_hash):
    cur.execute(
        """UPDATE usuarios SET senha_hash=%s, tentativas_login=0, bloqueado_ate=NULL
           WHERE id=%s""",
        (senha_hash, usuario_id),
    )


def registrar_falha(cur, usuario_id, max_tentativas, bloqueio_minutos):
    # O MySQL avalia as atribuições da esquerda para a direita: bloqueado_ate usa
    # o valor ANTIGO de tentativas_login, por isso o "+ 1".
    cur.execute(
        """UPDATE usuarios
           SET bloqueado_ate = IF(tentativas_login + 1 >= %s,
                                  DATE_ADD(NOW(), INTERVAL %s MINUTE), bloqueado_ate),
               tentativas_login = tentativas_login + 1
           WHERE id=%s""",
        (max_tentativas, bloqueio_minutos, usuario_id),
    )


def zerar_falhas(cur, usuario_id):
    cur.execute(
        "UPDATE usuarios SET tentativas_login=0, bloqueado_ate=NULL WHERE id=%s",
        (usuario_id,),
    )
