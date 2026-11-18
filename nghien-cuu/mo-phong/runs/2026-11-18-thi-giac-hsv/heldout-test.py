#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
heldout-test.py â€” Kiá»ƒm tra tá»•ng quÃ¡t hoÃ¡ trÃªn táº­p KHÃ”NG dÃ¹ng Ä‘á»ƒ tinh chá»‰nh.

VÃ¬ sao cáº§n: pipeline Ä‘áº¡t 100 % trÃªn táº­p tá»•ng há»£p ban Ä‘áº§u (seed 42) sau khi chá»‰nh
ngÆ°á»¡ng HSV. Con sá»‘ Ä‘Ã³ cÃ³ thá»ƒ lÃ  overfit: ngÆ°á»¡ng Ä‘Æ°á»£c chá»‰nh trÃªn chÃ­nh dá»¯ liá»‡u Ä‘Ã³.
Script nÃ y sinh táº­p má»›i vá»›i:
  - seed khÃ¡c (777)
  - Ä‘iá»u kiá»‡n KHÃ“ HÆ N: dáº£i sÃ¡ng rá»™ng hÆ¡n, xoay tá»›i 40Â°, nhiá»…u tá»›i 25, má» tá»›i ksize 2
rá»“i cháº¡y nguyÃªn pipeline, khÃ´ng chá»‰nh gÃ¬ thÃªm.

Káº¿t quáº£ dÃ¹ng Ä‘á»ƒ bÃ¡o cÃ¡o trung thá»±c: "Ä‘áº¡t X % trÃªn dá»¯ liá»‡u chÆ°a tá»«ng tháº¥y".

Cháº¡y:
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
    """Chuyá»ƒn ndarray/numpy scalar sang kiá»ƒu JSON Ä‘Æ°á»£c."""
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

    # Äiá»u kiá»‡n khÃ³ hÆ¡n táº­p huáº¥n luyá»‡n (dáº£i rá»™ng hÆ¡n, xoay nhiá»u hÆ¡n, nhiá»…u/má» hÆ¡n)
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
    print(f"HELD-OUT TEST (seed {SEED}, Ä‘iá»u kiá»‡n khÃ³ hÆ¡n táº­p tinh chá»‰nh)")
    print("=" * 60)
    print(f"  sá»‘ áº£nh                : {idx}")
    print(f"  object ground truth   : {metrics['total_gt_objects']}")
    print(f"  object khá»›p Ä‘Æ°á»£c      : {metrics['total_valid_matches']}")
    print(f"  Ä‘Ãºng cáº£ mÃ u vÃ  hÃ¬nh   : {metrics['correct_both']}")
    print(f"  accuracy mÃ u          : {metrics['accuracy_color']*100:.2f} %")
    print(f"  accuracy hÃ¬nh         : {metrics['accuracy_shape']*100:.2f} %")
    print(f"  accuracy tá»•ng         : {metrics['accuracy_overall']*100:.2f} %")

    with open(os.path.join(OUT_DIR, "metrics-heldout.json"), "w", encoding="utf-8") as f:
        json.dump(_jsonable(metrics), f, ensure_ascii=False, indent=2)

    print(f"  Ä‘Ã£ lÆ°u                : {os.path.join(OUT_DIR, 'metrics-heldout.json')}")


if __name__ == "__main__":
    main()

