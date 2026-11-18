"""Recompute job: re-run a model version over every logged sweep, one Ray task per scene.

Output: data/lake/predictions/<model>.parquet (one row per box, ego frame) and a run manifest
recording model spec, checkpoint hash, config hash, Ray resources and per-frame latency.
"""
from __future__ import annotations

import time
import uuid
from pathlib import Path

import numpy as np
import pandas as pd

from .common import Config, log, se3, write_manifest


def _compensate(prev: np.ndarray, T_city_prev: np.ndarray, T_city_cur: np.ndarray) -> np.ndarray:
    """Move an older sweep into the current ego frame using logged city poses."""
    T = np.linalg.inv(T_city_cur) @ T_city_prev
    out = prev.copy()
    out[:, :3] = prev[:, :3] @ T[:3, :3].T + T[:3, 3]
    return out


def _part_path(cfg: Config, model: str, log_id: str) -> Path:
    d = cfg.dir("lake") / "predictions" / "_parts" / model
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{log_id}.parquet"


def run_scene(config_path: str, log_id: str, model: str) -> str:
    """Runs inside a Ray worker. Reads its own inputs from the lake and checkpoints its output to
    predictions/_parts/<model>/<log_id>.parquet, so a crashed or preempted job resumes per scene."""
    import torch

    from . import lake
    from .detector.runner import Detector

    cfg = Config.load(config_path)
    torch.set_num_threads(int(cfg.raw["recompute"].get("torch_threads", 2)))
    spec = cfg.models[model]
    det = Detector(model, spec, device=cfg.raw["recompute"].get("device", "cpu"))
    frames = lake.table(cfg, "frames", log_id).sort_values("frame_idx")
    sweeps = lake.load_sweeps(cfg.dir("lake"), log_id)
    poses = {int(r.timestamp_ns): se3(r.city_qw, r.city_qx, r.city_qy, r.city_qz, r.city_tx_m, r.city_ty_m, r.city_tz_m)
             for r in frames.itertuples()}
    ts_list = frames.timestamp_ns.astype(np.int64).tolist()
    n_sw = int(spec.get("num_sweeps", 1))
    rows = []
    for i, ts in enumerate(ts_list):
        hist = [sweeps[ts]]
        for j in range(1, n_sw):
            if i - j < 0:
                break
            pts = ts_list[i - j]
            hist.append(_compensate(sweeps[pts], poses[pts], poses[ts]))
        t0 = time.perf_counter()
        dets = det.predict(hist)
        if det.device == "cuda":
            torch.cuda.synchronize()
        lat = (time.perf_counter() - t0) * 1e3
        for k, d in enumerate(sorted(dets, key=lambda d: -d["score"])):
            rows.append({"log_id": log_id, "timestamp_ns": ts, "frame_idx": i,
                         "pred_id": f"{model}:{log_id[:8]}:{ts}:{k:03d}", **d,
                         "range_m": float(np.hypot(d["x"], d["y"])), "latency_ms": lat})
        if not dets:  # keep a trace that the frame was processed
            rows.append({"log_id": log_id, "timestamp_ns": ts, "frame_idx": i, "pred_id": None,
                         "latency_ms": lat})
    df = pd.DataFrame(rows)
    df["model_version"] = model
    df["checkpoint_sha256"] = det.ckpt_sha
    df["device"] = det.device
    out = _part_path(cfg, model, log_id)
    df.to_parquet(out.with_suffix(".tmp"), index=False)
    out.with_suffix(".tmp").replace(out)
    return str(out)


