# Best Use of COOL — Evidence Protocol

## Objective

Produce reproducible evidence that the **claimed core VisionGuard OpenCV workload** executes under COOL on AWS Graviton/Arm and quantify its value against an appropriate baseline.

## Official target environment

Use the OpenCV Marketplace product **Cloud Optimized OpenCV For AWS Graviton4**, whose current Marketplace release is built on OpenCV 5.0 and exposes optimized Python environments under `/opt/cool`.

Recommended final-test principle: use one fixed Graviton4 instance type for both environments so CPU generation, vCPU count and host conditions are comparable.

## Evidence checklist

Record all of the following in `output/final_environment.txt`:

```bash
uname -a
uname -m
cat /etc/os-release
python3 --version
/opt/cool/venvs/python_3.12/bin/python -c 'import cv2; print(cv2.__version__); print(cv2.__file__); print(cv2.getBuildInformation())'
aws ec2 describe-instances --instance-ids "$INSTANCE_ID" --region "$AWS_REGION" --query 'Reservations[0].Instances[0].[InstanceId,InstanceType,ImageId,Architecture]' --output table
```

Expected architecture: `arm64` / `aarch64`.

The `cv2` path for the COOL run must resolve under `/opt/cool`.

## Baseline

On the **same Graviton host**, create a separate vanilla environment:

```bash
./scripts/setup_vanilla_baseline.sh
```

This pins vanilla `opencv-python-headless==5.0.0.93`.

## Run

```bash
./scripts/run_benchmarks.sh
```

Generated evidence:

- `output/baseline.json`
- `output/cool.json`
- `output/benchmark_comparison.json`

## Workload

The benchmark executes VisionGuard-relevant OpenCV operations over a deterministic 1920×1080 input:

- resize;
- color conversion;
- Gaussian blur;
- adaptive Gaussian threshold;
- Canny;
- morphology;
- contour extraction.

Input seed, dimensions, warm-up and iterations are included in the JSON report.

## Final report table

Fill only with measured values:

| Metric | Vanilla OpenCV 5 | COOL / OpenCV 5 | Delta |
|---|---:|---:|---:|
| Mean latency (ms) | TBD | TBD | TBD |
| Median latency (ms) | TBD | TBD | TBD |
| p95 latency (ms) | TBD | TBD | TBD |
| Throughput (workloads/s) | TBD | TBD | TBD |
| EC2 instance | same | same | controlled |
| Architecture | Arm64 | Arm64 | controlled |

## Cost evidence

If reporting cost, document the source and date of the EC2 and Marketplace hourly prices. Convert measured throughput to a transparent metric such as estimated cost per one million workload executions. Do not compare different instance sizes unless the difference is explicitly part of the architecture claim.

## No fabricated results

Vendor speedup claims may motivate the experiment but are **not** project results. The competition report and video should show only measurements produced by the project benchmark.
