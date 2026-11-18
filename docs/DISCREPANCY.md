# Tracing surprising numbers end to end

Written the way I'd explain it to the model owner. Every number below comes from a Parquet table in
`data/lake/` and every step has the command that reproduces it.

---

## 1. "v2 lost 20 points of vehicle precision" — mostly our evaluation, not the model

### The surprising number

The first regression report (`reports/before_roi_fix/regression_pp-kitti-v1_vs_pp-kitti-v2.md`) said:

| class | precision v1 → v2 | FP v1 → v2 |
|---|---|---|
| VEHICLE | 0.813 → **0.610** | 1,094 → **5,993** |

v2 runs the **same checkpoint** as v1. It only looks in more directions (4 rotated passes) and
stacks 3 sweeps. Five times more false positives from the same weights is suspicious, so I didn't
take it at face value.

### Step 1: aggregate → failure reasons

Every FP in `matches.parquet` carries a reason code (what, if anything, the box was near):

```
uv run replay trace pp-kitti-v2 --cls VEHICLE --status FP
```

Of v2's 5,993 vehicle FPs, **5,181 were `background`**: no labelled object of any category within
2 m. Only 243 were on unevaluated categories (trucks, buses) and 226 were class confusions. So these
are boxes on "nothing", and there are a lot of them.

### Step 2: reasons → frames

The worst frame was `2e3f2ae7` frame 24 (log time `315971954559589000`): **37 FPs for v2 vs 5 for v1**.

### Step 3: frames → boxes

In the BEV render (`reports/review_2e3f2ae7.mp4`, ~2.4 s in) and in Foxglove
(`data/mcap/2e3f2ae7-….mcap`, topic `/pred/pp-kitti-v2/boxes`), the red boxes form neat rows in
what are clearly **parking lots**, off the road and away from the green GT boxes. Clicking them shows
the metadata:

| pred_id | score | ego x, y | l / w / h (m) | distance to drivable area |
|---|---|---|---|---|
| `pp-kitti-v2:2e3f2ae7:315971954559589000:003` | 0.92 | 7.0, −12.9 | 4.0 / 1.6 / 1.4 | 8.0 m |
| `…:005` | 0.89 | −4.6, −12.9 | 3.9 / 1.6 / 1.4 | 7.9 m |
| `…:007` | 0.77 | 1.8, −12.7 | 4.2 / 1.6 / 1.5 | 7.7 m |
| `…:011` | 0.68 | 0.0, −16.7 | 4.2 / 1.6 / 1.4 | 11.8 m |

These are high-confidence, car-sized, car-shaped boxes in a row 8 m off the road. **They are almost
certainly real parked cars.**

### Step 4: boxes → root cause

Argoverse 2 doesn't label consistently far from the road. Its official detection eval scores only
inside a **region of interest: the drivable area from the log's map, dilated by 5 m**. Our evaluator
had no ROI filter, so every correctly detected parked car in a lot was counted as a false positive.

I checked this across the whole population, not just one frame (drivable areas come from
`data/raw/<log>/map/log_map_archive_*.json`):

| set | share inside the ROI |
|---|---|
| v2 vehicle **TPs** | 88.5% |
| v2 vehicle **"background" FPs** | **38.9%** |
| v1 vehicle "background" FPs | 27.8% |

True detections live on the road, and the "background" FPs mostly don't. v1 hid this because its
single forward-facing pass rarely looked sideways into parking lots. v2 looks everywhere, so it
"found" thousands of unlabelled cars.

### Fix

Added `evaluation.roi_filter: true` (`src/replay/roi.py`). GT **and** predictions outside drivable area + 5 m
are dropped before matching, which mirrors the official AV2 eval. Effect on the same predictions:

| model | class | precision before → after | FP before → after | mAP before → after |
|---|---|---|---|---|
| v1 | VEHICLE | 0.813 → 0.912 | 1,094 → 405 | 0.335 → 0.350 |
| v2 | VEHICLE | 0.610 → **0.748** | 5,993 → **2,772** | 0.587 → 0.632 |
| v2 | PEDESTRIAN | 0.548 → 0.726 | 1,969 → 833 | 0.261 → 0.303 |

### What stays true after the fix

