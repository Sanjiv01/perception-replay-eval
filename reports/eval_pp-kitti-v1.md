# Evaluation: `pp-kitti-v1`

Config hash `3e26f2518ea3`. Source rows: `data/lake/eval/pp-kitti-v1/matches.parquet` (75820 rows). Counts at the 2.0 m TP threshold.

## Per class and distance bucket

| cls        | bucket   |   mAP |   AP@0.5m |   AP@1m |   AP@2m |   AP@4m |   n_gt |   tp |   fp |   fn |   precision |   recall |   ATE_m |   ASE |   AOE_rad |
|:-----------|:---------|------:|----------:|--------:|--------:|--------:|-------:|-----:|-----:|-----:|------------:|---------:|--------:|------:|----------:|
| CYCLIST    | 0-20m    | 0.861 |     0.861 |   0.861 |   0.861 |   0.861 |    167 |  144 |   19 |   23 |       0.883 |    0.862 |   0.163 | 0.439 |     0.136 |
| CYCLIST    | 20-35m   | 0.568 |     0.568 |   0.568 |   0.568 |   0.568 |     45 |   26 |   18 |   19 |       0.591 |    0.578 |   0.133 | 0.486 |     0.486 |
| CYCLIST    | 35-50m   | 0.179 |     0.179 |   0.179 |   0.179 |   0.179 |    112 |   22 |   15 |   90 |       0.595 |    0.196 |   0.228 | 0.592 |     2.465 |
| CYCLIST    | all      | 0.589 |     0.589 |   0.589 |   0.589 |   0.589 |    324 |  192 |   52 |  132 |       0.787 |    0.593 |   0.166 | 0.463 |     0.45  |
| PEDESTRIAN | 0-20m    | 0.188 |     0.185 |   0.185 |   0.186 |   0.196 |   2143 |  396 |   33 | 1747 |       0.923 |    0.185 |   0.172 | 0.336 |     1.246 |
| PEDESTRIAN | 20-35m   | 0.104 |     0.103 |   0.103 |   0.103 |   0.104 |   2399 |  260 |   53 | 2139 |       0.831 |    0.108 |   0.145 | 0.336 |     1.309 |
| PEDESTRIAN | 35-50m   | 0.047 |     0.047 |   0.047 |   0.047 |   0.047 |   2130 |   89 |   22 | 2041 |       0.802 |    0.042 |   0.223 | 0.399 |     1.231 |
| PEDESTRIAN | all      | 0.115 |     0.114 |   0.114 |   0.115 |   0.116 |   6672 |  745 |  108 | 5927 |       0.873 |    0.112 |   0.168 | 0.344 |     1.266 |
| VEHICLE    | 0-20m    | 0.43  |     0.387 |   0.425 |   0.454 |   0.454 |   3677 | 1662 |  174 | 2015 |       0.905 |    0.452 |   0.298 | 0.255 |     0.191 |
| VEHICLE    | 20-35m   | 0.402 |     0.362 |   0.397 |   0.425 |   0.425 |   4079 | 1762 |  182 | 2317 |       0.906 |    0.432 |   0.299 | 0.253 |     0.547 |
| VEHICLE    | 35-50m   | 0.211 |     0.182 |   0.211 |   0.225 |   0.225 |   3495 |  777 |   49 | 2718 |       0.941 |    0.222 |   0.3   | 0.287 |     0.819 |
| VEHICLE    | all      | 0.35  |     0.315 |   0.344 |   0.371 |   0.371 |  11251 | 4201 |  405 | 7050 |       0.912 |    0.373 |   0.299 | 0.26  |     0.456 |

## Per scene (all distances)

