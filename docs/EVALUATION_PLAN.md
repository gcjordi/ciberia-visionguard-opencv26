# Evaluation Plan

## 1. Functional correctness

Run:

```bash
pytest -q
```

Required result for the submitted commit: all tests passing.

## 2. Scenario matrix

Create or collect rights-cleared videos across:

- clean / normal illumination;
- low light;
- overexposure;
- blur;
- sensor noise;
- partial occlusion;
- no intrusion;
- localized intrusion;
- scene-wide illumination change;
- subject entering and leaving the zone.

## 3. Ground truth

For each clip, label:

- whether an actual restricted-zone event occurs;
- whether visual evidence is intentionally degraded;
- desired autonomy class: autonomous action allowed vs human review preferred.

Keep labels separate from inference code.

## 4. Primary metrics

### Perception

- precision / recall / F1 for restricted-zone event detection;
- false-positive rate on no-event and scene-wide-change clips.

### Agent behavior

- task success rate;
- false autonomous-action rate;
- human-review recall on degraded/ambiguous cases;
- percentage of VERIFY/RE_OBSERVE cases that invoke an appropriate tool;
- percentage of re-perception calls that change the downstream action when evidence changes;
- trace completeness rate.

### Trust calibration

Report VCTS mean/median distributions for clean vs degraded groups and the overlap between them. Do not present VCTS as a probability unless separately calibrated.

### Runtime

- end-to-end mean/p95 analysis latency;
- COOL benchmark mean/median/p95;
- throughput;
- optional cost-normalized throughput.

## 5. Failure-case reporting

The final report must show at least:

- one false positive or near-miss if observed;
- one low-quality scene;
- one case where re-perception cannot recover trust;
- one limitation of the motion-only reference model.

## 6. Reproducibility metadata

Save:

- git commit hash;
- OpenCV version/path;
- Python version;
- AWS AMI and instance type;
- architecture;
- exact benchmark commands;
- evaluation data manifest and rights/source notes;
- raw JSON results.
