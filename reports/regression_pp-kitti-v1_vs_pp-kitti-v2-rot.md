# Regression report: `pp-kitti-v1` → `pp-kitti-v2-rot`

Logs: 4 AV2 val scenes · TP threshold 2.0 m · flag rule: mAP drop ≥ 0.02 on a slice with ≥ 20 GT objects.

Source tables: `data/lake/eval/regression_pp-kitti-v1_vs_pp-kitti-v2-rot_slices.parquet`, `data/lake/eval/regression_pp-kitti-v1_vs_pp-kitti-v2-rot_gt_flips.parquet`.

## Headline (all scenes, all distances)

| class | mAP base | mAP cand | Δ mAP | recall Δ | precision Δ | FP base→cand | FN base→cand |
|---|---|---|---|---|---|---|---|
| CYCLIST | 0.589 | 0.665 | **+0.076** | +0.105 | -0.457 | 52→459 | 132→98 |
| PEDESTRIAN | 0.115 | 0.258 | **+0.144** | +0.166 | -0.149 | 108→706 | 5927→4819 |
| VEHICLE | 0.350 | 0.690 | **+0.340** | +0.369 | -0.120 | 405→2190 | 7050→2900 |

## What got worse (1 slices flagged)

| scene | class | distance | GT | mAP base→cand | Δ mAP | Δ precision | Δ recall | FP base→cand |
|---|---|---|---|---|---|---|---|---|
| `2e3f2ae7` | CYCLIST | 35-50m | 74 | 0.195→0.167 | **-0.029** | -0.326 | +0.000 | 10→39 |

## What got better (all scenes)

| class | distance | GT | mAP base→cand | Δ mAP | Δ recall |
|---|---|---|---|---|---|
| VEHICLE | 0-20m | 3677 | 0.430→0.920 | +0.490 | +0.516 |
| VEHICLE | all | 11251 | 0.350→0.690 | +0.340 | +0.369 |
| VEHICLE | 20-35m | 4079 | 0.402→0.741 | +0.339 | +0.374 |
| CYCLIST | 20-35m | 45 | 0.568→0.794 | +0.226 | +0.267 |
| PEDESTRIAN | 0-20m | 2143 | 0.188→0.404 | +0.216 | +0.246 |
| VEHICLE | 35-50m | 3495 | 0.211→0.396 | +0.185 | +0.208 |
| PEDESTRIAN | 20-35m | 2399 | 0.104→0.250 | +0.147 | +0.157 |
| PEDESTRIAN | all | 6672 | 0.115→0.258 | +0.144 | +0.166 |
| CYCLIST | 0-20m | 167 | 0.861→0.952 | +0.091 | +0.102 |
| CYCLIST | all | 324 | 0.589→0.665 | +0.076 | +0.105 |
| PEDESTRIAN | 35-50m | 2130 | 0.047→0.121 | +0.074 | +0.096 |

## Box-level evidence

GT objects detected by base but missed by candidate (**lost**): 4 · missed by base but detected by candidate (**gained**): 5296.

Why the candidate lost them:

| cls        | reason            |   lost GT |
|:-----------|:------------------|----------:|
| PEDESTRIAN | mislocalized_pred |         3 |
| VEHICLE    | mislocalized_pred |         1 |

False positives by reason (base vs candidate):

| cls        | reason               |   base |   cand |    Δ |
|:-----------|:---------------------|-------:|-------:|-----:|
| VEHICLE    | background           |    271 |   1644 | 1373 |
| PEDESTRIAN | background           |     76 |    459 |  383 |
| CYCLIST    | background           |      9 |    240 |  231 |
| VEHICLE    | unevaluated_category |     38 |    235 |  197 |
| CYCLIST    | class_confusion      |     42 |    209 |  167 |
| PEDESTRIAN | unevaluated_category |     13 |    117 |  104 |
| VEHICLE    | class_confusion      |     30 |    125 |   95 |
| VEHICLE    | mislocalized         |     32 |    111 |   79 |
| PEDESTRIAN | mislocalized         |      8 |     52 |   44 |
| PEDESTRIAN | duplicate            |      5 |     49 |   44 |
| VEHICLE    | gt_filtered          |     31 |     63 |   32 |
| PEDESTRIAN | class_confusion      |      4 |     21 |   17 |
| CYCLIST    | unevaluated_category |      1 |     10 |    9 |
| VEHICLE    | duplicate            |      3 |     12 |    9 |
| PEDESTRIAN | gt_filtered          |      2 |      8 |    6 |

