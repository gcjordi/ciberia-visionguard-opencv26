.PHONY: install dev demo test run benchmark

install:
	python3 -m pip install -r requirements.txt

dev:
	python3 -m pip install -r requirements-dev.txt

demo:
	python3 tools/generate_demo_video.py --out data

test:
	pytest -q

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

benchmark:
	python3 benchmarks/bench_opencv.py --output output/benchmark.json
