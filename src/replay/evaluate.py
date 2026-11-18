"""Detection + tracking evaluation. Every aggregate is a group-by over matches.parquet.

matches.parquet has one row per (prediction or unmatched GT, match threshold):
  status TP / FP / FN, pred_id, gt_id, log_id, timestamp_ns, frame_idx, cls, bucket, score,
  center_err_m, scale_err, orient_err_rad, and a plain-language `reason` for each FP/FN.
So any number in a report can be reproduced with a filter + count on that table, and every row
points to a frame (log_id, timestamp_ns) and a box (pred_id / gt_id) you can find in the MCAP.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist

from . import lake, roi, tracking
from .common import Config, bucket_label, log, write_manifest, wrap_angle
from .detector.pointpillars import PC_RANGE


def gt_table(cfg: Config) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(evaluated GT, all GT). Evaluated GT is mapped to model classes and filtered to the ROI."""
    ann = lake.table(cfg, "annotations")
    ev = cfg.ev
    cat2cls = {c: k for k, cats in ev["class_map"].items() for c in cats}
    ann["cls"] = ann.category.map(cat2cls)
    keep = ann.cls.notna() & (ann.num_interior_pts >= ev["min_gt_interior_points"]) & (ann.range_m <= ev["max_range_m"])
    if ev.get("roi_filter", True):
        ann["in_roi"] = roi.in_roi(cfg, ann, "tx_m", "ty_m", lake.table(cfg, "frames"))
        keep &= ann.in_roi
    gt = ann[keep].copy()
    gt["bucket"] = bucket_label(ev["distance_buckets_m"], gt.range_m.to_numpy())
    return gt.reset_index(drop=True), ann


def in_model_fov(x, y, rotations_deg) -> np.ndarray:
    """True where (x, y) lies inside at least one of the model's rotated input crops."""
    x, y = np.asarray(x), np.asarray(y)
    ok = np.zeros(x.shape, bool)
    for r in np.deg2rad(rotations_deg):
        c, s = np.cos(-r), np.sin(-r)
        xr, yr = c * x - s * y, s * x + c * y
        ok |= (xr >= PC_RANGE[0]) & (xr < PC_RANGE[3]) & (yr >= PC_RANGE[1]) & (yr < PC_RANGE[4])
    return ok


def _match_frame(p: pd.DataFrame, g: pd.DataFrame, thr: float):
    """AV2-style greedy matching: preds by descending score take the nearest free GT within thr."""
    p = p.sort_values("score", ascending=False)
    D = cdist(p[["x", "y"]].to_numpy(), g[["tx_m", "ty_m"]].to_numpy()) if len(p) and len(g) else np.zeros((len(p), len(g)))
    taken = np.zeros(len(g), bool)
    pairs = []
    for i in range(len(p)):
        if len(g) == 0:
            pairs.append((i, -1, np.nan)); continue
        d = np.where(taken, np.inf, D[i])
        j = int(np.argmin(d))
        if d[j] <= thr:
            taken[j] = True
            pairs.append((i, j, d[j]))
        else:
            pairs.append((i, -1, np.nan))
    return p, pairs, taken, D


def _fp_reason(pr, all_g: pd.DataFrame, gt_frame_cls: pd.DataFrame, thr: float) -> str:
    if len(all_g):
        d = np.hypot(all_g.tx_m.to_numpy() - pr.x, all_g.ty_m.to_numpy() - pr.y)
        j = int(np.argmin(d))
        near = all_g.iloc[j]
        if d[j] <= max(thr, 1.0):
            if near.cls == pr.cls:
                return "duplicate" if near.gt_id in gt_frame_cls.gt_id.values else f"gt_filtered({_why_filtered(near)})"
            if isinstance(near.cls, str):
                return f"class_confusion(gt={near.cls})"
            return f"unevaluated_category(gt={near.category})"
        if d[j] <= 4.0 and near.cls == pr.cls:
            return f"mislocalized({d[j]:.1f}m)"
    return "background"


