#!/usr/bin/env bash
set -euo pipefail
# Run on the SAME Graviton4 EC2 host used for COOL. This creates a vanilla OpenCV 5 baseline venv.
BASELINE="${BASELINE_VENV:-$HOME/visionguard-vanilla}"
python3.12 -m venv "$BASELINE"
"$BASELINE/bin/pip" install --upgrade pip
"$BASELINE/bin/pip" install opencv-python-headless==5.0.0.93 numpy==2.3.5
"$BASELINE/bin/python" -c 'import cv2; print(cv2.__version__, cv2.__file__)'
echo "$BASELINE"
