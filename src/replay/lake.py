"""Read helpers for the Parquet lake."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.dataset as ds
import pyarrow.parquet as pq

from .common import Config


def table(cfg: Config, name: str, log_id: str | None = None) -> pd.DataFrame:
    p = cfg.dir("lake") / f"{name}.parquet"
    filt = [("log_id", "=", log_id)] if log_id else None
    return pq.read_table(p, filters=filt).to_pandas()


def predictions_path(cfg: Config, model: str) -> Path:
    d = cfg.dir("lake") / "predictions"
    d.mkdir(exist_ok=True)
    return d / f"{model}.parquet"


def eval_dir(cfg: Config, model: str) -> Path:
    d = cfg.dir("lake") / "eval" / model
    d.mkdir(parents=True, exist_ok=True)
    return d


def load_sweeps(lake: Path, log_id: str) -> dict[int, np.ndarray]:
    """{timestamp_ns: (N, 4) float32 [x, y, z, intensity]} for one log, ego frame."""
    t = ds.dataset(lake / "lidar" / f"log_id={log_id}", format="parquet").to_table(
        columns=["timestamp_ns", "x", "y", "z", "intensity"])
    ts = t["timestamp_ns"].to_numpy()
    xyz = np.stack([t[c].to_numpy().astype(np.float32) for c in ["x", "y", "z", "intensity"]], 1)
    order = np.argsort(ts, kind="stable")
    ts, xyz = ts[order], xyz[order]
    uniq, start = np.unique(ts, return_index=True)
    bounds = list(start) + [len(ts)]
    return {int(u): xyz[bounds[i]:bounds[i + 1]] for i, u in enumerate(uniq)}
