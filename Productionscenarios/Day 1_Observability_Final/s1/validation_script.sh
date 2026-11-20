#!/usr/bin/env bash
set -Eeuo pipefail
# s1 lab controller wrapper:  ./validation_script.sh {start|check|reset}
ACTION="${1:-}"
LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CTL="$LAB_DIR/../shared/labctl.py"
case "$ACTION" in
    start|check|reset) ;;
    *) echo "Usage: ./validation_script.sh {start|check|reset}"; exit 2 ;;
esac
if command -v python3 >/dev/null 2>&1; then PY=python3
elif command -v python >/dev/null 2>&1; then PY=python
else echo "[ERROR] Python 3 is required (python3 --version)."; exit 1; fi
exec "$PY" "$CTL" s1 "$ACTION"
