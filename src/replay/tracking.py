"""Minimal tracking-by-detection + CLEAR-MOT evaluation with per-frame, traceable events.

Tracker: per class, greedy nearest-neighbour association in the city frame with a constant-velocity
prediction. It's deliberately simple. It exists so the pipeline produces tracking metrics that
regress when detection quality regresses.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import cdist

from .common import se3


def _to_city(df: pd.DataFrame, frames: pd.DataFrame) -> np.ndarray:
    out = np.zeros((len(df), 2))
    f = frames.set_index("timestamp_ns")
    for ts, idx in df.groupby("timestamp_ns").indices.items():
        r = f.loc[ts]
        T = se3(r.city_qw, r.city_qx, r.city_qy, r.city_qz, r.city_tx_m, r.city_ty_m, r.city_tz_m)
        xy = df.iloc[idx][["x", "y"]].to_numpy()
        out[idx] = xy @ T[:2, :2].T + T[:2, 3]
    return out


def track(preds: pd.DataFrame, frames: pd.DataFrame, cfg_t: dict, min_score: float) -> pd.DataFrame:
    """Assign track_id to predictions. Returns pred_id -> track_id (confirmed tracks only)."""
    out = []
    for (lid, cls), g in preds[preds.score >= min_score].groupby(["log_id", "cls"]):
        g = g.sort_values("timestamp_ns").reset_index(drop=True)
        g[["cx", "cy"]] = _to_city(g, frames[frames.log_id == lid])
        tracks: list[dict] = []
        next_id = 0
        prev_ts = None
        for ts, idx in g.groupby("timestamp_ns").indices.items():
            dt = 0.1 if prev_ts is None else (ts - prev_ts) / 1e9
            prev_ts = ts
            det = g.loc[idx, ["cx", "cy"]].to_numpy()
            alive = [t for t in tracks if t["age"] <= cfg_t["max_age"]]
            pred_pos = np.array([t["pos"] + t["vel"] * dt for t in alive]).reshape(-1, 2)
            assigned = {}
            if len(alive) and len(det):
                D = cdist(det, pred_pos)
                r, c = linear_sum_assignment(D)
                for i, j in zip(r, c):
                    if D[i, j] <= cfg_t["max_match_dist_m"]:
                        assigned[i] = alive[j]
            for t in tracks:
                t["age"] += 1
            for k, i in enumerate(idx):
                t = assigned.get(k)
                if t is None:
                    t = {"id": f"{cls[:3]}-{next_id}", "pos": det[k], "vel": np.zeros(2), "hits": 0, "age": 0}
                    next_id += 1
                    tracks.append(t)
                else:
                    t["vel"] = 0.5 * t["vel"] + 0.5 * (det[k] - t["pos"]) / max(dt, 1e-3)
                    t["pos"] = det[k]
                t["hits"] += 1
                t["age"] = 0
                if t["hits"] >= cfg_t["min_hits"]:
                    out.append((g.at[i, "pred_id"], f"{lid[:8]}:{t['id']}"))
    return pd.DataFrame(out, columns=["pred_id", "track_id"])


def clear_mot(gt: pd.DataFrame, trk: pd.DataFrame, thr: float) -> pd.DataFrame:
    """Per-frame CLEAR-MOT counts. gt: rows with track_uuid; trk: predictions with track_id.

    Each output row lists the gt_ids involved in ID switches so a bad MOTA is traceable to frames.
    """
    rows = []
    for (lid, cls), gg in gt.groupby(["log_id", "cls"]):
        tt = trk[(trk.log_id == lid) & (trk.cls == cls)]
        tt_by = dict(tuple(tt.groupby("timestamp_ns")))
        last_match: dict[str, str] = {}
        for ts, g in gg.groupby("timestamp_ns"):
            t = tt_by.get(ts, tt.iloc[0:0])
            matches, idsw = 0, []
            dist_sum = 0.0
            if len(g) and len(t):
                D = cdist(g[["tx_m", "ty_m"]].to_numpy(), t[["x", "y"]].to_numpy())
                r, c = linear_sum_assignment(D)
                ok = D[r, c] <= thr
                for i, j in zip(r[ok], c[ok]):
                    gid, tid = g.iloc[i].track_uuid, t.iloc[j].track_id
                    if gid in last_match and last_match[gid] != tid:
                        idsw.append(g.iloc[i].gt_id)
                    last_match[gid] = tid
                    dist_sum += D[i, j]
                matches = int(ok.sum())
            rows.append({"log_id": lid, "timestamp_ns": ts, "frame_idx": int(g.frame_idx.iloc[0]), "cls": cls,
                         "n_gt": len(g), "n_trk": len(t), "matches": matches, "fp": len(t) - matches,
                         "fn": len(g) - matches, "idsw": len(idsw), "idsw_gt_ids": ",".join(idsw),
                         "dist_sum_m": dist_sum})
    return pd.DataFrame(rows)


def mota_summary(df: pd.DataFrame, by: list[str]) -> pd.DataFrame:
    s = df.groupby(by)[["n_gt", "matches", "fp", "fn", "idsw", "dist_sum_m"]].sum().reset_index()
    s["MOTA"] = 1 - (s.fn + s.fp + s.idsw) / s.n_gt.clip(lower=1)
    s["MOTP_m"] = s.dist_sum_m / s.matches.clip(lower=1)
    return s.drop(columns="dist_sum_m")
