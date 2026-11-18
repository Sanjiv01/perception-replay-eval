"""Convert raw AV2 logs into the Parquet lake and a replayable MCAP.

Lake layout (all keyed by log_id + timestamp_ns, frame_idx is derived and stable):
  frames.parquet           one row per lidar sweep: pose, point count, matched camera frame
  lidar/log_id=<id>/*.parquet   every lidar return, raw dtypes, logged timestamps untouched
  annotations.parquet      logged GT cuboids verbatim + derived yaw / range / frame_idx
  calibration.parquet      egovehicle_SE3_sensor + intrinsics for the logged camera
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.feather as feather
import pyarrow.parquet as pq
from tqdm import tqdm

from .common import Config, log, quat_to_yaw, write_manifest


def _sweep_files(raw: Path) -> list[Path]:
    return sorted((raw / "sensors" / "lidar").glob("*.feather"), key=lambda p: int(p.stem))


def ingest_log(cfg: Config, log_id: str) -> dict:
    raw = cfg.dir("raw") / log_id
    lake = cfg.dir("lake")
    cam = cfg.raw["dataset"]["camera"]
    max_frames = cfg.raw["dataset"].get("max_frames")

    sweeps = _sweep_files(raw)
    if max_frames:
        sweeps = sweeps[:max_frames]
    sweep_ts = np.array([int(p.stem) for p in sweeps], dtype=np.int64)

    # ---- lidar: one parquet per log, row per return, raw dtypes
    out_dir = lake / "lidar" / f"log_id={log_id}"
    out_dir.mkdir(parents=True, exist_ok=True)
    writer, npts = None, []
    for ts, p in tqdm(list(zip(sweep_ts, sweeps)), desc=f"ingest {log_id[:8]}", unit="sweep"):
        t = feather.read_table(p)
        t = t.add_column(0, "timestamp_ns", pa.array(np.full(t.num_rows, ts, dtype=np.int64)))
        npts.append(t.num_rows)
        if writer is None:
            writer = pq.ParquetWriter(out_dir / "part-0.parquet", t.schema, compression="zstd")
        writer.write_table(t)
    writer.close()

    # ---- poses + camera association
    poses = feather.read_table(raw / "city_SE3_egovehicle.feather").to_pandas()
    poses = poses.set_index("timestamp_ns")
    missing = set(sweep_ts) - set(poses.index)
    if missing:
        raise ValueError(f"{log_id}: {len(missing)} sweeps have no ego pose")
    cam_ts = np.array(sorted(int(p.stem) for p in (raw / "sensors" / "cameras" / cam).glob("*.jpg")), dtype=np.int64)
    j = np.clip(np.searchsorted(cam_ts, sweep_ts), 1, len(cam_ts) - 1)
    j = np.where(np.abs(cam_ts[j - 1] - sweep_ts) < np.abs(cam_ts[j] - sweep_ts), j - 1, j)
    frames = pd.DataFrame({
        "log_id": log_id,
        "frame_idx": np.arange(len(sweep_ts), dtype=np.int32),
        "timestamp_ns": sweep_ts,
        "n_points": np.array(npts, dtype=np.int32),
        "camera_timestamp_ns": cam_ts[j],
        "camera_dt_ms": (cam_ts[j] - sweep_ts) / 1e6,
    })
    for c in ["qw", "qx", "qy", "qz", "tx_m", "ty_m", "tz_m"]:
        frames["city_" + c] = poses.loc[sweep_ts, c].to_numpy()

    # ---- annotations: verbatim + derived columns
    ann = feather.read_table(raw / "annotations.feather").to_pandas()
    unknown_ts = ~ann.timestamp_ns.isin(set(sweep_ts))
    if max_frames:
        ann = ann[~unknown_ts]
    elif unknown_ts.any():
        raise ValueError(f"{log_id}: {unknown_ts.sum()} annotations at timestamps without a lidar sweep")
    idx = {t: i for i, t in enumerate(sweep_ts)}
    ann.insert(0, "log_id", log_id)
    ann.insert(2, "frame_idx", ann.timestamp_ns.map(idx).astype(np.int32))
    ann["yaw"] = quat_to_yaw(ann.qw, ann.qx, ann.qy, ann.qz)
    ann["range_m"] = np.hypot(ann.tx_m, ann.ty_m)
    ann["gt_id"] = ann.log_id.str[:8] + ":" + ann.timestamp_ns.astype(str) + ":" + ann.track_uuid.str[:8]

    # ---- calibration (lidar is already in the ego frame; keep camera extrinsics/intrinsics)
    ext = feather.read_table(raw / "calibration" / "egovehicle_SE3_sensor.feather").to_pandas()
    intr = feather.read_table(raw / "calibration" / "intrinsics.feather").to_pandas()
    calib = ext.merge(intr, on="sensor_name", how="left")
    calib.insert(0, "log_id", log_id)

    return {"frames": frames, "annotations": ann, "calibration": calib}


def _append(lake: Path, name: str, df: pd.DataFrame, log_ids: list[str]) -> None:
    """Upsert rows for these logs into a lake table (idempotent re-ingest)."""
    p = lake / f"{name}.parquet"
    if p.exists():
        old = pq.read_table(p)
        old = old.filter(pc.invert(pc.is_in(old["log_id"], pa.array(log_ids))))
        df = pd.concat([old.to_pandas(), df], ignore_index=True)
    pq.write_table(pa.Table.from_pandas(df, preserve_index=False), p, compression="zstd")


def ingest(cfg: Config, write_mcap: bool = True) -> None:
    from .mcap_io import write_log_mcap

    lake = cfg.dir("lake")
    parts = {"frames": [], "annotations": [], "calibration": []}
    for lid in cfg.logs:
        res = ingest_log(cfg, lid)
        for k in parts:
            parts[k].append(res[k])
        log.info("%s: %d sweeps, %d GT cuboids", lid, len(res["frames"]), len(res["annotations"]))
    for k, dfs in parts.items():
        _append(lake, k, pd.concat(dfs, ignore_index=True), cfg.logs)
    write_manifest(lake / "_ingest_manifest.json", config_hash=cfg.hash, logs=cfg.logs,
                   max_frames=cfg.raw["dataset"].get("max_frames"))
    if write_mcap:
        for lid in cfg.logs:
            write_log_mcap(cfg, lid, models=[])
