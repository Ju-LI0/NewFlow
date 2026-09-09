from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
    url_for
)

from app.models.music_profile import (
    buscar_perfil_por_usuario,
    criar_ou_atualizar_perfil
)


profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile")
def profile():

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    perfil = buscar_perfil_por_usuario(
        session["usuario_id"]
    )

    if not perfil:
        return redirect(url_for("profile.onboarding"))

    return render_template(
        "profile.html",
        usuario_nome=session["usuario_nome"],
        usuario_email=session["usuario_email"],
        perfil=perfil
    )


@profile_bp.route("/onboarding", methods=["GET", "POST"])
def onboarding():

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    if request.method == "POST":

        generos = request.form.get(
            "generos",
            ""
        ).strip()

        artistas = request.form.get(
            "artistas",
            ""
        ).strip()

        musicas_favoritas = request.form.get(
            "musicas_favoritas",
            ""
        ).strip()

        humor_preferido = request.form.get(
            "humor_preferido",
            ""
        ).strip()

        decadas_preferidas = request.form.get(
            "decadas_preferidas",
            ""
        ).strip()

        if not generos:
            return render_template(
                "onboarding.html",
                erro="Informe pelo menos um gênero musical."
            )

        try:

            criar_ou_atualizar_perfil(
                usuario_id=session["usuario_id"],
                generos=generos,
                artistas=artistas,
                musicas_favoritas=musicas_favoritas,
                humor_preferido=humor_preferido,
                decadas_preferidas=decadas_preferidas
            )

            return redirect(
                url_for("profile.profile")
            )

        except Exception as error:

            print(
                f"Erro ao salvar perfil musical: {error}"
            )

            return render_template(
                "onboarding.html",
                erro="Não foi possível salvar seu perfil."
            )

    perfil = buscar_perfil_por_usuario(
        session["usuario_id"]
    )

    return render_template(
        "onboarding.html",
        perfil=perfil
    )