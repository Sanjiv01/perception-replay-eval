"""PointPillars (KITTI, 3 classes) in pure PyTorch.

Network definition and anchor decoding are adapted from https://github.com/zhulf0804/PointPillars
(MIT License, Copyright (c) 2022 zhulf0804); see THIRD_PARTY_NOTICES.md. The original compiled CUDA
ops (hard voxelization, rotated NMS) are replaced here with torch / shapely equivalents so the
detector runs anywhere torch does (including Windows + Blackwell GPUs) with no build step.
State-dict keys are unchanged, so the published checkpoint loads as-is.
"""
from __future__ import annotations

import numpy as np
import shapely
import torch
import torch.nn as nn
import torch.nn.functional as F

KITTI_CLASSES = ["Pedestrian", "Cyclist", "Car"]
PC_RANGE = [0.0, -39.68, -3.0, 69.12, 39.68, 1.0]
VOXEL = [0.16, 0.16, 4.0]


# ----------------------------------------------------------------------------- ops (pure torch)

def hard_voxelize(pts: torch.Tensor, voxel_size, pc_range, max_points=32, max_voxels=40000):
    """Deterministic hard voxelization matching mmdet3d semantics.

    Voxels are ordered by first point appearance; each keeps its first `max_points` points.
    Returns voxels (M, max_points, C), coors (M, 3) as (x, y, z) indices, num_points (M,).
    """
    dev = pts.device
    vs = torch.tensor(voxel_size, device=dev)
    lo = torch.tensor(pc_range[:3], device=dev)
    grid = torch.round((torch.tensor(pc_range[3:], device=dev) - lo) / vs).long()
    c = torch.floor((pts[:, :3] - lo) / vs).long()
    keep = ((c >= 0) & (c < grid)).all(1)
    pts, c = pts[keep], c[keep]
    if pts.shape[0] == 0:
        return (pts.new_zeros((0, max_points, pts.shape[1])), c.new_zeros((0, 3)), c.new_zeros((0,)))
    lin = (c[:, 0] * grid[1] + c[:, 1]) * grid[2] + c[:, 2]
    uniq, inv = torch.unique(lin, return_inverse=True)
    n = pts.shape[0]
    ar = torch.arange(n, device=dev)
    first = torch.full((uniq.numel(),), n, device=dev, dtype=torch.long).scatter_reduce(0, inv, ar, "amin")
    order = torch.argsort(first)[:max_voxels]
    rank = torch.full((uniq.numel(),), -1, device=dev, dtype=torch.long)
    rank[order] = torch.arange(order.numel(), device=dev)
    vid = rank[inv]
    ok = vid >= 0
    pts, vid, ar, c = pts[ok], vid[ok], ar[ok], c[ok]
    srt = torch.argsort(vid * n + ar)            # group by voxel, keep original point order
    pts, vid, c = pts[srt], vid[srt], c[srt]
    counts = torch.bincount(vid, minlength=order.numel())
    starts = torch.cumsum(counts, 0) - counts
    slot = torch.arange(vid.numel(), device=dev) - starts[vid]
    m = slot < max_points
    voxels = pts.new_zeros((order.numel(), max_points, pts.shape[1]))
    voxels[vid[m], slot[m]] = pts[m]
    coors = torch.zeros((order.numel(), 3), dtype=torch.long, device=dev)
    coors[vid] = c
    return voxels, coors, counts.clamp(max=max_points)


def bev_polygons(xy: np.ndarray, sx: np.ndarray, sy: np.ndarray, rot: np.ndarray):
    """Shapely polygons for BEV boxes: centre xy, extents (sx, sy) along the box axes, rotation rot."""
    c, s = np.cos(rot), np.sin(rot)
    corners = np.array([[0.5, 0.5], [-0.5, 0.5], [-0.5, -0.5], [0.5, -0.5]])
    dx = corners[None, :, 0] * sx[:, None]
    dy = corners[None, :, 1] * sy[:, None]
    px = xy[:, 0:1] + dx * c[:, None] - dy * s[:, None]
    py = xy[:, 1:2] + dx * s[:, None] + dy * c[:, None]
    return shapely.polygons(np.stack([px, py], -1))


