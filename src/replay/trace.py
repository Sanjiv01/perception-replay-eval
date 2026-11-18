"""Drill from an aggregate number to frames to individual boxes.

    replay trace pp-kitti-v1 --cls VEHICLE --status FN
prints: the count, its breakdown by failure reason, the frames where it concentrates, and the
boxes in the worst frame (ids, range, lidar points, nearest prediction) with the log time to open
in Foxglove.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import lake
from .common import Config


def trace(cfg: Config, model: str, cls=None, bucket=None, log_id=None, status="FN", top=10) -> str:
    thr = cfg.ev["tp_threshold_m"]
    m = pd.read_parquet(lake.eval_dir(cfg, model) / "matches.parquet")
    m = m[m.threshold_m == thr]
    q = m
    if cls:
        q = q[q.cls == cls]
    if bucket:
        q = q[q.bucket == bucket]
    if log_id:
        q = q[q.log_id.str.startswith(log_id)]
    sel = q[q.status == status]
    total = len(q[q.status != ("FN" if status == "FP" else "FP")])
    L = [f"{model} | {status} | cls={cls or 'all'} bucket={bucket or 'all'} log={log_id or 'all'} @ {thr} m",
         f"  {len(sel)} {status} rows out of {total} {'GT' if status != 'FP' else 'predictions'} in the slice\n"]
    if sel.empty:
        return "\n".join(L)
    rs = sel.reason.fillna("-").str.replace(r"\(.*", "", regex=True).value_counts()
    L.append("  by reason:")
    L += [f"    {k:<28} {v:>6}  ({v / len(sel):.0%})" for k, v in rs.items()]
    L.append("\n  by distance bucket:")
    L += [f"    {k:<28} {v:>6}" for k, v in sel.bucket.value_counts().sort_index().items()]
    fr = sel.groupby(["log_id", "frame_idx", "timestamp_ns"]).size().sort_values(ascending=False).head(top)
    L.append(f"\n  top {len(fr)} frames:")
    L += [f"    {lid[:8]} frame {fi:>4}  t={ts}  {n} {status}" for (lid, fi, ts), n in fr.items()]

    (lid, fi, ts) = fr.index[0]
    boxes = sel[(sel.log_id == lid) & (sel.timestamp_ns == ts)]
    if status == "FP":
        preds = pd.read_parquet(lake.predictions_path(cfg, model), filters=[("log_id", "=", lid)])
        b = boxes.merge(preds[["pred_id", "x", "y", "yaw", "length", "width"]], on="pred_id")
        L.append(f"\n  boxes in worst frame ({lid[:8]} frame {fi}):")
        L += [f"    {r.pred_id}  {r.cls:<10} score={r.score:.2f} at ({r.x:6.1f},{r.y:6.1f}) r={r.range_m:5.1f}m  {r.reason}"
              for r in b.sort_values("score", ascending=False).itertuples()]
    else:
        ann = lake.table(cfg, "annotations", lid)
        b = boxes.merge(ann[["gt_id", "category", "tx_m", "ty_m", "track_uuid"]], on="gt_id")
        L.append(f"\n  boxes in worst frame ({lid[:8]} frame {fi}):")
        L += [f"    {r.gt_id}  {r.category:<16} at ({r.tx_m:6.1f},{r.ty_m:6.1f}) r={r.range_m:5.1f}m "
              f"pts={int(r.num_interior_pts) if not np.isnan(r.num_interior_pts) else '-':>5}  {r.reason}"
              for r in b.sort_values("range_m").itertuples()]
    L.append(f"\n  Foxglove: open data/mcap/{lid}.mcap, seek to {ts / 1e9:.3f} s, enable /eval/{model}/missed and /pred/{model}/boxes")
    return "\n".join(L)
