import os

from dotenv import load_dotenv
from flask import Flask, render_template

from app.routes.auth import auth_bp
from app.routes.profile import profile_bp
from app.routes.recommendations import recommendations_bp
from app.routes.chat import chat_bp


load_dotenv()


def create_app():

    base_dir = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )

    template_dir = os.path.join(
        base_dir,
        "templates"
    )

    static_dir = os.path.join(
        base_dir,
        "static"
    )

    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir
    )

    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY",
        "chave-desenvolvimento-newflow"
    )

    # ==================================================
    # PÁGINA INICIAL
    # ==================================================

    @app.route("/")
    def home():

        return render_template(
            "index.html"
        )

    # ==================================================
    # BLUEPRINTS
    # ==================================================

    app.register_blueprint(
        auth_bp
    )

    app.register_blueprint(
        profile_bp
    )

    app.register_blueprint(
        recommendations_bp
    )

    app.register_blueprint(
        chat_bp
    )

    return app