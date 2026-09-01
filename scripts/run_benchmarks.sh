#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASELINE="${BASELINE_VENV:-$HOME/visionguard-vanilla}"
COOL_PY="/opt/cool/venvs/python_3.12/bin/python"
mkdir -p "$ROOT/output"

"$BASELINE/bin/python" "$ROOT/benchmarks/bench_opencv.py" --iterations 50 --warmup 8 --output "$ROOT/output/baseline.json"
"$COOL_PY" "$ROOT/benchmarks/bench_opencv.py" --iterations 50 --warmup 8 --output "$ROOT/output/cool.json"
"$BASELINE/bin/python" "$ROOT/benchmarks/compare_results.py" "$ROOT/output/baseline.json" "$ROOT/output/cool.json" --output "$ROOT/output/benchmark_comparison.json"
