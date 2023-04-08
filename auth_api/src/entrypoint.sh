#!/bin/sh

wait_for_postgres() {
  echo "Waiting for PostgreSQL to be ready..."
  while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
    sleep 1
  done
  echo "PostgreSQL is ready."
}

# Wait for PostgreSQL service
wait_for_postgres

flask db upgrade
python manage.py runserver
