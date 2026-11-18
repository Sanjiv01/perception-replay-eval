# Evaluation: `pp-kitti-v2-rot`

Config hash `3e26f2518ea3`. Source rows: `data/lake/eval/pp-kitti-v2-rot/matches.parquet` (87594 rows). Counts at the 2.0 m TP threshold.

## Per class and distance bucket

| cls        | bucket   |   mAP |   AP@0.5m |   AP@1m |   AP@2m |   AP@4m |   n_gt |   tp |   fp |   fn |   precision |   recall |   ATE_m |   ASE |   AOE_rad |
|:-----------|:---------|------:|----------:|--------:|--------:|--------:|-------:|-----:|-----:|-----:|------------:|---------:|--------:|------:|----------:|
| CYCLIST    | 0-20m    | 0.952 |     0.952 |   0.952 |   0.952 |   0.952 |    167 |  161 |  129 |    6 |       0.555 |    0.964 |   0.163 | 0.446 |     0.332 |
| CYCLIST    | 20-35m   | 0.794 |     0.794 |   0.794 |   0.794 |   0.794 |     45 |   38 |  229 |    7 |       0.142 |    0.844 |   0.124 | 0.487 |     1.149 |
| CYCLIST    | 35-50m   | 0.162 |     0.156 |   0.164 |   0.164 |   0.164 |    112 |   27 |  101 |   85 |       0.211 |    0.241 |   0.25  | 0.559 |     2.301 |
| CYCLIST    | all      | 0.665 |     0.664 |   0.665 |   0.665 |   0.665 |    324 |  226 |  459 |   98 |       0.33  |    0.698 |   0.167 | 0.467 |     0.705 |
| PEDESTRIAN | 0-20m    | 0.404 |     0.394 |   0.394 |   0.402 |   0.426 |   2143 |  923 |  306 | 1220 |       0.751 |    0.431 |   0.167 | 0.335 |     1.478 |
| PEDESTRIAN | 20-35m   | 0.25  |     0.24  |   0.249 |   0.251 |   0.261 |   2399 |  637 |  260 | 1762 |       0.71  |    0.266 |   0.165 | 0.317 |     1.439 |
| PEDESTRIAN | 35-50m   | 0.121 |     0.12  |   0.12  |   0.121 |   0.122 |   2130 |  293 |  140 | 1837 |       0.677 |    0.138 |   0.208 | 0.378 |     1.403 |
| PEDESTRIAN | all      | 0.258 |     0.254 |   0.254 |   0.255 |   0.271 |   6672 | 1853 |  706 | 4819 |       0.724 |    0.278 |   0.173 | 0.336 |     1.453 |
| VEHICLE    | 0-20m    | 0.92  |     0.826 |   0.934 |   0.956 |   0.965 |   3677 | 3558 | 1063 |  119 |       0.77  |    0.968 |   0.273 | 0.234 |     0.174 |
| VEHICLE    | 20-35m   | 0.741 |     0.631 |   0.75  |   0.786 |   0.795 |   4079 | 3288 |  821 |  791 |       0.8   |    0.806 |   0.308 | 0.258 |     0.487 |
| VEHICLE    | 35-50m   | 0.396 |     0.328 |   0.408 |   0.423 |   0.423 |   3495 | 1505 |  306 | 1990 |       0.831 |    0.431 |   0.323 | 0.276 |     0.628 |
| VEHICLE    | all      | 0.69  |     0.601 |   0.702 |   0.729 |   0.73  |  11251 | 8351 | 2190 | 2900 |       0.792 |    0.742 |   0.296 | 0.251 |     0.379 |

## Per scene (all distances)

