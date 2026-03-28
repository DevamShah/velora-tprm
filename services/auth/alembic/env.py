"""
Alembic env.py for auth-service.
Schema: auth_svc
"""

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool, text

# ---------------------------------------------------------------------------
# Per-service configuration
# ---------------------------------------------------------------------------
SERVICE_SCHEMA = "auth_svc"

# Import auth service models when available
# from auth_service.models import Base
# target_metadata = Base.metadata
target_metadata = None  # Replace with auth service Base.metadata

# ---------------------------------------------------------------------------
# Alembic Config object
# ---------------------------------------------------------------------------
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override sqlalchemy.url from environment if available
db_url = os.environ.get("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)


def include_name(name, type_, parent_names):
    """Only include objects belonging to auth_svc schema."""
    if type_ == "schema":
        return name == SERVICE_SCHEMA
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        include_name=include_name,
        version_table_schema=SERVICE_SCHEMA,
    )
    with context.begin_transaction():
        context.execute(f"SET search_path TO {SERVICE_SCHEMA}")
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        connection.execute(text(f"SET search_path TO {SERVICE_SCHEMA}"))
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            include_name=include_name,
            version_table_schema=SERVICE_SCHEMA,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
