from __future__ import annotations

import logging
import os
import tempfile
import time
from pathlib import Path

import cv2
from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .agent import run_agent
from .aws_integration import emit_metrics, put_trace, upload_evidence
from .config import settings
from .models import ReviewRequest
from .store import store

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("visionguard")

app = FastAPI(title=settings.app_name, version=settings.version)
static_dir = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if settings.api_key and x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/")
def root() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/api/health")
def health() -> dict:
    major = cv2.__version__.split(".")[0]
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.version,
        "opencv_version": cv2.__version__,
        "opencv5_compliant": major == "5",
        "cool_candidate": str(getattr(cv2, "__file__", "")).startswith("/opt/cool"),
    }


@app.get("/api/info")
def info() -> dict:
    return {
        "project": settings.app_name,
        "concept": "Cognitive security layer for agentic visual systems",
        "vcts_thresholds": {"ACT": ">=85", "VERIFY": "65-84", "RE_OBSERVE": "40-64", "HUMAN_REVIEW": "<40"},
        "restricted_zone_start": settings.restricted_zone_start,
        "privacy": "No face recognition; uploads are temporary unless explicit AWS persistence is enabled.",
    }


@app.post("/api/analyze", dependencies=[Depends(require_api_key)])
async def analyze(file: UploadFile = File(...)) -> dict:
    suffix = Path(file.filename or "upload.mp4").suffix.lower()
    if suffix not in {".mp4", ".mov", ".avi", ".mkv", ".webm"}:
        raise HTTPException(status_code=415, detail="Supported video formats: mp4, mov, avi, mkv, webm")

    max_bytes = settings.max_upload_mb * 1024 * 1024
    data = await file.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise HTTPException(status_code=413, detail=f"Upload exceeds {settings.max_upload_mb} MB")

    started = time.perf_counter()
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(data)
            tmp_path = tmp.name
        outcome = run_agent(tmp_path, Path(file.filename or "upload").name)
        result = outcome.result.model_dump()
        result["aws"] = upload_evidence(tmp_path, outcome.result.trace_id)
        persisted = put_trace(outcome.result.trace_id, result)
        result["aws"]["trace_persisted_ddb"] = persisted
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        result["analysis_latency_ms"] = round(elapsed_ms, 2)
        result["aws"]["cloudwatch_metric_attempted"] = emit_metrics(
            outcome.result.vcts.score if outcome.result.vcts else None,
            outcome.result.final_action,
            elapsed_ms,
        )
        store.put(outcome.result.trace_id, result)
        log.info("analysis trace=%s action=%s vcts=%s", outcome.result.trace_id, outcome.result.final_action, outcome.result.vcts.score if outcome.result.vcts else None)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    finally:
        if tmp_path and os.path.exists(tmp_path) and not settings.persist_uploads:
            os.remove(tmp_path)


@app.get("/api/trace/{trace_id}", dependencies=[Depends(require_api_key)])
def get_trace(trace_id: str) -> dict:
    item = store.get(trace_id)
    if not item:
        raise HTTPException(status_code=404, detail="Trace not found in local process memory")
    return item


@app.post("/api/review/{trace_id}", dependencies=[Depends(require_api_key)])
def review(trace_id: str, request: ReviewRequest) -> dict:
    item = store.get(trace_id)
    if not item:
        raise HTTPException(status_code=404, detail="Trace not found")
    if not item.get("requires_human_approval"):
        raise HTTPException(status_code=409, detail="This trace does not require human approval")

    item["human_decision"] = request.decision
    item["final_action"] = "ACT" if request.decision == "approve" else "IGNORE"
    item["trace"].append(
        {
            "step": len(item["trace"]) + 1,
            "stage": "HUMAN_CONTROL",
            "message": "Human reviewer resolved the pending decision.",
            "data": {"decision": request.decision, "reviewer": request.reviewer, "note": request.note},
        }
    )
    store.put(trace_id, item)
    put_trace(trace_id, item)
    return item
