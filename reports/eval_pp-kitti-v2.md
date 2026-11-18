# Evaluation: `pp-kitti-v2`

Config hash `3e26f2518ea3`. Source rows: `data/lake/eval/pp-kitti-v2/matches.parquet` (93160 rows). Counts at the 2.0 m TP threshold.

## Per class and distance bucket

| cls        | bucket   |   mAP |   AP@0.5m |   AP@1m |   AP@2m |   AP@4m |   n_gt |   tp |   fp |   fn |   precision |   recall |   ATE_m |   ASE |   AOE_rad |
|:-----------|:---------|------:|----------:|--------:|--------:|--------:|-------:|-----:|-----:|-----:|------------:|---------:|--------:|------:|----------:|
| CYCLIST    | 0-20m    | 0.124 |     0.1   |   0.105 |   0.146 |   0.146 |    167 |   43 |  175 |  124 |       0.197 |    0.257 |   0.566 | 0.464 |     1.948 |
| CYCLIST    | 20-35m   | 0.26  |     0.26  |   0.26  |   0.26  |   0.26  |     45 |   21 |  310 |   24 |       0.063 |    0.467 |   0.112 | 0.489 |     1.532 |
| CYCLIST    | 35-50m   | 0.131 |     0.13  |   0.13  |   0.132 |   0.132 |    112 |   19 |  279 |   93 |       0.064 |    0.17  |   0.189 | 0.471 |     0.906 |
| CYCLIST    | all      | 0.13  |     0.123 |   0.125 |   0.137 |   0.137 |    324 |   83 |  764 |  241 |       0.098 |    0.256 |   0.365 | 0.472 |     1.604 |
| PEDESTRIAN | 0-20m    | 0.458 |     0.445 |   0.446 |   0.455 |   0.486 |   2143 | 1052 |  415 | 1091 |       0.717 |    0.491 |   0.191 | 0.361 |     1.522 |
| PEDESTRIAN | 20-35m   | 0.271 |     0.26  |   0.269 |   0.273 |   0.284 |   2399 |  711 |  227 | 1688 |       0.758 |    0.296 |   0.218 | 0.353 |     1.436 |
| PEDESTRIAN | 35-50m   | 0.177 |     0.169 |   0.178 |   0.18  |   0.181 |   2130 |  441 |  191 | 1689 |       0.698 |    0.207 |   0.258 | 0.393 |     1.451 |
| PEDESTRIAN | all      | 0.303 |     0.293 |   0.294 |   0.304 |   0.319 |   6672 | 2204 |  833 | 4468 |       0.726 |    0.33  |   0.213 | 0.365 |     1.48  |
| VEHICLE    | 0-20m    | 0.817 |     0.604 |   0.784 |   0.922 |   0.956 |   3677 | 3487 | 1090 |  190 |       0.762 |    0.948 |   0.437 | 0.217 |     0.272 |
| VEHICLE    | 20-35m   | 0.672 |     0.516 |   0.665 |   0.749 |   0.76  |   4079 | 3151 | 1104 |  928 |       0.741 |    0.772 |   0.395 | 0.232 |     0.363 |
| VEHICLE    | 35-50m   | 0.403 |     0.33  |   0.409 |   0.432 |   0.442 |   3495 | 1598 |  578 | 1897 |       0.734 |    0.457 |   0.36  | 0.272 |     0.38  |
| VEHICLE    | all      | 0.632 |     0.476 |   0.621 |   0.709 |   0.724 |  11251 | 8236 | 2772 | 3015 |       0.748 |    0.732 |   0.406 | 0.233 |     0.328 |

## Per scene (all distances)

