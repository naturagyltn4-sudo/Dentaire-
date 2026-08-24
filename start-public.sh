#!/bin/sh
set -eu

# Le domaine Railway généré pointe sur le port public 8000.
# L’API Uvicorn reste réservée au loopback sur 8001.
PORT=8000
export PORT
: "${ENV:=production}"

# Railway fournit habituellement postgresql:// ; SQLAlchemy async requiert asyncpg.
case "${DATABASE_URL:-}" in
  postgresql://*)
    DATABASE_URL="postgresql+asyncpg://${DATABASE_URL#postgresql://}"
    export DATABASE_URL
    ;;
  postgres://*)
    DATABASE_URL="postgresql+asyncpg://${DATABASE_URL#postgres://}"
    export DATABASE_URL
    ;;
esac

if [ -z "${DATABASE_URL:-}" ]; then
  echo "DATABASE_URL is required" >&2
  exit 1
fi

alembic upgrade head
python /app/railway_seed_public_demo.py

sed "s/__PORT__/${PORT}/g" /etc/nginx/templates/public.conf.template > /etc/nginx/conf.d/public.conf
uvicorn public_main:app --host 127.0.0.1 --port 8001 &
exec nginx -g 'daemon off;'
