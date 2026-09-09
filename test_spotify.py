from app.services.music_service import buscar_musica


def main():

    print()
    print("==============================")
    print("TESTE DE BUSCA - SPOTIFY")
    print("==============================")
    print()

    resultado = buscar_musica(
        musica="Blinding Lights",
        artista="The Weeknd"
    )

    if not resultado:

        print("❌ Música não encontrada.")

        return

    print("✅ Música encontrada!")
    print()

    print("Spotify ID:")
    print(resultado["spotify_id"])

    print()

    print("Música:")
    print(resultado["musica"])

    print()

    print("Artista:")
    print(resultado["artista"])

    print()

    print("Álbum:")
    print(resultado["album"])

    print()

    print("Capa:")
    print(resultado["capa_url"])

    print()

    print("Link Spotify:")
    print(resultado["spotify_url"])

    print()


if __name__ == "__main__":

    main()