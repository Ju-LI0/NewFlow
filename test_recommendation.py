from app.services.recommendation import (
    gerar_recomendacoes_usuario
)


USUARIO_ID = 1


print()
print("==============================")
print("TESTE DE RECOMENDAÇÃO")
print("==============================")
print()


try:

    ids = gerar_recomendacoes_usuario(
        USUARIO_ID
    )

    print(
        "✅ Recomendações geradas!"
    )

    print()

    print(
        "IDs salvos:",
        ids
    )


except Exception as error:

    print(
        "❌ Erro:"
    )

    print(
        type(error).__name__
    )

    print(
        error
    )