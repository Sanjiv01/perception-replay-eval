# Regression report: `pp-kitti-v1` → `pp-kitti-v2`

Logs: 4 AV2 val scenes · TP threshold 2.0 m · flag rule: mAP drop ≥ 0.02 on a slice with ≥ 20 GT objects.

Source tables: `data/lake/eval/regression_pp-kitti-v1_vs_pp-kitti-v2_slices.parquet`, `data/lake/eval/regression_pp-kitti-v1_vs_pp-kitti-v2_gt_flips.parquet`.

## Headline (all scenes, all distances)

| class | mAP base | mAP cand | Δ mAP | recall Δ | precision Δ | FP base→cand | FN base→cand |
|---|---|---|---|---|---|---|---|
| CYCLIST | 0.584 | 0.123 | **-0.461** | -0.336 | -0.574 | 103→999 | 132→241 |
| PEDESTRIAN | 0.108 | 0.261 | **+0.152** | +0.225 | -0.189 | 287→1969 | 6249→4664 |
| VEHICLE | 0.335 | 0.587 | **+0.252** | +0.357 | -0.203 | 1094→5993 | 8225→3598 |

## What got worse (7 slices flagged)

| scene | class | distance | GT | mAP base→cand | Δ mAP | Δ precision | Δ recall | FP base→cand |
|---|---|---|---|---|---|---|---|---|
| `2e3f2ae7` | CYCLIST | 0-20m | 142 | 1.000→0.087 | **-0.913** | -0.615 | -0.789 | 0→48 |
| `ALL` | CYCLIST | 0-20m | 167 | 0.860→0.111 | **-0.749** | -0.650 | -0.605 | 36→243 |
| `2e3f2ae7` | CYCLIST | all | 231 | 0.748→0.021 | **-0.728** | -0.787 | -0.615 | 21→272 |
| `ALL` | CYCLIST | all | 324 | 0.584→0.123 | **-0.461** | -0.574 | -0.336 | 103→999 |
| `ALL` | CYCLIST | 20-35m | 45 | 0.561→0.249 | **-0.312** | -0.384 | -0.111 | 34→409 |
| `2e3f2ae7` | CYCLIST | 35-50m | 74 | 0.175→0.001 | **-0.174** | -0.573 | -0.216 | 12→76 |
| `ALL` | CYCLIST | 35-50m | 112 | 0.150→0.127 | **-0.023** | -0.348 | -0.027 | 33→347 |

## What got better (all scenes)

| class | distance | GT | mAP base→cand | Δ mAP | Δ recall |
|---|---|---|---|---|---|
| VEHICLE | 0-20m | 4292 | 0.420→0.791 | +0.371 | +0.492 |
| VEHICLE | all | 12968 | 0.335→0.587 | +0.252 | +0.357 |
| PEDESTRIAN | 0-20m | 2211 | 0.179→0.413 | +0.234 | +0.312 |
| VEHICLE | 20-35m | 4708 | 0.366→0.584 | +0.218 | +0.331 |
| VEHICLE | 35-50m | 3968 | 0.202→0.376 | +0.174 | +0.241 |
| PEDESTRIAN | all | 7054 | 0.108→0.261 | +0.152 | +0.225 |
| PEDESTRIAN | 35-50m | 2288 | 0.044→0.158 | +0.114 | +0.175 |
| PEDESTRIAN | 20-35m | 2555 | 0.106→0.219 | +0.113 | +0.194 |

## Box-level evidence

GT objects detected by base but missed by candidate (**lost**): 663 · missed by base but detected by candidate (**gained**): 6766.

Why the candidate lost them:

| cls        | reason            |   lost GT |
|:-----------|:------------------|----------:|
| VEHICLE    | missed            |       254 |
| VEHICLE    | mislocalized_pred |       156 |
| CYCLIST    | class_confusion   |        77 |
| CYCLIST    | missed            |        73 |
| PEDESTRIAN | missed            |        62 |
| PEDESTRIAN | mislocalized_pred |        27 |
| PEDESTRIAN | class_confusion   |        11 |
| VEHICLE    | missed_sparse     |         3 |

False positives by reason (base vs candidate):

