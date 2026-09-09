import bcrypt

from app.database import get_connection


def criar_usuario(nome, email, senha):
    senha_hash = bcrypt.hashpw(
        senha.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO usuarios (nome, email, senha_hash)
                VALUES (%s, %s, %s)
                RETURNING id;
                """,
                (nome, email, senha_hash)
            )

            usuario_id = cursor.fetchone()[0]

        connection.commit()

        return usuario_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def buscar_usuario_por_email(email):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, nome, email, senha_hash
                FROM usuarios
                WHERE email = %s;
                """,
                (email,)
            )

            return cursor.fetchone()

    finally:
        connection.close()


def verificar_senha(senha, senha_hash):
    return bcrypt.checkpw(
        senha.encode("utf-8"),
        senha_hash.encode("utf-8")
    )