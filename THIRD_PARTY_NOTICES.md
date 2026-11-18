# Third-party notices

## zhulf0804/PointPillars (MIT)

`src/replay/detector/pointpillars.py` adapts the network definition and anchor decoding from
https://github.com/zhulf0804/PointPillars, and the pipeline downloads its published KITTI checkpoint
`pretrained/epoch_160.pth` at runtime (not redistributed here).

```
MIT License

Copyright (c) 2023 ZhuLifa

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Argoverse 2

Sensor data is downloaded at runtime from the public `s3://argoverse` bucket and is not redistributed.
Argoverse 2 is released under CC BY-NC-SA 4.0 (https://www.argoverse.org/about.html#terms-of-use);
outputs derived from it (reports, videos) inherit those non-commercial terms.

## KITTI demo frame (test fixture)

`tests/fixtures/kitti_000134.*` is one KITTI object-detection frame, redistributed via the zhulf0804/PointPillars
demo data. It is used only to check the port is correct. KITTI is licensed CC BY-NC-SA 3.0 (http://www.cvlibs.net/datasets/kitti/).
