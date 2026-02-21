#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required to run runtime validation."
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "docker compose is required to run runtime validation."
  exit 1
fi

APP_PORT="${APP_PORT:-8000}"
MAX_WAIT_SECONDS="${MAX_WAIT_SECONDS:-120}"
START_TS="$(date +%s)"

echo "Starting app and database containers..."
docker compose up -d --build db app

echo "Waiting for API docs endpoint on port ${APP_PORT}..."
until curl -fsS "http://127.0.0.1:${APP_PORT}/docs" >/dev/null; do
  if [ $(( "$(date +%s)" - START_TS )) -ge "$MAX_WAIT_SECONDS" ]; then
    echo "Timed out waiting for app startup after ${MAX_WAIT_SECONDS}s."
    echo "Recent app logs:"
    docker compose logs --tail=120 app || true
    exit 1
  fi
  sleep 2
done

echo "Running runtime checks inside app container..."
docker compose exec -T app sh -lc 'python - <<'"'"'PY'"'"'
from app.main import app

assert app.title == "Bookly API"
assert any(route.path == "/api/v1/loans/" for route in app.routes)
print("App import and route registration checks passed.")
PY'

echo "Running HTTP checks..."
curl -fsS "http://127.0.0.1:${APP_PORT}/openapi.json" >/dev/null

echo "Runtime validation passed."
