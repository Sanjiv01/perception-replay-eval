"""Write Foxglove-viewable MCAP files.

One file per log, data/mcap/<log_id>.mcap, containing:
  /tf                                   map->base_link per sweep, base_link->camera
  /lidar/points                         foxglove.PointCloud (ego frame, x y z intensity)
  /camera/<cam>/image|calibration       foxglove.CompressedImage + CameraCalibration
  /gt/boxes                             logged GT cuboids (evaluated classes green, others grey)
  /pred/<model>/boxes                   predictions, blue=TP red=FP grey=not scored (beyond range / outside ROI) (at tp_threshold_m)
  /eval/<model>/missed                  GT boxes the model missed (orange), i.e. the FNs
Every box carries metadata (gt_id / pred_id, class, score, status, matched id, center error)
so clicking it in Foxglove's 3D panel leads straight back to rows in the Parquet lake.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from foxglove_schemas_protobuf.CameraCalibration_pb2 import CameraCalibration
from foxglove_schemas_protobuf.Color_pb2 import Color
from foxglove_schemas_protobuf.CompressedImage_pb2 import CompressedImage
from foxglove_schemas_protobuf.CubePrimitive_pb2 import CubePrimitive
from foxglove_schemas_protobuf.FrameTransform_pb2 import FrameTransform
from foxglove_schemas_protobuf.FrameTransforms_pb2 import FrameTransforms
from foxglove_schemas_protobuf.KeyValuePair_pb2 import KeyValuePair
from foxglove_schemas_protobuf.PackedElementField_pb2 import PackedElementField
from foxglove_schemas_protobuf.PointCloud_pb2 import PointCloud
from foxglove_schemas_protobuf.Pose_pb2 import Pose
from foxglove_schemas_protobuf.Quaternion_pb2 import Quaternion
from foxglove_schemas_protobuf.SceneEntity_pb2 import SceneEntity
from foxglove_schemas_protobuf.SceneUpdate_pb2 import SceneUpdate
from foxglove_schemas_protobuf.TextPrimitive_pb2 import TextPrimitive
from foxglove_schemas_protobuf.Vector3_pb2 import Vector3
from google.protobuf.duration_pb2 import Duration
from google.protobuf.timestamp_pb2 import Timestamp
from mcap_protobuf.writer import Writer

from . import lake
from .common import Config, log, yaw_to_quat

LIFETIME = Duration(nanos=120_000_000)  # one 10 Hz frame + slack, so stale boxes vanish
COLORS = {
    "gt": Color(r=0.1, g=0.9, b=0.3, a=0.35),
    "gt_other": Color(r=0.6, g=0.6, b=0.6, a=0.15),
    "TP": Color(r=0.2, g=0.5, b=1.0, a=0.45),
    "FP": Color(r=1.0, g=0.15, b=0.15, a=0.55),
    "FN": Color(r=1.0, g=0.6, b=0.0, a=0.6),
    "not_scored": Color(r=0.6, g=0.6, b=0.6, a=0.3),  # beyond max_range_m or outside the ROI
}


def _ts(ns: int) -> Timestamp:
    return Timestamp(seconds=int(ns // 1_000_000_000), nanos=int(ns % 1_000_000_000))


def _cube_entity(ns, eid, x, y, z, l, w, h, yaw, color, label, meta: dict) -> SceneEntity:
    qw, qx, qy, qz = (float(v) for v in yaw_to_quat(yaw))
    x, y, z, l, w, h = (float(v) for v in (x, y, z, l, w, h))
    pose = Pose(position=Vector3(x=x, y=y, z=z), orientation=Quaternion(w=qw, x=qx, y=qy, z=qz))
    return SceneEntity(
        timestamp=_ts(ns), frame_id="base_link", id=eid, lifetime=LIFETIME, frame_locked=True,
        cubes=[CubePrimitive(pose=pose, size=Vector3(x=l, y=w, z=h), color=color)],
        texts=[TextPrimitive(pose=Pose(position=Vector3(x=x, y=y, z=z + h / 2 + 0.4),
                                       orientation=Quaternion(w=1)),
                             billboard=True, font_size=12, scale_invariant=True,
                             color=Color(r=1, g=1, b=1, a=0.9), text=label)] if label else [],
        metadata=[KeyValuePair(key=k, value=str(v)) for k, v in meta.items()],
    )


def _pointcloud(ns, pts: np.ndarray) -> PointCloud:
    f = PackedElementField
    return PointCloud(
        timestamp=_ts(ns), frame_id="base_link", pose=Pose(orientation=Quaternion(w=1)), point_stride=16,
        fields=[f(name="x", offset=0, type=f.FLOAT32), f(name="y", offset=4, type=f.FLOAT32),
                f(name="z", offset=8, type=f.FLOAT32), f(name="intensity", offset=12, type=f.FLOAT32)],
        data=np.ascontiguousarray(pts.astype(np.float32)).tobytes())


def write_log_mcap(cfg: Config, log_id: str, models: list[str]) -> None:
    lk = cfg.dir("lake")
    cam = cfg.raw["dataset"]["camera"]
    frames = lake.table(cfg, "frames", log_id).sort_values("timestamp_ns")
    ann = lake.table(cfg, "annotations", log_id)
    calib = lake.table(cfg, "calibration", log_id).set_index("sensor_name").loc[cam]
    sweeps = lake.load_sweeps(lk, log_id)
    eval_cats = {c for cats in cfg.ev["class_map"].values() for c in cats}
    gt_by_ts = dict(tuple(ann.groupby("timestamp_ns")))

    per_model = {}
    for m in models:
        preds = pd.read_parquet(lake.predictions_path(cfg, m), filters=[("log_id", "=", log_id)])
        mp = lake.eval_dir(cfg, m) / "matches.parquet"
        matches = pd.read_parquet(mp, filters=[("log_id", "=", log_id)]) if mp.exists() else None
        if matches is not None:
            thr = cfg.ev["tp_threshold_m"]
            mt = matches[matches.threshold_m == thr]
            st = mt.dropna(subset=["pred_id"]).set_index("pred_id")
            preds = preds.join(st[["status", "gt_id", "center_err_m"]], on="pred_id")
            fn = mt[mt.status == "FN"].merge(ann, on="gt_id", suffixes=("", "_gt"))
        else:
            preds["status"], fn = "TP", ann.iloc[0:0]
        per_model[m] = (dict(tuple(preds.groupby("timestamp_ns"))), dict(tuple(fn.groupby("timestamp_ns"))))

    out = cfg.dir("mcap") / f"{log_id}.mcap"
    raw_cam = cfg.dir("raw") / log_id / "sensors" / "cameras" / cam
    with open(out, "wb") as fh, Writer(fh) as w:
        for _, fr in frames.iterrows():
            ns = int(fr.timestamp_ns)
            tfs = FrameTransforms(transforms=[
                FrameTransform(timestamp=_ts(ns), parent_frame_id="map", child_frame_id="base_link",
                               translation=Vector3(x=fr.city_tx_m, y=fr.city_ty_m, z=fr.city_tz_m),
                               rotation=Quaternion(w=fr.city_qw, x=fr.city_qx, y=fr.city_qy, z=fr.city_qz)),
                FrameTransform(timestamp=_ts(ns), parent_frame_id="base_link", child_frame_id=cam,
                               translation=Vector3(x=calib.tx_m, y=calib.ty_m, z=calib.tz_m),
                               rotation=Quaternion(w=calib.qw, x=calib.qx, y=calib.qy, z=calib.qz)),
            ])
            w.write_message("/tf", tfs, log_time=ns, publish_time=ns)
            w.write_message("/lidar/points", _pointcloud(ns, sweeps[ns]), log_time=ns, publish_time=ns)

            cns = int(fr.camera_timestamp_ns)
            img = raw_cam / f"{cns}.jpg"
            if img.exists():
                w.write_message(f"/camera/{cam}/image", CompressedImage(
                    timestamp=_ts(cns), frame_id=cam, data=img.read_bytes(), format="jpeg"), log_time=ns, publish_time=ns)
                fx, fy, cx, cy = calib.fx_px, calib.fy_px, calib.cx_px, calib.cy_px
                w.write_message(f"/camera/{cam}/calibration", CameraCalibration(
                    timestamp=_ts(cns), frame_id=cam, width=int(calib.width_px), height=int(calib.height_px),
                    distortion_model="plumb_bob", D=[calib.k1, calib.k2, 0, 0, calib.k3],
                    K=[fx, 0, cx, 0, fy, cy, 0, 0, 1], R=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                    P=[fx, 0, cx, 0, 0, fy, cy, 0, 0, 0, 1, 0]), log_time=ns, publish_time=ns)

            gt = gt_by_ts.get(ns)
            ents = []
            if gt is not None:
                for g in gt.itertuples():
                    ev = g.category in eval_cats
                    ents.append(_cube_entity(
                        ns, g.track_uuid, g.tx_m, g.ty_m, g.tz_m, g.length_m, g.width_m, g.height_m, g.yaw,
                        COLORS["gt" if ev else "gt_other"], "",
                        {"gt_id": g.gt_id, "category": g.category, "track_uuid": g.track_uuid,
                         "num_interior_pts": g.num_interior_pts, "range_m": f"{g.range_m:.1f}"}))
            w.write_message("/gt/boxes", SceneUpdate(entities=ents), log_time=ns, publish_time=ns)

            for m, (pbt, fbt) in per_model.items():
                ents = []
                p = pbt.get(ns)
                if p is not None:
                    for r in p.itertuples():
                        st = r.status if isinstance(r.status, str) else "not_scored"
                        ents.append(_cube_entity(
                            ns, r.pred_id, r.x, r.y, r.z, r.length, r.width, r.height, r.yaw,
                            COLORS.get(st, COLORS["FP"]), f"{r.cls[:3]} {r.score:.2f}",
                            {"pred_id": r.pred_id, "class": r.cls, "score": f"{r.score:.3f}", "status": st,
                             "matched_gt_id": getattr(r, "gt_id", ""), "center_err_m": getattr(r, "center_err_m", "")}))
                w.write_message(f"/pred/{m}/boxes", SceneUpdate(entities=ents), log_time=ns, publish_time=ns)
                ents = []
                f = fbt.get(ns)
                if f is not None:
                    for g in f.itertuples():
                        ents.append(_cube_entity(
                            ns, "fn-" + g.track_uuid, g.tx_m, g.ty_m, g.tz_m, g.length_m + 0.2, g.width_m + 0.2,
                            g.height_m + 0.2, g.yaw, COLORS["FN"], f"MISS {g.cls[:3]}",
                            {"gt_id": g.gt_id, "class": g.cls, "category": g.category, "range_m": f"{g.range_m:.1f}",
                             "num_interior_pts": g.num_interior_pts}))
                w.write_message(f"/eval/{m}/missed", SceneUpdate(entities=ents), log_time=ns, publish_time=ns)
    log.info("wrote %s (%.0f MB)", out, out.stat().st_size / 1e6)
