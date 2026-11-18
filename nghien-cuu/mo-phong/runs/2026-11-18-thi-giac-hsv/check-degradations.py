#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check-degradations.py — Kiểm tra rằng các phép làm suy giảm THỰC SỰ thay đổi ảnh.

Vì sao cần: kết quả 100 % ở mọi điều kiện có thể là do phép suy giảm không được áp
(ví dụ hàm trả về ảnh gốc, hoặc tham số bằng 0). Script này so sánh trực tiếp.

Chạy: D:\\Python312\\python.exe check-degradations.py
"""

import os
import sys
import importlib.util

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import generate_dataset as G  # noqa: E402

# Tên file có dấu gạch ngang (robustness-test.py) nên không import trực tiếp được.
_spec = importlib.util.spec_from_file_location(
    "robustness_test",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "robustness-test.py"),
)
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)


def main():
    img, _fname, gts = G.generate_image(0, "do", "tron", 1.0, 0, 0, 0, False)
    gt = gts[0]
    base = img.astype(np.float32)

    print(f"{'điều kiện':22s} {'mean|diff|':>10s} {'max|diff|':>9s} {'std_in':>7s} {'std_out':>7s}")
    print("-" * 62)

    for name, spec in R.CONDITIONS.items():
        label, degrador, special = spec
        if special:
            print(f"{name:22s} {'(sinh ảnh riêng)':>10s}")
            continue
        try:
            out = degrador(img.copy(), gt)
        except TypeError:
            out = degrador(img.copy())
        if isinstance(out, tuple):
            out = out[0]
        a = out.astype(np.float32)
        print(f"{name:22s} {np.abs(a - base).mean():10.2f} "
              f"{np.abs(a - base).max():9.1f} {base.std():7.1f} {a.std():7.1f}")


if __name__ == "__main__":
    main()
