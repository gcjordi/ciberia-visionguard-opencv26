from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "CiberIA VisionGuard"
    version: str = "0.1.0"
    restricted_zone_start: float = float(os.getenv("VISIONGUARD_ZONE_START", "0.68"))
    max_upload_mb: int = int(os.getenv("VISIONGUARD_MAX_UPLOAD_MB", "50"))
    api_key: str | None = os.getenv("VISIONGUARD_API_KEY") or None
    s3_bucket: str | None = os.getenv("VISIONGUARD_S3_BUCKET") or None
    ddb_table: str | None = os.getenv("VISIONGUARD_DDB_TABLE") or None
    aws_region: str = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "eu-west-1"))
    cloudwatch_namespace: str = os.getenv("VISIONGUARD_CW_NAMESPACE", "CiberIA/VisionGuard")
    persist_uploads: bool = os.getenv("VISIONGUARD_PERSIST_UPLOADS", "0") == "1"
    min_motion_area_ratio: float = float(os.getenv("VISIONGUARD_MIN_MOTION_AREA_RATIO", "0.003"))
    max_frames: int = int(os.getenv("VISIONGUARD_MAX_FRAMES", "240"))
    sample_every: int = int(os.getenv("VISIONGUARD_SAMPLE_EVERY", "2"))


settings = Settings()
