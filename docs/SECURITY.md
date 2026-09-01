# Security Design

## Threat model

Relevant threats include malicious uploads, oversized inputs, credential leakage, public evidence exposure, unauthorized human approval, overly permissive IAM, compromised EC2 metadata access and unsafe fail-open behavior.

## Controls in the reference implementation

- video extension allow-list;
- configurable 50 MB upload cap;
- random temporary filenames;
- local upload deletion by default;
- optional `X-API-Key` application gate;
- no credentials in source or Terraform;
- EC2 instance profile for AWS access;
- S3 Block Public Access;
- S3 server-side encryption;
- S3 seven-day evidence lifecycle;
- DynamoDB pay-per-request + point-in-time recovery;
- least-privilege S3/DynamoDB/CloudWatch IAM policy;
- encrypted EC2 root volume;
- IMDSv2 required;
- SSH restricted to `admin_cidr`;
- systemd `NoNewPrivileges`, `PrivateTmp`, `ProtectSystem`;
- visual uncertainty fails toward human review, not autonomous action.

## Before a public endpoint

For the final judge endpoint, add TLS using a domain + ACM/ALB or another managed TLS termination path, configure a strong API key or judge-specific access control, and review Nginx request limits. Do not expose SSH to the Internet.
