#!/bin/sh

if [ "$DB_ENGINE" = "django.db.backends.postgresql" ]
then
    echo "Waiting for PostgreSQL..."

    while ! nc -z $DB_HOST $DB_PORT; do
        sleep 0.1
    done

    echo "PostgreSQL started"
fi

echo "Waiting for elastic..."
while ! nc -z $ELASTIC_ADDRESS; do
    sleep 0.1
done
echo "Elastic started"

exec "$@"
