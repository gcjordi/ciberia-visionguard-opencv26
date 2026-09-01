from __future__ import annotations

import argparse
import json
import platform
import statistics
import time
from pathlib import Path

import cv2
import numpy as np


def make_input(seed: int = 42, h: int = 1080, w: int = 1920) -> np.ndarray:
    rng = np.random.default_rng(seed)
    img = rng.integers(0, 256, size=(h, w, 3), dtype=np.uint8)
    for x in range(100, w, 280):
        cv2.rectangle(img, (x, 180), (min(x + 160, w - 1), 780), (225, 225, 225), 3)
    return img


def workload(img: np.ndarray) -> None:
    resized = cv2.resize(img, (1280, 720), interpolation=cv2.INTER_LINEAR)
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 1.5)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 3)
    edges = cv2.Canny(blurred, 60, 140)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
    cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)


def main() -> None:
    p = argparse.ArgumentParser(description="Reproducible OpenCV/COOL benchmark for VisionGuard")
    p.add_argument("--iterations", type=int, default=40)
    p.add_argument("--warmup", type=int, default=5)
    p.add_argument("--output", default="output/benchmark.json")
    args = p.parse_args()

    img = make_input()
    for _ in range(args.warmup):
        workload(img)

    samples_ms = []
    for _ in range(args.iterations):
        t0 = time.perf_counter_ns()
        workload(img)
        samples_ms.append((time.perf_counter_ns() - t0) / 1e6)

    samples_sorted = sorted(samples_ms)
    p95 = samples_sorted[min(len(samples_sorted) - 1, int(len(samples_sorted) * .95))]
    report = {
        "opencv_version": cv2.__version__,
        "cv2_path": str(getattr(cv2, "__file__", "")),
        "cool_active": str(getattr(cv2, "__file__", "")).startswith("/opt/cool"),
        "machine": platform.machine(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "iterations": args.iterations,
        "warmup": args.warmup,
        "input": {"width": 1920, "height": 1080, "seed": 42},
        "workload": ["resize", "cvtColor", "GaussianBlur", "adaptiveThreshold", "Canny", "morphologyEx", "findContours"],
        "mean_ms": round(statistics.mean(samples_ms), 4),
        "median_ms": round(statistics.median(samples_ms), 4),
        "p95_ms": round(p95, 4),
        "throughput_ops_per_s": round(1000.0 / statistics.mean(samples_ms), 3),
        "raw_ms": [round(x, 4) for x in samples_ms],
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
