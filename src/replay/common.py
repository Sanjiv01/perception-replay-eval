"""Shared config, paths and geometry helpers."""
from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import yaml

log = logging.getLogger("replay")

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "configs" / "pipeline.yaml"


@dataclass
class Config:
    raw: dict
    path: Path

    @classmethod
    def load(cls, path: str | Path | None = None) -> "Config":
        p = Path(path) if path else DEFAULT_CONFIG
        return cls(yaml.safe_load(p.read_text()), p)

    @property
    def hash(self) -> str:
        return hashlib.sha256(self.path.read_bytes()).hexdigest()[:12]

    def dir(self, key: str) -> Path:
        d = ROOT / self.raw["paths"][key]
        d.mkdir(parents=True, exist_ok=True)
        return d

    @property
    def logs(self) -> list[str]:
        return list(self.raw["dataset"]["logs"])

    @property
    def models(self) -> dict:
        """Main model versions plus ablations (ablations only run when named explicitly)."""
        return {**self.raw["models"], **(self.raw.get("ablations") or {})}

    @property
    def main_models(self) -> list[str]:
        return list(self.raw["models"])

    @property
    def ev(self) -> dict:
        return self.raw["evaluation"]


def write_manifest(path: Path, **kw) -> None:
    path.write_text(json.dumps(kw, indent=2, default=str))


# ---------------------------------------------------------------- geometry

def quat_to_yaw(qw, qx, qy, qz):
    """Heading (rotation about +z) of a wxyz quaternion, radians."""
    return np.arctan2(2.0 * (qw * qz + qx * qy), 1.0 - 2.0 * (qy * qy + qz * qz))


def quat_to_mat(qw, qx, qy, qz) -> np.ndarray:
    return np.array([
        [1 - 2 * (qy * qy + qz * qz), 2 * (qx * qy - qz * qw), 2 * (qx * qz + qy * qw)],
        [2 * (qx * qy + qz * qw), 1 - 2 * (qx * qx + qz * qz), 2 * (qy * qz - qx * qw)],
        [2 * (qx * qz - qy * qw), 2 * (qy * qz + qx * qw), 1 - 2 * (qx * qx + qy * qy)],
    ])


def yaw_to_quat(yaw):
    yaw = np.asarray(yaw, dtype=np.float64)
    return np.cos(yaw / 2), np.zeros_like(yaw), np.zeros_like(yaw), np.sin(yaw / 2)


def se3(qw, qx, qy, qz, tx, ty, tz) -> np.ndarray:
    T = np.eye(4)
    T[:3, :3] = quat_to_mat(qw, qx, qy, qz)
    T[:3, 3] = [tx, ty, tz]
    return T


def wrap_angle(a):
    return (np.asarray(a) + np.pi) % (2 * np.pi) - np.pi


def bucket_label(edges: list[float], r: np.ndarray) -> np.ndarray:
    """Distance bucket labels like '0-20m'. Values beyond the last edge get 'out'."""
    labels = np.array([f"{int(a)}-{int(b)}m" for a, b in zip(edges[:-1], edges[1:])] + ["out"])
    idx = np.clip(np.searchsorted(edges, r, side="right") - 1, 0, len(edges) - 1)
    idx = np.where(r >= edges[-1], len(edges) - 1, idx)
    return labels[idx]
