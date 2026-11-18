# Evaluation: `pp-kitti-v2`

Config hash `688b7dcf14dc`. Source rows: `data/lake/eval/pp-kitti-v2/matches.parquet` (120239 rows). Counts at the 2.0 m TP threshold.

## Per class and distance bucket

| cls        | bucket   |   mAP |   AP@0.5m |   AP@1m |   AP@2m |   AP@4m |   n_gt |   tp |   fp |   fn |   precision |   recall |   ATE_m |   ASE |   AOE_rad |
|:-----------|:---------|------:|----------:|--------:|--------:|--------:|-------:|-----:|-----:|-----:|------------:|---------:|--------:|------:|----------:|
| CYCLIST    | 0-20m    | 0.111 |     0.091 |   0.095 |   0.129 |   0.129 |    167 |   43 |  243 |  124 |       0.15  |    0.257 |   0.566 | 0.464 |     1.948 |
| CYCLIST    | 20-35m   | 0.249 |     0.249 |   0.249 |   0.249 |   0.249 |     45 |   21 |  409 |   24 |       0.049 |    0.467 |   0.112 | 0.489 |     1.532 |
| CYCLIST    | 35-50m   | 0.127 |     0.126 |   0.126 |   0.128 |   0.128 |    112 |   19 |  347 |   93 |       0.052 |    0.17  |   0.189 | 0.471 |     0.906 |
| CYCLIST    | all      | 0.123 |     0.117 |   0.119 |   0.129 |   0.129 |    324 |   83 |  999 |  241 |       0.077 |    0.256 |   0.365 | 0.472 |     1.604 |
| PEDESTRIAN | 0-20m    | 0.413 |     0.395 |   0.402 |   0.404 |   0.452 |   2211 | 1097 |  932 | 1114 |       0.541 |    0.496 |   0.19  | 0.36  |     1.524 |
| PEDESTRIAN | 20-35m   | 0.219 |     0.213 |   0.214 |   0.223 |   0.226 |   2555 |  797 |  644 | 1758 |       0.553 |    0.312 |   0.215 | 0.351 |     1.454 |
| PEDESTRIAN | 35-50m   | 0.158 |     0.152 |   0.158 |   0.16  |   0.161 |   2288 |  496 |  393 | 1792 |       0.558 |    0.217 |   0.253 | 0.391 |     1.46  |
| PEDESTRIAN | all      | 0.261 |     0.253 |   0.254 |   0.256 |   0.28  |   7054 | 2390 | 1969 | 4664 |       0.548 |    0.339 |   0.211 | 0.363 |     1.487 |
| VEHICLE    | 0-20m    | 0.791 |     0.584 |   0.766 |   0.894 |   0.92  |   4292 | 4037 | 2266 |  255 |       0.64  |    0.941 |   0.428 | 0.234 |     0.304 |
| VEHICLE    | 20-35m   | 0.584 |     0.443 |   0.581 |   0.649 |   0.662 |   4708 | 3498 | 2544 | 1210 |       0.579 |    0.743 |   0.395 | 0.241 |     0.371 |
| VEHICLE    | 35-50m   | 0.376 |     0.307 |   0.383 |   0.403 |   0.411 |   3968 | 1835 | 1183 | 2133 |       0.608 |    0.462 |   0.353 | 0.276 |     0.386 |
| VEHICLE    | all      | 0.587 |     0.439 |   0.582 |   0.657 |   0.671 |  12968 | 9370 | 5993 | 3598 |       0.61  |    0.723 |   0.401 | 0.245 |     0.345 |

## Per scene (all distances)

