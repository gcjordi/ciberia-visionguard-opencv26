# CiberIA VisionGuard — Technical Report

## 1. Executive summary

CiberIA VisionGuard is a cognitive-security layer for agentic visual AI. The system addresses a narrow but important safety question: **when an AI system sees something, how much should it trust that visual conclusion before acting?**

The prototype uses OpenCV 5 for substantive image/video analysis and implements a multi-step perception–decision–action loop. A **Visual Cognitive Trust Score (VCTS)** converts observable visual quality, temporal consistency, detection strength, stress robustness and geometry into an explicit autonomy gate. When evidence is uncertain, the agent chooses another OpenCV tool and re-perceives the scene. When evidence remains inadequate, autonomous action is withheld and a human decision is required.

The competition deployment uses the official OpenCV Cloud Optimized OpenCV Library (COOL) on AWS Graviton/Arm, with AWS services for evidence storage, trace persistence, observability and least-privilege access.

## 2. Problem

Computer-vision systems frequently expose confidence values from individual detectors, but that value alone does not represent the trustworthiness of the **whole perceptual situation**. A detection can be affected by poor illumination, blur, sensor noise, occlusion, sudden scene-wide change, unstable geometry or contradictory temporal evidence.

For agentic and Physical AI this becomes an action-safety problem: the visual result may trigger a tool call, alert, physical action or workflow escalation. A robust system should explicitly distinguish between:

- “I detected an event.”
- “The evidence is good enough to act autonomously.”

VisionGuard makes that distinction operational and auditable.

## 3. Target users

The reference use case is restricted-zone safety monitoring, but the design generalizes to:

- industrial inspection;
- infrastructure and utilities monitoring;
- robotics and autonomous inspection;
- safety operations;
- visual troubleshooting;
- AI assurance and security evaluation.

The prototype is not designed for biometric identification, behavioral profiling or mass surveillance.

## 4. System architecture

### 4.1 Runtime components

1. **Web/API layer** — FastAPI receives short videos and exposes evidence and human-review controls.
2. **OpenCV 5 perception engine** — reads video, extracts motion/geometry/quality/temporal features and runs degradation tests.
3. **VCTS trust engine** — converts evidence to a 0–100 visual trust score.
4. **Agent orchestrator** — chooses a next OpenCV tool or action from the evidence.
5. **Human-control gate** — prevents autonomous action when required thresholds are not met.
6. **AWS evidence/trace layer** — S3 (optional evidence), DynamoDB (trace), CloudWatch (metrics), IAM (least privilege).
7. **COOL Arm path** — core OpenCV workload runs on the official COOL Graviton AMI.

See `docs/architecture.svg` and `docs/diagrams/architecture.mmd`.

## 5. Substantive OpenCV 5 implementation

### 5.1 Video ingestion

`cv2.VideoCapture` decodes the incoming stream. Frames are sampled deterministically to bound runtime for the demo.

### 5.2 Motion evidence

For consecutive sampled frames:

1. convert to grayscale;
2. Gaussian blur;
3. `absdiff`;
4. binary threshold;
5. morphological close/dilate;
6. `findContours`;
7. compute the dominant motion bounding box and area;
8. test intersection with the configured restricted zone.

A global-change penalty reduces confidence when a large fraction of the frame changes simultaneously, which is more consistent with illumination/sensor disturbance than localized object motion.

### 5.3 Temporal evidence

Farneback optical flow (`calcOpticalFlowFarneback`) provides a separate temporal-motion signal. The trust model also considers recent persistence of motion and restricted-zone state.

### 5.4 Image quality

The pipeline measures:

- sharpness via Laplacian variance;
- exposure/brightness via mean luma;
- contrast via luma standard deviation.

These values are normalized to [0,1].

### 5.5 Visual cognitive stress tests

For the selected event pair, the same motion decision is repeated under:

- Gaussian blur;
- low light;
- high light;
- deterministic sensor noise;
- partial occlusion.

Each perturbation produces a decision-preservation value and geometric similarity. Their aggregate becomes the **stress robustness** component of VCTS.

### 5.6 Agent-selected re-perception

When VCTS is not sufficient for immediate action, the agent selects a tool based on the observed failure mode:

- low brightness/contrast → `CLAHE`;
- low sharpness → `UNSHARP`;
- poor robustness → `DENOISE`.

The tool transforms the frame pair and OpenCV analysis is executed again. The new evidence can change the final system action.

This is the key Agentic Vision property: **the first OpenCV result controls a later OpenCV tool call, and the second result controls the action.**

## 6. Visual Cognitive Trust Score (VCTS)

### 6.1 Components

Let all components be normalized to [0,1]:

- `D` = detection confidence;
- `Q` = image-quality score;
- `T` = temporal consistency;
- `R` = stress robustness;
- `G` = geometric consistency.

Reference implementation:

`VCTS = 100 × (0.25D + 0.20Q + 0.20T + 0.20R + 0.15G)`

### 6.2 Policy

- **85–100:** ACT
- **65–84:** VERIFY
- **40–64:** RE-OBSERVE
- **0–39:** HUMAN REVIEW

A second safety gate applies after verification: a high post-processing VCTS cannot erase evidence that the original observation was highly unstable under stress. In the reference build, initial stress robustness must also be at least 0.70 before verification can authorize autonomous action.

These thresholds are research defaults and are deliberately documented as calibration parameters rather than universal safety values.

## 7. Agentic workflow

The trace records five explicit stage types:

- `PERCEPTION`
- `DECISION`
- `TOOL_CALL`
- `ACTION`
- `HUMAN_CONTROL`

