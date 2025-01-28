#!/usr/bin/env bash

set -e

echo "Waiting for postgres..."

while ! nc -z "$DB__HOST" "$DB__PORT"; do
  sleep 0.1
done

echo "PostgreSQL started"

export PYTHONPATH=/opt/src
alembic upgrade head

exec "$@"
