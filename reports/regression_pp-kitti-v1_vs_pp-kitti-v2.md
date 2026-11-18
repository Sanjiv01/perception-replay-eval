# Regression report: `pp-kitti-v1` → `pp-kitti-v2`

Logs: 4 AV2 val scenes · TP threshold 2.0 m · flag rule: mAP drop ≥ 0.02 on a slice with ≥ 20 GT objects.

Source tables: `data/lake/eval/regression_pp-kitti-v1_vs_pp-kitti-v2_slices.parquet`, `data/lake/eval/regression_pp-kitti-v1_vs_pp-kitti-v2_gt_flips.parquet`.

## Headline (all scenes, all distances)

| class | mAP base | mAP cand | Δ mAP | recall Δ | precision Δ | FP base→cand | FN base→cand |
|---|---|---|---|---|---|---|---|
| CYCLIST | 0.589 | 0.130 | **-0.458** | -0.336 | -0.689 | 52→764 | 132→241 |
| PEDESTRIAN | 0.115 | 0.303 | **+0.188** | +0.219 | -0.148 | 108→833 | 5927→4468 |
| VEHICLE | 0.350 | 0.632 | **+0.282** | +0.359 | -0.164 | 405→2772 | 7050→3015 |

## What got worse (7 slices flagged)

| scene | class | distance | GT | mAP base→cand | Δ mAP | Δ precision | Δ recall | FP base→cand |
|---|---|---|---|---|---|---|---|---|
| `2e3f2ae7` | CYCLIST | 0-20m | 142 | 1.000→0.094 | **-0.906** | -0.589 | -0.789 | 0→43 |
| `ALL` | CYCLIST | 0-20m | 167 | 0.861→0.124 | **-0.736** | -0.686 | -0.605 | 19→175 |
| `2e3f2ae7` | CYCLIST | all | 231 | 0.751→0.024 | **-0.728** | -0.817 | -0.615 | 12→239 |
| `ALL` | CYCLIST | all | 324 | 0.589→0.130 | **-0.458** | -0.689 | -0.336 | 52→764 |
| `ALL` | CYCLIST | 20-35m | 45 | 0.568→0.260 | **-0.308** | -0.527 | -0.111 | 18→310 |
| `2e3f2ae7` | CYCLIST | 35-50m | 74 | 0.195→0.001 | **-0.195** | -0.615 | -0.216 | 10→66 |
| `ALL` | CYCLIST | 35-50m | 112 | 0.179→0.131 | **-0.048** | -0.531 | -0.027 | 15→279 |

## What got better (all scenes)

| class | distance | GT | mAP base→cand | Δ mAP | Δ recall |
|---|---|---|---|---|---|
| VEHICLE | 0-20m | 3677 | 0.430→0.817 | +0.387 | +0.496 |
| VEHICLE | all | 11251 | 0.350→0.632 | +0.282 | +0.359 |
| VEHICLE | 20-35m | 4079 | 0.402→0.672 | +0.270 | +0.341 |
| PEDESTRIAN | 0-20m | 2143 | 0.188→0.458 | +0.270 | +0.306 |
| VEHICLE | 35-50m | 3495 | 0.211→0.403 | +0.193 | +0.235 |
| PEDESTRIAN | all | 6672 | 0.115→0.303 | +0.188 | +0.219 |
| PEDESTRIAN | 20-35m | 2399 | 0.104→0.271 | +0.168 | +0.188 |
| PEDESTRIAN | 35-50m | 2130 | 0.047→0.177 | +0.130 | +0.165 |

## Box-level evidence

GT objects detected by base but missed by candidate (**lost**): 635 · missed by base but detected by candidate (**gained**): 6020.

Why the candidate lost them:

| cls        | reason            |   lost GT |
|:-----------|:------------------|----------:|
| VEHICLE    | missed            |       252 |
| VEHICLE    | mislocalized_pred |       134 |
| CYCLIST    | class_confusion   |        77 |
| CYCLIST    | missed            |        73 |
| PEDESTRIAN | missed            |        60 |
| PEDESTRIAN | mislocalized_pred |        27 |
| PEDESTRIAN | class_confusion   |         9 |
| VEHICLE    | missed_sparse     |         3 |

False positives by reason (base vs candidate):

