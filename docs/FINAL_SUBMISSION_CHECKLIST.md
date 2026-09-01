# Final Submission Checklist

## Project and code

- [ ] Freeze a submission commit/tag.
- [ ] Confirm `opencv-python-headless==5.0.0.93` in local reference requirements.
- [ ] Confirm COOL runtime uses `/opt/cool` and OpenCV 5.
- [ ] Run `pytest -q` and save output.
- [ ] Generate clean/degraded demos from the submitted code.
- [ ] Remove secrets, keys, private datasets and confidential CiberIA methodology not intended for submission.
- [ ] Confirm repository or archive is judge-accessible.
- [ ] Generate final ZIP from the exact tagged commit.

## AWS

- [ ] COOL Marketplace subscription active.
- [ ] Final EC2 instance is Graviton/Arm.
- [ ] Record instance type, AMI ID, region and architecture.
- [ ] Verify IMDSv2, encrypted EBS and restricted SSH.
- [ ] Verify S3 public access block and lifecycle.
- [ ] Verify DynamoDB trace persistence.
- [ ] Verify CloudWatch metrics.
- [ ] Verify judge endpoint works or arrange live screen-share.
- [ ] Add TLS/access control for any public endpoint.

## COOL special award

- [ ] Record COOL version/build information.
- [ ] Prove `cv2` comes from `/opt/cool`.
- [ ] Run vanilla and COOL benchmark on the same Graviton hardware.
- [ ] Save raw JSON outputs.
- [ ] Calculate performance/cost delta only from measured data.
- [ ] Add results to report and video.

## Agentic Vision special award

- [ ] Export an agent workflow diagram.
- [ ] Capture a trace where OpenCV output changes a later tool call.
- [ ] Capture a trace where later OpenCV output changes ACT/HUMAN_REVIEW.
- [ ] Demonstrate explicit human approval/rejection.
- [ ] Report task success and failure handling.
- [ ] Show observability and human control in the video.

## Evaluation

- [ ] Finalize rights-cleared evaluation set.
- [ ] Save data manifest and labels.
- [ ] Compute perception metrics.
- [ ] Compute agent-behavior metrics.
- [ ] Compare clean vs degraded VCTS distributions.
- [ ] Include at least one failure/limitation.
- [ ] Do not characterize VCTS as a probability unless calibrated.

## Devpost required fields/deliverables

- [ ] Complete `FINAL_EVIDENCE.md`.

- [ ] Project name/tagline/description complete.
- [ ] `Built with` complete.
- [ ] Special Award Consideration: both COOL + Agentic Vision.
- [ ] Repository URL supplied.
- [ ] Testing instructions supplied.
- [ ] Working endpoint supplied if used.
- [ ] Judge-accessible video URL supplied.
- [ ] Video runtime ≤5 minutes.
- [ ] ZIP/archive uploaded.
- [ ] Technical report included.
- [ ] Architecture diagram included.
- [ ] Pinned dependencies included.
- [ ] Build/deploy/test instructions included.
- [ ] Evaluation evidence included.
- [ ] Failure cases/limitations included.
- [ ] Responsible-use considerations included.

## IP / presentation hygiene

- [ ] Confirm every submitted image/video/dataset is owned or appropriately licensed.
- [ ] Keep proprietary CiberIA methods out of Submitted Materials unless intentionally licensed under competition terms.
- [ ] Do not include credentials, private weights or confidential data in report/video/archive.
- [ ] Verify every benchmark statement can be reproduced from raw evidence.
