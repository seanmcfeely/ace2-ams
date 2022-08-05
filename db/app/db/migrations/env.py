import alembic
import logging
import os
import sys

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool


# When running the "alembic" command to generate migrations, Python's import path does not have
# the folder containing this application code, so it is manually inserted so that imports work.
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
grandparent = os.path.dirname(parent)
sys.path.append(grandparent)

from db.config import get_settings

# Load the database schemas so that Alembic knows what it needs to create/update
from db import schemas
from db.database import Base

# Alembic Config object, which provides access to values within the .ini file
config = alembic.context.config

# Interpret the config file for logging
fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")


def run_migrations_online() -> None:
    """
    Run migrations in "online" mode
    """

    database_url = get_settings().database_url
    connectable = config.attributes.get("connection", None)
    config.set_main_option("sqlalchemy.url", database_url)

    if connectable is None:
        connectable = engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

    with connectable.connect() as connection:
        alembic.context.configure(connection=connection, target_metadata=Base.metadata)

        with alembic.context.begin_transaction():
            alembic.context.run_migrations()


def run_migrations_offline() -> None:
    """
    Run migrations in "offline" mode.
    """

    database_url = get_settings().database_url

    alembic.context.configure(url=database_url)

    with alembic.context.begin_transaction():
        alembic.context.run_migrations()


if alembic.context.is_offline_mode():
    logger.info("Running migrations offline")
    run_migrations_offline()
else:
    logger.info("Running migrations online")
    run_migrations_online()
