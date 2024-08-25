#!/bin/sh

# Wait for PostgreSQL to be ready
until pg_isready -h db -p 5432 -U ${POSTGRES_USER}; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

# Apply migrations
alembic upgrade head

# Keep the container running
exec "$@"
