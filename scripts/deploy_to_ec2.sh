#!/usr/bin/env bash
set -euo pipefail
# Usage: EC2_HOST=1.2.3.4 KEY=~/.ssh/key.pem S3_BUCKET=... DDB_TABLE=... ./scripts/deploy_to_ec2.sh
: "${EC2_HOST:?Set EC2_HOST}"
: "${KEY:?Set KEY to the EC2 private key path}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SSH=(ssh -i "$KEY" -o StrictHostKeyChecking=accept-new ubuntu@"$EC2_HOST")
SCP=(scp -i "$KEY" -o StrictHostKeyChecking=accept-new)

"${SSH[@]}" 'sudo mkdir -p /opt/visionguard && sudo chown ubuntu:ubuntu /opt/visionguard'
tar --exclude='.git' --exclude='output/*' -C "$ROOT" -czf - . | "${SSH[@]}" 'tar -xzf - -C /opt/visionguard'
"${SSH[@]}" "AWS_REGION='${AWS_REGION:-eu-west-1}' VISIONGUARD_S3_BUCKET='${S3_BUCKET:-}' VISIONGUARD_DDB_TABLE='${DDB_TABLE:-}' bash /opt/visionguard/scripts/install_cool_host.sh"
echo "Deployed: http://$EC2_HOST/"
