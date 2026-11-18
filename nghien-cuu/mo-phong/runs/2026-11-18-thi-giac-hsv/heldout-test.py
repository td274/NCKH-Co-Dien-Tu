#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
heldout-test.py - Kiem tra tong quat hoa tren tap KHONG dung de tinh chinh.

Chay:
  D:\\Python312\\python.exe heldout-test.py
"""

import json
import os
import random
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import generate_dataset as G  # noqa: E402
from src.detect import detect_objects  # noqa: E402
from src.evaluate import evaluate_image, aggregate_metrics, COLORS, SHAPES  # noqa: E402

SEED = 777
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ket-qua", "heldout")


def _jsonable(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, dict):
        return {k: _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    return obj


def main():
    random.seed(SEED)
    np.random.seed(SEED)
    os.makedirs(OUT_DIR, exist_ok=True)

    # Dieu kien kho hon tap huan luyen
    brightness_levels = [0.55, 0.75, 1.0, 1.25, 1.45]
    angles = [0, 10, 20, 30, 40]
    noises = [0, 10, 20, 25]
    blurs = [0, 1, 2]

    per_image_results = []
    idx = 0

    # 3 mau x 3 hinh x 5 dieu kien ngau nhien = 135 anh don
    for color in COLORS:
        for shape in SHAPES:
            for _ in range(5):
                b = random.choice(brightness_levels)
                a = random.choice(angles)
                n = random.choice(noises)
                bl = random.choice(blurs)
                img, _fname, gts = G.generate_image(idx, color, shape, b, a, n, bl, False)
                det, _dbg = detect_objects(img)
                per_image_results.append(evaluate_image(det, gts))
                idx += 1

    # 15 anh 2 vat
    for _ in range(15):
        color = random.choice(COLORS)
        shape = random.choice(SHAPES)
        b = random.choice(brightness_levels)
        a = random.choice(angles)
        n = random.choice(noises)
        bl = random.choice(blurs)
        img, _fname, gts = G.generate_image(idx, color, shape, b, a, n, bl, True)
        det, _dbg = detect_objects(img)
        per_image_results.append(evaluate_image(det, gts))
        idx += 1

    metrics = aggregate_metrics(per_image_results)

    print("=" * 60)
    print(f"HELD-OUT TEST (seed {SEED}, dieu kien kho hon tap tinh chinh)")
    print("=" * 60)
    print(f"  so anh                : {idx}")
    print(f"  object ground truth   : {metrics['total_gt_objects']}")
    print(f"  object khop duoc      : {metrics['total_valid_matches']}")
    print(f"  dung ca mau va hinh   : {metrics['correct_both']}")
    print(f"  accuracy mau          : {metrics['accuracy_color']*100:.2f} %")
    print(f"  accuracy hinh         : {metrics['accuracy_shape']*100:.2f} %")
    print(f"  accuracy tong         : {metrics['accuracy_overall']*100:.2f} %")

    with open(os.path.join(OUT_DIR, "metrics-heldout.json"), "w", encoding="utf-8") as f:
        json.dump(_jsonable(metrics), f, ensure_ascii=False, indent=2)

    print(f"  da luu                : {os.path.join(OUT_DIR, 'metrics-heldout.json')}")


if __name__ == "__main__":
    main()
