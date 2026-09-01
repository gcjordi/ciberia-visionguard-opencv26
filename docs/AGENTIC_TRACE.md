# Agentic Vision Evidence

The Agentic Vision requirement is satisfied by a traceable control loop in which **OpenCV output changes a subsequent plan/tool call/action**.

## Qualifying flow

```text
PERCEPTION
  OpenCV detects restricted-zone motion and measures image quality/temporal evidence
        ↓
DECISION
  VCTS = 65–84 → VERIFY
        ↓
TOOL_CALL
  Agent observes low brightness/contrast → selects CLAHE
        ↓
PERCEPTION
  OpenCV reprocesses the same evidence and produces a new VCTS
        ↓
ACTION
  if trust gates pass → ACT
  otherwise → HUMAN_REVIEW
```

## What the video should visibly prove

1. Show the initial OpenCV evidence and VCTS.
2. Show that the initial decision is not already final.
3. Show the selected OpenCV tool and the reason it was chosen.
4. Show the second visual result.
5. Show that the second result changes the final action.
6. In the degraded case, show the human approval request and resolve it explicitly.

## Example trace produced by the current code

The exact values depend on the active OpenCV build and encoded input, so use the real demo output rather than hard-coding scores in the submission.

```json
{
  "stage": "DECISION",
  "data": {"action": "VERIFY", "vcts": "<measured>"}
}
{
  "stage": "TOOL_CALL",
  "data": {"tool": "CLAHE", "reason": "<measured visual evidence>"}
}
{
  "stage": "PERCEPTION",
  "data": {"tool": "CLAHE", "vcts": "<measured after re-analysis>"}
}
{
  "stage": "ACTION",
  "data": {"action": "ACT or HUMAN_REVIEW"}
}
```

This evidence should be exported/screenshot from the final AWS/COOL runtime.
