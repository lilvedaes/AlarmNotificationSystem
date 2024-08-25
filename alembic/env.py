from logging.config import fileConfig
from sqlalchemy import create_engine, MetaData
from alembic import context
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Interpret the config file for Python logging.
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Database configuration
db_user = os.getenv("POSTGRES_USER")
db_pass = os.getenv("POSTGRES_PASSWORD")
db_host = os.getenv("POSTGRES_HOST")
db_port = os.getenv("POSTGRES_PORT")
db_name = os.getenv("POSTGRES_DB")

# Check if any of the required variables are missing
if not all([db_user, db_pass, db_host, db_port, db_name]):
    raise ValueError("Missing one or more environment variables")

# Construct the database URL
url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
config.set_main_option('sqlalchemy.url', url)

# Import your models to get the MetaData object
from app.models import Base  # Adjust import based on your actual structure

# Set the target metadata for Alembic
target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = create_engine(config.get_main_option("sqlalchemy.url"))

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
