from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import torch

from replay.common import bucket_label
from replay.detector.pointpillars import PointPillars, hard_voxelize, rotated_nms
from replay.evaluate import _match_frame, average_precision, in_model_fov

FIX = Path(__file__).parent / "fixtures"
CKPT = Path(__file__).parents[1] / "data" / "checkpoints" / "epoch_160.pth"


def test_ap_perfect_and_empty():
    assert average_precision(np.array([0.9, 0.8]), np.array([True, True]), 2) == pytest.approx(1.0)
    assert average_precision(np.array([]), np.array([], bool), 3) == 0.0
    assert np.isnan(average_precision(np.array([0.5]), np.array([False]), 0))


def test_ap_half_recall():
    # one TP out of two GT, ranked first -> precision 1 up to recall .5, then 0
    ap = average_precision(np.array([0.9, 0.1]), np.array([True, False]), 2)
    assert ap == pytest.approx(51 / 101, abs=1e-6)


def test_greedy_match_prefers_high_score():
    p = pd.DataFrame({"x": [0.0, 0.3], "y": [0.0, 0.0], "score": [0.2, 0.9]})
    g = pd.DataFrame({"tx_m": [0.1], "ty_m": [0.0]})
    ps, pairs, taken, _ = _match_frame(p, g, 2.0)
    by_score = {float(ps.iloc[i].score): j for i, j, _ in pairs}
    assert by_score[0.9] == 0 and by_score[0.2] == -1 and taken.all()


def test_buckets():
    assert list(bucket_label([0, 20, 35, 50], np.array([0, 19.9, 20, 49, 50, 80]))) == \
        ["0-20m", "0-20m", "20-35m", "35-50m", "out", "out"]


def test_fov_front_only_vs_360():
    assert in_model_fov([10, -10], [0, 0], [0]).tolist() == [True, False]
    assert in_model_fov([10, -10], [0, 0], [0, 90, 180, 270]).all()


def test_voxelize_keeps_first_points_and_order():
    pts = torch.tensor([[0.01, -39.6, 0, 1], [0.02, -39.6, 0, 2], [1.0, 0.0, 0, 3], [0.03, -39.6, 0, 4]])
    vox, coors, n = hard_voxelize(pts, [0.16, 0.16, 4], [0, -39.68, -3, 69.12, 39.68, 1], max_points=2)
    assert n.tolist() == [2, 1]
    assert vox[0, :, 3].tolist() == [1, 2]          # first two points in original order
    assert coors[0].tolist() == [0, 0, 0]


def test_rotated_nms_suppresses_overlap():
    xy = np.array([[0, 0], [0.2, 0], [10, 0]], float)
    keep = rotated_nms(xy, np.full(3, 2.0), np.full(3, 4.0), np.zeros(3), np.array([0.9, 0.8, 0.7]), 0.1)
    assert sorted(keep.tolist()) == [0, 2]


@pytest.mark.skipif(not CKPT.exists(), reason="checkpoint not downloaded (run `replay recompute` once)")
def test_port_reproduces_kitti_demo():
    """The pure-torch port must find the KITTI demo car at ~(12.7, 3.2) and cyclist at ~(15.5, -11.5)."""
    net = PointPillars().eval()
    net.load_state_dict(torch.load(CKPT, map_location="cpu", weights_only=True))
    pts = torch.from_numpy(np.fromfile(FIX / "kitti_000134.bin", dtype=np.float32).reshape(-1, 4))
    out = net(pts)
    def near(label, x, y):
        sel = out["labels"] == label
        d = np.hypot(out["boxes"][sel, 0] - x, out["boxes"][sel, 1] - y)
        return sel.any() and d.min() < 0.5 and out["scores"][sel][d.argmin()] > 0.8
    assert near(2, 12.65, 3.29) and near(1, 15.5, -11.4)
