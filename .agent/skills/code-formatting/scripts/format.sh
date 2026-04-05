#!/bin/bash
# Usage: .agent/skills/code-formatting/scripts/format.sh path/to/file1.py path/to/file2.tsx
# Formats ONLY the files passed as arguments.
# With no args: formats the entire project (fallback).

set -e

if [ -f "backend/.venv/bin/activate" ]; then
  source backend/.venv/bin/activate
fi

FILES=("$@")

if [ ${#FILES[@]} -eq 0 ]; then
  echo "⚠️  No files specified. Formatting entire project..."
  ruff format . && ruff check --fix .
  sqlfluff fix database/ --dialect postgres || true
  pnpm dlx prettier@3 --write "**/*.{ts,tsx,json,css,yml,yaml}" "Dockerfile*"
  exit 0
fi

for FILE in "${FILES[@]}"; do
  echo "🔧 Formatting: $FILE"
  case "$FILE" in
    *.py)
      ruff format "$FILE" && ruff check --fix "$FILE" ;;
    *.sql)
      sqlfluff fix "$FILE" --dialect postgres || true ;;
    *.ts|*.tsx|*.json|*.css|*.yml|*.yaml|Dockerfile*)
      pnpm dlx prettier@3 --write "$FILE" ;;
  esac
done

echo "✅ Done."