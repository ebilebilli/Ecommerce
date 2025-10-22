from sqlalchemy import create_engine, pool
from alembic import context
import os

url = os.getenv("DATABASE_URL") or context.config.get_main_option("sqlalchemy.url")
connectable = create_engine(url, poolclass=pool.NullPool)

def run_migrations_online():
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=None)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    # offline migrations
    url = os.getenv("DATABASE_URL") or context.config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=None,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    run_migrations_online()
