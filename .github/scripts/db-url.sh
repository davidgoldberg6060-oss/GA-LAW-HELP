#!/usr/bin/env bash
# Sourced by workflows. Derives driver-specific URLs from secrets.DATABASE_URL without printing them.
#  - LIBPQ_URL: plain postgresql:// for psql / pg_dump
#  - DATABASE_URL: postgresql+psycopg:// for SQLAlchemy (only psycopg v3 is installed)
# Both get sslmode=require when no sslmode is present.
set -euo pipefail
if [ -z "${DATABASE_URL:-}" ]; then
  echo "::error::Repository secret DATABASE_URL is not configured."; exit 1
fi
case "$DATABASE_URL" in
  sqlite*) echo "::error::DATABASE_URL points at SQLite; refusing."; exit 1 ;;
esac
_rest="${DATABASE_URL#*://}"
case "$_rest" in *sslmode=*) ;; *\?*) _rest="${_rest}&sslmode=require" ;; *) _rest="${_rest}?sslmode=require" ;; esac
LIBPQ_URL="postgresql://${_rest}"
DATABASE_URL="postgresql+psycopg://${_rest}"
echo "::add-mask::${LIBPQ_URL}"
echo "::add-mask::${DATABASE_URL}"
export LIBPQ_URL DATABASE_URL
unset _rest
