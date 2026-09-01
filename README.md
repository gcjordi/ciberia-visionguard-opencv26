# CiberIA VisionGuard

**Cognitive Security for Agentic Vision**

[OpenCV AI Competition 2026, powered by AWS](https://opencv26.devpost.com/)

CiberIA VisionGuard is a competition-ready reference implementation that asks a safety question beyond ordinary visual detection:

> **Should an AI agent trust its own visual evidence enough to act?**

The project uses **OpenCV 5** for substantive video analysis and drives a real multi-step agent loop in which visual evidence changes the next tool call and the final action. The AWS competition path is designed for **AWS Graviton/Arm** and the official **Cloud Optimized OpenCV Library (COOL)** environment.

## Competition focus

- **Overall competition** — substantive OpenCV 5 + meaningful AWS deployment.
- **Agentic Vision Award** — perception → decision → OpenCV tool call → re-perception → action/human approval.
- **Best Use of COOL Award** — core OpenCV workload on COOL/Graviton with a reproducible vanilla-vs-COOL benchmark.

## Core concept: Visual Cognitive Trust Score (VCTS)

VisionGuard separates detector confidence from autonomy confidence. It combines five evidence dimensions into a 0–100 **Visual Cognitive Trust Score (VCTS)**:

- detection confidence;
- image quality;
- temporal consistency;
- stress robustness;
- geometric consistency.

The default policy is:

| VCTS | Default policy |
|---:|---|
| 85–100 | `ACT` |
| 65–84 | `VERIFY` |
| 40–64 | `RE_OBSERVE` |
| 0–39 | `HUMAN_REVIEW` |

VCTS is a research heuristic, **not** a calibrated probability of correctness.

## Agentic Vision loop

```text
VIDEO / CAMERA
      │
      ▼
 OpenCV 5 perception
      │
      ▼
 Visual evidence + VCTS
      │
      ▼
 Agent policy decision
      │
      ├── High trust ───────────────► ACT
      │
      └── Uncertain
              │
              ▼
      Select OpenCV tool
      CLAHE / UNSHARP / DENOISE
              │
              ▼
          Re-perceive
              │
          ┌───┴────┐
          ▼        ▼
         ACT   HUMAN REVIEW
```

The agent is deliberately deterministic and auditable. It does not require an LLM to prove agentic behavior: OpenCV output directly determines a later OpenCV operation and downstream action.

## What the MVP implements

1. Video ingestion with OpenCV `VideoCapture`.
2. Motion evidence using Gaussian filtering, frame differencing, thresholding, morphology and contours.
3. Farneback optical flow for temporal evidence.
4. Restricted-zone intersection analysis.
5. Image-quality analysis using sharpness, exposure and contrast measures.
6. Stress testing under blur, low/high illumination, sensor noise and partial occlusion.
7. VCTS calculation and policy selection.
8. Agent-selected OpenCV re-perception using `CLAHE`, `UNSHARP` or `DENOISE`.
9. Explicit human approval/rejection when trust is inadequate.
10. Structured traces showing exactly which visual evidence changed which later decision.

## Repository structure

```text
app/                       FastAPI application, OpenCV pipeline, VCTS and agent loop
benchmarks/                Reproducible vanilla OpenCV vs COOL benchmark
data/                      Rights-safe synthetic demonstration videos
deploy/aws/terraform/      AWS infrastructure as code
docs/                      Technical report, diagrams and Devpost material
evidence/                  Final benchmark, trace and screenshot evidence
scripts/                   Local, AWS, COOL and benchmark automation
tests/                     Deterministic test suite
tools/                     Synthetic demo-video generator
output/                    Generated runtime results
```

## Local quick start

### Requirements

- Python 3.12
- OpenCV 5 runtime from `requirements-dev.txt`

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python tools/generate_demo_video.py --out data
pytest -q
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open:

```text
http://localhost:8000
```

Included demos:

- `data/demo_clean_intrusion.mp4`
- `data/demo_degraded_intrusion.mp4`

The bundled videos are synthetic and contain no biometric identity data or third-party media.

## API

- `GET /api/health` — runtime, OpenCV version and COOL-path status.
- `GET /api/info` — VCTS policy and privacy posture.
- `POST /api/analyze` — analyze a video and return evidence + full agent trace.
- `GET /api/trace/{trace_id}` — inspect the trace held by the current process.
- `POST /api/review/{trace_id}` — resolve a human-review gate.

See [`docs/API.md`](docs/API.md).

## AWS / COOL deployment

The competition deployment is designed around:

- Amazon EC2 Graviton/Arm running the official COOL Marketplace image;
- Amazon S3 for optional short-lived encrypted evidence;
- Amazon DynamoDB for structured traces;
- Amazon CloudWatch for latency/VCTS/action observability;
- AWS IAM with least-privilege instance permissions;
- Terraform for repeatable infrastructure.

For the owner deployment flow, start with [`docs/DEPLOYMENT_AWS.md`](docs/DEPLOYMENT_AWS.md).

For judges or reviewers, use [`docs/JUDGE_QUICKSTART.md`](docs/JUDGE_QUICKSTART.md).

## COOL benchmark

The benchmark compares **the same deterministic 1080p workload on the same Graviton host**:

1. vanilla OpenCV 5 Arm environment;
2. official COOL `/opt/cool` environment.

It records mean, median and p95 latency, throughput, architecture, OpenCV version and the exact `cv2` path.

No performance claim is pre-filled. Final competition numbers must come from the real AWS run and be stored under `evidence/benchmarks/`.

See [`docs/COOL_EVIDENCE.md`](docs/COOL_EVIDENCE.md).

## Required competition evidence

The repository already contains templates for:

- technical report;
- architecture diagram;
- agent workflow diagram;
- reproducible testing instructions;
- OpenCV 5 / AWS deployment documentation;
- COOL benchmark evidence;
- Agentic Vision trace evidence;
- responsible-use and security analysis;
- failure-case evaluation;
- ≤5-minute demo video script;
- Devpost copy-ready submission draft;
- final submission checklist.

Start with [`docs/REPOSITORY_STATUS.md`](docs/REPOSITORY_STATUS.md) to see what is implemented and what must still be replaced with real final-run evidence.

## Responsible-use posture

VisionGuard is a decision-confidence and safety research prototype. The reference implementation does **not** perform face recognition, biometric matching, demographic inference, emotion recognition or persistent identity tracking. Low-trust evidence fails toward additional verification or human review rather than autonomous action.

See [`docs/RESPONSIBLE_USE.md`](docs/RESPONSIBLE_USE.md) and [`docs/SECURITY.md`](docs/SECURITY.md).

## Intellectual property

No open-source license is granted by this repository unless a separate license is added later. See [`NOTICE.md`](NOTICE.md).
