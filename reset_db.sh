#!/usr/bin/env bash

set -e

DB_NAME="module_certificator_db"
DB_USER="module_certificator_user"
DB_CONTAINER="module_certificator_postgres"

echo "Drop database..."

docker exec "$DB_CONTAINER" \
  dropdb \
  -U "$DB_USER" \
  --if-exists \
  "$DB_NAME"

echo "Create database..."

docker exec "$DB_CONTAINER" \
  createdb \
  -U "$DB_USER" \
  -O "$DB_USER" \
  "$DB_NAME"

echo "Run Alembic migrations..."

alembic upgrade head

echo "Load seed data..."

docker exec -i "$DB_CONTAINER" \
  psql \
  -U "$DB_USER" \
  -d "$DB_NAME" \
  < db/sql/seed.sql

echo "Database reset complete."