v2 still produces about 7× more in-ROI vehicle FPs than v1 (2,772 vs 405). Part of that is real
coverage (v1 never looked behind the car, so it couldn't produce FPs there). The precision drop
from 0.91 to 0.75 is the real, honest number to discuss.

**For the model owner:** "The headline precision drop was mostly us scoring parked cars that the
dataset doesn't label. After matching AV2's own evaluation region, v2 is 0.75 precision / 0.73 recall
on vehicles vs v1's 0.91 / 0.37: a large net win, with a real but smaller precision cost."

---

## 2. "Cyclist mAP fell from 0.59 to 0.13" — a real regression, and which change caused it

After the ROI fix, v2 still regresses badly on cyclists (`reports/regression_pp-kitti-v1_vs_pp-kitti-v2.md`):
cyclist mAP 0.589 → 0.130 and cyclist FPs 52 → 764, concentrated in scene `2e3f2ae7` at 0–20 m
(mAP 1.000 → 0.094).

**Reasons → boxes:** `replay trace pp-kitti-v2 --cls CYCLIST --status FP` shows **541 of the 764 cyclist
FPs are `class_confusion(gt=PEDESTRIAN)`**: pedestrians labelled as cyclists. v1 made that mistake 36 times.

**Hypothesis:** stacking 3 sweeps (0.2 s) smears a walking pedestrian about 0.3 m along their direction of
travel. The KITTI-trained model has never seen motion smear. A pedestrian with a "tail" looks like a
person on a bike (a 1.7 m-long anchor).

**Test:** v2 bundles two changes, so I ran each alone over the same 4 logs (`ablations:` in the config):

| version | change | cyclist mAP | peds called cyclists | ped mAP | vehicle mAP |
|---|---|---|---|---|---|
| v1 | none | 0.589 | 36 | 0.115 | 0.350 |
| v2-rot | 4 rotated passes only | **0.665** | 193 | 0.258 | **0.690** |
| v2-sweeps | 3-sweep stacking only | **0.073** | 199 | 0.113 | 0.319 |
| v2 | both | 0.130 | 541 | 0.303 | 0.632 |

Sweep stacking alone destroys cyclists and helps nothing else: vehicles even get slightly worse. The
rotated passes alone improve all three classes. Together, the two compound (more passes × smeared
pedestrians = 541 confusions).

**For the model owner:** "Ship the 360° change, drop sweep stacking. The checkpoint wasn't trained on
multi-sweep input, so it reads moving pedestrians as cyclists. `v1 → v2-rot` regresses only one slice
(cyclists 35–50 m in one scene, −0.03 mAP on 74 GT), see `reports/regression_pp-kitti-v1_vs_pp-kitti-v2-rot.md`.
Multi-sweep is only worth revisiting with a model trained on it (with a time channel)."

---

## 3. Smaller one: "v1 vehicle recall is 0.37"

`replay trace pp-kitti-v1 --cls VEHICLE --status FN`: 75% of v1's 8,225 missed vehicles (pre-ROI)
have reason `outside_model_input_crop`. The KITTI model only sees x ∈ [0, 69] m, |y| < 40 m in front
of the car. The worst frame (`2e3f2ae7` frame 107, 30 FNs) is a row of parked cars directly behind and
beside the ego vehicle. That isn't a detection failure. v1 was never shown those points. It's the
motivation for v2's rotated passes, which take vehicle recall from 0.37 to 0.74.

## 4. Same root cause, different metric: "tracking didn't improve"

Before the ROI fix, vehicle mAP rose +0.25 from v1 to v2 but vehicle **MOTA moved only +0.004**
(`reports/before_roi_fix/regression_…md`, tracking section). The off-road parked cars above the
tracker's 0.3 score threshold were tracked consistently frame after frame, and each became a
"false track" that cancelled the recall gain. After the ROI fix the same predictions give **MOTA
0.319 → 0.477 (+0.158)**. One root cause, two misleading metrics. That's why the fix belongs in the
evaluator and not in a per-report footnote.

Still open: ID switches roughly double (vehicles 103 → 204), because the simple greedy tracker
sees more objects in 360°. The next step would be per-class score thresholds and a gating radius
tuned on `tracking_frame.parquet`, whose `idsw_gt_ids` column lists exactly which objects switched in which frame.