## Worst frames for the candidate (open in Foxglove at this log time)

| scene | frame | log time (ns) | lost GT | FP base→cand |
|---|---|---|---|---|
| `280269f9` | 7 | 315977572759815000 | 0 | 4→18 |
| `2e3f2ae7` | 83 | 315971960459871000 | 0 | 0→13 |
| `280269f9` | 48 | 315977576859881000 | 0 | 1→14 |
| `2e3f2ae7` | 94 | 315971961560036000 | 0 | 1→13 |
| `280269f9` | 104 | 315977582460227000 | 0 | 3→15 |
| `2e3f2ae7` | 8 | 315971952959773000 | 0 | 0→12 |
| `280269f9` | 3 | 315977572359693000 | 0 | 3→15 |
| `280269f9` | 24 | 315977574459824000 | 0 | 0→12 |

Drill in: `uv run replay trace pp-kitti-v2-rot --log <scene> --status FN` or `--status FP`.

## Tracking (CLEAR-MOT)

| class | MOTA base | MOTA cand | Δ | ID switches base→cand |
|---|---|---|---|---|
| CYCLIST | 0.568 | 0.556 | -0.012 | 0→0 |
| PEDESTRIAN | 0.085 | 0.192 | +0.106 | 27→89 |
| VEHICLE | 0.319 | 0.551 | +0.232 | 103→181 |

Largest per-scene MOTA drops:

| scene | class | MOTA base→cand | Δ |
|---|---|---|---|
| `2e3f2ae7` | CYCLIST | 0.732→0.615 | -0.117 |
| `04994d08` | PEDESTRIAN | 0.027→0.070 | +0.042 |
| `280269f9` | VEHICLE | 0.395→0.460 | +0.066 |
| `0b86f508` | PEDESTRIAN | 0.093→0.174 | +0.081 |
| `2e3f2ae7` | PEDESTRIAN | 0.294→0.382 | +0.087 |

## Full slice table

