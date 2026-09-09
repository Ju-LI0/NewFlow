import os

from app.models.music_profile import (
    buscar_perfil_por_usuario
)

from app.models.recommendation import (
    criar_recomendacao,
    listar_recomendacoes_por_usuario,
    excluir_recomendacoes_do_usuario
)

from app.services.ai_agent import (
    gerar_recomendacoes
)

from app.services.music_service import (
    buscar_musica
)


def spotify_configurado():

    client_id = os.getenv(
        "SPOTIFY_CLIENT_ID"
    )

    client_secret = os.getenv(
        "SPOTIFY_CLIENT_SECRET"
    )

    return bool(
        client_id
        and client_secret
    )


def gerar_recomendacoes_usuario(usuario_id):

    # ==================================================
    # 1. BUSCA O PERFIL MUSICAL
    # ==================================================

    perfil = buscar_perfil_por_usuario(
        usuario_id
    )

    if not perfil:

        raise ValueError(
            "O usuário ainda não possui um perfil musical."
        )

    generos = perfil[2]
    artistas = perfil[3]
    musicas_favoritas = perfil[4]
    humor_preferido = perfil[5]
    decadas_preferidas = perfil[6]

    # ==================================================
    # 2. GEMINI GERA AS RECOMENDAÇÕES
    # ==================================================

    print()
    print("==============================")
    print("GERANDO RECOMENDAÇÕES COM GEMINI")
    print("==============================")
    print()

    recomendacoes = gerar_recomendacoes(
        generos=generos,
        artistas=artistas,
        musicas_favoritas=musicas_favoritas,
        humor_preferido=humor_preferido,
        decadas_preferidas=decadas_preferidas
    )

    # ==================================================
    # 3. VALIDAMOS O RESULTADO
    # ==================================================

    if not recomendacoes:

        raise ValueError(
            "A IA não retornou recomendações."
        )

    if len(recomendacoes) != 5:

        raise ValueError(
            "A IA não retornou exatamente "
            "5 recomendações."
        )

    print(
        "✅ Gemini retornou 5 recomendações."
    )

    # ==================================================
    # 4. TENTA BUSCAR DADOS NO SPOTIFY
    # ==================================================

    dados_spotify = [
        None
        for _ in recomendacoes
    ]

    if spotify_configurado():

        print()
        print("==============================")
        print("INTEGRAÇÃO COM SPOTIFY")
        print("==============================")
        print()

        for indice, recomendacao in enumerate(
            recomendacoes
        ):

            try:

                resultado_spotify = buscar_musica(
                    musica=recomendacao.musica,
                    artista=recomendacao.artista
                )

                dados_spotify[indice] = (
                    resultado_spotify
                )

                if resultado_spotify:

                    print(
                        "✅ Spotify encontrou:",
                        resultado_spotify["musica"],
                        "-",
                        resultado_spotify["artista"]
                    )

                else:

                    print(
                        "⚠️ Spotify não encontrou:",
                        recomendacao.musica,
                        "-",
                        recomendacao.artista
                    )

            except Exception as error:

                print(
                    "⚠️ Spotify indisponível."
                )

                print(
                    "Motivo:",
                    error
                )

                print(
                    "➡️ Continuando sem dados do Spotify."
                )

                dados_spotify[indice] = None

    else:

        print()
        print(
            "ℹ️ Spotify não configurado."
        )

        print(
            "➡️ Recomendações continuarão "
            "funcionando normalmente."
        )

    # ==================================================
    # 5. SOMENTE AGORA ALTERAMOS O BANCO
    # ==================================================

    print()
    print("==============================")
    print("SALVANDO RECOMENDAÇÕES")
    print("==============================")
    print()

    excluir_recomendacoes_do_usuario(
        usuario_id
    )

    ids = []

    for indice, recomendacao in enumerate(
        recomendacoes
    ):

        spotify = dados_spotify[indice]

        spotify_id = None
        album = None
        capa_url = None
        spotify_url = None

        if spotify:

            spotify_id = spotify.get(
                "spotify_id"
            )

            album = spotify.get(
                "album"
            )

            capa_url = spotify.get(
                "capa_url"
            )

            spotify_url = spotify.get(
                "spotify_url"
            )

        recomendacao_id = criar_recomendacao(
            usuario_id=usuario_id,
            musica=recomendacao.musica,
            artista=recomendacao.artista,
            motivo=recomendacao.motivo,
            spotify_id=spotify_id,
            album=album,
            capa_url=capa_url,
            spotify_url=spotify_url
        )

        ids.append(
            recomendacao_id
        )

        print(
            f"✅ {indice + 1}. "
            f"{recomendacao.musica} - "
            f"{recomendacao.artista}"
        )

    print()
    print(
        "✅ Todas as recomendações foram salvas!"
    )
    print()

    return ids


def buscar_recomendacoes_usuario(usuario_id):

    return listar_recomendacoes_por_usuario(
        usuario_id
    )