| log_id                               | cls        |   mAP |   AP@2m |   n_gt |   tp |   fp |   fn |   recall |
|:-------------------------------------|:-----------|------:|--------:|-------:|-----:|-----:|-----:|---------:|
| 04994d08-156c-3018-9717-ba0e29be8153 | CYCLIST    |       |         |      0 |    0 |   47 |    0 |    0     |
| 04994d08-156c-3018-9717-ba0e29be8153 | PEDESTRIAN | 0.099 |   0.096 |   3344 |  366 |   84 | 2978 |    0.109 |
| 04994d08-156c-3018-9717-ba0e29be8153 | VEHICLE    | 0.664 |   0.718 |   4284 | 3112 |  293 | 1172 |    0.726 |
| 0b86f508-5df9-4a46-bc59-5b9536dbde9f | CYCLIST    | 0.509 |   0.512 |     93 |   52 |   61 |   41 |    0.559 |
| 0b86f508-5df9-4a46-bc59-5b9536dbde9f | PEDESTRIAN | 0.301 |   0.302 |    396 |  135 |  102 |  261 |    0.341 |
| 0b86f508-5df9-4a46-bc59-5b9536dbde9f | VEHICLE    | 0.745 |   0.773 |   3121 | 2455 |  335 |  666 |    0.787 |
| 280269f9-6111-311d-b351-ce9f63f88c81 | CYCLIST    |       |         |      0 |    0 |  150 |    0 |    0     |
| 280269f9-6111-311d-b351-ce9f63f88c81 | PEDESTRIAN | 0.414 |   0.418 |   2429 | 1049 |  193 | 1380 |    0.432 |
| 280269f9-6111-311d-b351-ce9f63f88c81 | VEHICLE    | 0.815 |   0.852 |   1746 | 1553 |  933 |  193 |    0.889 |
| 2e3f2ae7-9ab9-3aef-a3ce-a0a97a0cb1ab | CYCLIST    | 0.745 |   0.745 |    231 |  174 |  201 |   57 |    0.753 |
| 2e3f2ae7-9ab9-3aef-a3ce-a0a97a0cb1ab | PEDESTRIAN | 0.569 |   0.558 |    503 |  303 |  327 |  200 |    0.602 |
| 2e3f2ae7-9ab9-3aef-a3ce-a0a97a0cb1ab | VEHICLE    | 0.551 |   0.561 |   2100 | 1231 |  629 |  869 |    0.586 |

## Why boxes failed (FP/FN reasons)

| status   | cls        | reason               |   count |
|:---------|:-----------|:---------------------|--------:|
| FN       | CYCLIST    | missed               |      76 |
| FN       | CYCLIST    | missed_sparse        |      18 |
| FN       | CYCLIST    | class_confusion      |       4 |
| FN       | PEDESTRIAN | missed               |    2599 |
| FN       | PEDESTRIAN | missed_sparse        |    1308 |
| FN       | PEDESTRIAN | mislocalized_pred    |     696 |
| FN       | PEDESTRIAN | class_confusion      |     216 |
| FN       | VEHICLE    | missed               |    1703 |
| FN       | VEHICLE    | missed_sparse        |     867 |
| FN       | VEHICLE    | mislocalized_pred    |     325 |
| FN       | VEHICLE    | class_confusion      |       5 |
| FP       | CYCLIST    | background           |     240 |
| FP       | CYCLIST    | class_confusion      |     209 |
| FP       | CYCLIST    | unevaluated_category |      10 |
| FP       | PEDESTRIAN | background           |     459 |
| FP       | PEDESTRIAN | unevaluated_category |     117 |
| FP       | PEDESTRIAN | mislocalized         |      52 |
| FP       | PEDESTRIAN | duplicate            |      49 |
| FP       | PEDESTRIAN | class_confusion      |      21 |
| FP       | PEDESTRIAN | gt_filtered          |       8 |
| FP       | VEHICLE    | background           |    1644 |
| FP       | VEHICLE    | unevaluated_category |     235 |
| FP       | VEHICLE    | class_confusion      |     125 |
| FP       | VEHICLE    | mislocalized         |     111 |
| FP       | VEHICLE    | gt_filtered          |      63 |
| FP       | VEHICLE    | duplicate            |      12 |

## Tracking (CLEAR-MOT, 2 m)

| cls        |   n_gt |   matches |   fp |   fn |   idsw |   MOTA |   MOTP_m |
|:-----------|-------:|----------:|-----:|-----:|-------:|-------:|---------:|
| CYCLIST    |    324 |       220 |   40 |  104 |      0 |  0.556 |    0.165 |
| PEDESTRIAN |   6672 |      1577 |  210 | 5095 |     89 |  0.192 |    0.168 |
| VEHICLE    |  11251 |      7772 | 1389 | 3479 |    181 |  0.551 |    0.285 |

Reproduce any count, e.g. FN for vehicles 35-50m:

```python
m = pd.read_parquet('data/lake/eval/pp-kitti-v2-rot/matches.parquet')
m.query("threshold_m == 2 and cls == 'VEHICLE' and bucket == '35-50m' and status == 'FN'")
```
