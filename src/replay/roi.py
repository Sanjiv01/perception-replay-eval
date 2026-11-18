"""AV2 region of interest: drivable area (from the log's vector map) dilated by 5 m.

The official AV2 detection eval drops GT and predictions outside this ROI; we do the same
(config: evaluation.roi_filter). Without it, cars in parking lots that AV2 labels sparsely
are scored as false positives. See docs/DISCREPANCY.md.
"""
from __future__ import annotations

import json
from functools import lru_cache

import numpy as np
import pandas as pd
import shapely
from shapely.ops import unary_union

from .common import Config, se3


@lru_cache(maxsize=16)
def _roi(raw_dir: str, log_id: str, dilation_m: float):
    from pathlib import Path

    f = next((Path(raw_dir) / log_id / "map").glob("log_map_archive_*.json"))
    j = json.loads(f.read_text())
    polys = [shapely.Polygon([(p["x"], p["y"]) for p in da["area_boundary"]]) for da in j["drivable_areas"].values()]
    roi = unary_union(polys).buffer(dilation_m)
    shapely.prepare(roi)
    return roi


def in_roi(cfg: Config, df: pd.DataFrame, x: str, y: str, frames: pd.DataFrame) -> np.ndarray:
    """Boolean mask: ego-frame (x, y) of each row lies inside its log's ROI at that timestamp."""
    out = np.zeros(len(df), bool)
    if not len(df):
        return out
    f = frames.set_index(["log_id", "timestamp_ns"])
    dil = float(cfg.ev.get("roi_dilation_m", 5.0))
    df = df.reset_index(drop=True)
    for (lid, ts), idx in df.groupby(["log_id", "timestamp_ns"]).indices.items():
        r = f.loc[(lid, ts)]
        T = se3(r.city_qw, r.city_qx, r.city_qy, r.city_qz, r.city_tx_m, r.city_ty_m, r.city_tz_m)
        xy = df.iloc[idx][[x, y]].to_numpy(float) @ T[:2, :2].T + T[:2, 3]
        out[idx] = shapely.contains_xy(_roi(str(cfg.dir("raw")), lid, dil), xy[:, 0], xy[:, 1])
    return out
