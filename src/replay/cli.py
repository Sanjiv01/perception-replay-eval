"""`replay` command line. `replay all` runs the whole pipeline end to end."""
from __future__ import annotations

import argparse
import logging
import time

from .common import Config, log

STAGES = ["download", "ingest", "recompute", "evaluate", "export", "regress"]


def _stage(name, fn, *a, **kw):
    t = time.time()
    log.info("==> %s", name)
    out = fn(*a, **kw)
    log.info("<== %s (%.1fs)", name, time.time() - t)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="replay", description=__doc__)
    ap.add_argument("--config", default=None, help="pipeline yaml (default configs/pipeline.yaml)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("scout", help="list candidate val logs with class counts")
    sub.add_parser("download", help="fetch configured logs from the public AV2 S3 bucket")
    sub.add_parser("ingest", help="raw AV2 -> Parquet lake + base MCAP")
    p = sub.add_parser("recompute", help="run model versions over all scenes with Ray")
    p.add_argument("--models", nargs="*")
    p.add_argument("--no-ray", action="store_true")
    p.add_argument("--force", action="store_true", help="recompute scenes even if checkpointed")
    p = sub.add_parser("evaluate", help="detection + tracking metrics per frame/class/distance")
    p.add_argument("--models", nargs="*")
    p = sub.add_parser("export", help="write review MCAPs with GT + predictions + eval status")
    p.add_argument("--models", nargs="*")
    p = sub.add_parser("regress", help="regression report between two model versions")
    p.add_argument("base", nargs="?")
    p.add_argument("candidate", nargs="?")
    p = sub.add_parser("trace", help="drill a metric down to frames and boxes")
    p.add_argument("model")
    p.add_argument("--cls", default=None)
    p.add_argument("--bucket", default=None)
    p.add_argument("--log", default=None)
    p.add_argument("--status", default="FN", choices=["FN", "FP", "TP"])
    p.add_argument("--top", type=int, default=10)
    p = sub.add_parser("render", help="render a BEV review video for one log")
    p.add_argument("log_id")
    p.add_argument("--models", nargs="*")
    p = sub.add_parser("all", help="download -> ingest -> recompute -> evaluate -> export -> regress")
    p.add_argument("--no-ray", action="store_true")
    a = ap.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S")
    cfg = Config.load(a.config)
    models = getattr(a, "models", None) or cfg.main_models

    from . import download, evaluate, ingest, mcap_io, recompute, regression, trace

    if a.cmd == "scout":
        download.scout(cfg)
    elif a.cmd == "download":
        _stage("download", download.download, cfg)
    elif a.cmd == "ingest":
        _stage("ingest", ingest.ingest, cfg)
    elif a.cmd == "recompute":
        _stage("recompute", recompute.recompute, cfg, models, use_ray=not a.no_ray, force=a.force)
    elif a.cmd == "evaluate":
        _stage("evaluate", evaluate.evaluate, cfg, models)
    elif a.cmd == "export":
        for lid in cfg.logs:
            _stage(f"export {lid[:8]}", mcap_io.write_log_mcap, cfg, lid, models)
    elif a.cmd == "regress":
        base, cand = a.base or models[0], a.candidate or models[1]
        _stage("regress", regression.regress, cfg, base, cand)
    elif a.cmd == "trace":
        print(trace.trace(cfg, a.model, cls=a.cls, bucket=a.bucket, log_id=a.log, status=a.status, top=a.top))
    elif a.cmd == "render":
        from . import render
        render.render_log(cfg, a.log_id, models)
    elif a.cmd == "all":
        t = time.time()
        _stage("download", download.download, cfg)
        _stage("ingest", ingest.ingest, cfg, write_mcap=False)
        _stage("recompute", recompute.recompute, cfg, models, use_ray=not a.no_ray)
        _stage("evaluate", evaluate.evaluate, cfg, models)
        for lid in cfg.logs:
            _stage(f"export {lid[:8]}", mcap_io.write_log_mcap, cfg, lid, models)
        if len(models) >= 2:
            _stage("regress", regression.regress, cfg, models[0], models[1])
        log.info("pipeline finished in %.0fs. Reports in %s, MCAPs in %s", time.time() - t,
                 cfg.dir("reports"), cfg.dir("mcap"))


if __name__ == "__main__":
    main()