def _why_filtered(row) -> str:
    if row.num_interior_pts == 0:
        return "no_lidar_points"
    return "beyond_range" if bool(row.get("in_roi", True)) else "outside_roi"


def match_all(cfg: Config, model: str, gt: pd.DataFrame, ann: pd.DataFrame) -> pd.DataFrame:
    ev = cfg.ev
    preds = pd.read_parquet(lake.predictions_path(cfg, model))
    frames = preds[["log_id", "timestamp_ns", "frame_idx"]].drop_duplicates()
    preds = preds.dropna(subset=["pred_id"])
    preds = preds[preds.range_m <= ev["max_range_m"]].copy()
    if ev.get("roi_filter", True):
        preds = preds[roi.in_roi(cfg, preds, "x", "y", lake.table(cfg, "frames"))].copy()
    preds["bucket"] = bucket_label(ev["distance_buckets_m"], preds.range_m.to_numpy())
    rot = cfg.models[model]["rotations_deg"]

    cat2cls = {c: k for k, cats in ev["class_map"].items() for c in cats}
    ann = ann.assign(cls=ann.category.map(cat2cls))
    ann_by = dict(tuple(ann.groupby(["log_id", "timestamp_ns"])))
    gt_by = dict(tuple(gt.groupby(["log_id", "timestamp_ns", "cls"])))
    pr_by = dict(tuple(preds.groupby(["log_id", "timestamp_ns", "cls"])))
    rows = []
    for fr in frames.itertuples():
        key = (fr.log_id, fr.timestamp_ns)
        all_g = ann_by.get(key, ann.iloc[0:0])
        for cls in ev["class_map"]:
            g = gt_by.get(key + (cls,), gt.iloc[0:0])
            p = pr_by.get(key + (cls,), preds.iloc[0:0])
            for thr in ev["match_thresholds_m"]:
                ps, pairs, taken, D = _match_frame(p, g, thr)
                base = {"log_id": fr.log_id, "timestamp_ns": fr.timestamp_ns, "frame_idx": fr.frame_idx,
                        "cls": cls, "threshold_m": thr}
                for i, j, d in pairs:
                    pr = ps.iloc[i]
                    r = {**base, "pred_id": pr.pred_id, "score": pr.score, "bucket": pr.bucket, "range_m": pr.range_m}
                    if j >= 0:
                        gg = g.iloc[j]
                        inter = np.prod(np.minimum([pr.length, pr.width, pr.height], [gg.length_m, gg.width_m, gg.height_m]))
                        union = pr.length * pr.width * pr.height + gg.length_m * gg.width_m * gg.height_m - inter
                        r.update(status="TP", gt_id=gg.gt_id, bucket=gg.bucket, range_m=gg.range_m, center_err_m=d,
                                 scale_err=1 - inter / union, orient_err_rad=abs(float(wrap_angle(pr.yaw - gg.yaw))))
                    else:
                        r.update(status="FP", reason=_fp_reason(pr, all_g, g, thr))
                    rows.append(r)
                fov = in_model_fov(g.tx_m.to_numpy(), g.ty_m.to_numpy(), rot)
                for j in np.nonzero(~taken)[0]:
                    gg = g.iloc[j]
                    if not fov[j]:
                        reason = "outside_model_input_crop"
                    elif len(p) and D[:, j].min() <= 4.0:
                        reason = f"mislocalized_pred({D[:, j].min():.1f}m)"
                    else:
                        reason = "missed"
                        for oc in ev["class_map"]:
                            if oc == cls:
                                continue
                            q = pr_by.get(key + (oc,))
                            if q is not None and np.hypot(q.x - gg.tx_m, q.y - gg.ty_m).min() <= thr:
                                reason = f"class_confusion(pred={oc})"
                                break
                        if reason == "missed" and gg.num_interior_pts < 10:
                            reason = "missed_sparse(<10 pts)"
                    rows.append({**base, "status": "FN", "gt_id": gg.gt_id, "bucket": gg.bucket,
                                 "range_m": gg.range_m, "num_interior_pts": gg.num_interior_pts, "reason": reason})
    m = pd.DataFrame(rows)
    m["model_version"] = model
    return m


