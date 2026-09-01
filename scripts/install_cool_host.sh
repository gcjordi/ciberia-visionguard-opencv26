#!/usr/bin/env bash
set -euo pipefail
# Run on the official COOL Marketplace AMI after copying the repository to /opt/visionguard.
ROOT="${VISIONGUARD_ROOT:-/opt/visionguard}"
COOL_PY="/opt/cool/venvs/python_3.12/bin/python"
COOL_PIP="/opt/cool/venvs/python_3.12/bin/pip"

if [[ ! -x "$COOL_PY" ]]; then
  echo "Official COOL environment not found. Verify the Marketplace AMI and version." >&2
  exit 2
fi

sudo apt-get update
sudo apt-get install -y nginx
sudo chown -R "$(id -un)":"$(id -gn)" "$ROOT"
cd "$ROOT"
"$COOL_PIP" install -r requirements-cool.txt
"$COOL_PY" -c 'import cv2; print("Active OpenCV:", cv2.__version__, cv2.__file__)'

sudo tee /etc/systemd/system/visionguard.service >/dev/null <<SERVICE
[Unit]
Description=CiberIA VisionGuard
After=network-online.target

[Service]
User=$(id -un)
WorkingDirectory=$ROOT
Environment=AWS_REGION=${AWS_REGION:-eu-west-1}
Environment=VISIONGUARD_S3_BUCKET=${VISIONGUARD_S3_BUCKET:-}
Environment=VISIONGUARD_DDB_TABLE=${VISIONGUARD_DDB_TABLE:-}
Environment=VISIONGUARD_PERSIST_UPLOADS=${VISIONGUARD_PERSIST_UPLOADS:-0}
ExecStart=$COOL_PY -m uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=on-failure
RestartSec=3
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=$ROOT /tmp

[Install]
WantedBy=multi-user.target
SERVICE

sudo tee /etc/nginx/sites-available/visionguard >/dev/null <<'NGINX'
server {
    listen 80 default_server;
    server_name _;
    client_max_body_size 50m;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 180s;
    }
}
NGINX
sudo ln -sf /etc/nginx/sites-available/visionguard /etc/nginx/sites-enabled/default
sudo systemctl daemon-reload
sudo systemctl enable --now visionguard nginx
sudo systemctl restart nginx
curl -fsS http://127.0.0.1:8000/api/health
