# Evaluation: `pp-kitti-v1`

Config hash `688b7dcf14dc`. Source rows: `data/lake/eval/pp-kitti-v1/matches.parquet` (87999 rows). Counts at the 2.0 m TP threshold.

## Per class and distance bucket

| cls        | bucket   |   mAP |   AP@0.5m |   AP@1m |   AP@2m |   AP@4m |   n_gt |   tp |   fp |   fn |   precision |   recall |   ATE_m |   ASE |   AOE_rad |
|:-----------|:---------|------:|----------:|--------:|--------:|--------:|-------:|-----:|-----:|-----:|------------:|---------:|--------:|------:|----------:|
| CYCLIST    | 0-20m    | 0.86  |     0.86  |   0.86  |   0.86  |   0.86  |    167 |  144 |   36 |   23 |       0.8   |    0.862 |   0.163 | 0.439 |     0.136 |
| CYCLIST    | 20-35m   | 0.561 |     0.561 |   0.561 |   0.561 |   0.561 |     45 |   26 |   34 |   19 |       0.433 |    0.578 |   0.133 | 0.486 |     0.486 |
| CYCLIST    | 35-50m   | 0.15  |     0.15  |   0.15  |   0.15  |   0.15  |    112 |   22 |   33 |   90 |       0.4   |    0.196 |   0.228 | 0.592 |     2.465 |
| CYCLIST    | all      | 0.584 |     0.584 |   0.584 |   0.584 |   0.584 |    324 |  192 |  103 |  132 |       0.651 |    0.593 |   0.166 | 0.463 |     0.45  |
| PEDESTRIAN | 0-20m    | 0.179 |     0.175 |   0.175 |   0.177 |   0.189 |   2211 |  408 |  125 | 1803 |       0.765 |    0.185 |   0.171 | 0.335 |     1.243 |
| PEDESTRIAN | 20-35m   | 0.106 |     0.106 |   0.106 |   0.106 |   0.107 |   2555 |  301 |  122 | 2254 |       0.712 |    0.118 |   0.143 | 0.332 |     1.276 |
| PEDESTRIAN | 35-50m   | 0.044 |     0.044 |   0.044 |   0.044 |   0.044 |   2288 |   96 |   40 | 2192 |       0.706 |    0.042 |   0.218 | 0.39  |     1.29  |
| PEDESTRIAN | all      | 0.108 |     0.108 |   0.108 |   0.108 |   0.11  |   7054 |  805 |  287 | 6249 |       0.737 |    0.114 |   0.166 | 0.341 |     1.261 |
| VEHICLE    | 0-20m    | 0.42  |     0.374 |   0.422 |   0.442 |   0.442 |   4292 | 1925 |  397 | 2367 |       0.829 |    0.449 |   0.303 | 0.272 |     0.256 |
| VEHICLE    | 20-35m   | 0.366 |     0.326 |   0.362 |   0.388 |   0.389 |   4708 | 1940 |  536 | 2768 |       0.784 |    0.412 |   0.302 | 0.258 |     0.556 |
| VEHICLE    | 35-50m   | 0.202 |     0.173 |   0.203 |   0.215 |   0.215 |   3968 |  878 |  161 | 3090 |       0.845 |    0.221 |   0.303 | 0.29  |     0.783 |
| VEHICLE    | all      | 0.335 |     0.297 |   0.336 |   0.353 |   0.353 |  12968 | 4743 | 1094 | 8225 |       0.813 |    0.366 |   0.303 | 0.269 |     0.476 |

## Per scene (all distances)

