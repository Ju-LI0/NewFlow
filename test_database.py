from app.database import get_connection


try:
    connection = get_connection()

    print("✅ Conexão com o PostgreSQL realizada com sucesso!")

    connection.close()

except Exception as error:
    print("❌ Erro ao conectar com o PostgreSQL:")
    print(error)