from app.models.user import criar_usuario, buscar_usuario_por_email


nome = "Júlio"
email = "julio@newflow.com"
senha = "SenhaTeste123"


try:
    usuario_id = criar_usuario(
        nome,
        email,
        senha
    )

    print(f"✅ Usuário criado com sucesso! ID: {usuario_id}")

    usuario = buscar_usuario_por_email(email)

    if usuario:
        print("✅ Usuário encontrado no PostgreSQL!")
        print(f"ID: {usuario[0]}")
        print(f"Nome: {usuario[1]}")
        print(f"E-mail: {usuario[2]}")
        print(f"Hash da senha: {usuario[3]}")

except Exception as error:
    print("❌ Erro ao trabalhar com usuário:")
    print(error)