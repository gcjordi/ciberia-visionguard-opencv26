from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("baseline")
    p.add_argument("cool")
    p.add_argument("--output", default="output/benchmark_comparison.json")
    args = p.parse_args()
    b = json.loads(Path(args.baseline).read_text())
    c = json.loads(Path(args.cool).read_text())
    speedup = b["mean_ms"] / c["mean_ms"] if c["mean_ms"] else 0
    latency_reduction = (1 - c["mean_ms"] / b["mean_ms"]) * 100 if b["mean_ms"] else 0
    result = {
        "baseline": b,
        "cool": c,
        "mean_latency_speedup_x": round(speedup, 4),
        "mean_latency_reduction_pct": round(latency_reduction, 2),
        "methodology_note": "Run both environments on the same AWS Graviton4 instance type, image dimensions, seed, warmup and iteration count.",
    }
    Path(args.output).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