def rotated_nms(xy, sx, sy, rot, scores, thr) -> np.ndarray:
    """Greedy BEV NMS on rotated boxes. Returns kept indices sorted by score."""
    order = np.argsort(-scores)
    polys = bev_polygons(xy[order], sx[order], sy[order], rot[order])
    areas = shapely.area(polys)
    alive = np.ones(len(order), bool)
    keep = []
    for i in range(len(order)):
        if not alive[i]:
            continue
        keep.append(order[i])
        rest = np.nonzero(alive[i + 1:])[0] + i + 1
        if rest.size == 0:
            break
        inter = shapely.area(shapely.intersection(polys[i], polys[rest]))
        iou = inter / (areas[i] + areas[rest] - inter + 1e-9)
        alive[rest[iou > thr]] = False
    return np.array(keep, dtype=np.int64)


def limit_period(val, offset=0.5, period=np.pi):
    return val - torch.floor(val / period + offset) * period


# ----------------------------------------------------------------------------- network

class PillarEncoder(nn.Module):
    def __init__(self, voxel_size, point_cloud_range, in_channel, out_channel):
        super().__init__()
        self.out_channel = out_channel
        self.vx, self.vy = voxel_size[0], voxel_size[1]
        self.x_offset = voxel_size[0] / 2 + point_cloud_range[0]
        self.y_offset = voxel_size[1] / 2 + point_cloud_range[1]
        self.x_l = int((point_cloud_range[3] - point_cloud_range[0]) / voxel_size[0])
        self.y_l = int((point_cloud_range[4] - point_cloud_range[1]) / voxel_size[1])
        self.conv = nn.Conv1d(in_channel, out_channel, 1, bias=False)
        self.bn = nn.BatchNorm1d(out_channel, eps=1e-3, momentum=0.01)

    def forward(self, pillars, coors_batch, npoints_per_pillar):
        device = pillars.device
        offset_pt_center = pillars[:, :, :3] - torch.sum(pillars[:, :, :3], dim=1, keepdim=True) / npoints_per_pillar[:, None, None]
        x_off = pillars[:, :, :1] - (coors_batch[:, None, 1:2] * self.vx + self.x_offset)
        y_off = pillars[:, :, 1:2] - (coors_batch[:, None, 2:3] * self.vy + self.y_offset)
        features = torch.cat([pillars, offset_pt_center, x_off, y_off], dim=-1)
        features[:, :, 0:1] = x_off  # consistent with mmdet3d (issue #1150)
        features[:, :, 1:2] = y_off
        ids = torch.arange(0, pillars.size(1), device=device)
        mask = (ids[:, None] < npoints_per_pillar[None, :]).permute(1, 0).contiguous()
        features *= mask[:, :, None]
        features = features.permute(0, 2, 1).contiguous()
        features = F.relu(self.bn(self.conv(features)))
        pooled = torch.max(features, dim=-1)[0]
        canvases = []
        bs = int(coors_batch[-1, 0]) + 1
        for i in range(bs):
            sel = coors_batch[:, 0] == i
            cc = coors_batch[sel]
            canvas = torch.zeros((self.x_l, self.y_l, self.out_channel), dtype=torch.float32, device=device)
            canvas[cc[:, 1], cc[:, 2]] = pooled[sel]
            canvases.append(canvas.permute(2, 1, 0).contiguous())
        return torch.stack(canvases, dim=0)


