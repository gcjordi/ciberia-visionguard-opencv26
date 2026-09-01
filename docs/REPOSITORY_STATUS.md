# Repository Status Before Final Submission

This repository is deliberately split between **implemented project assets** and **evidence that must come from the final AWS/OpenCV 5 run**.

## Implemented

- [x] FastAPI web application and API.
- [x] OpenCV video-ingestion pipeline.
- [x] motion, contour and restricted-zone evidence.
- [x] Farneback optical-flow temporal evidence.
- [x] image-quality evidence.
- [x] deterministic visual stress tests.
- [x] VCTS trust calculation.
- [x] deterministic agent orchestration.
- [x] agent-selected CLAHE / unsharp / denoise re-perception.
- [x] human-review gate and approval/rejection endpoint.
- [x] structured agent trace.
- [x] optional S3/DynamoDB/CloudWatch integrations.
- [x] Terraform infrastructure.
- [x] AWS CloudShell quick-start script.
- [x] vanilla-vs-COOL benchmark scripts.
- [x] synthetic rights-safe demonstration videos.
- [x] deterministic automated tests.
- [x] architecture and agent-loop diagrams.
- [x] technical report and responsible-use documentation.
- [x] Devpost submission draft and demo-video script.

## Must be completed with real final-run evidence

- [ ] Run the submitted commit under vanilla OpenCV 5.
- [ ] Run the submitted commit on the official AWS COOL/Graviton environment.
- [ ] Record exact region, instance type, AMI, COOL version, OpenCV version and `cv2` path.
- [ ] Run the final COOL benchmark and store raw JSON under `evidence/benchmarks/`.
- [ ] Record representative agent traces under `evidence/traces/`.
- [ ] Capture final screenshots under `evidence/screenshots/`.
- [ ] Complete quantitative evaluation and at least one failure/limitation case.
- [ ] Replace every `TBD` in `DEVPOST_SUBMISSION.md` and `COOL_EVIDENCE.md`.
- [ ] Add final repository URL.
- [ ] Add final HTTPS judge endpoint or arrange the permitted live demonstration.
- [ ] Record and publish the ≤5-minute judge-accessible video.
- [ ] Add the exact submitted Git commit hash to `FINAL_EVIDENCE.md`.

## Rule

Do not replace a `TBD` with an estimated or vendor-reported number. Competition claims must be backed by project measurements from the final environment.
