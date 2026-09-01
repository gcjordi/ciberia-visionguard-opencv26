# Competition Compliance Matrix

This matrix maps the published OpenCV AI Competition 2026 requirements to concrete VisionGuard evidence.

| Requirement / rubric item | VisionGuard implementation | Submission evidence |
|---|---|---|
| Substantive OpenCV 5 | VideoCapture, filtering, thresholding, morphology, contours, optical flow, quality analysis, CLAHE, denoise, stress transforms | `app/vision.py`, `/api/health`, technical report |
| Meaningful AWS component | Core OpenCV workload on EC2 Graviton/COOL; S3, DynamoDB, CloudWatch, IAM | Terraform, AWS diagram, live endpoint |
| Technical report | Problem, users, architecture, OpenCV, AWS, evaluation, limitations, responsible use | `docs/TECHNICAL_REPORT.md` |
| Judge-accessible repository/archive | Complete source package; may remain private if judges can access it | repository URL + ZIP |
| Pinned dependencies | Exact runtime/dev pins; COOL-specific requirements | `requirements*.txt` |
| Build/deploy/test instructions | Local and COOL/AWS commands | README + scripts + Terraform |
| Architecture diagram | OpenCV/AWS/COOL/agent components | `docs/architecture.svg`, `.png`, Mermaid source |
| Working endpoint or live screen-share | FastAPI + Nginx deploy path | deployed URL or arranged screen-share |
| Video ≤5 minutes | Script includes team, working app, architecture, results | `docs/DEMO_SCRIPT.md` |
| Evaluation evidence | deterministic functional tests, demo scenarios, benchmark tooling | `tests/`, `benchmarks/`, `output/` |
| Failure cases / limitations | explicit low-trust/human-review scenario and report limitations | degraded demo + report |
| Responsible use | no biometrics, synthetic data, retention controls, human gate | `docs/RESPONSIBLE_USE.md` |
| COOL executes core workload on Arm | `/opt/cool` Python runtime on official Graviton4 AMI | health output + benchmark JSON + screenshot/video |
| COOL version / AWS configuration | recorded in evidence template | `docs/COOL_EVIDENCE.md` |
| Reproducible COOL baseline comparison | same Graviton instance, same input/seed/iterations; vanilla vs COOL venv | `scripts/run_benchmarks.sh` |
| Agent perception→decision→action | VCTS decision triggers OpenCV tool call and final action | `app/agent.py`, trace JSON, diagram |
| Visual result changes later decision/tool/action | uncertainty selects CLAHE/UNSHARP/DENOISE; re-analysis controls ACT/HUMAN_REVIEW | live trace + `docs/AGENTIC_TRACE.md` |
| Task success / failure handling | clean and degraded scenarios; API errors and human gating | tests + evaluation report |
| Observability | structured trace + CloudWatch metrics | trace JSON + AWS metrics |
| Human control | explicit approval/reject endpoint | `/api/review/{trace_id}` |
| Security | IAM role, IMDSv2, encrypted EBS/S3, restricted SSH, ephemeral uploads | Terraform + `docs/SECURITY.md` |
| UX | web UI exposes score, decisions, trace, raw evidence, human control | live demo |
| Documentation/presentation | report, diagrams, API, testing, video plan | `docs/` |

## Special-award opt-in

Select both:

- **Best Use of COOL Award**
- **Agentic Vision Award**

## Items that cannot be truthfully completed before the AWS build/final submission

Do **not** fabricate these. Fill them after the real deployment:

- final public/private repository URL;
- final working endpoint URL;
- final YouTube/Vimeo video URL;
- exact regional COOL AMI ID;
- exact EC2 instance used for final benchmark;
- measured COOL/vanilla latency, throughput and cost values;
- final evaluation dataset size and empirical metrics;
- prior hackathon/competition history if any.
