#!/usr/bin/env bash
set -euo pipefail

BACKUP_PATH="${1:-}"
DB_PATH="${2:-instance/app.db}"

if [[ -z "$BACKUP_PATH" ]]; then
  echo "Usage: bash scripts/restore_sqlite.sh <backup.db> [target.db]" >&2
  exit 1
fi
if [[ ! -f "$BACKUP_PATH" ]]; then
  echo "Backup DB not found: $BACKUP_PATH" >&2
  exit 1
fi

mkdir -p "$(dirname "$DB_PATH")"
if [[ -f "$DB_PATH" ]]; then
  safety_copy="$DB_PATH.before-restore-$(date +%Y%m%d-%H%M%S)"
  cp "$DB_PATH" "$safety_copy"
  echo "Current DB copied to $safety_copy"
fi
cp "$BACKUP_PATH" "$DB_PATH"
echo "Restored $BACKUP_PATH to $DB_PATH"