| log_id                               | cls        |   mAP |   AP@2m |   n_gt |   tp |   fp |   fn |   recall |
|:-------------------------------------|:-----------|------:|--------:|-------:|-----:|-----:|-----:|---------:|
| 04994d08-156c-3018-9717-ba0e29be8153 | CYCLIST    |       |         |      0 |    0 |   61 |    0 |    0     |
| 04994d08-156c-3018-9717-ba0e29be8153 | PEDESTRIAN | 0.123 |   0.122 |   3370 |  496 |  205 | 2874 |    0.147 |
| 04994d08-156c-3018-9717-ba0e29be8153 | VEHICLE    | 0.678 |   0.744 |   4331 | 3281 |  615 | 1050 |    0.758 |
| 0b86f508-5df9-4a46-bc59-5b9536dbde9f | CYCLIST    | 0.463 |   0.463 |     93 |   51 |  103 |   42 |    0.548 |
| 0b86f508-5df9-4a46-bc59-5b9536dbde9f | PEDESTRIAN | 0.236 |   0.231 |    398 |  154 |  311 |  244 |    0.387 |
| 0b86f508-5df9-4a46-bc59-5b9536dbde9f | VEHICLE    | 0.572 |   0.633 |   3538 | 2512 | 1358 | 1026 |    0.71  |
| 280269f9-6111-311d-b351-ce9f63f88c81 | CYCLIST    |       |         |      0 |    0 |  563 |    0 |    0     |
| 280269f9-6111-311d-b351-ce9f63f88c81 | PEDESTRIAN | 0.399 |   0.397 |   2783 | 1441 |  732 | 1342 |    0.518 |
| 280269f9-6111-311d-b351-ce9f63f88c81 | VEHICLE    | 0.575 |   0.754 |   1746 | 1486 | 2095 |  260 |    0.851 |
| 2e3f2ae7-9ab9-3aef-a3ce-a0a97a0cb1ab | CYCLIST    | 0.021 |   0.029 |    231 |   32 |  272 |  199 |    0.139 |
| 2e3f2ae7-9ab9-3aef-a3ce-a0a97a0cb1ab | PEDESTRIAN | 0.475 |   0.466 |    503 |  299 |  721 |  204 |    0.594 |
| 2e3f2ae7-9ab9-3aef-a3ce-a0a97a0cb1ab | VEHICLE    | 0.499 |   0.527 |   3353 | 2091 | 1925 | 1262 |    0.624 |

## Why boxes failed (FP/FN reasons)

| status   | cls        | reason               |   count |
|:---------|:-----------|:---------------------|--------:|
| FN       | CYCLIST    | missed               |     146 |
| FN       | CYCLIST    | class_confusion      |      79 |
| FN       | CYCLIST    | missed_sparse        |      16 |
| FN       | PEDESTRIAN | missed               |    2297 |
| FN       | PEDESTRIAN | missed_sparse        |    1245 |
| FN       | PEDESTRIAN | mislocalized_pred    |     840 |
| FN       | PEDESTRIAN | class_confusion      |     282 |
| FN       | VEHICLE    | missed               |    1944 |
| FN       | VEHICLE    | missed_sparse        |     900 |
| FN       | VEHICLE    | mislocalized_pred    |     743 |
| FN       | VEHICLE    | class_confusion      |      11 |
| FP       | CYCLIST    | class_confusion      |     591 |
| FP       | CYCLIST    | background           |     394 |
| FP       | CYCLIST    | unevaluated_category |      11 |
| FP       | CYCLIST    | gt_filtered          |       2 |
| FP       | CYCLIST    | duplicate            |       1 |
| FP       | PEDESTRIAN | background           |    1572 |
| FP       | PEDESTRIAN | mislocalized         |     153 |
| FP       | PEDESTRIAN | unevaluated_category |     129 |
| FP       | PEDESTRIAN | duplicate            |      85 |
| FP       | PEDESTRIAN | class_confusion      |      27 |
| FP       | PEDESTRIAN | gt_filtered          |       3 |
| FP       | VEHICLE    | background           |    5181 |
| FP       | VEHICLE    | mislocalized         |     298 |
| FP       | VEHICLE    | unevaluated_category |     243 |
| FP       | VEHICLE    | class_confusion      |     226 |
| FP       | VEHICLE    | gt_filtered          |      45 |

## Tracking (CLEAR-MOT, 2 m)

| cls        |   n_gt |   matches |   fp |   fn |   idsw |   MOTA |   MOTP_m |
|:-----------|-------:|----------:|-----:|-----:|-------:|-------:|---------:|
| CYCLIST    |    324 |        63 |   94 |  261 |      4 | -0.108 |    0.266 |
| PEDESTRIAN |   7054 |      2049 | 1058 | 5005 |    153 |  0.119 |    0.215 |
| VEHICLE    |  12968 |      8475 | 4549 | 4493 |    233 |  0.285 |    0.389 |

Reproduce any count, e.g. FN for vehicles 35-50m:

```python
m = pd.read_parquet('data/lake/eval/pp-kitti-v2/matches.parquet')
m.query("threshold_m == 2 and cls == 'VEHICLE' and bucket == '35-50m' and status == 'FN'")
```
