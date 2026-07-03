#!/usr/bin/env bash
set -euo pipefail

DB_PATH="${1:-instance/app.db}"
BACKUP_DIR="${2:-backups}"

if [[ ! -f "$DB_PATH" ]]; then
  echo "SQLite DB not found: $DB_PATH" >&2
  exit 1
fi

mkdir -p "$BACKUP_DIR"
stamp="$(date +%Y%m%d-%H%M%S)"
backup_path="$BACKUP_DIR/app-$stamp.db"
cp "$DB_PATH" "$backup_path"
sha256sum "$backup_path" > "$backup_path.sha256"
echo "$backup_path"
