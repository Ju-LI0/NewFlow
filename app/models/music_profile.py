from app.database import get_connection


def buscar_perfil_por_usuario(usuario_id):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    usuario_id,
                    generos,
                    artistas,
                    musicas_favoritas,
                    humor_preferido,
                    decadas_preferidas
                FROM perfis_musicais
                WHERE usuario_id = %s;
                """,
                (usuario_id,)
            )

            return cursor.fetchone()

    finally:
        connection.close()


def criar_ou_atualizar_perfil(
    usuario_id,
    generos,
    artistas,
    musicas_favoritas,
    humor_preferido,
    decadas_preferidas
):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO perfis_musicais (
                    usuario_id,
                    generos,
                    artistas,
                    musicas_favoritas,
                    humor_preferido,
                    decadas_preferidas
                )
                VALUES (%s, %s, %s, %s, %s, %s)

                ON CONFLICT (usuario_id)
                DO UPDATE SET
                    generos = EXCLUDED.generos,
                    artistas = EXCLUDED.artistas,
                    musicas_favoritas = EXCLUDED.musicas_favoritas,
                    humor_preferido = EXCLUDED.humor_preferido,
                    decadas_preferidas = EXCLUDED.decadas_preferidas,
                    atualizado_em = CURRENT_TIMESTAMP

                RETURNING id;
                """,
                (
                    usuario_id,
                    generos,
                    artistas,
                    musicas_favoritas,
                    humor_preferido,
                    decadas_preferidas
                )
            )

            perfil_id = cursor.fetchone()[0]

        connection.commit()

        return perfil_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()