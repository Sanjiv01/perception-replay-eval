"""Regression diff between two model versions over the same replayed logs.

Three levels, each traceable to the next:
  1. slice table: per scene x class x distance bucket, metric deltas with support counts
  2. box flips: every GT that was detected by base and missed by candidate (and vice versa),
     plus candidate-only false positives, each with its frame and the candidate's failure reason
  3. worst frames: where the flips concentrate, with the Foxglove timestamp to jump to
"""
from __future__ import annotations

import pandas as pd

from . import lake
from .common import Config, log

KEYS = ["log_id", "cls", "bucket"]
MIN_SUPPORT = 20      # GT objects needed before a slice can be flagged
FLAG_DROP = 0.02      # mAP drop that counts as a regression


def _flips(cfg: Config, base: str, cand: str) -> pd.DataFrame:
    thr = cfg.ev["tp_threshold_m"]

    def gt_status(model):
        m = pd.read_parquet(lake.eval_dir(cfg, model) / "matches.parquet")
        m = m[(m.threshold_m == thr) & m.gt_id.notna()]
        return m[["gt_id", "log_id", "timestamp_ns", "frame_idx", "cls", "bucket", "range_m", "status", "reason", "pred_id", "center_err_m"]]

    b, c = gt_status(base), gt_status(cand)
    j = b.merge(c, on=["gt_id", "log_id", "timestamp_ns", "frame_idx", "cls", "bucket", "range_m"], suffixes=("_base", "_cand"))
    j["flip"] = "same"
    j.loc[(j.status_base == "TP") & (j.status_cand == "FN"), "flip"] = "lost"      # regression
    j.loc[(j.status_base == "FN") & (j.status_cand == "TP"), "flip"] = "gained"
    return j


def regress(cfg: Config, base: str, cand: str) -> None:
    ev = cfg.ev
    sb = pd.read_parquet(lake.eval_dir(cfg, base) / "metrics_scene.parquet")
    sc = pd.read_parquet(lake.eval_dir(cfg, cand) / "metrics_scene.parquet")
    cb = pd.read_parquet(lake.eval_dir(cfg, base) / "metrics_class_bucket.parquet").assign(log_id="ALL")
    cc = pd.read_parquet(lake.eval_dir(cfg, cand) / "metrics_class_bucket.parquet").assign(log_id="ALL")
    cols = ["mAP", "AP@2m", "precision", "recall", "ATE_m", "n_gt", "tp", "fp", "fn"]
    d = pd.concat([sb, cb]).merge(pd.concat([sc, cc]), on=KEYS, suffixes=("_base", "_cand"))
    for c in ["mAP", "AP@2m", "precision", "recall", "ATE_m", "fp", "fn"]:
        d[f"d_{c}"] = d[f"{c}_cand"] - d[f"{c}_base"]
    d["support"] = d.n_gt_base
    d["verdict"] = "ok"
    d.loc[(d.d_mAP <= -FLAG_DROP) & (d.support >= MIN_SUPPORT), "verdict"] = "REGRESSED"
    d.loc[(d.d_mAP >= FLAG_DROP) & (d.support >= MIN_SUPPORT), "verdict"] = "improved"
    d.loc[d.support < MIN_SUPPORT, "verdict"] = "low-support"

    flips = _flips(cfg, base, cand)
    tag = f"{base}_vs_{cand}"
    out_dir = cfg.dir("lake") / "eval"
    d.to_parquet(out_dir / f"regression_{tag}_slices.parquet", index=False)
    flips.to_parquet(out_dir / f"regression_{tag}_gt_flips.parquet", index=False)

    # candidate-only FPs by reason
    thr = ev["tp_threshold_m"]
    fpc = pd.read_parquet(lake.eval_dir(cfg, cand) / "matches.parquet").query("threshold_m == @thr and status == 'FP'")
    fpb = pd.read_parquet(lake.eval_dir(cfg, base) / "matches.parquet").query("threshold_m == @thr and status == 'FP'")

    tb = pd.read_parquet(lake.eval_dir(cfg, base) / "tracking_summary.parquet")
    tc = pd.read_parquet(lake.eval_dir(cfg, cand) / "tracking_summary.parquet")
    tr = tb.merge(tc, on=["log_id", "cls"], how="outer", suffixes=("_base", "_cand"))
    tr["d_MOTA"] = tr.MOTA_cand - tr.MOTA_base
    tr["d_idsw"] = tr.idsw_cand - tr.idsw_base

    _report(cfg, base, cand, d, flips, fpb, fpc, tr)


