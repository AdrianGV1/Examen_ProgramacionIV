from logging.config import fileConfig
from pathlib import Path

from alembic import context
from flask import current_app, Flask

from app import create_app
from app.extensions import db


config = context.config

if config.config_file_name is not None and Path(config.config_file_name).exists():
	fileConfig(config.config_file_name)

app = create_app()

target_metadata = db.metadata


def run_migrations_offline() -> None:
	"""Run migrations in 'offline' mode."""
	with app.app_context():
		url = app.config.get("SQLALCHEMY_DATABASE_URI")
		context.configure(
			url=url,
			target_metadata=target_metadata,
			literal_binds=True,
			dialect_opts={"paramstyle": "named"},
			compare_type=True,
		)

		with context.begin_transaction():
			context.run_migrations()


def run_migrations_online() -> None:
	"""Run migrations in 'online' mode."""
	with app.app_context():
		connectable = db.engine

		with connectable.connect() as connection:
			context.configure(
				connection=connection,
				target_metadata=target_metadata,
				compare_type=True,
			)

			with context.begin_transaction():
				context.run_migrations()


if context.is_offline_mode():
	run_migrations_offline()
else:
	run_migrations_online()