def _headroom_ok(rc: dict) -> tuple[bool, str]:
    """Keep the host alive: refuse to start new work if RAM headroom or GPU temperature is unsafe."""
    import subprocess

    import psutil

    vm = psutil.virtual_memory()
    free_frac = vm.available / vm.total
    msg = f"ram free {free_frac:.0%}"
    if free_frac < rc.get("min_free_ram_frac", 0.10):
        return False, msg
    try:
        t = subprocess.run(["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=5).stdout.split()
        temp = float(t[0]) if t else 0.0
    except Exception:
        temp = 0.0
    msg += f", gpu {temp:.0f}C"
    return temp < rc.get("max_gpu_temp_c", 85), msg


def recompute(cfg: Config, models: list[str] | None = None, use_ray: bool = True, force: bool = False) -> None:
    import ray

    from . import lake

    models = models or cfg.main_models
    rc = cfg.raw["recompute"]
    t0 = time.time()
    todo = [(m, lid) for m in models for lid in cfg.logs if force or not _part_path(cfg, m, lid).exists()]
    log.info("recompute: %d scene tasks to run, %d already checkpointed", len(todo), len(models) * len(cfg.logs) - len(todo))
    resources = {}
    if todo and use_ray:
        import torch
        import os

        # Resource caps: by default Ray sizes itself to the whole machine with no headroom.
        # max_cpus defaults to 90% of logical cores; tasks are admitted one at a time only while
        # >=10% RAM is free and the GPU is below max_gpu_temp_c.
        ncpu = int(rc.get("max_cpus") or max(1, int((os.cpu_count() or 2) * 0.9)))
        ray.init(ignore_reinit_error=True, include_dashboard=False, log_to_driver=False,
                 num_cpus=ncpu, num_gpus=1 if (rc.get("device") == "cuda" and torch.cuda.is_available()) else 0,
                 object_store_memory=int(rc.get("object_store_mb", 512)) * 1024 * 1024)
        gpus = rc["num_gpus_per_task"] if ray.cluster_resources().get("GPU", 0) else 0
        task = ray.remote(num_gpus=gpus, num_cpus=rc["num_cpus_per_task"])(run_scene)
        max_inflight = max(1, int(round(1 / gpus))) if gpus else max(1, ncpu // rc["num_cpus_per_task"])
        queue, pending = list(todo), []
        while queue or pending:
            while queue and len(pending) < max_inflight:
                ok, msg = _headroom_ok(rc)
                if not ok and pending:
                    log.warning("holding new scene tasks (%s)", msg)
                    break
                if not ok:  # nothing running: wait for the host to recover
                    log.warning("waiting for headroom (%s)", msg)
                    time.sleep(10)
                    continue
                m, lid = queue.pop(0)
                pending.append(task.remote(str(cfg.path), lid, m))
                log.info("started %s %s (%s, %d in flight)", m, lid[:8], msg, len(pending))
            done, pending = ray.wait(pending, num_returns=1, timeout=30)
            for d in done:
                log.info("scene done: %s (%d queued, %d running)", ray.get(d), len(queue), len(pending))
        resources = ray.cluster_resources()
        ray.shutdown()
    elif todo:
        for m, lid in todo:
            log.info("scene done: %s", run_scene(str(cfg.path), lid, m))

    for m in models:
        df = pd.concat([pd.read_parquet(_part_path(cfg, m, lid)) for lid in cfg.logs], ignore_index=True)
        run_id = uuid.uuid4().hex[:8]
        df["run_id"] = run_id
        out = lake.predictions_path(cfg, m)
        df.to_parquet(out, index=False)
        lat = df.drop_duplicates(["log_id", "timestamp_ns"]).latency_ms
        write_manifest(out.with_suffix(".manifest.json"), model=m, run_id=run_id, spec=cfg.models[m],
                       checkpoint_sha256=df.checkpoint_sha256.iloc[0], config_hash=cfg.hash, logs=cfg.logs,
                       n_frames=int(len(lat)), n_boxes=int(df.pred_id.notna().sum()),
                       latency_ms_p50=float(lat.median()), latency_ms_p95=float(lat.quantile(0.95)),
                       ray_resources=resources, wall_s=round(time.time() - t0, 1))
        log.info("%s: %d boxes over %d frames -> %s (p50 %.0f ms/frame)", m, df.pred_id.notna().sum(), len(lat), out, lat.median())
