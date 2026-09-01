# Devpost Final Submission — Copy-Ready Draft

> Replace every `TBD` with final measured/hosted evidence before submission.

## Project name

**CiberIA VisionGuard**

## Tagline

**Cognitive security for agentic vision: know when AI should not trust what it sees.**

## Built with

- OpenCV 5
- Cloud Optimized OpenCV Library (COOL)
- Python
- FastAPI
- AWS EC2 Graviton
- Amazon S3
- Amazon DynamoDB
- Amazon CloudWatch
- AWS IAM
- Terraform

## Project description

### Inspiration

Agentic and Physical AI systems increasingly act on visual evidence. Traditional computer-vision confidence values tell us whether a detector thinks it saw something, but not whether the complete visual situation is reliable enough for an autonomous action. Blur, low light, sensor noise, occlusion, temporal instability and scene-wide changes can all produce brittle decisions.

CiberIA VisionGuard explores a cognitive-security question: **does the AI know when it should not trust what it sees?**

### What it does

VisionGuard places a trust layer between OpenCV perception and an agent action. OpenCV 5 analyzes a video stream, detects localized motion entering a restricted zone, measures quality and temporal evidence, and stress-tests the decision under visual degradations.

The system calculates a **Visual Cognitive Trust Score (VCTS)** from detection confidence, image quality, temporal consistency, stress robustness and geometric consistency.

The score governs a multi-step agent loop:

- high trust → ACT;
- uncertain evidence → invoke another OpenCV tool and re-perceive;
- insufficient trust → withhold autonomous action and request human approval.

This means the vision result is not merely explained by a chatbot. It directly changes a later OpenCV tool call and the final system action.

### How we built it

The core perception engine uses OpenCV 5 for video decoding, Gaussian filtering, frame differencing, thresholding, morphology, contours, optical flow, Laplacian quality analysis, CLAHE, denoising and perturbation-based stress tests.

The agent orchestrator is deterministic and auditable. It selects a verification tool based on measured visual failure modes and emits a step-by-step trace of PERCEPTION, DECISION, TOOL_CALL, ACTION and HUMAN_CONTROL events.

The AWS competition deployment runs the core OpenCV workload on the official COOL Marketplace AMI on AWS Graviton/Arm. S3 optionally stores short-lived encrypted evidence, DynamoDB stores traces, CloudWatch records latency/VCTS/action metrics, IAM uses least privilege, and Terraform makes the deployment reproducible.

### Agentic Vision evidence

In the clean demonstration, initial evidence triggers a VERIFY decision. The agent selects an additional OpenCV operation, re-runs perception and can authorize the alert only if the trust gates pass.

In the degraded demonstration, visual stress instability causes the system to withhold autonomous action and request explicit human approval.

The trace therefore demonstrates a true perception → decision/tool call → re-perception → action loop.

### COOL evidence

The final benchmark runs the same deterministic OpenCV 5 workload in two environments on the same Graviton host:

- vanilla OpenCV 5 Arm wheel;
- official COOL `/opt/cool` environment.

Measured result: **TBD**.

Final environment: **TBD EC2 instance / AMI / region**.

### Challenges

The central challenge was avoiding a superficial “AI explains a vision result” architecture. VisionGuard instead had to make uncertainty operational: image/video evidence must alter the next OpenCV computation and determine whether autonomous action remains permitted.

A second challenge was designing a benchmark that measures COOL fairly. The repository therefore controls hardware, input seed, dimensions, warm-up and iteration count, and records the exact OpenCV path and version.

### Accomplishments

- substantive OpenCV 5 pipeline;
- explicit VCTS trust model;
- agent-selected OpenCV re-perception;
- human-in-the-loop safety gate;
- reproducible AWS/Graviton/COOL deployment;
- deterministic stress tests and synthetic demo data;
- trace and observability designed for judging and reproducibility.

### What we learned

A detector confidence score and an autonomy confidence decision are different concepts. By separating perceptual evidence from the policy that determines whether an agent may act, computer vision becomes easier to audit, stress-test and govern.

### What's next

Future work includes semantic detectors, multi-camera evidence, domain-calibrated VCTS, richer adversarial vision tests, policy-specific approval workflows, and integration with broader CiberIA cognitive-security evaluation modules.

## Special Award Consideration

Select both:

- **Best Use of COOL Award**
- **Agentic Vision Award**

## Repository URL — required

`TBD_REPOSITORY_URL`

## Testing instructions — required

```text
Local validation:
1. Use Python 3.12.
2. python3.12 -m venv .venv
3. source .venv/bin/activate
4. pip install -r requirements-dev.txt
5. python tools/generate_demo_video.py --out data
6. pytest -q
7. uvicorn app.main:app --host 0.0.0.0 --port 8000
8. Open http://localhost:8000 and upload data/demo_clean_intrusion.mp4 and data/demo_degraded_intrusion.mp4.

COOL/AWS validation:
1. Use the official Cloud Optimized OpenCV for AWS Graviton4 Marketplace AMI.
2. Verify /api/health reports OpenCV 5 and cv2 loaded from /opt/cool.
3. Run ./scripts/setup_vanilla_baseline.sh.
4. Run ./scripts/run_benchmarks.sh.
5. Inspect output/baseline.json, output/cool.json and output/benchmark_comparison.json.
6. The degraded scenario should demonstrate a human-review gate; resolve it in the UI to append the human-control trace.
```

## Working web endpoint

`TBD_WORKING_ENDPOINT`

## Video URL — required, ≤5 minutes

`TBD_YOUTUBE_OR_VIMEO_URL`

## ZIP/archive — required

Upload the final archive generated from the submitted commit. Complete `FINAL_EVIDENCE.md` with the exact commit hash and measured evidence before creating the final ZIP.
