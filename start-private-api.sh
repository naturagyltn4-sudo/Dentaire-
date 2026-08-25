#!/bin/sh

set -eu

: "${PORT:=8000}"

: "${ENV:=production}"

: "${INSTANCE_CLINIC_ID:=1}"

: "${TEST_ADMIN_EMAIL:=demo-admin@dentaire-qa.fr}"

: "${TEST_ADMIN_NOM:=Demo}"

: "${TEST_ADMIN_PRENOM:=Admin}"

case "${DATABASE_URL:-}" in

  postgresql://*) DATABASE_URL="postgresql+asyncpg://${DATABASE_URL#postgresql://}"; export DATABASE_URL ;;
  
  postgres://*) DATABASE_URL="postgresql+asyncpg://${DATABASE_URL#postgres://}"; export DATABASE_URL ;;
  
esac

if [ -z "${DATABASE_URL:-}" ]; then echo "DATABASE_URL is required" >&2; exit 1; fi

if [ -z "${TEST_ADMIN_PASSWORD:-}" ]; then echo "TEST_ADMIN_PASSWORD is required" >&2; exit 1; fi

alembic upgrade head

printf '%s\n' "$TEST_ADMIN_PASSWORD" | python /app/bootstrap_admin.py --email "$TEST_ADMIN_EMAIL" --nom "$TEST_ADMIN_NOM" --prenom "$TEST_ADMIN_PRENOM" --clinic-id "$INSTANCE_CLINIC_ID" --password-stdin --force

exec uvicorn main:app --host 0.0.0.0 --port "$PORT"