| cls        | reason               |   base |   cand |    Δ |
|:-----------|:---------------------|-------:|-------:|-----:|
| VEHICLE    | background           |    976 |   5181 | 4205 |
| PEDESTRIAN | background           |    226 |   1572 | 1346 |
| CYCLIST    | class_confusion      |     47 |    591 |  544 |
| CYCLIST    | background           |     55 |    394 |  339 |
| VEHICLE    | mislocalized         |     39 |    298 |  259 |
| VEHICLE    | unevaluated_category |     39 |    243 |  204 |
| VEHICLE    | class_confusion      |     35 |    226 |  191 |
| PEDESTRIAN | unevaluated_category |     13 |    129 |  116 |
| PEDESTRIAN | mislocalized         |     38 |    153 |  115 |
| PEDESTRIAN | duplicate            |      5 |     85 |   80 |
| VEHICLE    | gt_filtered          |      2 |     45 |   43 |
| PEDESTRIAN | class_confusion      |      4 |     27 |   23 |
| CYCLIST    | unevaluated_category |      1 |     11 |   10 |
| CYCLIST    | gt_filtered          |      0 |      2 |    2 |
| PEDESTRIAN | gt_filtered          |      1 |      3 |    2 |
| CYCLIST    | duplicate            |      0 |      1 |    1 |
| VEHICLE    | duplicate            |      3 |      0 |   -3 |

## Worst frames for the candidate (open in Foxglove at this log time)

| scene | frame | log time (ns) | lost GT | FP base→cand |
|---|---|---|---|---|
| `2e3f2ae7` | 24 | 315971954559589000 | 1 | 5→37 |
| `2e3f2ae7` | 18 | 315971953959742000 | 1 | 4→34 |
| `280269f9` | 49 | 315977576960077000 | 1 | 0→29 |
| `2e3f2ae7` | 27 | 315971954859514000 | 1 | 6→34 |
| `2e3f2ae7` | 23 | 315971954460056000 | 1 | 5→33 |
| `2e3f2ae7` | 14 | 315971953559620000 | 1 | 4→32 |
| `2e3f2ae7` | 29 | 315971955059904000 | 1 | 5→33 |
| `2e3f2ae7` | 28 | 315971954959711000 | 1 | 7→35 |

Drill in: `uv run replay trace pp-kitti-v2 --log <scene> --status FN` or `--status FP`.

## Tracking (CLEAR-MOT)

| class | MOTA base | MOTA cand | Δ | ID switches base→cand |
|---|---|---|---|---|
| CYCLIST | 0.565 | -0.108 | -0.673 | 0→4 |
| PEDESTRIAN | 0.075 | 0.119 | +0.044 | 30→153 |
| VEHICLE | 0.281 | 0.285 | +0.004 | 124→233 |

Largest per-scene MOTA drops:

| scene | class | MOTA base→cand | Δ |
|---|---|---|---|
| `2e3f2ae7` | CYCLIST | 0.727→-0.312 | -1.039 |
| `280269f9` | VEHICLE | 0.330→-0.060 | -0.390 |
| `2e3f2ae7` | PEDESTRIAN | 0.286→-0.068 | -0.354 |
| `2e3f2ae7` | VEHICLE | 0.172→0.077 | -0.095 |
| `0b86f508` | PEDESTRIAN | 0.085→0.030 | -0.055 |

## Full slice table