| log_id                               | cls        |   mAP |   AP@2m |   n_gt |   tp |   fp |   fn |   recall |
|:-------------------------------------|:-----------|------:|--------:|-------:|-----:|-----:|-----:|---------:|
| 04994d08-156c-3018-9717-ba0e29be8153 | CYCLIST    |       |         |      0 |    0 |    7 |    0 |    0     |
| 04994d08-156c-3018-9717-ba0e29be8153 | PEDESTRIAN | 0.038 |   0.038 |   3370 |  117 |   23 | 3253 |    0.035 |
| 04994d08-156c-3018-9717-ba0e29be8153 | VEHICLE    | 0.324 |   0.354 |   4331 | 1516 |  101 | 2815 |    0.35  |
| 0b86f508-5df9-4a46-bc59-5b9536dbde9f | CYCLIST    | 0.186 |   0.186 |     93 |   18 |    9 |   75 |    0.194 |
| 0b86f508-5df9-4a46-bc59-5b9536dbde9f | PEDESTRIAN | 0.116 |   0.117 |    398 |   54 |   33 |  344 |    0.136 |
| 0b86f508-5df9-4a46-bc59-5b9536dbde9f | VEHICLE    | 0.361 |   0.376 |   3538 | 1362 |  161 | 2176 |    0.385 |
| 280269f9-6111-311d-b351-ce9f63f88c81 | CYCLIST    |       |         |      0 |    0 |   66 |    0 |    0     |
| 280269f9-6111-311d-b351-ce9f63f88c81 | PEDESTRIAN | 0.15  |   0.148 |   2783 |  465 |  181 | 2318 |    0.167 |
| 280269f9-6111-311d-b351-ce9f63f88c81 | VEHICLE    | 0.449 |   0.463 |   1746 |  855 |  421 |  891 |    0.49  |
| 2e3f2ae7-9ab9-3aef-a3ce-a0a97a0cb1ab | CYCLIST    | 0.748 |   0.748 |    231 |  174 |   21 |   57 |    0.753 |
| 2e3f2ae7-9ab9-3aef-a3ce-a0a97a0cb1ab | PEDESTRIAN | 0.331 |   0.331 |    503 |  169 |   50 |  334 |    0.336 |
| 2e3f2ae7-9ab9-3aef-a3ce-a0a97a0cb1ab | VEHICLE    | 0.267 |   0.279 |   3353 | 1010 |  411 | 2343 |    0.301 |

## Why boxes failed (FP/FN reasons)

| status   | cls        | reason                   |   count |
|:---------|:-----------|:-------------------------|--------:|
| FN       | CYCLIST    | missed                   |      81 |
| FN       | CYCLIST    | outside_model_input_crop |      39 |
| FN       | CYCLIST    | missed_sparse            |      12 |
| FN       | PEDESTRIAN | outside_model_input_crop |    3364 |
| FN       | PEDESTRIAN | missed                   |    1813 |
| FN       | PEDESTRIAN | missed_sparse            |     704 |
| FN       | PEDESTRIAN | mislocalized_pred        |     267 |
| FN       | PEDESTRIAN | class_confusion          |     101 |
| FN       | VEHICLE    | outside_model_input_crop |    6162 |
| FN       | VEHICLE    | missed                   |    1387 |
| FN       | VEHICLE    | mislocalized_pred        |     388 |
| FN       | VEHICLE    | missed_sparse            |     283 |
| FN       | VEHICLE    | class_confusion          |       5 |
| FP       | CYCLIST    | background               |      55 |
| FP       | CYCLIST    | class_confusion          |      47 |
| FP       | CYCLIST    | unevaluated_category     |       1 |
| FP       | PEDESTRIAN | background               |     226 |
| FP       | PEDESTRIAN | mislocalized             |      38 |
| FP       | PEDESTRIAN | unevaluated_category     |      13 |
| FP       | PEDESTRIAN | duplicate                |       5 |
| FP       | PEDESTRIAN | class_confusion          |       4 |
| FP       | PEDESTRIAN | gt_filtered              |       1 |
| FP       | VEHICLE    | background               |     976 |
| FP       | VEHICLE    | mislocalized             |      39 |
| FP       | VEHICLE    | unevaluated_category     |      39 |
| FP       | VEHICLE    | class_confusion          |      35 |
| FP       | VEHICLE    | duplicate                |       3 |
| FP       | VEHICLE    | gt_filtered              |       2 |

## Tracking (CLEAR-MOT, 2 m)

| cls        |   n_gt |   matches |   fp |   fn |   idsw |   MOTA |   MOTP_m |
|:-----------|-------:|----------:|-----:|-----:|-------:|-------:|---------:|
| CYCLIST    |    324 |       187 |    4 |  137 |      0 |  0.565 |    0.164 |
| PEDESTRIAN |   7054 |       695 |  137 | 6359 |     30 |  0.075 |    0.158 |
| VEHICLE    |  12968 |      4422 |  656 | 8546 |    124 |  0.281 |    0.294 |

Reproduce any count, e.g. FN for vehicles 35-50m:

```python
m = pd.read_parquet('data/lake/eval/pp-kitti-v1/matches.parquet')
m.query("threshold_m == 2 and cls == 'VEHICLE' and bucket == '35-50m' and status == 'FN'")
```
