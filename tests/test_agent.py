from pathlib import Path

from app.agent import run_agent
from tools.generate_demo_video import make_video


def test_agent_produces_trace(tmp_path: Path):
    video = tmp_path / "demo.mp4"
    make_video(video, degraded=False, width=480, height=270, frames=80, fps=20)
    out = run_agent(str(video), "demo.mp4").result
    assert len(out.trace) >= 3
    assert out.final_action in {"ACT", "HUMAN_REVIEW", "IGNORE"}
    if out.vcts:
        assert 0 <= out.vcts.score <= 100