class Backbone(nn.Module):
    def __init__(self, in_channel, out_channels, layer_nums, layer_strides=(2, 2, 2)):
        super().__init__()
        self.multi_blocks = nn.ModuleList()
        for i in range(len(layer_strides)):
            blocks = [nn.Conv2d(in_channel, out_channels[i], 3, stride=layer_strides[i], bias=False, padding=1),
                      nn.BatchNorm2d(out_channels[i], eps=1e-3, momentum=0.01), nn.ReLU(inplace=True)]
            for _ in range(layer_nums[i]):
                blocks += [nn.Conv2d(out_channels[i], out_channels[i], 3, bias=False, padding=1),
                           nn.BatchNorm2d(out_channels[i], eps=1e-3, momentum=0.01), nn.ReLU(inplace=True)]
            in_channel = out_channels[i]
            self.multi_blocks.append(nn.Sequential(*blocks))

    def forward(self, x):
        outs = []
        for blk in self.multi_blocks:
            x = blk(x)
            outs.append(x)
        return outs


class Neck(nn.Module):
    def __init__(self, in_channels, upsample_strides, out_channels):
        super().__init__()
        self.decoder_blocks = nn.ModuleList()
        for i in range(len(in_channels)):
            self.decoder_blocks.append(nn.Sequential(
                nn.ConvTranspose2d(in_channels[i], out_channels[i], upsample_strides[i], stride=upsample_strides[i], bias=False),
                nn.BatchNorm2d(out_channels[i], eps=1e-3, momentum=0.01), nn.ReLU(inplace=True)))

    def forward(self, x):
        return torch.cat([blk(xi) for blk, xi in zip(self.decoder_blocks, x)], dim=1)


class Head(nn.Module):
    def __init__(self, in_channel, n_anchors, n_classes):
        super().__init__()
        self.conv_cls = nn.Conv2d(in_channel, n_anchors * n_classes, 1)
        self.conv_reg = nn.Conv2d(in_channel, n_anchors * 7, 1)
        self.conv_dir_cls = nn.Conv2d(in_channel, n_anchors * 2, 1)

    def forward(self, x):
        return self.conv_cls(x), self.conv_reg(x), self.conv_dir_cls(x)


def make_anchors(feature_map_size, device):
    """(y_l, x_l, 3 classes, 2 rotations, 7) anchors, identical to the original generator."""
    ranges = [[0, -39.68, -0.6, 69.12, 39.68, -0.6], [0, -39.68, -0.6, 69.12, 39.68, -0.6],
              [0, -39.68, -1.78, 69.12, 39.68, -1.78]]
    sizes = [[0.6, 0.8, 1.73], [0.6, 1.76, 1.73], [1.6, 3.9, 1.56]]
    rots = torch.tensor([0, 1.57], device=device)
    ny, nx = int(feature_map_size[0]), int(feature_map_size[1])
    out = []
    for rg, sz in zip(ranges, sizes):
        xs = torch.linspace(rg[0], rg[3], nx + 1, device=device)
        ys = torch.linspace(rg[1], rg[4], ny + 1, device=device)
        xs = xs[:nx] + (xs[1] - xs[0]) / 2
        ys = ys[:ny] + (ys[1] - ys[0]) / 2
        zs = torch.tensor([rg[2]], device=device)
        g = [t[..., None] for t in torch.meshgrid(xs, ys, zs, rots, indexing="ij")]
        size = torch.tensor(sz, device=device)[None, None, None, None, :].repeat(nx, ny, 1, len(rots), 1)
        g.insert(3, size)
        a = torch.cat(g, dim=-1).permute(2, 1, 0, 3, 4).contiguous().squeeze(0)  # (ny, nx, 2, 7)
        out.append(a[:, :, None])
    return torch.cat(out, dim=2)


def anchors2bboxes(anchors, deltas):
    da = torch.sqrt(anchors[:, 3] ** 2 + anchors[:, 4] ** 2)
    x = deltas[:, 0] * da + anchors[:, 0]
    y = deltas[:, 1] * da + anchors[:, 1]
    z = deltas[:, 2] * anchors[:, 5] + anchors[:, 2] + anchors[:, 5] / 2
    w = anchors[:, 3] * torch.exp(deltas[:, 3])
    l = anchors[:, 4] * torch.exp(deltas[:, 4])
    h = anchors[:, 5] * torch.exp(deltas[:, 5])
    z = z - h / 2
    theta = anchors[:, 6] + deltas[:, 6]
    return torch.stack([x, y, z, w, l, h, theta], dim=1)


