from app.database import get_connection


def criar_recomendacao(
    usuario_id,
    musica,
    artista,
    motivo,
    spotify_id=None,
    album=None,
    capa_url=None,
    spotify_url=None
):
    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO recomendacoes (
                    usuario_id,
                    musica,
                    artista,
                    motivo,
                    spotify_id,
                    album,
                    capa_url,
                    spotify_url
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                RETURNING id;
                """,
                (
                    usuario_id,
                    musica,
                    artista,
                    motivo,
                    spotify_id,
                    album,
                    capa_url,
                    spotify_url
                )
            )

            recomendacao_id = cursor.fetchone()[0]

        connection.commit()

        return recomendacao_id

    except Exception:

        connection.rollback()

        raise

    finally:

        connection.close()


def listar_recomendacoes_por_usuario(usuario_id):

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    id,
                    musica,
                    artista,
                    motivo,
                    criado_em,
                    spotify_id,
                    album,
                    capa_url,
                    spotify_url
                FROM recomendacoes
                WHERE usuario_id = %s
                ORDER BY criado_em DESC;
                """,
                (usuario_id,)
            )

            return cursor.fetchall()

    finally:

        connection.close()


def excluir_recomendacoes_do_usuario(usuario_id):

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                DELETE FROM recomendacoes
                WHERE usuario_id = %s;
                """,
                (usuario_id,)
            )

        connection.commit()

    except Exception:

        connection.rollback()

        raise

    finally:

        connection.close()