A qualifying trace therefore shows, in sequence:

1. OpenCV visual output;
2. the trust decision;
3. selected OpenCV re-analysis tool;
4. new OpenCV evidence;
5. final action or human-control request.

See `docs/AGENTIC_TRACE.md`.

## 8. AWS deployment

### 8.1 Final competition topology

**Compute:** EC2 Graviton4 with official COOL Marketplace AMI. The Marketplace documentation exposes optimized Python environments under `/opt/cool/venvs/`.

**Evidence:** S3 bucket with public access blocked, AES-256 server-side encryption and seven-day lifecycle deletion in the reference Terraform configuration.

**Trace:** DynamoDB pay-per-request table keyed by `trace_id`.

**Observability:** CloudWatch custom metrics for analysis latency, VCTS and action counts.

**Identity:** an EC2 instance role has only the S3 object, DynamoDB item and CloudWatch metric permissions required by the application.

**Host security:** encrypted EBS, IMDSv2 required, SSH restricted by administrator CIDR, systemd hardening, uploads temporary by default.

### 8.2 Meaningful AWS component

The core visual workload itself runs on AWS EC2/Graviton via COOL, so AWS is not merely storage or hosting. S3, DynamoDB, CloudWatch and IAM support reproducible operation and judge evidence.

## 9. COOL integration

For the Best Use of COOL path, the claimed core image/video workload must execute under the official `/opt/cool` environment on Graviton/Arm. The project verifies this at runtime by reporting the exact `cv2.__version__` and `cv2.__file__` path.

The benchmark uses operations specifically relevant to VisionGuard and common COOL acceleration targets: resize, Gaussian blur, adaptive thresholding, Canny, morphology and contour extraction.

No fabricated performance numbers are included. The final report must insert actual measured results from the AWS run.

## 10. Reproducible evaluation

### 10.1 Functional tests

`pytest` covers:

- VCTS weights and thresholds;
- restricted-zone motion detection;
- bounded image quality scores;
- five stress-test modes;
- complete agent trace generation.

### 10.2 Demo scenarios

Synthetic videos are generated deterministically by `tools/generate_demo_video.py`. This provides repeatability and eliminates third-party data-rights ambiguity.

### 10.3 Agentic metrics

The final evaluation should report, at minimum:

- event-detection precision/recall on the chosen test set;
- task success rate;
- false autonomous-action rate;
- human-review rate;
- percentage of uncertain cases in which re-perception changes the decision appropriately;
- trace completeness;
- mean/p95 end-to-end latency.

### 10.4 COOL metrics

Record for both vanilla and COOL environments:

- exact AMI/instance type;
- architecture (`aarch64`);
- exact OpenCV version and `cv2` path;
- fixed benchmark input dimensions and seed;
- warm-up and measured iterations;
- mean, median and p95 latency;
- throughput;
- optional EC2 cost normalization after measured runtime.

## 11. Failure handling

The system explicitly handles:

- unsupported video formats;
- uploads above the configured size;
- unreadable videos;
- no detected restricted-zone event;
- low-trust evidence;
- failed S3/DynamoDB/CloudWatch calls without causing unsafe visual action;
- a pending human-review state.

AWS persistence failures do not upgrade a visual action. They are observability/storage failures, not trust evidence.

## 12. Security

- no embedded AWS credentials;
- IAM role rather than long-lived keys on EC2;
- optional API key gate;
- input size and extension allow-list;
- sanitized source name;
- temporary upload deletion by default;
- S3 public access block and encryption;
- short S3 lifecycle;
- encrypted EBS;
- IMDSv2 required;
- SSH CIDR restriction;
- systemd sandboxing controls;
- traceable human approval.

## 13. Responsible use

The prototype intentionally avoids face recognition and identity inference. The included data is synthetic. A production deployment must define a lawful purpose, establish camera/data governance, calibrate VCTS thresholds for the actual domain, test bias/failure modes, set retention limits and preserve human override for consequential actions.

The system must not be represented as proving that an event is safe or unsafe. VCTS is an evidence-quality/trust heuristic for the demonstrated workflow, not a universal probability of correctness.

## 14. Limitations

- reference perception is motion/geometric rather than semantic object recognition;
- single-camera fixed-zone assumption;
- synthetic test data is necessary for reproducibility but does not represent all real conditions;
- stress tests are illustrative, not exhaustive adversarial robustness evaluation;
- thresholds require domain-specific calibration;
- the final COOL benefit must be measured on the actual AWS Marketplace AMI and cannot be inferred from vendor claims.

## 15. Demonstration

The judge video should show:

1. active OpenCV 5/COOL runtime;
2. clean scenario;
3. degraded scenario;
4. trace where visual evidence triggers another OpenCV tool call;
5. human approval gate;
6. AWS architecture;
7. actual benchmark comparison;
8. principal limitations.

See `docs/DEMO_SCRIPT.md`.

## 16. Reproducibility

A judge should be able to:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python tools/generate_demo_video.py --out data
pytest -q
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

For the COOL path, use the official Marketplace AMI and follow `docs/COOL_EVIDENCE.md`.

## 17. References

- OpenCV 5: https://docs.opencv.org/5.0/
- OpenCV COOL: https://opencv.org/COOL/
- COOL AWS Graviton4 Marketplace: https://aws.amazon.com/marketplace/pp/prodview-fdvbfiewzuehs
- AWS Graviton resources: https://aws.amazon.com/ec2/graviton/resources/
- Competition: https://opencv26.devpost.com/
