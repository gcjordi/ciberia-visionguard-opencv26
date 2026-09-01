from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import cv2
import numpy as np

from .config import settings
from .models import MotionEvidence, QualityMetrics, StressResult


@dataclass
class FrameObservation:
    frame_index: int
    prev_frame: np.ndarray
    frame: np.ndarray
    quality: QualityMetrics
    evidence: MotionEvidence
    temporal_consistency: float
    geometry_consistency: float


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))


def bbox_iou(a: tuple[int, int, int, int] | None, b: tuple[int, int, int, int] | None) -> float:
    if not a or not b:
        return 0.5 if (a is None and b is None) else 0.0
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    x1, y1 = max(ax, bx), max(ay, by)
    x2, y2 = min(ax + aw, bx + bw), min(ay + ah, by + bh)
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    union = aw * ah + bw * bh - inter
    return 0.0 if union <= 0 else inter / union


def image_quality(frame: np.ndarray) -> QualityMetrics:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    mean_luma = float(gray.mean())
    std_luma = float(gray.std())

    sharpness = _clamp01(1.0 - math.exp(-lap_var / 180.0))
    # A broad "usable exposure" plateau avoids over-penalizing naturally dim scenes.
    if 50.0 <= mean_luma <= 205.0:
        brightness = 1.0
    elif mean_luma < 50.0:
        brightness = _clamp01(mean_luma / 50.0)
    else:
        brightness = _clamp01((255.0 - mean_luma) / 50.0)
    contrast = _clamp01(std_luma / 35.0)
    overall = _clamp01(0.45 * sharpness + 0.30 * brightness + 0.25 * contrast)
    return QualityMetrics(
        sharpness=round(sharpness, 4),
        brightness=round(brightness, 4),
        contrast=round(contrast, 4),
        overall=round(overall, 4),
        raw_laplacian_variance=round(lap_var, 3),
        raw_mean_luma=round(mean_luma, 3),
        raw_std_luma=round(std_luma, 3),
    )


def _optical_flow_metrics(prev_gray: np.ndarray, gray: np.ndarray) -> tuple[float, float]:
    flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    mag, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
    finite = mag[np.isfinite(mag)]
    if finite.size == 0:
        return 0.0, 0.0
    mean_mag = float(np.mean(finite))
    p90 = float(np.percentile(finite, 90)) + 1e-6
    coherence = _clamp01(1.0 - float(np.std(finite)) / p90)
    return round(mean_mag, 4), round(coherence, 4)


