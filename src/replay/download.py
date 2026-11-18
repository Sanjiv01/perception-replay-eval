"""Anonymous download of Argoverse 2 sensor logs from the public S3 bucket.

Only what the pipeline needs is fetched: lidar sweeps, annotations, ego poses, calibration and a
single camera stream. Files land byte-for-byte under data/raw/<log_id>/ with the AV2 layout.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import boto3
from botocore import UNSIGNED
from botocore.config import Config as BotoConfig
from tqdm import tqdm

from .common import Config, log


def _client():
    return boto3.client("s3", config=BotoConfig(signature_version=UNSIGNED, max_pool_connections=32),
                        region_name="us-east-1")


def _list(s3, bucket: str, prefix: str):
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=prefix):
        yield from page.get("Contents", [])


def download_log(cfg: Config, log_id: str, s3=None) -> Path:
    s3 = s3 or _client()
    ds = cfg.raw["dataset"]
    bucket, base = ds["s3_bucket"], f"{ds['s3_prefix']}/{ds['split']}/{log_id}/"
    out = cfg.dir("raw") / log_id
    wanted = [base + "annotations.feather", base + "city_SE3_egovehicle.feather"]
    prefixes = [base + "calibration/", base + "map/", base + "sensors/lidar/", base + f"sensors/cameras/{ds['camera']}/"]
    objs = [(k, None) for k in wanted]
    for p in prefixes:
        objs += [(o["Key"], o["Size"]) for o in _list(s3, bucket, p)]

    todo = []
    for key, size in objs:
        dst = out / key[len(base):]
        if dst.exists() and (size is None or dst.stat().st_size == size):
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        todo.append((key, dst))

    def fetch(item):
        key, dst = item
        tmp = dst.with_suffix(dst.suffix + ".part")
        s3.download_file(bucket, key, str(tmp))
        tmp.replace(dst)

    if todo:
        with ThreadPoolExecutor(16) as ex:
            list(tqdm(ex.map(fetch, todo), total=len(todo), desc=f"download {log_id[:8]}", unit="file"))
    log.info("log %s: %d files present (%d fetched)", log_id, len(objs), len(todo))
    return out


def download(cfg: Config) -> None:
    s3 = _client()
    for lid in cfg.logs:
        download_log(cfg, lid, s3)


def scout(cfg: Config, n: int = 40) -> None:
    """Print per-log class counts for the first n val logs to help pick diverse scenes."""
    import io

    import pyarrow.feather as feather

    s3 = _client()
    ds = cfg.raw["dataset"]
    prefix = f"{ds['s3_prefix']}/{ds['split']}/"
    r = s3.list_objects_v2(Bucket=ds["s3_bucket"], Prefix=prefix, Delimiter="/", MaxKeys=n)
    for cp in r.get("CommonPrefixes", []):
        lid = cp["Prefix"].rstrip("/").split("/")[-1]
        body = s3.get_object(Bucket=ds["s3_bucket"], Key=cp["Prefix"] + "annotations.feather")["Body"].read()
        df = feather.read_table(io.BytesIO(body)).to_pandas()
        df = df[df.num_interior_pts > 0]
        nfr = df.timestamp_ns.nunique()
        c = df.groupby("category").track_uuid.nunique()
        print(f"{lid} frames={nfr} veh={c.get('REGULAR_VEHICLE', 0)} ped={c.get('PEDESTRIAN', 0)} "
              f"cyc={c.get('BICYCLIST', 0) + c.get('MOTORCYCLIST', 0)} large={c.get('LARGE_VEHICLE', 0) + c.get('BOX_TRUCK', 0) + c.get('BUS', 0)}")
