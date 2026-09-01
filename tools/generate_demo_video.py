from __future__ import annotations

import argparse
from pathlib import Path
import cv2
import numpy as np


def make_video(path: Path, degraded: bool, width: int = 640, height: int = 360, frames: int = 110, fps: int = 20) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(path), fourcc, fps, (width, height))
    rng = np.random.default_rng(123)
    for i in range(frames):
        bg = np.full((height, width, 3), 70, dtype=np.uint8)
        # Structural details make quality and edge metrics meaningful.
        cv2.line(bg, (0, int(height * .75)), (width, int(height * .75)), (105, 105, 105), 2)
        zone_x = int(width * .68)
        cv2.rectangle(bg, (zone_x, 0), (width - 1, height - 1), (82, 67, 67), -1)
        cv2.line(bg, (zone_x, 0), (zone_x, height), (150, 150, 150), 2)
        cv2.putText(bg, "RESTRICTED", (zone_x + 18, 32), cv2.FONT_HERSHEY_SIMPLEX, .6, (185, 185, 185), 1, cv2.LINE_AA)

        x = -70 + int(i * (width + 150) / frames)
        y = int(height * .42)
        # Stylized moving subject (non-biometric).
        cv2.circle(bg, (x + 30, y - 24), 18, (210, 210, 210), -1)
        cv2.rectangle(bg, (x + 10, y - 5), (x + 50, y + 75), (210, 210, 210), -1)
        cv2.line(bg, (x + 10, y + 15), (x - 6, y + 55), (210, 210, 210), 8)
        cv2.line(bg, (x + 50, y + 15), (x + 66, y + 55), (210, 210, 210), 8)

        if degraded and i > 62:
            bg = cv2.convertScaleAbs(bg, alpha=.58, beta=-20)
            bg = cv2.GaussianBlur(bg, (9, 9), 2.0)
            noise = rng.normal(0, 10, bg.shape).astype(np.float32)
            bg = np.clip(bg.astype(np.float32) + noise, 0, 255).astype(np.uint8)
            if 70 <= i <= 88:
                cv2.rectangle(bg, (zone_x + 15, 80), (zone_x + 125, 285), (15, 15, 15), -1)
        writer.write(bg)
    writer.release()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="data")
    args = p.parse_args()
    out = Path(args.out)
    make_video(out / "demo_clean_intrusion.mp4", degraded=False)
    make_video(out / "demo_degraded_intrusion.mp4", degraded=True)
    print(out.resolve())


if __name__ == "__main__":
    main()
