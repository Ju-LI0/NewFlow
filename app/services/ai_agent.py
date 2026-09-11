import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field


load_dotenv()


# ============================================================
# CONFIGURAÇÃO
# ============================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)


if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY não foi configurada "
        "no arquivo .env"
    )


# ============================================================
# CLIENTE GEMINI
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options=types.HttpOptions(
        api_version="v1",
        timeout=8000,
        retry_options=types.HttpRetryOptions(
            attempts=1
        )
    )
)


# ============================================================
# MODELOS GEMINI
# ============================================================

MODELO_PRINCIPAL = "gemini-3.8-flash"

MODELO_FALLBACK_1 = "gemini-3.7-flash"

MODELO_FALLBACK_2 = "gemini-3.6-flash"


# ============================================================
# EXCEÇÕES
# ============================================================

class GeminiRateLimitError(Exception):
    pass


class GeminiTemporaryError(Exception):
    pass


# ============================================================
# ESTRUTURA DAS RECOMENDAÇÕES
# ============================================================

class Recomendacao(BaseModel):

    musica: str = Field(
        description="Nome da música recomendada."
    )

    artista: str = Field(
        description="Nome do artista da música."
    )

    motivo: str = Field(
        description=(
            "Explicação curta de por que "
            "a música combina com o usuário."
        )
    )


class ListaRecomendacoes(BaseModel):

    recomendacoes: list[Recomendacao] = Field(
        description=(
            "Lista contendo exatamente "
            "5 músicas recomendadas."
        )
    )


# ============================================================
# VERIFICAÇÃO DE RATE LIMIT
# ============================================================

def _verificar_erro_rate_limit(error):

    mensagem = str(error).lower()

    return (
        "429" in mensagem
        or "rate limit" in mensagem
        or "quota exceeded" in mensagem
        or "too many requests" in mensagem
        or "resource_exhausted" in mensagem
    )


# ============================================================
# VERIFICAÇÃO DE ERRO TEMPORÁRIO
# ============================================================

def _verificar_erro_temporario(error):

    mensagem = str(error).lower()

    return (
        "500" in mensagem
        or "internal server error" in mensagem
        or "api_error" in mensagem
        or "503" in mensagem
        or "service unavailable" in mensagem
        or "high demand" in mensagem
        or "temporarily unavailable" in mensagem
        or "timeout" in mensagem
        or "timed out" in mensagem
        or "readtimeout" in mensagem
    )


# ============================================================
# CHAMADA À INTERACTIONS API
# ============================================================

def _chamar_modelo(
    modelo,
    prompt,
    resposta_estruturada=False
):

    print()
    print("==============================")
    print("CHAMADA AO GEMINI")
    print("==============================")
    print(
        f"Modelo: {modelo}"
    )
    print(
        "API: Interactions API"
    )
    print()

    argumentos = {
        "model": modelo,
        "input": prompt
    }

    # --------------------------------------------------------
    # SAÍDA ESTRUTURADA
    # --------------------------------------------------------

    if resposta_estruturada:

        argumentos["response_format"] = {
            "type": "text",
            "mime_type": "application/json",
            "schema": (
                ListaRecomendacoes
                .model_json_schema()
            )
        }

    interaction = client.interactions.create(
        **argumentos
    )

    if not interaction:

        raise GeminiTemporaryError(
            "O Gemini não retornou uma interação."
        )

    if not interaction.output_text:

        raise GeminiTemporaryError(
            "O Gemini retornou uma resposta vazia."
        )

    print()
    print(
        "✅ Gemini respondeu com sucesso."
    )
    print(
        f"Modelo utilizado: {modelo}"
    )
    print()

    return interaction


# ============================================================
# EXECUTA GEMINI COM FALLBACK
# ============================================================