| log_id   | cls        | bucket   |   support |   mAP_base |   mAP_cand |   d_mAP |   d_recall |   d_precision | verdict     |
|:---------|:-----------|:---------|----------:|-----------:|-----------:|--------:|-----------:|--------------:|:------------|
| 04994d08 | CYCLIST    | 0-20m    |         0 |    nan     |    nan     | nan     |      0     |         0     | low-support |
| 04994d08 | CYCLIST    | 20-35m   |         0 |    nan     |    nan     | nan     |      0     |         0     | low-support |
| 04994d08 | CYCLIST    | 35-50m   |         0 |    nan     |    nan     | nan     |      0     |         0     | low-support |
| 04994d08 | CYCLIST    | all      |         0 |    nan     |    nan     | nan     |      0     |         0     | low-support |
| 04994d08 | PEDESTRIAN | 0-20m    |      1062 |      0.097 |      0.198 |   0.101 |      0.13  |        -0.162 | improved    |
| 04994d08 | PEDESTRIAN | 20-35m   |      1373 |      0.019 |      0.081 |   0.062 |      0.071 |        -0.008 | improved    |
| 04994d08 | PEDESTRIAN | 35-50m   |       909 |      0.01  |      0.019 |   0.009 |      0.014 |        -0.027 | ok          |
| 04994d08 | PEDESTRIAN | all      |      3344 |      0.039 |      0.099 |   0.06  |      0.074 |        -0.115 | improved    |
| 04994d08 | VEHICLE    | 0-20m    |      1559 |      0.382 |      0.902 |   0.52  |      0.559 |        -0.061 | improved    |
| 04994d08 | VEHICLE    | 20-35m   |      1808 |      0.351 |      0.664 |   0.313 |      0.353 |        -0.047 | improved    |
| 04994d08 | VEHICLE    | 35-50m   |       917 |      0.163 |      0.268 |   0.105 |      0.116 |        -0.01  | improved    |
| 04994d08 | VEHICLE    | all      |      4284 |      0.32  |      0.664 |   0.344 |      0.377 |        -0.051 | improved    |
| 0b86f508 | CYCLIST    | 0-20m    |        25 |      0.059 |      0.654 |   0.595 |      0.68  |        -0.067 | improved    |
| 0b86f508 | CYCLIST    | 20-35m   |        30 |      0.361 |      0.738 |   0.377 |      0.4   |        -0.18  | improved    |
| 0b86f508 | CYCLIST    | 35-50m   |        38 |      0.139 |      0.241 |   0.103 |      0.132 |        -0.278 | improved    |
| 0b86f508 | CYCLIST    | all      |        93 |      0.189 |      0.509 |   0.32  |      0.366 |        -0.26  | improved    |
| 0b86f508 | PEDESTRIAN | 0-20m    |       191 |      0.143 |      0.394 |   0.25  |      0.304 |        -0.239 | improved    |
| 0b86f508 | PEDESTRIAN | 20-35m   |       110 |      0.197 |      0.356 |   0.16  |      0.182 |        -0.286 | improved    |
| 0b86f508 | PEDESTRIAN | 35-50m   |        95 |      0.04  |      0.063 |   0.023 |      0.032 |        -0.3   | improved    |
| 0b86f508 | PEDESTRIAN | all      |       396 |      0.131 |      0.301 |   0.17  |      0.205 |        -0.261 | improved    |
| 0b86f508 | VEHICLE    | 0-20m    |      1081 |      0.37  |      0.908 |   0.537 |      0.555 |        -0.086 | improved    |
| 0b86f508 | VEHICLE    | 20-35m   |      1065 |      0.468 |      0.804 |   0.336 |      0.363 |        -0.092 | improved    |
| 0b86f508 | VEHICLE    | 35-50m   |       975 |      0.292 |      0.506 |   0.214 |      0.241 |        -0.042 | improved    |
| 0b86f508 | VEHICLE    | all      |      3121 |      0.378 |      0.745 |   0.367 |      0.392 |        -0.079 | improved    |
| 280269f9 | CYCLIST    | 0-20m    |         0 |    nan     |    nan     | nan     |      0     |         0     | low-support |
| 280269f9 | CYCLIST    | 20-35m   |         0 |    nan     |    nan     | nan     |      0     |         0     | low-support |
| 280269f9 | CYCLIST    | 35-50m   |         0 |    nan     |    nan     | nan     |      0     |         0     | low-support |
| 280269f9 | CYCLIST    | all      |         0 |    nan     |    nan     | nan     |      0     |         0     | low-support |
| 280269f9 | PEDESTRIAN | 0-20m    |       707 |      0.279 |      0.651 |   0.372 |      0.38  |        -0.032 | improved    |
| 280269f9 | PEDESTRIAN | 20-35m   |       753 |      0.18  |      0.441 |   0.261 |      0.28  |        -0.007 | improved    |
| 280269f9 | PEDESTRIAN | 35-50m   |       969 |      0.066 |      0.209 |   0.144 |      0.169 |        -0.111 | improved    |
| 280269f9 | PEDESTRIAN | all      |      2429 |      0.161 |      0.414 |   0.253 |      0.265 |        -0.04  | improved    |
| 280269f9 | VEHICLE    | 0-20m    |       538 |      0.59  |      0.955 |   0.364 |      0.375 |        -0.225 | improved    |
| 280269f9 | VEHICLE    | 20-35m   |       623 |      0.44  |      0.895 |   0.455 |      0.49  |        -0.162 | improved    |
| 280269f9 | VEHICLE    | 35-50m   |       585 |      0.342 |      0.61  |   0.268 |      0.326 |        -0.215 | improved    |
| 280269f9 | VEHICLE    | all      |      1746 |      0.456 |      0.815 |   0.36  |      0.4   |        -0.197 | improved    |
| 2e3f2ae7 | CYCLIST    | 0-20m    |       142 |      1     |      1     |  -0     |      0     |        -0.202 | ok          |
| 2e3f2ae7 | CYCLIST    | 20-35m   |        15 |      1     |      1     |   0     |      0     |        -0.776 | low-support |
| 2e3f2ae7 | CYCLIST    | 35-50m   |        74 |      0.195 |      0.167 |  -0.029 |      0     |        -0.326 | REGRESSED   |
| 2e3f2ae7 | CYCLIST    | all      |       231 |      0.751 |      0.745 |  -0.006 |      0     |        -0.471 | ok          |
| 2e3f2ae7 | PEDESTRIAN | 0-20m    |       183 |      0.4   |      0.719 |   0.319 |      0.339 |        -0.378 | improved    |
| 2e3f2ae7 | PEDESTRIAN | 20-35m   |       163 |      0.463 |      0.732 |   0.269 |      0.294 |        -0.37  | improved    |
| 2e3f2ae7 | PEDESTRIAN | 35-50m   |       157 |      0.124 |      0.236 |   0.112 |      0.153 |        -0.202 | improved    |
| 2e3f2ae7 | PEDESTRIAN | all      |       503 |      0.333 |      0.569 |   0.236 |      0.266 |        -0.347 | improved    |
| 2e3f2ae7 | VEHICLE    | 0-20m    |       499 |      0.543 |      0.984 |   0.441 |      0.447 |        -0.265 | improved    |
| 2e3f2ae7 | VEHICLE    | 20-35m   |       583 |      0.391 |      0.699 |   0.308 |      0.334 |        -0.148 | improved    |
| 2e3f2ae7 | VEHICLE    | 35-50m   |      1018 |      0.105 |      0.28  |   0.176 |      0.193 |        -0.079 | improved    |
| 2e3f2ae7 | VEHICLE    | all      |      2100 |      0.287 |      0.551 |   0.264 |      0.292 |        -0.183 | improved    |
| ALL      | CYCLIST    | 0-20m    |       167 |      0.861 |      0.952 |   0.091 |      0.102 |        -0.328 | improved    |
| ALL      | CYCLIST    | 20-35m   |        45 |      0.568 |      0.794 |   0.226 |      0.267 |        -0.449 | improved    |
| ALL      | CYCLIST    | 35-50m   |       112 |      0.179 |      0.162 |  -0.017 |      0.045 |        -0.384 | ok          |
| ALL      | CYCLIST    | all      |       324 |      0.589 |      0.665 |   0.076 |      0.105 |        -0.457 | improved    |
| ALL      | PEDESTRIAN | 0-20m    |      2143 |      0.188 |      0.404 |   0.216 |      0.246 |        -0.172 | improved    |
| ALL      | PEDESTRIAN | 20-35m   |      2399 |      0.104 |      0.25  |   0.147 |      0.157 |        -0.121 | improved    |
| ALL      | PEDESTRIAN | 35-50m   |      2130 |      0.047 |      0.121 |   0.074 |      0.096 |        -0.125 | improved    |
| ALL      | PEDESTRIAN | all      |      6672 |      0.115 |      0.258 |   0.144 |      0.166 |        -0.149 | improved    |
| ALL      | VEHICLE    | 0-20m    |      3677 |      0.43  |      0.92  |   0.49  |      0.516 |        -0.135 | improved    |
| ALL      | VEHICLE    | 20-35m   |      4079 |      0.402 |      0.741 |   0.339 |      0.374 |        -0.106 | improved    |
| ALL      | VEHICLE    | 35-50m   |      3495 |      0.211 |      0.396 |   0.185 |      0.208 |        -0.11  | improved    |
| ALL      | VEHICLE    | all      |     11251 |      0.35  |      0.69  |   0.34  |      0.369 |        -0.12  | improved    |