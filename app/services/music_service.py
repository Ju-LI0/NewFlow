import base64
import os
import time

import requests

from dotenv import load_dotenv


load_dotenv()


SPOTIFY_CLIENT_ID = os.getenv(
    "SPOTIFY_CLIENT_ID"
)

SPOTIFY_CLIENT_SECRET = os.getenv(
    "SPOTIFY_CLIENT_SECRET"
)


TOKEN_URL = (
    "https://accounts.spotify.com/api/token"
)

API_URL = (
    "https://api.spotify.com/v1"
)


_access_token = None
_token_expires_at = 0


def obter_token():

    global _access_token
    global _token_expires_at

    # --------------------------------------------------
    # REUTILIZA O TOKEN ENQUANTO ELE ESTIVER VÁLIDO
    # --------------------------------------------------

    if (
        _access_token
        and time.time() < _token_expires_at
    ):
        return _access_token

    if not SPOTIFY_CLIENT_ID:

        raise RuntimeError(
            "SPOTIFY_CLIENT_ID não foi configurado "
            "no arquivo .env"
        )

    if not SPOTIFY_CLIENT_SECRET:

        raise RuntimeError(
            "SPOTIFY_CLIENT_SECRET não foi configurado "
            "no arquivo .env"
        )

    # --------------------------------------------------
    # CRIA AUTORIZAÇÃO BASIC
    # --------------------------------------------------

    credenciais = (
        f"{SPOTIFY_CLIENT_ID}:"
        f"{SPOTIFY_CLIENT_SECRET}"
    )

    credenciais_base64 = base64.b64encode(
        credenciais.encode("utf-8")
    ).decode("utf-8")

    headers = {
        "Authorization": (
            f"Basic {credenciais_base64}"
        ),
        "Content-Type": (
            "application/x-www-form-urlencoded"
        )
    }

    data = {
        "grant_type": "client_credentials"
    }

    # --------------------------------------------------
    # SOLICITA TOKEN
    # --------------------------------------------------

    response = requests.post(
        TOKEN_URL,
        headers=headers,
        data=data,
        timeout=10
    )

    # --------------------------------------------------
    # DIAGNÓSTICO DE ERRO DE AUTENTICAÇÃO
    # --------------------------------------------------

    if response.status_code != 200:

        print()
        print("==============================")
        print("ERRO DE AUTENTICAÇÃO SPOTIFY")
        print("==============================")
        print(
            "Status:",
            response.status_code
        )
        print(
            "Resposta:",
            response.text
        )
        print()

        raise RuntimeError(
            "Não foi possível autenticar "
            "com o Spotify."
        )

    dados = response.json()

    _access_token = dados["access_token"]

    expires_in = dados.get(
        "expires_in",
        3600
    )

    # Deixamos uma margem de segurança
    _token_expires_at = (
        time.time()
        + expires_in
        - 60
    )

    return _access_token


def buscar_musica(
    musica,
    artista
):

    token = obter_token()

    # --------------------------------------------------
    # MONTA A PESQUISA
    # --------------------------------------------------

    query = (
        f"track:{musica} "
        f"artist:{artista}"
    )

    headers = {
        "Authorization": (
            f"Bearer {token}"
        )
    }

    params = {
        "q": query,
        "type": "track",
        "market": "BR",
        "limit": 1
    }

    # --------------------------------------------------
    # PESQUISA NO SPOTIFY
    # --------------------------------------------------

    response = requests.get(
        f"{API_URL}/search",
        headers=headers,
        params=params,
        timeout=10
    )

    # --------------------------------------------------
    # DIAGNÓSTICO DE ERRO DE BUSCA
    # --------------------------------------------------

    if response.status_code != 200:

        print()
        print("==============================")
        print("ERRO DE BUSCA SPOTIFY")
        print("==============================")
        print(
            "Status:",
            response.status_code
        )
        print(
            "Resposta:",
            response.text
        )
        print()

        raise RuntimeError(
            "Não foi possível pesquisar "
            "a música no Spotify."
        )

    dados = response.json()

    # --------------------------------------------------
    # OBTÉM AS FAIXAS
    # --------------------------------------------------

    tracks = (
        dados
        .get("tracks", {})
        .get("items", [])
    )

    if not tracks:

        return None

    track = tracks[0]

    # --------------------------------------------------
    # DADOS DO ÁLBUM
    # --------------------------------------------------

    album = track.get(
        "album",
        {}
    )

    imagens = album.get(
        "images",
        []
    )

    capa = None

    if imagens:

        capa = imagens[0].get(
            "url"
        )

    # --------------------------------------------------
    # DADOS DO ARTISTA
    # --------------------------------------------------

    artistas = track.get(
        "artists",
        []
    )

    nome_artista = artista

    if artistas:

        nome_artista = artistas[0].get(
            "name",
            artista
        )

    # --------------------------------------------------
    # LINK DO SPOTIFY
    # --------------------------------------------------

    external_urls = track.get(
        "external_urls",
        {}
    )

    spotify_url = external_urls.get(
        "spotify"
    )

    # --------------------------------------------------
    # RETORNA OS DADOS
    # --------------------------------------------------

    return {
        "spotify_id": track.get(
            "id"
        ),

        "musica": track.get(
            "name",
            musica
        ),

        "artista": nome_artista,

        "album": album.get(
            "name"
        ),

        "capa_url": capa,

        "spotify_url": spotify_url
    }


def buscar_musicas(
    recomendacoes
):

    resultados = []

    for recomendacao in recomendacoes:

        musica = buscar_musica(
            musica=recomendacao.musica,
            artista=recomendacao.artista
        )

        if musica:

            resultados.append({
                **musica,
                "motivo": recomendacao.motivo
            })

    return resultados