def _executar_interacao(
    prompt,
    resposta_estruturada=False
):

    modelos = [
        MODELO_PRINCIPAL,
        MODELO_FALLBACK_1,
        MODELO_FALLBACK_2
    ]

    ultimo_erro = None

    for indice, modelo in enumerate(modelos):

        try:

            response = _chamar_modelo(
                modelo=modelo,
                prompt=prompt,
                resposta_estruturada=(
                    resposta_estruturada
                )
            )

            return response

        except Exception as error:

            ultimo_erro = error

            print()
            print("==============================")
            print("ERRO NO GEMINI")
            print("==============================")
            print(
                f"Modelo: {modelo}"
            )
            print(
                f"Tipo: {type(error).__name__}"
            )
            print(
                f"Mensagem: {str(error)}"
            )
            print()

            # ------------------------------------------------
            # RATE LIMIT
            # ------------------------------------------------

            if _verificar_erro_rate_limit(error):

                print(
                    "⚠️ Limite/quota do Gemini atingido."
                )

                if indice < len(modelos) - 1:

                    print(
                        "➡️ Tentando próximo modelo..."
                    )

                    continue

                raise GeminiRateLimitError(
                    "O limite ou quota do Gemini "
                    "foi atingido temporariamente."
                ) from error

            # ------------------------------------------------
            # ERROS TEMPORÁRIOS
            # ------------------------------------------------

            if _verificar_erro_temporario(error):

                print(
                    "⚠️ Gemini temporariamente "
                    "indisponível."
                )

                if indice < len(modelos) - 1:

                    print(
                        "➡️ Tentando próximo modelo..."
                    )

                    continue

                raise GeminiTemporaryError(
                    "Os modelos do Gemini estão "
                    "temporariamente indisponíveis. "
                    "Tente novamente em alguns instantes."
                ) from error

            # ------------------------------------------------
            # ERRO NÃO RECUPERÁVEL
            # ------------------------------------------------

            raise

    raise GeminiTemporaryError(
        "Não foi possível obter resposta "
        "do Gemini."
    ) from ultimo_erro


# ============================================================
# PERGUNTA NORMAL AO GEMINI
# ============================================================

def perguntar_gemini(pergunta):

    interaction = _executar_interacao(
        prompt=pergunta
    )

    return interaction.output_text


# ============================================================
# GERAR RECOMENDAÇÕES MUSICAIS
# ============================================================

def gerar_recomendacoes(
    generos,
    artistas,
    musicas_favoritas,
    humor_preferido,
    decadas_preferidas
):

    prompt = f"""
Você é o agente musical do NewFlow.

Sua função é recomendar músicas personalizadas
com base no perfil musical do usuário.

PERFIL DO USUÁRIO

Gêneros favoritos:
{generos or "Não informado"}

Artistas favoritos:
{artistas or "Não informado"}

Músicas favoritas:
{musicas_favoritas or "Não informado"}

Humor musical:
{humor_preferido or "Não informado"}

Décadas favoritas:
{decadas_preferidas or "Não informado"}


REGRAS

1. Recomende exatamente 5 músicas.

2. Priorize músicas relacionadas aos gêneros,
   artistas e músicas informados pelo usuário.

3. Procure também apresentar algumas
   descobertas que o usuário provavelmente
   ainda não conhece.

4. Não recomende músicas que estejam
   explicitamente nas músicas favoritas.

5. Explique de forma curta e natural
   por que cada música combina com o usuário.

6. Cada recomendação deve conter:

   - musica
   - artista
   - motivo

7. Mantenha cada motivo curto,
   preferencialmente em uma ou duas frases.

8. Não adicione informações extras
   fora das recomendações.

9. Retorne exatamente 5 recomendações.
"""

    interaction = _executar_interacao(
        prompt=prompt,
        resposta_estruturada=True
    )

    # ========================================================
    # VALIDAR JSON
    # ========================================================

    try:

        resultado = (
            ListaRecomendacoes
            .model_validate_json(
                interaction.output_text
            )
        )

    except Exception as error:

        print()
        print("==============================")
        print("ERRO AO VALIDAR RESPOSTA")
        print("==============================")
        print(
            f"Tipo: {type(error).__name__}"
        )
        print(
            f"Erro: {str(error)}"
        )
        print()
        print(
            "Resposta recebida:"
        )
        print(
            interaction.output_text
        )
        print()

        raise GeminiTemporaryError(
            "O Gemini retornou uma resposta "
            "incompleta ou inválida. "
            "Tente gerar novamente."
        ) from error

    # ========================================================
    # VALIDAR QUANTIDADE
    # ========================================================

    if not resultado.recomendacoes:

        raise ValueError(
            "O Gemini não retornou nenhuma "
            "recomendação."
        )

    if len(resultado.recomendacoes) != 5:

        raise ValueError(
            "O Gemini não retornou exatamente "
            "5 recomendações."
        )

    # ========================================================
    # SUCESSO
    # ========================================================

    print()
    print(
        "✅ Gemini retornou 5 recomendações."
    )
    print()

    for indice, recomendacao in enumerate(
        resultado.recomendacoes,
        start=1
    ):

        print(
            f"{indice}. "
            f"{recomendacao.musica} - "
            f"{recomendacao.artista}"
        )

    print()

    return resultado.recomendacoes