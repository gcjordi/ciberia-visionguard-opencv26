# Judge / Reviewer Quick Start

This document gives reviewers the shortest reproducible path through the project.

## What to verify

VisionGuard is intended to demonstrate four concrete properties:

1. OpenCV 5 performs substantive image/video analysis.
2. OpenCV output changes a later agent decision and OpenCV tool call.
3. low-trust evidence can gate autonomous action behind human approval.
4. the core OpenCV workload can be run and benchmarked with COOL on AWS Graviton/Arm.

## Local functional test

Requirements: Python 3.12.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000`.

Use the bundled synthetic videos:

```text
data/demo_clean_intrusion.mp4
data/demo_degraded_intrusion.mp4
```

## API health

```bash
curl http://localhost:8000/api/health
```

The final AWS competition endpoint should report an OpenCV 5 runtime. The COOL deployment should additionally show a `cv2` path from `/opt/cool`.

## Agentic Vision evidence

For each analysis, inspect the returned `trace` array. Relevant stages are:

```text
PERCEPTION
DECISION
TOOL_CALL
PERCEPTION / RE-PERCEPTION
ACTION
HUMAN_CONTROL (when required)
```

A qualifying trace should show that measured visual evidence caused a later OpenCV verification tool to be selected and that the re-perception result then affected `ACT` vs `HUMAN_REVIEW`.

See [`AGENTIC_TRACE.md`](AGENTIC_TRACE.md).

## Human-control test

When an analysis returns `requires_human_approval: true`, use the web UI or:

```http
POST /api/review/{trace_id}
```

with:

```json
{
  "decision": "approve",
  "reviewer": "judge-demo",
  "note": "Manual review test"
}
```

Use `reject` instead of `approve` to test the negative path.

## COOL evidence

On the official AWS Graviton/COOL host:

```bash
bash scripts/setup_vanilla_baseline.sh
bash scripts/run_benchmarks.sh
```

Review:

```text
output/baseline.json
output/cool.json
output/benchmark_comparison.json
```

The comparison is valid only when both environments use the same host, input dimensions, seed, warm-up and iteration count.

See [`COOL_EVIDENCE.md`](COOL_EVIDENCE.md).

## Full documentation

- [`TECHNICAL_REPORT.md`](TECHNICAL_REPORT.md)
- [`COMPLIANCE_MATRIX.md`](COMPLIANCE_MATRIX.md)
- [`EVALUATION_PLAN.md`](EVALUATION_PLAN.md)
- [`RESPONSIBLE_USE.md`](RESPONSIBLE_USE.md)
- [`SECURITY.md`](SECURITY.md)
