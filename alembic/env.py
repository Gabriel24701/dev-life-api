import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Garante a raiz do projeto no sys.path independente do cwd de onde o
# comando `alembic` for chamado. O projeto e "flat" (sem pacote `app/`),
# rodando como `uvicorn main:app` a partir da raiz do repo.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import Base, SQLALCHEMY_DATABASE_URL  # noqa: E402
import models.models  # noqa: E402,F401  (registra as tabelas em Base.metadata)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Reaproveita a mesma resolucao de DATABASE_URL usada pela aplicacao (fallback
# SQLite local + reescrita postgres:// -> postgresql://) em vez de duplicar
# essa logica ou hardcodear a URL no alembic.ini.
#
# "%" e escapado como "%%" porque o ConfigParser interno do Alembic trata "%"
# como sintaxe de interpolacao (%(name)s) — sem isso, uma senha com caractere
# URL-encoded (ex.: "%40" pra "@") quebra o set_main_option.
config.set_main_option(
    "sqlalchemy.url", SQLALCHEMY_DATABASE_URL.replace("%", "%%")
)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
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
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
