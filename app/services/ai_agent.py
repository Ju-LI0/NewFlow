import os
import time

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field


load_dotenv()


GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)


if not GEMINI_API_KEY:

    raise RuntimeError(
        "GEMINI_API_KEY não foi configurada "
        "no arquivo .env"
    )


client = genai.Client(
    api_key=GEMINI_API_KEY
)


MODEL_NAME = "gemini-3.7-flash"


# ==================================================
# CONFIGURAÇÕES DE RETENTATIVA
# ==================================================

MAX_TENTATIVAS = 3

TEMPOS_ESPERA = [
    2,
    5,
    10
]


# ==================================================
# EXCEÇÕES PERSONALIZADAS
# ==================================================

class GeminiRateLimitError(Exception):

    """
    Exceção utilizada quando o Gemini retorna
    erro de limite/quota.
    """

    pass


class GeminiTemporaryError(Exception):

    """
    Exceção utilizada quando o Gemini apresenta
    um erro temporário de servidor.
    """

    pass


# ==================================================
# MODELOS DE RESPOSTA
# ==================================================

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
        description="Lista de músicas recomendadas."
    )


# ==================================================
# VERIFICAÇÃO DE ERROS
# ==================================================

def _verificar_erro_rate_limit(error):

    mensagem = str(error).lower()

    return (
        "429" in mensagem
        or "rate limit" in mensagem
        or "quota exceeded" in mensagem
        or "too many requests" in mensagem
        or "resource_exhausted" in mensagem
    )


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
    )


# ==================================================
# FUNÇÃO PRINCIPAL DO GEMINI
# ==================================================

def _executar_interacao(
    prompt,
    response_format=None
):

    ultima_excecao = None

    for tentativa in range(
        MAX_TENTATIVAS
    ):

        try:

            print()
            print(
                f"🤖 Gemini - tentativa "
                f"{tentativa + 1}/{MAX_TENTATIVAS}"
            )

            argumentos = {
                "model": MODEL_NAME,
                "input": prompt
            }

            if response_format:

                argumentos[
                    "response_format"
                ] = response_format

            interaction = (
                client.interactions.create(
                    **argumentos
                )
            )

            print(
                "✅ Gemini respondeu com sucesso."
            )

            return interaction

        except Exception as error:

            ultima_excecao = error

            # ------------------------------------------
            # LIMITE / QUOTA
            # ------------------------------------------

            if _verificar_erro_rate_limit(
                error
            ):

                print()
                print(
                    "⚠️ Limite/quota do Gemini atingido."
                )

                raise GeminiRateLimitError(
                    "O limite de requisições do Gemini "
                    "foi atingido temporariamente."
                ) from error

            # ------------------------------------------
            # ERRO TEMPORÁRIO
            # ------------------------------------------

            if _verificar_erro_temporario(
                error
            ):

                if tentativa >= (
                    MAX_TENTATIVAS - 1
                ):

                    print()
                    print(
                        "❌ Gemini continua indisponível "
                        "após as tentativas."
                    )

                    raise GeminiTemporaryError(
                        "O Gemini está temporariamente "
                        "indisponível. Tente novamente "
                        "em alguns instantes."
                    ) from error

                tempo_espera = TEMPOS_ESPERA[
                    tentativa
                ]

                print()
                print(
                    "⚠️ Gemini está temporariamente "
                    "indisponível."
                )

                print(
                    f"⏳ Aguardando "
                    f"{tempo_espera} segundos "
                    f"antes de tentar novamente..."
                )

                time.sleep(
                    tempo_espera
                )

                continue

            # ------------------------------------------
            # ERRO DESCONHECIDO
            # ------------------------------------------

            raise

    raise GeminiTemporaryError(
        "Não foi possível obter resposta do Gemini."
    ) from ultima_excecao


# ==================================================
# PERGUNTA SIMPLES AO GEMINI
# ==================================================

def perguntar_gemini(
    pergunta
):

    interaction = _executar_interacao(
        prompt=pergunta
    )

    return interaction.output_text


# ==================================================
# GERAÇÃO DE RECOMENDAÇÕES
# ==================================================

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

6. Responda somente no formato estruturado
   solicitado.
"""

    response_format = {
        "type": "text",
        "mime_type": "application/json",
        "schema": (
            ListaRecomendacoes
            .model_json_schema()
        )
    }

    interaction = _executar_interacao(
        prompt=prompt,
        response_format=response_format
    )

    # ==================================================
    # VALIDAÇÃO DA RESPOSTA
    # ==================================================

    resultado = (
        ListaRecomendacoes
        .model_validate_json(
            interaction.output_text
        )
    )

    if not resultado.recomendacoes:

        raise ValueError(
            "O Gemini não retornou nenhuma "
            "recomendação."
        )

    if len(
        resultado.recomendacoes
    ) != 5:

        raise ValueError(
            "O Gemini não retornou exatamente "
            "5 recomendações."
        )

    return resultado.recomendacoes