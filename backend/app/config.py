import os
from dotenv import load_dotenv

load_dotenv()

# --- Postgres is the primary database. ---
# Priority: DATABASE_URL > POSTGRES_* parts (+ defaults) > SQLITE_URL fallback.
# The SQLite fallback keeps `pytest` and zero-setup local runs working;
# docker compose and production always use Postgres.
PG_DEFAULTS = {
    "username": "shopsmart",
    "password": "shopsmart",
    "host": "localhost",
    "port": "5432",
    "database": "shopsmart",
}

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    pg_user = os.getenv("POSTGRES_USER", PG_DEFAULTS["username"])
    pg_pass = os.getenv("POSTGRES_PASSWORD", PG_DEFAULTS["password"])
    pg_host = os.getenv("POSTGRES_HOST", PG_DEFAULTS["host"])
    pg_port = os.getenv("POSTGRES_PORT", PG_DEFAULTS["port"])
    pg_db = os.getenv("POSTGRES_DB", PG_DEFAULTS["database"])
    pg_url = f"postgresql+psycopg2://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
    # Explicit opt-out for environments without Postgres (CI quick runs):
    #   SQLITE_URL=sqlite:///./shopsmart.db
    if os.getenv("SQLITE_URL"):
        DATABASE_URL = os.getenv("SQLITE_URL")
    else:
        DATABASE_URL = pg_url

DATABASE = {
    "dialect": "postgresql",
    "driver": "psycopg2",
    "username": os.getenv("POSTGRES_USER", PG_DEFAULTS["username"]),
    "password": os.getenv("POSTGRES_PASSWORD", PG_DEFAULTS["password"]),
    "host": os.getenv("POSTGRES_HOST", PG_DEFAULTS["host"]),
    "port": os.getenv("POSTGRES_PORT", PG_DEFAULTS["port"]),
    "database": os.getenv("POSTGRES_DB", PG_DEFAULTS["database"]),
    "url": DATABASE_URL,
}

IS_SQLITE = DATABASE_URL.startswith("sqlite")
