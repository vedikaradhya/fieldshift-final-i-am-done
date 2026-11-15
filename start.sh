#!/usr/bin/env sh
# Local launcher for macOS and Linux. Docker is optional and not used here.
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$PROJECT_DIR"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3.12 or newer is required." >&2
  exit 1
fi
if ! command -v npm >/dev/null 2>&1; then
  echo "Node.js and npm are required." >&2
  exit 1
fi

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example." >&2
  echo "Set a unique SECRET_KEY (at least 32 random bytes) in .env, then run this command again." >&2
  exit 1
fi

SECRET_VALUE=$(sed -n 's/^SECRET_KEY=//p' .env | tail -n 1)
case "$SECRET_VALUE" in
  ""|replace-with-a-32-byte-secret|development-only-change-me*)
    echo "Refusing to start with the sample SECRET_KEY. Set a unique secret in .env first." >&2
    exit 1
    ;;
esac

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
.venv/bin/python -m pip install --quiet -r backend/requirements.txt

if [ ! -d frontend/node_modules ]; then
  (cd frontend && npm install)
fi

mkdir -p .run
nohup .venv/bin/python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 >.run/api.log 2>&1 &
API_PID=$!
nohup sh -c 'cd frontend && npm run dev' >.run/web.log 2>&1 &
WEB_PID=$!

echo "$API_PID" >.run/api.pid
echo "$WEB_PID" >.run/web.pid
echo "AgriSpace is running without Docker."
echo "Web: http://localhost:5173"
echo "API docs: http://localhost:8000/docs"
echo "Logs: .run/api.log and .run/web.log"
echo "Stop: kill $(cat .run/api.pid) $(cat .run/web.pid)"
