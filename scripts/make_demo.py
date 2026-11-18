"""Build reports/media/demo.mp4: a ~40 s walkthrough made only from pipeline outputs.

    uv run python scripts/make_demo.py
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from replay.common import Config  # noqa: E402
from replay.trace import trace  # noqa: E402

BG, FG, ACC = "#0b0f14", "#e2e8f0", "#60a5fa"


def card(path: Path, title: str, body: str, size=10.5):
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor=BG)
    fig.text(0.04, 0.92, title, color=ACC, fontsize=22, weight="bold", family="DejaVu Sans")
    fig.text(0.04, 0.86, body, color=FG, fontsize=size, family="DejaVu Sans Mono", va="top")
    fig.savefig(path, facecolor=BG)
    plt.close(fig)


def clip(img: Path, secs: float, out: Path):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-t", str(secs), "-i", str(img),
                    "-vf", "scale=1280:720,format=yuv420p", "-r", "10", "-c:v", "libx264", str(out)], check=True)


def main():
    cfg = Config.load()
    tmp = Path(tempfile.mkdtemp())
    reg = (ROOT / "reports" / "regression_pp-kitti-v1_vs_pp-kitti-v2.md").read_text(encoding="utf-8")
    head = reg.split("## Headline")[1].split("## What got worse")[0].strip().splitlines()
    worse = reg.split("## What got worse")[1].split("## What got better")[0].strip().splitlines()[:7]
    cards = [
        ("av2-replay", "Mini perception replay & recompute pipeline\n\n"
         "Argoverse 2 logs  ->  Parquet lake + MCAP\n"
         "Ray recompute: PointPillars (KITTI ckpt) x 2 model versions\n"
         "Per-frame / class / distance metrics, every number traceable to frame + box\n"
         "Regression diff  ->  Foxglove overlays\n\n"
         "$ uv run replay all", 5),
        ("1 command, 6 stages", "\n".join([
            "==> download    4 AV2 val logs from public S3 (lidar, poses, GT, camera, map)",
            "==> ingest      628 sweeps, 73k GT cuboids -> Parquet; timestamps verified",
            "==> recompute   Ray, 1 task per scene, checkpointed + resumable",
            "==> evaluate    matches.parquet: 1 row per box, with a failure reason",
            "==> export      data/mcap/<log>.mcap: lidar, camera, GT, preds (TP/FP), misses",
            "==> regress     reports/regression_v1_vs_v2.md", ]), 5),
        ("Regression: v1 -> v2", "\n".join(head[1:]).replace("**", "") + "\n\nWhat got worse:\n" + "\n".join(worse[2:]).replace("**", ""), 7),
        ("Trace: why did cyclists collapse?", trace(cfg, "pp-kitti-v2", cls="CYCLIST", status="FP", top=4).split("\n  boxes in worst")[0], 7),
        ("Root cause (ablation)", "\n".join([
            "version        change                 cyclist mAP   peds->cyclist FPs",
            "v1             1 forward pass             0.589            36",
            "v2-rot         4 rotated passes           0.665           193",
            "v2-sweeps      3-sweep stacking           0.073           199",
            "v2             both                       0.130           541",
            "",
            "Sweep stacking smears walking pedestrians into cyclist-shaped blobs.",
            "Recommendation: ship v2-rot (360 deg), drop multi-sweep.",
            "",
            "Also traced: a 20-pt 'precision drop' = unlabelled parked cars off-road.",
            "Fix: AV2 drivable-area ROI filter (now default). See docs/DISCREPANCY.md", ]), 7),
    ]
    parts = []
    for i, (t, b, s) in enumerate(cards):
        png, mp4 = tmp / f"c{i}.png", tmp / f"c{i}.mp4"
        card(png, t, b, size=10 if len(b) > 900 else 12)
        clip(png, s, mp4)
        parts.append(mp4)
    bev = ROOT / "reports" / "media" / "review_2e3f2ae7.mp4"
    bev_clip = tmp / "bev.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "1.0", "-t", "9", "-i", str(bev),
                    "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=0x0b0f14,format=yuv420p",
                    "-r", "10", "-c:v", "libx264", str(bev_clip)], check=True)
    parts.append(bev_clip)
    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts))
    out = ROOT / "reports" / "media" / "demo.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-c:v", "libx264", "-crf", "24", "-pix_fmt", "yuv420p", str(out)], check=True)
    shutil.rmtree(tmp)
    print("wrote", out)


if __name__ == "__main__":
    main()
