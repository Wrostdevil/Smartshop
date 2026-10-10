from logging.config import fileConfig
import os
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Prefer the single source of truth in app.config (DATABASE_URL),
# fall back to the legacy POSTGRES_* interpolation in alembic.ini.
try:
    from app.config import DATABASE_URL

    config.set_main_option("sqlalchemy.url", DATABASE_URL)
except Exception:
    section = config.config_ini_section
    config.set_section_option(section, "POSTGRES_USER", os.environ.get("POSTGRES_USER", "shopsmart"))
    config.set_section_option(section, "POSTGRES_PASSWORD", os.environ.get("POSTGRES_PASSWORD", "shopsmart"))
    config.set_section_option(section, "POSTGRES_DB", os.environ.get("POSTGRES_DB", "shopsmart"))
    config.set_section_option(section, "POSTGRES_HOST", os.environ.get("POSTGRES_HOST", "localhost"))

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata MUST be a MetaData object (was a plain list before — broken).
from app.db import Base
import app.models.sqlalchemy  # noqa: F401 — register all models

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