| log_id   | cls        | bucket   |   support |   mAP_base |   mAP_cand |   d_mAP |   d_recall |   d_precision | verdict     |
|:---------|:-----------|:---------|----------:|-----------:|-----------:|--------:|-----------:|--------------:|:------------|
| 04994d08 | CYCLIST    | 0-20m    |         0 |    nan     |    nan     | nan     |      0     |         0     | low-support |
| 04994d08 | CYCLIST    | 20-35m   |         0 |    nan     |    nan     | nan     |      0     |         0     | low-support |
| 04994d08 | CYCLIST    | 35-50m   |         0 |    nan     |    nan     | nan     |      0     |         0     | low-support |
| 04994d08 | CYCLIST    | all      |         0 |    nan     |    nan     | nan     |      0     |         0     | low-support |
| 04994d08 | PEDESTRIAN | 0-20m    |      1088 |      0.093 |      0.218 |   0.125 |      0.174 |        -0.208 | improved    |
| 04994d08 | PEDESTRIAN | 20-35m   |      1373 |      0.017 |      0.091 |   0.073 |      0.093 |         0.063 | improved    |
| 04994d08 | PEDESTRIAN | 35-50m   |       909 |      0.01  |      0.076 |   0.066 |      0.068 |         0.092 | improved    |
| 04994d08 | PEDESTRIAN | all      |      3370 |      0.038 |      0.123 |   0.086 |      0.112 |        -0.128 | improved    |
| 04994d08 | VEHICLE    | 0-20m    |      1559 |      0.382 |      0.857 |   0.475 |      0.553 |        -0.105 | improved    |
| 04994d08 | VEHICLE    | 20-35m   |      1808 |      0.35  |      0.688 |   0.339 |      0.377 |        -0.088 | improved    |
| 04994d08 | VEHICLE    | 35-50m   |       964 |      0.174 |      0.385 |   0.211 |      0.229 |        -0.089 | improved    |
| 04994d08 | VEHICLE    | all      |      4331 |      0.324 |      0.678 |   0.354 |      0.408 |        -0.095 | improved    |
| 0b86f508 | CYCLIST    | 0-20m    |        25 |      0.059 |      0.485 |   0.425 |      0.44  |        -0.183 | improved    |
| 0b86f508 | CYCLIST    | 20-35m   |        30 |      0.357 |      0.575 |   0.217 |      0.3   |        -0.188 | improved    |
| 0b86f508 | CYCLIST    | 35-50m   |        38 |      0.139 |      0.396 |   0.257 |      0.342 |        -0.5   | improved    |
| 0b86f508 | CYCLIST    | all      |        93 |      0.186 |      0.463 |   0.277 |      0.355 |        -0.335 | improved    |
| 0b86f508 | PEDESTRIAN | 0-20m    |       191 |      0.134 |      0.354 |   0.22  |      0.356 |        -0.163 | improved    |
| 0b86f508 | PEDESTRIAN | 20-35m   |       110 |      0.197 |      0.194 |  -0.003 |      0.136 |        -0.578 | ok          |
| 0b86f508 | PEDESTRIAN | 35-50m   |        97 |      0.017 |      0.088 |   0.071 |      0.175 |        -0.074 | improved    |
| 0b86f508 | PEDESTRIAN | all      |       398 |      0.116 |      0.236 |   0.12  |      0.251 |        -0.29  | improved    |
| 0b86f508 | VEHICLE    | 0-20m    |      1167 |      0.366 |      0.753 |   0.388 |      0.511 |        -0.21  | improved    |
| 0b86f508 | VEHICLE    | 20-35m   |      1193 |      0.446 |      0.573 |   0.127 |      0.242 |        -0.254 | improved    |
| 0b86f508 | VEHICLE    | 35-50m   |      1178 |      0.266 |      0.39  |   0.125 |      0.225 |        -0.3   | improved    |
| 0b86f508 | VEHICLE    | all      |      3538 |      0.361 |      0.572 |   0.211 |      0.325 |        -0.245 | improved    |
| 280269f9 | CYCLIST    | 0-20m    |         0 |    nan     |    nan     | nan     |      0     |         0     | low-support |
| 280269f9 | CYCLIST    | 20-35m   |         0 |    nan     |    nan     | nan     |      0     |         0     | low-support |
| 280269f9 | CYCLIST    | 35-50m   |         0 |    nan     |    nan     | nan     |      0     |         0     | low-support |
| 280269f9 | CYCLIST    | all      |         0 |    nan     |    nan     | nan     |      0     |         0     | low-support |
| 280269f9 | PEDESTRIAN | 0-20m    |       749 |      0.264 |      0.677 |   0.413 |      0.501 |        -0.074 | improved    |
| 280269f9 | PEDESTRIAN | 20-35m   |       909 |      0.171 |      0.37  |   0.2   |      0.332 |        -0.049 | improved    |
| 280269f9 | PEDESTRIAN | 35-50m   |      1125 |      0.064 |      0.257 |   0.193 |      0.266 |        -0.092 | improved    |
| 280269f9 | PEDESTRIAN | all      |      2783 |      0.15  |      0.399 |   0.249 |      0.351 |        -0.057 | improved    |
| 280269f9 | VEHICLE    | 0-20m    |       538 |      0.59  |      0.632 |   0.042 |      0.37  |        -0.272 | improved    |
| 280269f9 | VEHICLE    | 20-35m   |       623 |      0.426 |      0.625 |   0.199 |      0.437 |        -0.228 | improved    |
| 280269f9 | VEHICLE    | 35-50m   |       585 |      0.325 |      0.484 |   0.159 |      0.274 |        -0.27  | improved    |
| 280269f9 | VEHICLE    | all      |      1746 |      0.449 |      0.575 |   0.127 |      0.361 |        -0.255 | improved    |
| 2e3f2ae7 | CYCLIST    | 0-20m    |       142 |      1     |      0.087 |  -0.913 |     -0.789 |        -0.615 | REGRESSED   |
| 2e3f2ae7 | CYCLIST    | 20-35m   |        15 |      1     |      0.017 |  -0.983 |     -0.933 |        -0.618 | low-support |
| 2e3f2ae7 | CYCLIST    | 35-50m   |        74 |      0.175 |      0.001 |  -0.174 |     -0.216 |        -0.573 | REGRESSED   |
| 2e3f2ae7 | CYCLIST    | all      |       231 |      0.748 |      0.021 |  -0.728 |     -0.615 |        -0.787 | REGRESSED   |
| 2e3f2ae7 | PEDESTRIAN | 0-20m    |       183 |      0.399 |      0.639 |   0.24  |      0.311 |        -0.576 | improved    |
| 2e3f2ae7 | PEDESTRIAN | 20-35m   |       163 |      0.462 |      0.645 |   0.182 |      0.313 |        -0.402 | improved    |
| 2e3f2ae7 | PEDESTRIAN | 35-50m   |       157 |      0.121 |      0.115 |  -0.006 |      0.14  |        -0.356 | ok          |
| 2e3f2ae7 | PEDESTRIAN | all      |       503 |      0.331 |      0.475 |   0.143 |      0.258 |        -0.479 | improved    |
| 2e3f2ae7 | VEHICLE    | 0-20m    |      1028 |      0.458 |      0.823 |   0.365 |      0.443 |        -0.208 | improved    |
| 2e3f2ae7 | VEHICLE    | 20-35m   |      1084 |      0.277 |      0.431 |   0.154 |      0.291 |        -0.197 | improved    |
| 2e3f2ae7 | VEHICLE    | 35-50m   |      1241 |      0.101 |      0.32  |   0.219 |      0.251 |        -0.173 | improved    |
| 2e3f2ae7 | VEHICLE    | all      |      3353 |      0.267 |      0.499 |   0.232 |      0.322 |        -0.19  | improved    |
| ALL      | CYCLIST    | 0-20m    |       167 |      0.86  |      0.111 |  -0.749 |     -0.605 |        -0.65  | REGRESSED   |
| ALL      | CYCLIST    | 20-35m   |        45 |      0.561 |      0.249 |  -0.312 |     -0.111 |        -0.384 | REGRESSED   |
| ALL      | CYCLIST    | 35-50m   |       112 |      0.15  |      0.127 |  -0.023 |     -0.027 |        -0.348 | REGRESSED   |
| ALL      | CYCLIST    | all      |       324 |      0.584 |      0.123 |  -0.461 |     -0.336 |        -0.574 | REGRESSED   |
| ALL      | PEDESTRIAN | 0-20m    |      2211 |      0.179 |      0.413 |   0.234 |      0.312 |        -0.225 | improved    |
| ALL      | PEDESTRIAN | 20-35m   |      2555 |      0.106 |      0.219 |   0.113 |      0.194 |        -0.158 | improved    |
| ALL      | PEDESTRIAN | 35-50m   |      2288 |      0.044 |      0.158 |   0.114 |      0.175 |        -0.148 | improved    |
| ALL      | PEDESTRIAN | all      |      7054 |      0.108 |      0.261 |   0.152 |      0.225 |        -0.189 | improved    |
| ALL      | VEHICLE    | 0-20m    |      4292 |      0.42  |      0.791 |   0.371 |      0.492 |        -0.189 | improved    |
| ALL      | VEHICLE    | 20-35m   |      4708 |      0.366 |      0.584 |   0.218 |      0.331 |        -0.205 | improved    |
| ALL      | VEHICLE    | 35-50m   |      3968 |      0.202 |      0.376 |   0.174 |      0.241 |        -0.237 | improved    |
| ALL      | VEHICLE    | all      |     12968 |      0.335 |      0.587 |   0.252 |      0.357 |        -0.203 | improved    |