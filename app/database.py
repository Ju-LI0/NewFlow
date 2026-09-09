import os

import psycopg
from dotenv import load_dotenv


load_dotenv()


def get_connection():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL não foi configurada no arquivo .env"
        )

    return psycopg.connect(database_url)