def average_precision(scores: np.ndarray, is_tp: np.ndarray, n_gt: int) -> float:
    """101-point interpolated AP (as in the AV2 detection eval)."""
    if n_gt == 0:
        return np.nan
    if len(scores) == 0:
        return 0.0
    o = np.argsort(-scores, kind="stable")
    tp = np.cumsum(is_tp[o])
    fp = np.cumsum(~is_tp[o])
    rec = tp / n_gt
    prec = tp / np.maximum(tp + fp, 1)
    prec = np.maximum.accumulate(prec[::-1])[::-1]
    grid = np.linspace(0, 1, 101)
    idx = np.searchsorted(rec, grid, side="left")
    return float(np.mean(np.where(idx < len(prec), prec[np.minimum(idx, len(prec) - 1)], 0.0)))


def summarize(m: pd.DataFrame, by: list[str], ev: dict) -> pd.DataFrame:
    """AP per threshold + counts/errors at the TP threshold, grouped by `by` (e.g. cls, bucket, log)."""
    out = []
    tp_thr = ev["tp_threshold_m"]
    for key, g in m.groupby(by, dropna=False):
        key = key if isinstance(key, tuple) else (key,)
        r = dict(zip(by, key))
        for thr, gt_ in g.groupby("threshold_m"):
            pr = gt_[gt_.status != "FN"]
            n_gt = int((gt_.status != "FP").sum())  # TP + FN = all GT in slice
            r[f"AP@{thr:g}m"] = average_precision(pr.score.to_numpy(), (pr.status == "TP").to_numpy(), n_gt)
        aps = [r[f"AP@{t:g}m"] for t in ev["match_thresholds_m"]]
        r["mAP"] = np.nan if np.all(np.isnan(aps)) else float(np.nanmean(aps))
        t = g[g.threshold_m == tp_thr]
        tp, fp, fn = (t.status == "TP").sum(), (t.status == "FP").sum(), (t.status == "FN").sum()
        r.update(n_gt=int(tp + fn), n_pred=int(tp + fp), tp=int(tp), fp=int(fp), fn=int(fn),
                 precision=tp / max(tp + fp, 1), recall=tp / max(tp + fn, 1),
                 ATE_m=t.loc[t.status == "TP", "center_err_m"].mean(),
                 ASE=t.loc[t.status == "TP", "scale_err"].mean(),
                 AOE_rad=t.loc[t.status == "TP", "orient_err_rad"].mean(),
                 n_frames=int(t[["log_id", "timestamp_ns"]].drop_duplicates().shape[0]))
        out.append(r)
    return pd.DataFrame(out)


