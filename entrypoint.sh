#!/bin/sh

echo "Waiting for database..."

until pg_isready -h db -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB
do
  sleep 2
done

echo "Database ready."

echo "Running migrations..."
alembic upgrade head

#Remove --reload for production, but keep it for development to enable hot-reloading of the FastAPI app.
echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 80 --reload