def _f(v, signed=False):
    if pd.isna(v):
        return ""
    return f"{v:+.3f}" if signed else f"{v:.3f}"


def _report(cfg, base, cand, d, flips, fpb, fpc, tr):
    L = []
    tag = f"{base}_vs_{cand}"
    L.append(f"# Regression report: `{base}` → `{cand}`\n")
    L.append(f"Logs: {len(cfg.logs)} AV2 val scenes · TP threshold {cfg.ev['tp_threshold_m']} m · "
             f"flag rule: mAP drop ≥ {FLAG_DROP} on a slice with ≥ {MIN_SUPPORT} GT objects.\n")
    L.append(f"Source tables: `data/lake/eval/regression_{tag}_slices.parquet`, "
             f"`data/lake/eval/regression_{tag}_gt_flips.parquet`.\n")

    ov = d[(d.log_id == "ALL") & (d.bucket == "all")]
    L.append("## Headline (all scenes, all distances)\n")
    L.append("| class | mAP base | mAP cand | Δ mAP | recall Δ | precision Δ | FP base→cand | FN base→cand |")
    L.append("|---|---|---|---|---|---|---|---|")
    for r in ov.itertuples():
        L.append(f"| {r.cls} | {_f(r.mAP_base)} | {_f(r.mAP_cand)} | **{_f(r.d_mAP, True)}** | {_f(r.d_recall, True)} | "
                 f"{_f(r.d_precision, True)} | {r.fp_base}→{r.fp_cand} | {r.fn_base}→{r.fn_cand} |")

    reg = d[d.verdict == "REGRESSED"].sort_values("d_mAP")
    L.append(f"\n## What got worse ({len(reg)} slices flagged)\n")
    if len(reg):
        L.append("| scene | class | distance | GT | mAP base→cand | Δ mAP | Δ precision | Δ recall | FP base→cand |")
        L.append("|---|---|---|---|---|---|---|---|---|")
        for r in reg.itertuples():
            L.append(f"| `{r.log_id[:8]}` | {r.cls} | {r.bucket} | {r.support} | {_f(r.mAP_base)}→{_f(r.mAP_cand)} | "
                     f"**{_f(r.d_mAP, True)}** | {_f(r.d_precision, True)} | {_f(r.d_recall, True)} | {r.fp_base}→{r.fp_cand} |")
    else:
        L.append("No slice crossed the regression threshold.")

    imp = d[(d.verdict == "improved") & (d.log_id == "ALL")].sort_values("d_mAP", ascending=False)
    L.append(f"\n## What got better (all scenes)\n")
    L.append("| class | distance | GT | mAP base→cand | Δ mAP | Δ recall |")
    L.append("|---|---|---|---|---|---|")
    for r in imp.itertuples():
        L.append(f"| {r.cls} | {r.bucket} | {r.support} | {_f(r.mAP_base)}→{_f(r.mAP_cand)} | {_f(r.d_mAP, True)} | {_f(r.d_recall, True)} |")

    L.append("\n## Box-level evidence\n")
    fc = flips.flip.value_counts()
    L.append(f"GT objects detected by base but missed by candidate (**lost**): {fc.get('lost', 0)} · "
             f"missed by base but detected by candidate (**gained**): {fc.get('gained', 0)}.\n")
    lost = flips[flips.flip == "lost"]
    if len(lost):
        lr = (lost.assign(reason=lost.reason_cand.str.replace(r"\(.*", "", regex=True))
              .groupby(["cls", "reason"]).size().rename("lost GT").reset_index().sort_values("lost GT", ascending=False))
        L.append("Why the candidate lost them:\n")
        L.append(lr.to_markdown(index=False))
    fpr = (pd.concat([fpb.assign(v="base"), fpc.assign(v="cand")])
           .assign(reason=lambda x: x.reason.str.replace(r"\(.*", "", regex=True))
           .pivot_table(index=["cls", "reason"], columns="v", values="threshold_m", aggfunc="count", fill_value=0)
           .reset_index())
    fpr.columns.name = None
    if "cand" in fpr and "base" in fpr:
        fpr["Δ"] = fpr["cand"] - fpr["base"]
        fpr = fpr.sort_values("Δ", ascending=False)
    L.append("\nFalse positives by reason (base vs candidate):\n")
    L.append(fpr.to_markdown(index=False))

    # worst frames: lost GT + new FP per frame
    fp_frame = (fpc.groupby(["log_id", "timestamp_ns", "frame_idx"]).size().rename("fp_cand").to_frame()
                .join(fpb.groupby(["log_id", "timestamp_ns", "frame_idx"]).size().rename("fp_base"), how="outer").fillna(0))
    lost_frame = lost.groupby(["log_id", "timestamp_ns", "frame_idx"]).size().rename("lost_gt")
    wf = fp_frame.join(lost_frame, how="outer").fillna(0)
    wf["damage"] = wf.lost_gt + (wf.fp_cand - wf.fp_base).clip(lower=0)
    wf = wf.sort_values("damage", ascending=False).head(8).reset_index()
    L.append("\n## Worst frames for the candidate (open in Foxglove at this log time)\n")
    L.append("| scene | frame | log time (ns) | lost GT | FP base→cand |")
    L.append("|---|---|---|---|---|")
    for r in wf.itertuples():
        L.append(f"| `{r.log_id[:8]}` | {int(r.frame_idx)} | {int(r.timestamp_ns)} | {int(r.lost_gt)} | {int(r.fp_base)}→{int(r.fp_cand)} |")
    L.append(f"\nDrill in: `uv run replay trace {cand} --log <scene> --status FN` or `--status FP`.\n")

    L.append("## Tracking (CLEAR-MOT)\n")
    t = tr[tr.log_id.isna()]
    L.append("| class | MOTA base | MOTA cand | Δ | ID switches base→cand |")
    L.append("|---|---|---|---|---|")
    for r in t.itertuples():
        L.append(f"| {r.cls} | {_f(r.MOTA_base)} | {_f(r.MOTA_cand)} | {_f(r.d_MOTA, True)} | {int(r.idsw_base)}→{int(r.idsw_cand)} |")
    ts = tr[tr.log_id.notna()].sort_values("d_MOTA").head(5)
    L.append("\nLargest per-scene MOTA drops:\n")
    L.append("| scene | class | MOTA base→cand | Δ |")
    L.append("|---|---|---|---|")
    for r in ts.itertuples():
        L.append(f"| `{r.log_id[:8]}` | {r.cls} | {_f(r.MOTA_base)}→{_f(r.MOTA_cand)} | {_f(r.d_MOTA, True)} |")

    L.append("\n## Full slice table\n")
    full = d.sort_values(["log_id", "cls", "bucket"])[["log_id", "cls", "bucket", "support", "mAP_base", "mAP_cand", "d_mAP", "d_recall", "d_precision", "verdict"]]
    full = full.assign(log_id=full.log_id.str[:8])
    L.append(full.round(3).to_markdown(index=False))
    out = cfg.dir("reports") / f"regression_{tag}.md"
    out.write_text("\n".join(L), encoding="utf-8")
    log.info("wrote %s", out)
