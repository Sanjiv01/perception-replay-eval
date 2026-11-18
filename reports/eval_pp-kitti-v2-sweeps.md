# Evaluation: `pp-kitti-v2-sweeps`

Config hash `3e26f2518ea3`. Source rows: `data/lake/eval/pp-kitti-v2-sweeps/matches.parquet` (77462 rows). Counts at the 2.0 m TP threshold.

## Per class and distance bucket

| cls        | bucket   |   mAP |   AP@0.5m |   AP@1m |   AP@2m |   AP@4m |   n_gt |   tp |   fp |   fn |   precision |   recall |   ATE_m |   ASE |   AOE_rad |
|:-----------|:---------|------:|----------:|--------:|--------:|--------:|-------:|-----:|-----:|-----:|------------:|---------:|--------:|------:|----------:|
| CYCLIST    | 0-20m    | 0.061 |     0.037 |   0.043 |   0.081 |   0.081 |    167 |   22 |   73 |  145 |       0.232 |    0.132 |   0.529 | 0.46  |     1.984 |
| CYCLIST    | 20-35m   | 0.068 |     0.068 |   0.068 |   0.068 |   0.068 |     45 |    8 |   88 |   37 |       0.083 |    0.178 |   0.073 | 0.466 |     0.127 |
| CYCLIST    | 35-50m   | 0.108 |     0.105 |   0.105 |   0.111 |   0.111 |    112 |   13 |   54 |   99 |       0.194 |    0.116 |   0.203 | 0.512 |     0.29  |
| CYCLIST    | all      | 0.073 |     0.066 |   0.067 |   0.08  |   0.08  |    324 |   43 |  215 |  281 |       0.167 |    0.133 |   0.345 | 0.477 |     1.126 |
| PEDESTRIAN | 0-20m    | 0.186 |     0.183 |   0.184 |   0.184 |   0.194 |   2143 |  399 |   53 | 1744 |       0.883 |    0.186 |   0.19  | 0.382 |     1.135 |
| PEDESTRIAN | 20-35m   | 0.109 |     0.109 |   0.109 |   0.109 |   0.109 |   2399 |  279 |   50 | 2120 |       0.848 |    0.116 |   0.194 | 0.39  |     1.239 |
| PEDESTRIAN | 35-50m   | 0.055 |     0.055 |   0.055 |   0.055 |   0.055 |   2130 |  108 |   25 | 2022 |       0.812 |    0.051 |   0.264 | 0.436 |     1.287 |
| PEDESTRIAN | all      | 0.113 |     0.113 |   0.113 |   0.113 |   0.114 |   6672 |  786 |  128 | 5886 |       0.86  |    0.118 |   0.202 | 0.392 |     1.193 |
| VEHICLE    | 0-20m    | 0.379 |     0.281 |   0.36  |   0.431 |   0.443 |   3677 | 1593 |  178 | 2084 |       0.899 |    0.433 |   0.446 | 0.226 |     0.437 |
| VEHICLE    | 20-35m   | 0.352 |     0.304 |   0.338 |   0.379 |   0.388 |   4079 | 1578 |  199 | 2501 |       0.888 |    0.387 |   0.349 | 0.217 |     0.345 |
| VEHICLE    | 35-50m   | 0.23  |     0.203 |   0.229 |   0.239 |   0.249 |   3495 |  860 |  124 | 2635 |       0.874 |    0.246 |   0.313 | 0.267 |     0.355 |
| VEHICLE    | all      | 0.319 |     0.258 |   0.307 |   0.35  |   0.361 |  11251 | 4031 |  501 | 7220 |       0.889 |    0.358 |   0.38  | 0.231 |     0.384 |

## Per scene (all distances)