| cls        | reason               |   base |   cand |    Δ |
|:-----------|:---------------------|-------:|-------:|-----:|
| VEHICLE    | background           |    271 |   2017 | 1746 |
| CYCLIST    | class_confusion      |     42 |    546 |  504 |
| PEDESTRIAN | background           |     76 |    513 |  437 |
| VEHICLE    | mislocalized         |     32 |    246 |  214 |
| CYCLIST    | background           |      9 |    204 |  195 |
| VEHICLE    | class_confusion      |     30 |    214 |  184 |
| VEHICLE    | unevaluated_category |     38 |    201 |  163 |
| PEDESTRIAN | unevaluated_category |     13 |    126 |  113 |
| PEDESTRIAN | duplicate            |      5 |     82 |   77 |
| PEDESTRIAN | mislocalized         |      8 |     80 |   72 |
| VEHICLE    | gt_filtered          |     31 |     94 |   63 |
| PEDESTRIAN | class_confusion      |      4 |     26 |   22 |
| CYCLIST    | unevaluated_category |      1 |     11 |   10 |
| PEDESTRIAN | gt_filtered          |      2 |      6 |    4 |
| CYCLIST    | gt_filtered          |      0 |      2 |    2 |
| CYCLIST    | duplicate            |      0 |      1 |    1 |
| VEHICLE    | duplicate            |      3 |      0 |   -3 |

## Worst frames for the candidate (open in Foxglove at this log time)

| scene | frame | log time (ns) | lost GT | FP base→cand |
|---|---|---|---|---|
| `280269f9` | 7 | 315977572759815000 | 1 | 4→24 |
| `280269f9` | 71 | 315977579159736000 | 2 | 2→18 |
| `280269f9` | 16 | 315977573659586000 | 4 | 1→14 |
| `2e3f2ae7` | 24 | 315971954559589000 | 1 | 0→15 |
| `2e3f2ae7` | 84 | 315971960559404000 | 1 | 0→15 |
| `280269f9` | 10 | 315977573059735000 | 2 | 4→18 |
| `2e3f2ae7` | 143 | 315971966459686000 | 1 | 1→16 |
| `280269f9` | 34 | 315977575459792000 | 2 | 1→15 |

Drill in: `uv run replay trace pp-kitti-v2 --log <scene> --status FN` or `--status FP`.

## Tracking (CLEAR-MOT)

| class | MOTA base | MOTA cand | Δ | ID switches base→cand |
|---|---|---|---|---|
| CYCLIST | 0.568 | -0.080 | -0.648 | 0→4 |
| PEDESTRIAN | 0.085 | 0.210 | +0.125 | 27→145 |
| VEHICLE | 0.319 | 0.477 | +0.158 | 103→204 |

Largest per-scene MOTA drops:

| scene | class | MOTA base→cand | Δ |
|---|---|---|---|
| `2e3f2ae7` | CYCLIST | 0.732→-0.286 | -1.017 |
| `2e3f2ae7` | PEDESTRIAN | 0.294→0.161 | -0.133 |
| `280269f9` | VEHICLE | 0.395→0.279 | -0.116 |
| `04994d08` | PEDESTRIAN | 0.027→0.094 | +0.067 |
| `0b86f508` | PEDESTRIAN | 0.093→0.197 | +0.104 |

## Full slice table