| log_id                               | cls        |   mAP |   AP@2m |   n_gt |   tp |   fp |   fn |   recall |
|:-------------------------------------|:-----------|------:|--------:|-------:|-----:|-----:|-----:|---------:|
| 04994d08-156c-3018-9717-ba0e29be8153 | CYCLIST    |       |         |      0 |    0 |    4 |    0 |    0     |
| 04994d08-156c-3018-9717-ba0e29be8153 | PEDESTRIAN | 0.039 |   0.039 |   3344 |  117 |    9 | 3227 |    0.035 |
| 04994d08-156c-3018-9717-ba0e29be8153 | VEHICLE    | 0.32  |   0.346 |   4284 | 1496 |   54 | 2788 |    0.349 |
| 0b86f508-5df9-4a46-bc59-5b9536dbde9f | CYCLIST    | 0.189 |   0.189 |     93 |   18 |    7 |   75 |    0.194 |
| 0b86f508-5df9-4a46-bc59-5b9536dbde9f | PEDESTRIAN | 0.131 |   0.133 |    396 |   54 |   11 |  342 |    0.136 |
| 0b86f508-5df9-4a46-bc59-5b9536dbde9f | VEHICLE    | 0.378 |   0.393 |   3121 | 1233 |   53 | 1888 |    0.395 |
| 280269f9-6111-311d-b351-ce9f63f88c81 | CYCLIST    |       |         |      0 |    0 |   29 |    0 |    0     |
| 280269f9-6111-311d-b351-ce9f63f88c81 | PEDESTRIAN | 0.161 |   0.161 |   2429 |  405 |   53 | 2024 |    0.167 |
| 280269f9-6111-311d-b351-ce9f63f88c81 | VEHICLE    | 0.456 |   0.47  |   1746 |  855 |  185 |  891 |    0.49  |
| 2e3f2ae7-9ab9-3aef-a3ce-a0a97a0cb1ab | CYCLIST    | 0.751 |   0.751 |    231 |  174 |   12 |   57 |    0.753 |
| 2e3f2ae7-9ab9-3aef-a3ce-a0a97a0cb1ab | PEDESTRIAN | 0.333 |   0.333 |    503 |  169 |   35 |  334 |    0.336 |
| 2e3f2ae7-9ab9-3aef-a3ce-a0a97a0cb1ab | VEHICLE    | 0.287 |   0.29  |   2100 |  617 |  113 | 1483 |    0.294 |

## Why boxes failed (FP/FN reasons)

| status   | cls        | reason                   |   count |
|:---------|:-----------|:-------------------------|--------:|
| FN       | CYCLIST    | missed                   |      81 |
| FN       | CYCLIST    | outside_model_input_crop |      39 |
| FN       | CYCLIST    | missed_sparse            |      12 |
| FN       | PEDESTRIAN | outside_model_input_crop |    3134 |
| FN       | PEDESTRIAN | missed                   |    1745 |
| FN       | PEDESTRIAN | missed_sparse            |     698 |
| FN       | PEDESTRIAN | mislocalized_pred        |     254 |
| FN       | PEDESTRIAN | class_confusion          |      96 |
| FN       | VEHICLE    | outside_model_input_crop |    5453 |
| FN       | VEHICLE    | missed                   |    1179 |
| FN       | VEHICLE    | missed_sparse            |     226 |
| FN       | VEHICLE    | mislocalized_pred        |     187 |
| FN       | VEHICLE    | class_confusion          |       5 |
| FP       | CYCLIST    | class_confusion          |      42 |
| FP       | CYCLIST    | background               |       9 |
| FP       | CYCLIST    | unevaluated_category     |       1 |
| FP       | PEDESTRIAN | background               |      76 |
| FP       | PEDESTRIAN | unevaluated_category     |      13 |
| FP       | PEDESTRIAN | mislocalized             |       8 |
| FP       | PEDESTRIAN | duplicate                |       5 |
| FP       | PEDESTRIAN | class_confusion          |       4 |
| FP       | PEDESTRIAN | gt_filtered              |       2 |
| FP       | VEHICLE    | background               |     271 |
| FP       | VEHICLE    | unevaluated_category     |      38 |
| FP       | VEHICLE    | mislocalized             |      32 |
| FP       | VEHICLE    | gt_filtered              |      31 |
| FP       | VEHICLE    | class_confusion          |      30 |
| FP       | VEHICLE    | duplicate                |       3 |

## Tracking (CLEAR-MOT, 2 m)

| cls        |   n_gt |   matches |   fp |   fn |   idsw |   MOTA |   MOTP_m |
|:-----------|-------:|----------:|-----:|-----:|-------:|-------:|---------:|
| CYCLIST    |    324 |       187 |    3 |  137 |      0 |  0.568 |    0.164 |
| PEDESTRIAN |   6672 |       644 |   48 | 6028 |     27 |  0.085 |    0.161 |
| VEHICLE    |  11251 |      3938 |  248 | 7313 |    103 |  0.319 |    0.292 |

Reproduce any count, e.g. FN for vehicles 35-50m:

```python
m = pd.read_parquet('data/lake/eval/pp-kitti-v1/matches.parquet')
m.query("threshold_m == 2 and cls == 'VEHICLE' and bucket == '35-50m' and status == 'FN'")
```