def detect_motion(prev_frame: np.ndarray, frame: np.ndarray, zone_start: float | None = None) -> MotionEvidence:
    zone_start = settings.restricted_zone_start if zone_start is None else zone_start
    h, w = frame.shape[:2]
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    prev_blur = cv2.GaussianBlur(prev_gray, (5, 5), 0)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    diff = cv2.absdiff(prev_blur, blur)
    _, mask = cv2.threshold(diff, 22, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.dilate(mask, kernel, iterations=1)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    min_area = settings.min_motion_area_ratio * h * w
    contours = [c for c in contours if cv2.contourArea(c) >= min_area]
    flow_mean, flow_coherence = _optical_flow_metrics(prev_gray, gray)
    if not contours:
        return MotionEvidence(
            present=False,
            in_restricted_zone=False,
            confidence=0.0,
            area_ratio=0.0,
            flow_mean=flow_mean,
            flow_coherence=flow_coherence,
        )

    contour = max(contours, key=cv2.contourArea)
    x, y, bw, bh = cv2.boundingRect(contour)
    area_ratio = float(cv2.contourArea(contour) / (h * w))
    cx, cy = x + bw / 2.0, y + bh / 2.0
    zone_x = int(w * zone_start)
    in_zone = (x + bw) >= zone_x

    area_conf = _clamp01(area_ratio / 0.025)
    geometry_conf = _clamp01((bw * bh) / (h * w) / 0.04)
    confidence = _clamp01(0.70 * area_conf + 0.25 * geometry_conf + 0.05 * flow_coherence)
    # Scene-wide change (e.g. sudden illumination/noise) is not strong object-level evidence.
    if area_ratio > 0.35:
        confidence *= 0.30
    elif area_ratio > 0.20:
        confidence *= 0.60
    return MotionEvidence(
        present=True,
        in_restricted_zone=bool(in_zone),
        confidence=round(confidence, 4),
        bbox=(int(x), int(y), int(bw), int(bh)),
        centroid=(round(cx, 2), round(cy, 2)),
        area_ratio=round(area_ratio, 6),
        flow_mean=flow_mean,
        flow_coherence=flow_coherence,
    )


def enhance_pair(prev_frame: np.ndarray, frame: np.ndarray, tool: str) -> tuple[np.ndarray, np.ndarray]:
    tool = tool.upper()

    def clahe_one(img: np.ndarray) -> np.ndarray:
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        cl = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(l)
        return cv2.cvtColor(cv2.merge((cl, a, b)), cv2.COLOR_LAB2BGR)

    def unsharp(img: np.ndarray) -> np.ndarray:
        blur = cv2.GaussianBlur(img, (0, 0), 2.0)
        return cv2.addWeighted(img, 1.7, blur, -0.7, 0)

    def denoise(img: np.ndarray) -> np.ndarray:
        return cv2.fastNlMeansDenoisingColored(img, None, 5, 5, 7, 21)

    fn = {
        "CLAHE": clahe_one,
        "UNSHARP": unsharp,
        "DENOISE": denoise,
    }.get(tool)
    if fn is None:
        return prev_frame.copy(), frame.copy()
    return fn(prev_frame), fn(frame)


def select_verification_tool(q: QualityMetrics, robustness: float) -> str:
    if q.brightness < 0.62 or q.contrast < 0.55:
        return "CLAHE"
    if q.sharpness < 0.55:
        return "UNSHARP"
    if robustness < 0.65:
        return "DENOISE"
    return "CLAHE"


def _noise(img: np.ndarray, seed: int = 7, sigma: float = 15.0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    noise = rng.normal(0, sigma, img.shape).astype(np.float32)
    return np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)


def _occlude(img: np.ndarray) -> np.ndarray:
    out = img.copy()
    h, w = out.shape[:2]
    x1, y1 = int(w * 0.62), int(h * 0.30)
    x2, y2 = int(w * 0.82), int(h * 0.68)
    cv2.rectangle(out, (x1, y1), (x2, y2), (0, 0, 0), -1)
    return out


def stress_test_pair(prev_frame: np.ndarray, frame: np.ndarray, baseline: MotionEvidence) -> list[StressResult]:
    transforms = {
        "gaussian_blur": lambda x: cv2.GaussianBlur(x, (11, 11), 3.0),
        "low_light": lambda x: cv2.convertScaleAbs(x, alpha=0.55, beta=-25),
        "high_light": lambda x: cv2.convertScaleAbs(x, alpha=1.25, beta=30),
        "sensor_noise": lambda x: _noise(x),
        "partial_occlusion": _occlude,
    }
    results: list[StressResult] = []
    for name, fn in transforms.items():
        p2, f2 = fn(prev_frame), fn(frame)
        ev = detect_motion(p2, f2)
        preserved = ev.in_restricted_zone == baseline.in_restricted_zone
        geo = bbox_iou(ev.bbox, baseline.bbox) if baseline.present else (1.0 if not ev.present else 0.0)
        confidence = _clamp01(0.7 * (1.0 if preserved else 0.0) + 0.3 * geo)
        results.append(
            StressResult(
                name=name,
                decision_preserved=preserved,
                geometry_similarity=round(geo, 4),
                confidence=round(confidence, 4),
            )
        )
    return results


def summarize_stress(results: Iterable[StressResult]) -> float:
    vals = [r.confidence for r in results]
    return round(float(np.mean(vals)) if vals else 0.5, 4)


def _temporal_consistency(history: list[MotionEvidence], current: MotionEvidence) -> float:
    if not history:
        return 0.5
    recent = history[-4:] + [current]
    zone_flags = np.array([1.0 if x.in_restricted_zone else 0.0 for x in recent], dtype=np.float32)
    present_flags = np.array([1.0 if x.present else 0.0 for x in recent], dtype=np.float32)
    if current.in_restricted_zone:
        persistence = float(zone_flags.mean())
    else:
        persistence = float((1.0 - zone_flags).mean())
    presence = float(present_flags.mean()) if current.present else float((1.0 - present_flags).mean())
    flow = float(np.mean([x.flow_coherence for x in recent]))
    return round(_clamp01(0.60 * persistence + 0.30 * presence + 0.10 * flow), 4)


def analyze_video(path: str | Path, max_frames: int | None = None, sample_every: int | None = None) -> list[FrameObservation]:
    max_frames = settings.max_frames if max_frames is None else max_frames
    sample_every = settings.sample_every if sample_every is None else sample_every
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError("OpenCV could not open the video")

    observations: list[FrameObservation] = []
    history: list[MotionEvidence] = []
    prev_sample: np.ndarray | None = None
    prev_bbox = None
    idx = -1
    sampled = 0
    while sampled < max_frames:
        ok, frame = cap.read()
        if not ok:
            break
        idx += 1
        if idx % sample_every != 0:
            continue
        sampled += 1
        if prev_sample is None:
            prev_sample = frame
            continue
        q = image_quality(frame)
        ev = detect_motion(prev_sample, frame)
        temporal = _temporal_consistency(history, ev)
        geometry = bbox_iou(prev_bbox, ev.bbox) if ev.present else 0.7
        observations.append(
            FrameObservation(
                frame_index=idx,
                prev_frame=prev_sample.copy(),
                frame=frame.copy(),
                quality=q,
                evidence=ev,
                temporal_consistency=temporal,
                geometry_consistency=round(geometry, 4),
            )
        )
        history.append(ev)
        if ev.bbox:
            prev_bbox = ev.bbox
        prev_sample = frame
    cap.release()
    return observations
