"""Model-version wrapper: AV2 ego-frame sweeps in, AV2-convention boxes out."""
from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path

import numpy as np
import torch

from ..common import ROOT, log
from .pointpillars import KITTI_CLASSES, PointPillars, rotated_nms

# KITTI class -> evaluated class name
CLASS_OUT = {"Car": "VEHICLE", "Pedestrian": "PEDESTRIAN", "Cyclist": "CYCLIST"}
CKPT_DIR = ROOT / "data" / "checkpoints"


def fetch_checkpoint(url: str, sha256: str | None) -> tuple[Path, str]:
    CKPT_DIR.mkdir(parents=True, exist_ok=True)
    dst = CKPT_DIR / Path(url).name
    if not dst.exists():
        log.info("downloading checkpoint %s", url)
        tmp = dst.with_suffix(".part")
        urllib.request.urlretrieve(url, tmp)
        tmp.replace(dst)
    digest = hashlib.sha256(dst.read_bytes()).hexdigest()
    if sha256 and digest != sha256:
        raise ValueError(f"checkpoint sha256 mismatch: {digest} != {sha256}")
    return dst, digest


def _rot2d(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s], [s, c]], dtype=np.float32)


class Detector:
    def __init__(self, name: str, spec: dict, device: str | None = None):
        self.name, self.spec = name, spec
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        path, self.ckpt_sha = fetch_checkpoint(spec["checkpoint_url"], spec.get("checkpoint_sha256"))
        self.net = PointPillars().to(self.device).eval()
        state = torch.load(path, map_location=self.device, weights_only=True)
        missing, unexpected = self.net.load_state_dict(state, strict=False)
        if missing or unexpected:
            raise RuntimeError(f"checkpoint mismatch: missing={missing} unexpected={unexpected}")
        self.net.score_thr = float(spec.get("score_thr", 0.1))

    def _one_pass(self, pts: np.ndarray, rot: float) -> np.ndarray:
        """Run the net on a cloud rotated by -rot; return (K, 9) [x y z l w h yaw score label] in ego frame."""
        p = pts.copy()
        if rot:
            p[:, :2] = p[:, :2] @ _rot2d(-rot).T
        p[:, 2] -= self.spec["sensor_height_m"]
        p[:, 3] *= self.spec["intensity_scale"]
        out = self.net(torch.from_numpy(p).to(self.device))
        b = out["boxes"]
        if len(b) == 0:
            return np.zeros((0, 9), np.float32)
        # KITTI-lidar (mmdet3d v0) -> standard: length along heading, yaw CCW from +x.
        yaw = -b[:, 6] - np.pi / 2
        xy = b[:, :2] @ _rot2d(rot).T
        z = b[:, 2] + b[:, 5] / 2 + self.spec["sensor_height_m"]
        res = np.stack([xy[:, 0], xy[:, 1], z, b[:, 4], b[:, 3], b[:, 5], yaw + rot,
                        out["scores"], out["labels"]], 1)
        return res.astype(np.float32)

    def predict(self, sweeps: list[np.ndarray]) -> list[dict]:
        """sweeps[0] is the current sweep (ego frame, x y z intensity); others are older sweeps
        already motion-compensated into the current ego frame."""
        pts = np.concatenate(sweeps[: self.spec.get("num_sweeps", 1)], 0).astype(np.float32)
        dets = np.concatenate([self._one_pass(pts, np.deg2rad(r)) for r in self.spec["rotations_deg"]], 0)
        if len(self.spec["rotations_deg"]) > 1 and len(dets):
            keep = []
            for c in np.unique(dets[:, 8]):
                idx = np.nonzero(dets[:, 8] == c)[0]
                k = rotated_nms(dets[idx, :2], dets[idx, 3], dets[idx, 4], dets[idx, 6], dets[idx, 7], 0.1)
                keep.append(idx[k])
            dets = dets[np.concatenate(keep)]
        yaw = (dets[:, 6] + np.pi) % (2 * np.pi) - np.pi
        return [dict(x=d[0], y=d[1], z=d[2], length=d[3], width=d[4], height=d[5], yaw=yw, score=d[7],
                     cls=CLASS_OUT[KITTI_CLASSES[int(d[8])]]) for d, yw in zip(dets, yaw)]
