#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="/opt/cool/venvs/python_3.12/bin/python"
if [[ ! -x "$PY" ]]; then
  echo "COOL Python environment not found at $PY. Launch the official COOL AWS Marketplace AMI first." >&2
  exit 2
fi
cd "$ROOT"
"$PY" -c 'import cv2; print("COOL/OpenCV:", cv2.__version__, cv2.__file__)'
exec "$PY" -m uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
