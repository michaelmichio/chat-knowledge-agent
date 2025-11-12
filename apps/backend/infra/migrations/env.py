import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# --- PATH FIX: pastikan Alembic tahu lokasi backend
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../apps/backend"))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# --- IMPORT SETUP
from core.config import get_settings
from infra.db.base import Base
from domain.documents.models import Document  # ⬅️ import langsung model

# --- Alembic config
config = context.config
fileConfig(config.config_file_name)

settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

target_metadata = Base.metadata

print("🔍 DEBUG target_metadata:", target_metadata.tables.keys())  # ⬅️ tampilkan di log

def run_migrations_offline():
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        print("🔍 DEBUG Alembic sees tables:", target_metadata.tables.keys())  # ⬅️ tampilkan di log

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
