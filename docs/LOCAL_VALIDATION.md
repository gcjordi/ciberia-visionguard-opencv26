# Local Build Validation

Validation performed while assembling the reference package:

- Python module compilation: PASS
- Unit/integration test suite: **6 passed**
- FastAPI `/api/health`: PASS
- FastAPI clean demo `/api/analyze`: PASS
- Clean demo agent flow: `VERIFY → OpenCV tool call → ACT`
- Degraded demo agent flow: `VERIFY → OpenCV tool call → HUMAN_REVIEW`
- Human-review resolution endpoint: PASS
- Architecture PNG/SVG generation: PASS

## Runtime caveat

The assembly environment available for this package contained OpenCV **4.13.0**, so the code-level test execution above is a backward-compatibility validation rather than the competition compliance run.

The submitted dependency file pins **OpenCV 5.0.0.93**, whose x86-64 and AArch64 wheels are published on PyPI, and the competition COOL path is designed for the official OpenCV 5-based `/opt/cool` Marketplace environment.

Before final submission, rerun all tests on:

1. vanilla OpenCV 5.0.0.93; and
2. the official COOL/OpenCV 5 AWS Graviton runtime.

Only the final AWS/OpenCV 5 run should be presented as competition compliance evidence.
