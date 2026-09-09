from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    session,
    url_for
)

from app.models.music_profile import (
    buscar_perfil_por_usuario
)

from app.services.recommendation import (
    buscar_recomendacoes_usuario,
    gerar_recomendacoes_usuario
)

from app.services.ai_agent import (
    GeminiRateLimitError,
    GeminiTemporaryError
)


recommendations_bp = Blueprint(
    "recommendations",
    __name__
)


@recommendations_bp.route(
    "/recommendations"
)
def recommendations():

    if "usuario_id" not in session:

        return redirect(
            url_for("auth.login")
        )

    usuario_id = session["usuario_id"]

    perfil = buscar_perfil_por_usuario(
        usuario_id
    )

    if not perfil:

        return redirect(
            url_for("profile.onboarding")
        )

    recomendacoes = buscar_recomendacoes_usuario(
        usuario_id
    )

    return render_template(
        "dashboard.html",
        usuario_nome=session["usuario_nome"],
        perfil=perfil,
        recomendacoes=recomendacoes
    )


@recommendations_bp.route(
    "/recommendations/generate"
)
def generate_recommendations():

    if "usuario_id" not in session:

        return redirect(
            url_for("auth.login")
        )

    usuario_id = session["usuario_id"]

    try:

        print()
        print("==============================")
        print("GERANDO NOVAS RECOMENDAÇÕES")
        print("==============================")
        print()

        ids = gerar_recomendacoes_usuario(
            usuario_id
        )

        print(
            "✅ Novas recomendações geradas!"
        )

        print(
            "IDs:",
            ids
        )

        print()

        flash(
            "✨ Suas recomendações foram atualizadas!",
            "success"
        )

    except GeminiRateLimitError as error:

        print()
        print(
            "⚠️ LIMITE DO GEMINI ATINGIDO"
        )

        print(
            error
        )

        print()

        flash(
            "⏳ O limite do Gemini foi atingido "
            "temporariamente. Tente novamente "
            "em alguns instantes.",
            "rate_limit"
        )

    except GeminiTemporaryError as error:

        print()
        print(
            "⚠️ GEMINI TEMPORARIAMENTE INDISPONÍVEL"
        )

        print(
            error
        )

        print()

        flash(
            "🤖 A IA está temporariamente "
            "indisponível. Tente novamente "
            "em alguns instantes.",
            "temporary"
        )

    except Exception as error:

        print()
        print(
            "❌ ERRO AO GERAR RECOMENDAÇÕES"
        )

        print(
            type(error).__name__
        )

        print(
            error
        )

        print()

        flash(
            "Não foi possível gerar novas "
            "recomendações.",
            "error"
        )

    return redirect(
        url_for(
            "recommendations.recommendations"
        )
    )