def evaluate(cfg: Config, models: list[str]) -> None:
    gt, ann = gt_table(cfg)
    ev = cfg.ev
    frames = lake.table(cfg, "frames")
    for model in models:
        d = lake.eval_dir(cfg, model)
        m = match_all(cfg, model, gt, ann)
        m.to_parquet(d / "matches.parquet", index=False)
        allb = m.assign(bucket="all")
        summarize(pd.concat([m, allb]), ["cls", "bucket"], ev).to_parquet(d / "metrics_class_bucket.parquet", index=False)
        summarize(pd.concat([m, allb]), ["log_id", "cls", "bucket"], ev).to_parquet(d / "metrics_scene.parquet", index=False)
        t = m[m.threshold_m == ev["tp_threshold_m"]]
        per_frame = (t.pivot_table(index=["log_id", "timestamp_ns", "frame_idx", "cls"], columns="status",
                                   values="threshold_m", aggfunc="count", fill_value=0)
                     .reindex(columns=["TP", "FP", "FN"], fill_value=0).reset_index())
        per_frame.columns.name = None
        per_frame.to_parquet(d / "metrics_frame.parquet", index=False)

        # tracking
        preds = pd.read_parquet(lake.predictions_path(cfg, model)).dropna(subset=["pred_id"])
        preds = preds[preds.range_m <= ev["max_range_m"]]
        if ev.get("roi_filter", True):
            preds = preds[roi.in_roi(cfg, preds, "x", "y", frames)]
        tcfg = cfg.raw["tracking"]
        tid = tracking.track(preds, frames, tcfg, min_score=tcfg.get("min_score", 0.3))
        trk = preds.merge(tid, on="pred_id")
        trk.to_parquet(d / "tracks.parquet", index=False)
        mot = tracking.clear_mot(gt, trk, ev["tp_threshold_m"])
        mot.to_parquet(d / "tracking_frame.parquet", index=False)
        ms = pd.concat([tracking.mota_summary(mot, ["cls"]),
                        tracking.mota_summary(mot, ["log_id", "cls"])], ignore_index=True)
        ms.to_parquet(d / "tracking_summary.parquet", index=False)
        write_manifest(d / "manifest.json", model=model, config_hash=cfg.hash, n_match_rows=len(m),
                       predictions_manifest=str(lake.predictions_path(cfg, model).with_suffix(".manifest.json")))
        cb = pd.read_parquet(d / "metrics_class_bucket.parquet")
        log.info("%s\n%s", model, cb[cb.bucket == "all"][["cls", "mAP", "AP@2m", "precision", "recall", "n_gt", "tp", "fp", "fn"]].round(3).to_string(index=False))
        _write_eval_report(cfg, model)


def _fmt(df: pd.DataFrame) -> str:
    df = df.copy()
    for c in df.columns:
        if df[c].dtype.kind == "f":
            df[c] = df[c].map(lambda v: "" if pd.isna(v) else f"{v:.3f}")
    return df.to_markdown(index=False)


def _write_eval_report(cfg: Config, model: str) -> None:
    d = lake.eval_dir(cfg, model)
    cb = pd.read_parquet(d / "metrics_class_bucket.parquet")
    sc = pd.read_parquet(d / "metrics_scene.parquet")
    ts = pd.read_parquet(d / "tracking_summary.parquet")
    m = pd.read_parquet(d / "matches.parquet")
    t = m[m.threshold_m == cfg.ev["tp_threshold_m"]]
    reasons = (t[t.status != "TP"].assign(reason=lambda x: x.reason.str.replace(r"\(.*", "", regex=True))
               .groupby(["status", "cls", "reason"]).size().rename("count").reset_index()
               .sort_values(["status", "cls", "count"], ascending=[True, True, False]))
    cols = ["cls", "bucket", "mAP", "AP@0.5m", "AP@1m", "AP@2m", "AP@4m", "n_gt", "tp", "fp", "fn", "precision", "recall", "ATE_m", "ASE", "AOE_rad"]
    txt = [f"# Evaluation: `{model}`\n",
           f"Config hash `{cfg.hash}`. Source rows: `data/lake/eval/{model}/matches.parquet` "
           f"({len(m)} rows). Counts at the {cfg.ev['tp_threshold_m']} m TP threshold.\n",
           "## Per class and distance bucket\n", _fmt(cb[cols]),
           "\n## Per scene (all distances)\n", _fmt(sc[sc.bucket == "all"][["log_id", "cls", "mAP", "AP@2m", "n_gt", "tp", "fp", "fn", "recall"]]),
           "\n## Why boxes failed (FP/FN reasons)\n", reasons.to_markdown(index=False),
           "\n## Tracking (CLEAR-MOT, 2 m)\n", _fmt(ts[ts.log_id.isna()].drop(columns="log_id")),
           "\nReproduce any count, e.g. FN for vehicles 35-50m:\n",
           "```python\nm = pd.read_parquet('data/lake/eval/%s/matches.parquet')\n"
           "m.query(\"threshold_m == 2 and cls == 'VEHICLE' and bucket == '35-50m' and status == 'FN'\")\n```\n" % model]
    (cfg.dir("reports") / f"eval_{model}.md").write_text("\n".join(txt), encoding="utf-8")
