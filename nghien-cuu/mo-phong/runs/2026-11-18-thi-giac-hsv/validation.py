#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validation.py - Sinh tap validation seed 555 va danh gia pipeline.
Dung de chon tham so, khong duoc dung trong bao cao cuoi cung.
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

SEED = 555
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ket-qua", "validation")


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

    # Dieu kien trung binh-kho
    brightness_levels = [0.70, 0.90, 1.0, 1.15, 1.30]
    angles = [0, 10, 20, 25, 30]
    noises = [0, 8, 12, 15]
    blurs = [0, 1]

    per_image_results = []
    idx = 0

    # 3 mau x 3 hinh x 5 dieu kien = 135 anh don
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
    print(f"VALIDATION (seed {SEED}, dieu kien trung binh-kho)")
    print("=" * 60)
    print(f"  so anh                : {idx}")
    print(f"  object ground truth   : {metrics['total_gt_objects']}")
    print(f"  object khop duoc      : {metrics['total_valid_matches']}")
    print(f"  dung ca mau va hinh   : {metrics['correct_both']}")
    print(f"  accuracy mau          : {metrics['accuracy_color']*100:.2f} %")
    print(f"  accuracy hinh         : {metrics['accuracy_shape']*100:.2f} %")
    print(f"  accuracy tong         : {metrics['accuracy_overall']*100:.2f} %")

    with open(os.path.join(OUT_DIR, "metrics-validation.json"), "w", encoding="utf-8") as f:
        json.dump(_jsonable(metrics), f, ensure_ascii=False, indent=2)

    print(f"  da luu                : {os.path.join(OUT_DIR, 'metrics-validation.json')}")


if __name__ == "__main__":
    main()