class PointPillars(nn.Module):
    def __init__(self, nclasses=3, max_num_points=32, max_voxels=40000):
        super().__init__()
        self.nclasses = nclasses
        self.max_num_points, self.max_voxels = max_num_points, max_voxels
        self.pillar_encoder = PillarEncoder(VOXEL, PC_RANGE, in_channel=9, out_channel=64)
        self.backbone = Backbone(64, [64, 128, 256], [3, 5, 5])
        self.neck = Neck([64, 128, 256], [1, 2, 4], [128, 128, 128])
        self.head = Head(384, n_anchors=2 * nclasses, n_classes=nclasses)
        self.nms_pre, self.nms_thr, self.score_thr, self.max_num = 100, 0.01, 0.1, 50
        self._anchors = None

    @torch.no_grad()
    def forward(self, pts: torch.Tensor) -> dict:
        """pts: (N, 4) x y z reflectance in the KITTI velodyne frame. Returns numpy dict for one cloud.

        Boxes are (x, y, z_bottom, w, l, h, theta) in the original mmdet3d-v0 / KITTI-lidar convention.
        """
        vox, coors, npts = hard_voxelize(pts, VOXEL, PC_RANGE, self.max_num_points, self.max_voxels)
        empty = {"boxes": np.zeros((0, 7), np.float32), "labels": np.zeros(0, np.int64), "scores": np.zeros(0, np.float32)}
        if vox.shape[0] == 0:
            return empty
        coors_b = F.pad(coors, (1, 0), value=0)
        feat = self.pillar_encoder(vox, coors_b, npts)
        cls, reg, dirc = self.head(self.neck(self.backbone(feat)))
        if self._anchors is None or self._anchors.device != cls.device:
            self._anchors = make_anchors(cls.shape[-2:], cls.device)
        cls = torch.sigmoid(cls[0].permute(1, 2, 0).reshape(-1, self.nclasses))
        reg = reg[0].permute(1, 2, 0).reshape(-1, 7)
        dirc = torch.max(dirc[0].permute(1, 2, 0).reshape(-1, 2), dim=1)[1]
        anchors = self._anchors.reshape(-1, 7)
        inds = cls.max(1)[0].topk(self.nms_pre)[1]
        cls, reg, dirc, anchors = cls[inds], reg[inds], dirc[inds], anchors[inds]
        boxes = anchors2bboxes(anchors, reg)

        cls_np, boxes_np, dir_np = cls.cpu().numpy(), boxes.cpu().numpy(), dirc.cpu().numpy()
        rb, rl, rs = [], [], []
        for i in range(self.nclasses):
            s = cls_np[:, i]
            sel = s > self.score_thr
            if not sel.any():
                continue
            b, s, d = boxes_np[sel], s[sel], dir_np[sel]
            # original nms_cuda uses (w along x, l along y) rotated by theta
            keep = rotated_nms(b[:, :2], b[:, 3], b[:, 4], b[:, 6], s, self.nms_thr)
            b, s, d = b[keep].copy(), s[keep], d[keep]
            th = torch.from_numpy(b[:, 6])
            b[:, 6] = (limit_period(th, 1, np.pi) + (1 - torch.from_numpy(d)) * np.pi).numpy()
            rb.append(b); rl.append(np.full(len(b), i)); rs.append(s)
        if not rb:
            return empty
        b, l, s = np.concatenate(rb), np.concatenate(rl), np.concatenate(rs)
        if len(b) > self.max_num:
            top = np.argsort(-s)[: self.max_num]
            b, l, s = b[top], l[top], s[top]
        return {"boxes": b.astype(np.float32), "labels": l.astype(np.int64), "scores": s.astype(np.float32)}
