from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from .config import settings

log = logging.getLogger(__name__)


def _boto3():
    try:
        import boto3
        return boto3
    except Exception:
        return None


def upload_evidence(path: str | Path, trace_id: str) -> dict[str, Any]:
    if not settings.s3_bucket or not settings.persist_uploads:
        return {"s3_persisted": False}
    boto3 = _boto3()
    if not boto3:
        return {"s3_persisted": False, "error": "boto3 unavailable"}
    key = f"evidence/{trace_id}/{Path(path).name}"
    try:
        s3 = boto3.client("s3", region_name=settings.aws_region)
        s3.upload_file(str(path), settings.s3_bucket, key, ExtraArgs={"ServerSideEncryption": "AES256"})
        return {"s3_persisted": True, "bucket": settings.s3_bucket, "key": key}
    except Exception as exc:
        log.warning("S3 upload failed: %s", exc)
        return {"s3_persisted": False, "error": "upload failed"}


def put_trace(trace_id: str, payload: dict[str, Any]) -> bool:
    if not settings.ddb_table:
        return False
    boto3 = _boto3()
    if not boto3:
        return False
    try:
        ddb = boto3.resource("dynamodb", region_name=settings.aws_region)
        table = ddb.Table(settings.ddb_table)
        table.put_item(Item={"trace_id": trace_id, "payload": json.dumps(payload, separators=(",", ":"))})
        return True
    except Exception as exc:
        log.warning("DynamoDB write failed: %s", exc)
        return False


def emit_metrics(vcts: float | None, final_action: str, elapsed_ms: float) -> bool:
    boto3 = _boto3()
    if not boto3:
        return False
    try:
        cw = boto3.client("cloudwatch", region_name=settings.aws_region)
        metrics = [
            {"MetricName": "AnalysisLatency", "Unit": "Milliseconds", "Value": float(elapsed_ms)},
            {"MetricName": "Analyses", "Unit": "Count", "Value": 1.0},
            {"MetricName": f"Action_{final_action}", "Unit": "Count", "Value": 1.0},
        ]
        if vcts is not None:
            metrics.append({"MetricName": "VCTS", "Unit": "None", "Value": float(vcts)})
        cw.put_metric_data(Namespace=settings.cloudwatch_namespace, MetricData=metrics)
        return True
    except Exception as exc:
        log.debug("CloudWatch metric emit skipped/failed: %s", exc)
        return False
