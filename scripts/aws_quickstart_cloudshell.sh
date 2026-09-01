#!/usr/bin/env bash
set -euo pipefail

# CiberIA VisionGuard - simple AWS CloudShell deployment
# Required: subscribe to the official COOL Marketplace AMI and export COOL_AMI_ID=ami-...
# Optional overrides: AWS_REGION, INSTANCE_TYPE, VPC_ID, SUBNET_ID, KEY_NAME, ADMIN_CIDR

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TF_DIR="$ROOT/deploy/aws/terraform"

: "${COOL_AMI_ID:?Set COOL_AMI_ID to the regional COOL Marketplace AMI ID, e.g. export COOL_AMI_ID=ami-0123456789abcdef0}"

AWS_REGION="${AWS_REGION:-${AWS_DEFAULT_REGION:-$(aws configure get region 2>/dev/null || true)}}"
if [[ -z "${AWS_REGION}" || "${AWS_REGION}" == "None" ]]; then
  AWS_REGION="eu-west-1"
fi
export AWS_REGION AWS_DEFAULT_REGION="$AWS_REGION"
INSTANCE_TYPE="${INSTANCE_TYPE:-c8g.xlarge}"

command -v aws >/dev/null || { echo "AWS CLI is required (normally preinstalled in AWS CloudShell)." >&2; exit 2; }
command -v curl >/dev/null || { echo "curl is required." >&2; exit 2; }
command -v ssh >/dev/null || { echo "ssh is required." >&2; exit 2; }

if ! command -v terraform >/dev/null 2>&1; then
  echo "[1/8] Installing Terraform in this CloudShell session..."
  sudo dnf install -y dnf-plugins-core >/dev/null
  if [[ ! -f /etc/yum.repos.d/hashicorp.repo ]]; then
    sudo dnf config-manager --add-repo https://rpm.releases.hashicorp.com/AmazonLinux/hashicorp.repo >/dev/null
  fi
  sudo dnf -y install terraform >/dev/null
else
  echo "[1/8] Terraform already available: $(terraform version | head -n1)"
fi

ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
echo "AWS account: $ACCOUNT_ID | Region: $AWS_REGION"

if [[ -z "${VPC_ID:-}" ]]; then
  VPC_ID="$(aws ec2 describe-vpcs --filters Name=is-default,Values=true --query 'Vpcs[0].VpcId' --output text)"
fi
if [[ -z "${VPC_ID}" || "${VPC_ID}" == "None" ]]; then
  echo "No default VPC found. Set VPC_ID and SUBNET_ID explicitly, then rerun." >&2
  exit 3
fi

if [[ -z "${SUBNET_ID:-}" ]]; then
  SUBNET_ID="$(aws ec2 describe-subnets --filters Name=vpc-id,Values="$VPC_ID" --query 'Subnets[0].SubnetId' --output text)"
fi
if [[ -z "${SUBNET_ID}" || "${SUBNET_ID}" == "None" ]]; then
  echo "No subnet found in VPC $VPC_ID. Set SUBNET_ID explicitly, then rerun." >&2
  exit 3
fi

echo "[2/8] Network selected: VPC=$VPC_ID SUBNET=$SUBNET_ID"

if [[ -z "${ADMIN_CIDR:-}" ]]; then
  CURRENT_IP="$(curl -fsS https://checkip.amazonaws.com | tr -d '[:space:]')"
  ADMIN_CIDR="${CURRENT_IP}/32"
fi
echo "SSH administration source: $ADMIN_CIDR"

KEY_NAME="${KEY_NAME:-visionguard-key}"
KEY_PATH="$HOME/${KEY_NAME}.pem"
if aws ec2 describe-key-pairs --key-names "$KEY_NAME" >/dev/null 2>&1; then
  if [[ ! -f "$KEY_PATH" ]]; then
    KEY_NAME="visionguard-key-$(date +%Y%m%d-%H%M%S)"
    KEY_PATH="$HOME/${KEY_NAME}.pem"
    echo "Existing AWS key has no local PEM; creating $KEY_NAME instead."
    aws ec2 create-key-pair --key-name "$KEY_NAME" --key-type rsa --key-format pem --query 'KeyMaterial' --output text > "$KEY_PATH"
  fi
else
  echo "[3/8] Creating EC2 key pair: $KEY_NAME"
  aws ec2 create-key-pair --key-name "$KEY_NAME" --key-type rsa --key-format pem --query 'KeyMaterial' --output text > "$KEY_PATH"
fi
chmod 400 "$KEY_PATH"

cat > "$TF_DIR/terraform.tfvars" <<VARS
aws_region    = "$AWS_REGION"
cool_ami_id   = "$COOL_AMI_ID"
instance_type = "$INSTANCE_TYPE"
vpc_id        = "$VPC_ID"
subnet_id     = "$SUBNET_ID"
admin_cidr    = "$ADMIN_CIDR"
key_name      = "$KEY_NAME"
VARS

echo "[4/8] Provisioning AWS infrastructure with Terraform..."
cd "$TF_DIR"
terraform init -upgrade
terraform validate
terraform apply -auto-approve

PUBLIC_IP="$(terraform output -raw public_ip)"
INSTANCE_ID="$(terraform output -raw instance_id)"
S3_BUCKET="$(terraform output -raw evidence_bucket)"
DDB_TABLE="$(terraform output -raw dynamodb_table)"

echo "[5/8] Waiting for EC2 instance checks: $INSTANCE_ID"
aws ec2 wait instance-status-ok --instance-ids "$INSTANCE_ID"

# Give sshd a short chance to become reachable after status checks.
for n in {1..12}; do
  if ssh -i "$KEY_PATH" -o BatchMode=yes -o ConnectTimeout=5 -o StrictHostKeyChecking=accept-new ubuntu@"$PUBLIC_IP" 'echo ready' >/dev/null 2>&1; then
    break
  fi
  if [[ "$n" == "12" ]]; then
    echo "EC2 is healthy but SSH is not reachable from $ADMIN_CIDR." >&2
    echo "Update the security-group SSH source to your current CloudShell IP and rerun only the deployment step." >&2
    exit 4
  fi
  sleep 5
done

echo "[6/8] Copying VisionGuard and installing it in the official COOL environment..."
cd "$ROOT"
AWS_REGION="$AWS_REGION" \
EC2_HOST="$PUBLIC_IP" \
KEY="$KEY_PATH" \
S3_BUCKET="$S3_BUCKET" \
DDB_TABLE="$DDB_TABLE" \
./scripts/deploy_to_ec2.sh

echo "[7/8] Verifying public health endpoint..."
curl -fsS "http://$PUBLIC_IP/api/health"
echo

echo "[8/8] Deployment complete."
echo ""
echo "VisionGuard URL: http://$PUBLIC_IP/"
echo "Health:          http://$PUBLIC_IP/api/health"
echo "EC2 instance:    $INSTANCE_ID"
echo "S3 evidence:     $S3_BUCKET"
echo "DynamoDB traces: $DDB_TABLE"
echo "Key file:        $KEY_PATH"
echo ""
echo "IMPORTANT: keep $TF_DIR/terraform.tfstate. It is needed to manage or destroy this deployment later."
echo "For final submission, add HTTPS and run the COOL-vs-vanilla benchmark documented in docs/DEPLOYMENT_GUIDE_CA.md."