| log_id                               | cls        |   mAP |   AP@2m |   n_gt |   tp |   fp |   fn |   recall |
|:-------------------------------------|:-----------|------:|--------:|-------:|-----:|-----:|-----:|---------:|
| 04994d08-156c-3018-9717-ba0e29be8153 | CYCLIST    |       |         |      0 |    0 |   49 |    0 |    0     |
| 04994d08-156c-3018-9717-ba0e29be8153 | PEDESTRIAN | 0.139 |   0.137 |   3344 |  495 |  100 | 2849 |    0.148 |
| 04994d08-156c-3018-9717-ba0e29be8153 | VEHICLE    | 0.681 |   0.748 |   4284 | 3249 |  333 | 1035 |    0.758 |
| 0b86f508-5df9-4a46-bc59-5b9536dbde9f | CYCLIST    | 0.475 |   0.475 |     93 |   51 |   74 |   42 |    0.548 |
| 0b86f508-5df9-4a46-bc59-5b9536dbde9f | PEDESTRIAN | 0.34  |   0.332 |    396 |  151 |  122 |  245 |    0.381 |
| 0b86f508-5df9-4a46-bc59-5b9536dbde9f | VEHICLE    | 0.6   |   0.661 |   3121 | 2170 |  593 |  951 |    0.695 |
| 280269f9-6111-311d-b351-ce9f63f88c81 | CYCLIST    |       |         |      0 |    0 |  402 |    0 |    0     |
| 280269f9-6111-311d-b351-ce9f63f88c81 | PEDESTRIAN | 0.485 |   0.487 |   2429 | 1259 |  245 | 1170 |    0.518 |
| 280269f9-6111-311d-b351-ce9f63f88c81 | VEHICLE    | 0.594 |   0.78  |   1746 | 1486 | 1138 |  260 |    0.851 |
| 2e3f2ae7-9ab9-3aef-a3ce-a0a97a0cb1ab | CYCLIST    | 0.024 |   0.032 |    231 |   32 |  239 |  199 |    0.139 |
| 2e3f2ae7-9ab9-3aef-a3ce-a0a97a0cb1ab | PEDESTRIAN | 0.507 |   0.499 |    503 |  299 |  366 |  204 |    0.594 |
| 2e3f2ae7-9ab9-3aef-a3ce-a0a97a0cb1ab | VEHICLE    | 0.596 |   0.614 |   2100 | 1331 |  708 |  769 |    0.634 |

## Why boxes failed (FP/FN reasons)

| status   | cls        | reason               |   count |
|:---------|:-----------|:---------------------|--------:|
| FN       | CYCLIST    | missed               |     146 |
| FN       | CYCLIST    | class_confusion      |      79 |
| FN       | CYCLIST    | missed_sparse        |      16 |
| FN       | PEDESTRIAN | missed               |    2196 |
| FN       | PEDESTRIAN | missed_sparse        |    1209 |
| FN       | PEDESTRIAN | mislocalized_pred    |     808 |
| FN       | PEDESTRIAN | class_confusion      |     255 |
| FN       | VEHICLE    | missed               |    1751 |
| FN       | VEHICLE    | missed_sparse        |     799 |
| FN       | VEHICLE    | mislocalized_pred    |     454 |
| FN       | VEHICLE    | class_confusion      |      11 |
| FP       | CYCLIST    | class_confusion      |     546 |
| FP       | CYCLIST    | background           |     204 |
| FP       | CYCLIST    | unevaluated_category |      11 |
| FP       | CYCLIST    | gt_filtered          |       2 |
| FP       | CYCLIST    | duplicate            |       1 |
| FP       | PEDESTRIAN | background           |     513 |
| FP       | PEDESTRIAN | unevaluated_category |     126 |
| FP       | PEDESTRIAN | duplicate            |      82 |
| FP       | PEDESTRIAN | mislocalized         |      80 |
| FP       | PEDESTRIAN | class_confusion      |      26 |
| FP       | PEDESTRIAN | gt_filtered          |       6 |
| FP       | VEHICLE    | background           |    2017 |
| FP       | VEHICLE    | mislocalized         |     246 |
| FP       | VEHICLE    | class_confusion      |     214 |
| FP       | VEHICLE    | unevaluated_category |     201 |
| FP       | VEHICLE    | gt_filtered          |      94 |

## Tracking (CLEAR-MOT, 2 m)

| cls        |   n_gt |   matches |   fp |   fn |   idsw |   MOTA |   MOTP_m |
|:-----------|-------:|----------:|-----:|-----:|-------:|-------:|---------:|
| CYCLIST    |    324 |        63 |   85 |  261 |      4 | -0.08  |    0.266 |
| PEDESTRIAN |   6672 |      1933 |  387 | 4739 |    145 |  0.21  |    0.212 |
| VEHICLE    |  11251 |      7633 | 2066 | 3618 |    204 |  0.477 |    0.397 |

Reproduce any count, e.g. FN for vehicles 35-50m:

```python
m = pd.read_parquet('data/lake/eval/pp-kitti-v2/matches.parquet')
m.query("threshold_m == 2 and cls == 'VEHICLE' and bucket == '35-50m' and status == 'FN'")
```
