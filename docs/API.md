# API Reference

## `GET /api/health`

Reports application version, OpenCV version, OpenCV 5 compliance and whether the active `cv2` path appears to come from `/opt/cool`.

## `GET /api/info`

Reports project concept, VCTS thresholds, restricted-zone configuration and privacy posture.

## `POST /api/analyze`

Multipart field: `file`.

Accepted extensions: `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`.

Returns:

- trace ID;
- OpenCV runtime details;
- selected frame/evidence;
- quality metrics;
- stress-test results;
- VCTS breakdown;
- initial and final action;
- selected verification tool;
- human-review status;
- full agent trace;
- AWS persistence/observability result.

## `GET /api/trace/{trace_id}`

Returns the current in-process trace copy. DynamoDB persistence is used on AWS when configured.

## `POST /api/review/{trace_id}`

JSON:

```json
{
  "decision": "approve",
  "reviewer": "judge-demo",
  "note": "Optional note"
}
```

Only traces requiring human approval can be resolved.
