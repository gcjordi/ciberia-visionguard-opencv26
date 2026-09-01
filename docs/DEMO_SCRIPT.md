# Judge Video Script — Maximum 5 Minutes

Target length: **4:30–4:50**. The final video must be public or unlisted and judge-accessible.

## 0:00–0:25 — Team + problem

On camera:

“I'm Jordi Garcia Castillón, and this is CiberIA VisionGuard: a cognitive-security layer for agentic vision. The question is not only whether an AI can see an event, but whether it should trust its own visual evidence enough to act.”

Show the title and one-sentence problem.

## 0:25–0:55 — Architecture

Show `docs/architecture.png`.

Explain:

- OpenCV 5/COOL runs the core visual workload on AWS Graviton;
- VCTS evaluates trust;
- the agent can invoke another OpenCV tool;
- uncertain cases are stopped by human control;
- S3/DynamoDB/CloudWatch provide evidence, trace and observability.

## 0:55–2:05 — Clean scenario

Show `/api/health` first so the video captures:

- OpenCV 5 version;
- COOL path under `/opt/cool`;
- AWS endpoint.

Upload `demo_clean_intrusion.mp4`.

Show:

1. restricted-zone evidence;
2. VCTS;
3. initial VERIFY decision;
4. agent-selected OpenCV tool call;
5. new perception result;
6. final ACT decision.

Emphasize: **the first visual result changes the next tool call; the second visual result changes the action.**

## 2:05–3:15 — Degraded scenario + human control

Upload `demo_degraded_intrusion.mp4`.

Show low/unstable evidence and stress-test results. Show the agent invoking an additional OpenCV tool. Then show that the original stress-robustness safety gate prevents autonomous action even if post-processing improves some metrics.

The UI must display **HUMAN_REVIEW**. Click Approve or Reject and show the trace append the human decision.

## 3:15–3:55 — COOL evidence

Terminal:

```bash
uname -m
/opt/cool/venvs/python_3.12/bin/python -c 'import cv2; print(cv2.__version__, cv2.__file__)'
cat output/benchmark_comparison.json
```

Display the actual measured vanilla-vs-COOL values. State the EC2 Graviton instance type and that both runs used the same hardware/input/seed/iteration count.

## 3:55–4:25 — Evaluation and responsible operation

Show:

- passing tests;
- empirical task metrics from the final evaluation;
- one failure/limitation;
- no face recognition / synthetic demo data;
- ephemeral upload default;
- human-control gate.

## 4:25–4:45 — Closing

“VisionGuard treats perceptual uncertainty as a cybersecurity and autonomy-control problem. It makes visual trust explicit, measurable and actionable before an AI agent does something in the world.”

End with project name, repository and demo URL.

## Mandatory recording checklist

Before publishing, verify the video visibly contains:

- [ ] team/member introduction;
- [ ] working application;
- [ ] architecture;
- [ ] principal results;
- [ ] OpenCV 5/COOL runtime evidence;
- [ ] agentic trace;
- [ ] AWS deployment;
- [ ] failure/limitation;
- [ ] actual benchmark result;
- [ ] runtime ≤5:00.
