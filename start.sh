#!/bin/bash

until PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_URL -U $POSTGRES_USER -d $POSTGRES_DB -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

flask initdb
flask run --host 0.0.0.0
