#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$ROOT_DIR/.venv-build"
APP_NAME="Mouse Locator"
APP_PATH="$ROOT_DIR/dist/$APP_NAME.app"
DMG_PATH="$ROOT_DIR/dist/$APP_NAME.dmg"

cd "$ROOT_DIR"

if ! command -v create-dmg >/dev/null 2>&1; then
  printf 'create-dmg is required to package the app as a DMG. Install it with `brew install create-dmg`.\n' >&2
  exit 1
fi

python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/python" -m pip install --upgrade pip setuptools wheel
"$VENV_DIR/bin/python" -m pip install -r requirements.txt
"$VENV_DIR/bin/python" scripts/generate_icon.py

rm -rf build dist
"$VENV_DIR/bin/python" setup.py py2app
create-dmg --overwrite --no-version-in-filename --no-code-sign "$APP_PATH" "$ROOT_DIR/dist"

printf '\nBuilt %s\n' "${APP_PATH#$ROOT_DIR/}"
printf 'Built %s\n' "${DMG_PATH#$ROOT_DIR/}"
