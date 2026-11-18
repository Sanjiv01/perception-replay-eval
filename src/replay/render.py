"""Render a bird's-eye review video (one panel per model) for a log: GT, TP, FP, FN overlaid on lidar."""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Polygon

from . import lake
from .common import Config, log
from .evaluate import gt_table

C = {"gt": "#22c55e", "TP": "#3b82f6", "FP": "#ef4444", "FN": "#f59e0b"}


def _corners(x, y, l, w, yaw):
    c, s = np.cos(yaw), np.sin(yaw)
    d = np.array([[l, w], [-l, w], [-l, -w], [l, -w]]) / 2
    return np.stack([x + d[:, 0] * c - d[:, 1] * s, y + d[:, 0] * s + d[:, 1] * c], 1)


def render_log(cfg: Config, log_id: str, models: list[str], out: Path | None = None, lim=50, fps=10) -> Path:
    thr = cfg.ev["tp_threshold_m"]
    sweeps = lake.load_sweeps(cfg.dir("lake"), log_id)
    gt, _ = gt_table(cfg)
    gt = gt[gt.log_id == log_id]
    per = {}
    for m in models:
        p = pd.read_parquet(lake.predictions_path(cfg, m), filters=[("log_id", "=", log_id)]).dropna(subset=["pred_id"])
        mt = pd.read_parquet(lake.eval_dir(cfg, m) / "matches.parquet", filters=[("log_id", "=", log_id)])
        mt = mt[mt.threshold_m == thr]
        p = p.merge(mt[mt.status != "FN"][["pred_id", "status"]], on="pred_id", how="inner")
        fn = mt[mt.status == "FN"][["gt_id"]].merge(gt, on="gt_id")
        per[m] = (dict(tuple(p.groupby("timestamp_ns"))), dict(tuple(fn.groupby("timestamp_ns"))))
    gt_by = dict(tuple(gt.groupby("timestamp_ns")))
    tmp = Path(tempfile.mkdtemp())
    ts_all = sorted(sweeps)
    for k, ts in enumerate(ts_all):
        fig, axes = plt.subplots(1, len(models), figsize=(7 * len(models), 7.4), dpi=90, facecolor="#0b0f14")
        axes = np.atleast_1d(axes)
        pts = sweeps[ts]
        pts = pts[(np.abs(pts[:, 0]) < lim) & (np.abs(pts[:, 1]) < lim) & (pts[:, 2] > 0.2)]
        for ax, m in zip(axes, models):
            ax.set_facecolor("#0b0f14")
            ax.scatter(pts[:, 0], pts[:, 1], s=0.15, c="#64748b", linewidths=0)
            g = gt_by.get(ts)
            if g is not None:
                for r in g.itertuples():
                    ax.add_patch(Polygon(_corners(r.tx_m, r.ty_m, r.length_m, r.width_m, r.yaw), fill=False, ec=C["gt"], lw=0.8))
            pb, fb = per[m]
            p = pb.get(ts)
            n = {"TP": 0, "FP": 0, "FN": 0}
            if p is not None:
                for r in p.itertuples():
                    n[r.status] += 1
                    ax.add_patch(Polygon(_corners(r.x, r.y, r.length, r.width, r.yaw), fill=True, alpha=0.45, fc=C[r.status], ec=C[r.status], lw=0.8))
            f = fb.get(ts)
            if f is not None:
                n["FN"] = len(f)
                ax.scatter(f.tx_m, f.ty_m, s=60, marker="o", facecolors="none", edgecolors=C["FN"], linewidths=1.4)
            ax.add_patch(Polygon(_corners(1.4, 0, 4.8, 2.0, 0), fc="white", ec="white"))
            ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_aspect("equal")
            ax.set_xticks([]); ax.set_yticks([])
            ax.set_title(f"{m}   TP {n['TP']}  FP {n['FP']}  FN {n['FN']}", color="white", fontsize=12)
        fig.suptitle(f"AV2 {log_id[:8]}  frame {k:03d}  t={ts}   green=GT  blue=TP  red=FP  orange ring=missed GT",
                     color="#cbd5e1", fontsize=10, y=0.02)
        fig.tight_layout(rect=(0, 0.03, 1, 1))
        fig.savefig(tmp / f"{k:04d}.png", facecolor=fig.get_facecolor())
        plt.close(fig)
    out = out or (cfg.dir("reports") / "media").joinpath(f"review_{log_id[:8]}.mp4")
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", str(tmp / "%04d.png"),
                    "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "26", str(out)], check=True)
    shutil.rmtree(tmp)
    log.info("wrote %s", out)
    return out
