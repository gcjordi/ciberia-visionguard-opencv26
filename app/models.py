from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field


ActionName = Literal["OBSERVE", "ACT", "VERIFY", "RE_OBSERVE", "HUMAN_REVIEW", "IGNORE"]


class QualityMetrics(BaseModel):
    sharpness: float = Field(ge=0, le=1)
    brightness: float = Field(ge=0, le=1)
    contrast: float = Field(ge=0, le=1)
    overall: float = Field(ge=0, le=1)
    raw_laplacian_variance: float
    raw_mean_luma: float
    raw_std_luma: float


class MotionEvidence(BaseModel):
    present: bool
    in_restricted_zone: bool
    confidence: float = Field(ge=0, le=1)
    bbox: tuple[int, int, int, int] | None = None
    centroid: tuple[float, float] | None = None
    area_ratio: float = Field(ge=0, le=1)
    flow_mean: float = 0.0
    flow_coherence: float = Field(default=0.0, ge=0, le=1)


class StressResult(BaseModel):
    name: str
    decision_preserved: bool
    geometry_similarity: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)


class VCTSBreakdown(BaseModel):
    detection: float
    image_quality: float
    temporal_consistency: float
    stress_robustness: float
    geometry_consistency: float
    score: float


class TraceStep(BaseModel):
    step: int
    stage: Literal["PERCEPTION", "DECISION", "TOOL_CALL", "ACTION", "HUMAN_CONTROL"]
    message: str
    data: dict[str, Any] = Field(default_factory=dict)


class AnalysisResult(BaseModel):
    trace_id: str
    opencv_version: str
    opencv5_compliant: bool
    source: str
    frame_index: int | None
    quality: QualityMetrics | None
    evidence: MotionEvidence | None
    stress_tests: list[StressResult] = Field(default_factory=list)
    vcts: VCTSBreakdown | None
    initial_action: ActionName
    final_action: ActionName
    selected_tool: str | None = None
    requires_human_approval: bool = False
    human_decision: str | None = None
    trace: list[TraceStep] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    aws: dict[str, Any] = Field(default_factory=dict)


class ReviewRequest(BaseModel):
    decision: Literal["approve", "reject"]
    reviewer: str | None = None
    note: str | None = None