| log_id   | cls        | bucket   |   support |   mAP_base |   mAP_cand |   d_mAP |   d_recall |   d_precision | verdict     |
|:---------|:-----------|:---------|----------:|-----------:|-----------:|--------:|-----------:|--------------:|:------------|
| 04994d08 | CYCLIST    | 0-20m    |         0 |    nan     |    nan     | nan     |      0     |         0     | low-support |
| 04994d08 | CYCLIST    | 20-35m   |         0 |    nan     |    nan     | nan     |      0     |         0     | low-support |
| 04994d08 | CYCLIST    | 35-50m   |         0 |    nan     |    nan     | nan     |      0     |         0     | low-support |
| 04994d08 | CYCLIST    | all      |         0 |    nan     |    nan     | nan     |      0     |         0     | low-support |
| 04994d08 | PEDESTRIAN | 0-20m    |      1062 |      0.097 |      0.249 |   0.152 |      0.177 |        -0.171 | improved    |
| 04994d08 | PEDESTRIAN | 20-35m   |      1373 |      0.019 |      0.101 |   0.082 |      0.093 |         0.013 | improved    |
| 04994d08 | PEDESTRIAN | 35-50m   |       909 |      0.01  |      0.078 |   0.069 |      0.068 |         0.157 | improved    |
| 04994d08 | PEDESTRIAN | all      |      3344 |      0.039 |      0.139 |   0.101 |      0.113 |        -0.097 | improved    |
| 04994d08 | VEHICLE    | 0-20m    |      1559 |      0.382 |      0.86  |   0.478 |      0.553 |        -0.056 | improved    |
| 04994d08 | VEHICLE    | 20-35m   |      1808 |      0.351 |      0.691 |   0.34  |      0.377 |        -0.059 | improved    |
| 04994d08 | VEHICLE    | 35-50m   |       917 |      0.163 |      0.374 |   0.211 |      0.228 |        -0.067 | improved    |
| 04994d08 | VEHICLE    | all      |      4284 |      0.32  |      0.681 |   0.361 |      0.409 |        -0.058 | improved    |
| 0b86f508 | CYCLIST    | 0-20m    |        25 |      0.059 |      0.486 |   0.427 |      0.44  |        -0.135 | improved    |
| 0b86f508 | CYCLIST    | 20-35m   |        30 |      0.361 |      0.576 |   0.215 |      0.3   |        -0.214 | improved    |
| 0b86f508 | CYCLIST    | 35-50m   |        38 |      0.139 |      0.413 |   0.274 |      0.342 |        -0.394 | improved    |
| 0b86f508 | CYCLIST    | all      |        93 |      0.189 |      0.475 |   0.285 |      0.355 |        -0.312 | improved    |
| 0b86f508 | PEDESTRIAN | 0-20m    |       191 |      0.143 |      0.456 |   0.313 |      0.34  |        -0.281 | improved    |
| 0b86f508 | PEDESTRIAN | 20-35m   |       110 |      0.197 |      0.274 |   0.078 |      0.136 |        -0.301 | improved    |
| 0b86f508 | PEDESTRIAN | 35-50m   |        95 |      0.04  |      0.177 |   0.137 |      0.179 |        -0.1   | improved    |
| 0b86f508 | PEDESTRIAN | all      |       396 |      0.131 |      0.34  |   0.209 |      0.245 |        -0.278 | improved    |
| 0b86f508 | VEHICLE    | 0-20m    |      1081 |      0.37  |      0.753 |   0.382 |      0.5   |        -0.167 | improved    |
| 0b86f508 | VEHICLE    | 20-35m   |      1065 |      0.468 |      0.609 |   0.142 |      0.213 |        -0.185 | improved    |
| 0b86f508 | VEHICLE    | 35-50m   |       975 |      0.292 |      0.424 |   0.132 |      0.173 |        -0.173 | improved    |
| 0b86f508 | VEHICLE    | all      |      3121 |      0.378 |      0.6   |   0.222 |      0.3   |        -0.173 | improved    |
| 280269f9 | CYCLIST    | 0-20m    |         0 |    nan     |    nan     | nan     |      0     |         0     | low-support |
| 280269f9 | CYCLIST    | 20-35m   |         0 |    nan     |    nan     | nan     |      0     |         0     | low-support |
| 280269f9 | CYCLIST    | 35-50m   |         0 |    nan     |    nan     | nan     |      0     |         0     | low-support |
| 280269f9 | CYCLIST    | all      |         0 |    nan     |    nan     | nan     |      0     |         0     | low-support |
| 280269f9 | PEDESTRIAN | 0-20m    |       707 |      0.279 |      0.747 |   0.468 |      0.489 |        -0.09  | improved    |
| 280269f9 | PEDESTRIAN | 20-35m   |       753 |      0.18  |      0.49  |   0.311 |      0.341 |         0.022 | improved    |
| 280269f9 | PEDESTRIAN | 35-50m   |       969 |      0.066 |      0.284 |   0.218 |      0.259 |        -0.088 | improved    |
| 280269f9 | PEDESTRIAN | all      |      2429 |      0.161 |      0.485 |   0.323 |      0.352 |        -0.047 | improved    |
| 280269f9 | VEHICLE    | 0-20m    |       538 |      0.59  |      0.635 |   0.045 |      0.37  |        -0.213 | improved    |
| 280269f9 | VEHICLE    | 20-35m   |       623 |      0.44  |      0.651 |   0.211 |      0.437 |        -0.249 | improved    |
| 280269f9 | VEHICLE    | 35-50m   |       585 |      0.342 |      0.515 |   0.173 |      0.274 |        -0.336 | improved    |
| 280269f9 | VEHICLE    | all      |      1746 |      0.456 |      0.594 |   0.138 |      0.361 |        -0.256 | improved    |
| 2e3f2ae7 | CYCLIST    | 0-20m    |       142 |      1     |      0.094 |  -0.906 |     -0.789 |        -0.589 | REGRESSED   |
| 2e3f2ae7 | CYCLIST    | 20-35m   |        15 |      1     |      0.017 |  -0.983 |     -0.933 |        -0.875 | low-support |
| 2e3f2ae7 | CYCLIST    | 35-50m   |        74 |      0.195 |      0.001 |  -0.195 |     -0.216 |        -0.615 | REGRESSED   |
| 2e3f2ae7 | CYCLIST    | all      |       231 |      0.751 |      0.024 |  -0.728 |     -0.615 |        -0.817 | REGRESSED   |
| 2e3f2ae7 | PEDESTRIAN | 0-20m    |       183 |      0.4   |      0.661 |   0.261 |      0.311 |        -0.432 | improved    |
| 2e3f2ae7 | PEDESTRIAN | 20-35m   |       163 |      0.463 |      0.694 |   0.231 |      0.313 |        -0.312 | improved    |
| 2e3f2ae7 | PEDESTRIAN | 35-50m   |       157 |      0.124 |      0.142 |   0.018 |      0.14  |        -0.318 | ok          |
| 2e3f2ae7 | PEDESTRIAN | all      |       503 |      0.333 |      0.507 |   0.175 |      0.258 |        -0.379 | improved    |
| 2e3f2ae7 | VEHICLE    | 0-20m    |       499 |      0.543 |      0.994 |   0.452 |      0.447 |        -0.234 | improved    |
| 2e3f2ae7 | VEHICLE    | 20-35m   |       583 |      0.391 |      0.719 |   0.328 |      0.357 |        -0.199 | improved    |
| 2e3f2ae7 | VEHICLE    | 35-50m   |      1018 |      0.105 |      0.347 |   0.243 |      0.278 |        -0.155 | improved    |
| 2e3f2ae7 | VEHICLE    | all      |      2100 |      0.287 |      0.596 |   0.309 |      0.34  |        -0.192 | improved    |
| ALL      | CYCLIST    | 0-20m    |       167 |      0.861 |      0.124 |  -0.736 |     -0.605 |        -0.686 | REGRESSED   |
| ALL      | CYCLIST    | 20-35m   |        45 |      0.568 |      0.26  |  -0.308 |     -0.111 |        -0.527 | REGRESSED   |
| ALL      | CYCLIST    | 35-50m   |       112 |      0.179 |      0.131 |  -0.048 |     -0.027 |        -0.531 | REGRESSED   |
| ALL      | CYCLIST    | all      |       324 |      0.589 |      0.13  |  -0.458 |     -0.336 |        -0.689 | REGRESSED   |
| ALL      | PEDESTRIAN | 0-20m    |      2143 |      0.188 |      0.458 |   0.27  |      0.306 |        -0.206 | improved    |
| ALL      | PEDESTRIAN | 20-35m   |      2399 |      0.104 |      0.271 |   0.168 |      0.188 |        -0.073 | improved    |
| ALL      | PEDESTRIAN | 35-50m   |      2130 |      0.047 |      0.177 |   0.13  |      0.165 |        -0.104 | improved    |
| ALL      | PEDESTRIAN | all      |      6672 |      0.115 |      0.303 |   0.188 |      0.219 |        -0.148 | improved    |
| ALL      | VEHICLE    | 0-20m    |      3677 |      0.43  |      0.817 |   0.387 |      0.496 |        -0.143 | improved    |
| ALL      | VEHICLE    | 20-35m   |      4079 |      0.402 |      0.672 |   0.27  |      0.341 |        -0.166 | improved    |
| ALL      | VEHICLE    | 35-50m   |      3495 |      0.211 |      0.403 |   0.193 |      0.235 |        -0.206 | improved    |
| ALL      | VEHICLE    | all      |     11251 |      0.35  |      0.632 |   0.282 |      0.359 |        -0.164 | improved    |