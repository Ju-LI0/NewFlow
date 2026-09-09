from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
    url_for
)

from app.models.user import (
    buscar_usuario_por_email,
    criar_usuario,
    verificar_senha
)

from app.models.music_profile import (
    buscar_perfil_por_usuario
)


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        senha = request.form.get(
            "senha",
            ""
        )

        if not email or not senha:

            return render_template(
                "login.html",
                erro="Preencha o e-mail e a senha."
            )

        usuario = buscar_usuario_por_email(email)

        if not usuario:

            return render_template(
                "login.html",
                erro="E-mail ou senha incorretos."
            )

        senha_hash = usuario[3]

        if not verificar_senha(
            senha,
            senha_hash
        ):

            return render_template(
                "login.html",
                erro="E-mail ou senha incorretos."
            )

        session["usuario_id"] = usuario[0]
        session["usuario_nome"] = usuario[1]
        session["usuario_email"] = usuario[2]

        perfil = buscar_perfil_por_usuario(
            usuario[0]
        )

        if perfil:

            return redirect(
                url_for(
                    "recommendations.recommendations"
                )
            )

        return redirect(
            url_for("profile.onboarding")
        )

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        nome = request.form.get(
            "nome",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        senha = request.form.get(
            "senha",
            ""
        )

        if not nome or not email or not senha:

            return render_template(
                "register.html",
                erro="Preencha todos os campos."
            )

        if len(senha) < 6:

            return render_template(
                "register.html",
                erro="A senha deve ter pelo menos 6 caracteres."
            )

        usuario_existente = buscar_usuario_por_email(
            email
        )

        if usuario_existente:

            return render_template(
                "register.html",
                erro="Este e-mail já está cadastrado."
            )

        try:

            criar_usuario(
                nome,
                email,
                senha
            )

            return redirect(
                url_for("auth.login")
            )

        except Exception as error:

            print(
                f"Erro ao criar usuário: {error}"
            )

            return render_template(
                "register.html",
                erro="Não foi possível criar sua conta."
            )

    return render_template("register.html")


@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("auth.login")
    )