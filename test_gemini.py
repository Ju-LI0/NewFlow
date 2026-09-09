import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


api_key = os.getenv("GEMINI_API_KEY")


print("================================")
print("TESTE DO GEMINI - NEWFLOW")
print("================================")


if not api_key:

    print("❌ GEMINI_API_KEY não encontrada.")
    print("Verifique o arquivo .env.")

    raise SystemExit


print("✅ GEMINI_API_KEY encontrada.")
print(f"Chave iniciada com: {api_key[:8]}...")


try:

    client = genai.Client(
        api_key=api_key
    )

    print("✅ Cliente Gemini criado.")
    print("📡 Enviando pergunta para o Gemini...")


    interaction = client.interactions.create(

        model="gemini-3.8-flash",

        input=(
            "Você é o agente musical do NewFlow. "
            "Recomende 3 músicas para uma pessoa que "
            "gosta de Rock, Rap e Pop. "
            "Responda em português."
        )
    )


    print()
    print("================================")
    print("🤖 RESPOSTA DO GEMINI")
    print("================================")
    print()

    print(
        interaction.output_text
    )


except Exception as error:

    print()
    print("================================")
    print("❌ ERRO AO CONECTAR COM O GEMINI")
    print("================================")
    print()

    print(
        type(error).__name__
    )

    print()

    print(
        str(error)
    )