| log_id                               | cls        |   mAP |   AP@2m |   n_gt |   tp |   fp |   fn |   recall |
|:-------------------------------------|:-----------|------:|--------:|-------:|-----:|-----:|-----:|---------:|
| 04994d08-156c-3018-9717-ba0e29be8153 | CYCLIST    |       |         |      0 |    0 |    6 |    0 |    0     |
| 04994d08-156c-3018-9717-ba0e29be8153 | PEDESTRIAN | 0.039 |   0.039 |   3344 |  128 |   13 | 3216 |    0.038 |
| 04994d08-156c-3018-9717-ba0e29be8153 | VEHICLE    | 0.326 |   0.355 |   4284 | 1504 |   53 | 2780 |    0.351 |
| 0b86f508-5df9-4a46-bc59-5b9536dbde9f | CYCLIST    | 0.196 |   0.196 |     93 |   19 |   12 |   74 |    0.204 |
| 0b86f508-5df9-4a46-bc59-5b9536dbde9f | PEDESTRIAN | 0.128 |   0.128 |    396 |   53 |   17 |  343 |    0.134 |
| 0b86f508-5df9-4a46-bc59-5b9536dbde9f | VEHICLE    | 0.314 |   0.339 |   3121 | 1086 |  134 | 2035 |    0.348 |
| 280269f9-6111-311d-b351-ce9f63f88c81 | CYCLIST    |       |         |      0 |    0 |  161 |    0 |    0     |
| 280269f9-6111-311d-b351-ce9f63f88c81 | PEDESTRIAN | 0.18  |   0.178 |   2429 |  461 |   56 | 1968 |    0.19  |
| 280269f9-6111-311d-b351-ce9f63f88c81 | VEHICLE    | 0.291 |   0.402 |   1746 |  762 |  223 |  984 |    0.436 |
| 2e3f2ae7-9ab9-3aef-a3ce-a0a97a0cb1ab | CYCLIST    | 0.047 |   0.065 |    231 |   24 |   36 |  207 |    0.104 |
| 2e3f2ae7-9ab9-3aef-a3ce-a0a97a0cb1ab | PEDESTRIAN | 0.274 |   0.274 |    503 |  144 |   42 |  359 |    0.286 |
| 2e3f2ae7-9ab9-3aef-a3ce-a0a97a0cb1ab | VEHICLE    | 0.319 |   0.322 |   2100 |  679 |   91 | 1421 |    0.323 |

## Why boxes failed (FP/FN reasons)

| status   | cls        | reason                   |   count |
|:---------|:-----------|:-------------------------|--------:|
| FN       | CYCLIST    | missed                   |     227 |
| FN       | CYCLIST    | outside_model_input_crop |      39 |
| FN       | CYCLIST    | missed_sparse            |      11 |
| FN       | CYCLIST    | class_confusion          |       4 |
| FN       | PEDESTRIAN | outside_model_input_crop |    3133 |
| FN       | PEDESTRIAN | missed                   |    1701 |
| FN       | PEDESTRIAN | missed_sparse            |     673 |
| FN       | PEDESTRIAN | mislocalized_pred        |     281 |
| FN       | PEDESTRIAN | class_confusion          |      98 |
| FN       | VEHICLE    | outside_model_input_crop |    5452 |
| FN       | VEHICLE    | missed                   |    1282 |
| FN       | VEHICLE    | mislocalized_pred        |     262 |
| FN       | VEHICLE    | missed_sparse            |     214 |
| FN       | VEHICLE    | class_confusion          |      10 |
| FP       | CYCLIST    | class_confusion          |     199 |
| FP       | CYCLIST    | background               |      12 |
| FP       | CYCLIST    | unevaluated_category     |       3 |
| FP       | CYCLIST    | gt_filtered              |       1 |
| FP       | PEDESTRIAN | background               |      93 |
| FP       | PEDESTRIAN | duplicate                |      10 |
| FP       | PEDESTRIAN | class_confusion          |       9 |
| FP       | PEDESTRIAN | mislocalized             |       7 |
| FP       | PEDESTRIAN | unevaluated_category     |       6 |
| FP       | PEDESTRIAN | gt_filtered              |       3 |
| FP       | VEHICLE    | background               |     295 |
| FP       | VEHICLE    | mislocalized             |     103 |
| FP       | VEHICLE    | unevaluated_category     |      41 |
| FP       | VEHICLE    | gt_filtered              |      39 |
| FP       | VEHICLE    | class_confusion          |      23 |

## Tracking (CLEAR-MOT, 2 m)

| cls        |   n_gt |   matches |   fp |   fn |   idsw |   MOTA |   MOTP_m |
|:-----------|-------:|----------:|-----:|-----:|-------:|-------:|---------:|
| CYCLIST    |    324 |        35 |   14 |  289 |      2 |  0.059 |    0.286 |
| PEDESTRIAN |   6672 |       676 |   69 | 5996 |     23 |  0.088 |    0.193 |
| VEHICLE    |  11251 |      3791 |  343 | 7460 |    102 |  0.297 |    0.373 |

Reproduce any count, e.g. FN for vehicles 35-50m:

```python
m = pd.read_parquet('data/lake/eval/pp-kitti-v2-sweeps/matches.parquet')
m.query("threshold_m == 2 and cls == 'VEHICLE' and bucket == '35-50m' and status == 'FN'")
```
