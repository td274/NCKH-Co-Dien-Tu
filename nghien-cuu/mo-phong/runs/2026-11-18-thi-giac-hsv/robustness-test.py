#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
robustness-test.py
Nghien cuu do ben vung cua pipeline thi giac voi cac dieu kien thuc te.
KHONG dung de tinh chinh tham so — chi de bao cao trung thuc.

Chay:
    D:\\Python312\\python.exe robustness-test.py
"""

import json
import os
import random
import sys
import math

import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import generate_dataset as G
from src.detect import detect_objects, draw_detections
from src.evaluate import evaluate_image, aggregate_metrics


RUN_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(RUN_DIR, 'output')
FIG_DIR = os.path.join(RUN_DIR, 'figures')

SEED_BASE = 2026
N_PER_CONDITION = 36  # 4 anh / (3 mau x 3 hinh)

COLORS = G.COLORS
SHAPES = G.SHAPES

BRIGHTNESS_LEVELS = [0.7, 1.0, 1.3]
ANGLES = [0, 15, 30]
NOISES = [0, 8, 15]
BLURS = [0, 1]


def _base_color(color, brightness):
    return np.clip(G.BASE_COLORS[color].astype(np.float32) * brightness,
                   0, 255).astype(np.uint8)


def degrade_none(image, gt=None):
    return image


def degrade_gradient(image, gt=None):
    """Nhan anh voi gradient tuyen tinh, mot phia toi 40-60 %."""
    h, w = image.shape[:2]
    f = random.uniform(0.40, 0.60)
    axis = random.choice(['h', 'v'])
    if axis == 'h':
        grad = np.linspace(1.0, f, w).reshape(1, w, 1).astype(np.float32)
    else:
        grad = np.linspace(1.0, f, h).reshape(h, 1, 1).astype(np.float32)
    out = image.astype(np.float32) * grad
    return np.clip(out, 0, 255).astype(np.uint8)


def degrade_shadow(image, gt):
    """Ve bong toi mo len mot phan vat, do toi 45-65 %."""
    out = image.astype(np.float32)
    cx, cy = gt['center_px']
    # Dat bong ngay tren vat, lech nho de bao dam che phan dang ke
    offset = random.choice([-1, 1]) * random.randint(0, 10)
    if random.random() < 0.5:
        ex, ey = cx + offset, cy + random.randint(-8, 8)
    else:
        ex, ey = cx + random.randint(-8, 8), cy + offset
    ax = int(gt['radius'] * random.uniform(1.2, 1.6))
    ay = int(gt['radius'] * random.uniform(1.1, 1.4))
    angle = random.randint(0, 180)

    # Mask trang/den, lam mo nhe de tao bong mo
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.ellipse(mask, (ex, ey), (ax, ay), angle, 0, 360, 255, -1)
    mask = cv2.GaussianBlur(mask.astype(np.float32), (11, 11), 0) / 255.0
    mask = np.clip(mask, 0, 1)

    alpha = random.uniform(0.50, 0.70)
    factor = 1.0 - alpha * mask
    factor = factor[..., np.newaxis]
    out = out * factor
    return np.clip(out, 0, 255).astype(np.uint8)


def degrade_jpeg_noise(image, gt=None):
    """Nhieu Gauss sigma=15-25 roi nen JPEG quality 50-70."""
    sigma = random.uniform(15, 25)
    q = random.randint(50, 70)
    noise = np.random.normal(0, sigma, image.shape).astype(np.float32)
    noisy = np.clip(image.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    ok, buf = cv2.imencode('.jpg', noisy,
                           [int(cv2.IMWRITE_JPEG_QUALITY), q])
    if not ok:
        return noisy
    return cv2.imdecode(buf, 1)


def degrade_perspective(image, gt=None):
    """Warp phoi canh, dich cac goc 8-12 % kich thuoc anh theo 4 huong ngau nhien."""
    h, w = image.shape[:2]
    max_off = int(random.uniform(0.08, 0.12) * min(w, h))
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    dst = np.float32([
        [random.randint(0, max_off), random.randint(0, max_off)],
        [w - random.randint(0, max_off), random.randint(0, max_off)],
        [w - random.randint(0, max_off), h - random.randint(0, max_off)],
        [random.randint(0, max_off), h - random.randint(0, max_off)],
    ])
    M = cv2.getPerspectiveTransform(src, dst)
    return cv2.warpPerspective(image, M, (w, h), borderMode=cv2.BORDER_REPLICATE)


def degrade_combined(image, gt):
    """Ket hop gradient + shadow + jpeg_noise + perspective — dieu kien thuc te nhat."""
    img = degrade_gradient(image, gt)
    img = degrade_shadow(img, gt)
    img = degrade_jpeg_noise(img, gt)
    img = degrade_perspective(img, gt)
    return img


def generate_occlusion_image(main_color, main_shape, brightness, angle,
                             sigma, blur, seed):
    """Sinh anh co vat thu hai che khuat 15-25 % dien tich vat chinh."""
    random.seed(seed)
    np.random.seed(seed)
    bg = random.randint(220, 250)
    canvas = np.full((G.IMG_H, G.IMG_W, 3), bg, dtype=np.uint8)

    c1 = G.random_center(margin=120)
    r1 = random.randint(38, 55)
    col1 = _base_color(main_color, brightness)
    bbox1 = G.draw_shape(canvas, main_shape, c1, r1, col1, angle)

    # Tim vi tri occluder de overlap 15-25 %
    occ_color = random.choice([c for c in COLORS if c != main_color])
    occ_shape = random.choice(SHAPES)
    col2 = _base_color(occ_color, brightness)
    c2, r2, bbox2, occ_angle = None, None, None, None

    # Mask vat chinh
    mask_main = np.zeros((G.IMG_H, G.IMG_W), dtype=np.uint8)
    tmp = np.zeros_like(canvas)
    white = np.array([255, 255, 255], dtype=np.uint8)
    G.draw_shape(tmp, main_shape, c1, r1, white, angle)
    mask_main = cv2.cvtColor(tmp, cv2.COLOR_BGR2GRAY)
    main_area = cv2.countNonZero(mask_main)

    for _ in range(80):
        ang = random.uniform(0, 2 * math.pi)
        dist = random.uniform(0.45, 0.95) * r1
        cand = (int(c1[0] + dist * math.cos(ang)),
                int(c1[1] + dist * math.sin(ang)))
        r2 = random.randint(35, 55)
        tmp2 = np.zeros_like(canvas)
        occ_angle = random.choice(ANGLES)
        G.draw_shape(tmp2, occ_shape, cand, r2, white, occ_angle)
        mask_occ = cv2.cvtColor(tmp2, cv2.COLOR_BGR2GRAY)
        inter = cv2.countNonZero(cv2.bitwise_and(mask_main, mask_occ))
        if 0.15 <= inter / max(main_area, 1) <= 0.30:
            c2, bbox2 = cand, cv2.boundingRect(np.argwhere(mask_occ > 0))
            break

    if c2 is None:
        # fallback: dat gan tam
        c2 = (c1[0] + r1 // 2, c1[1] + r1 // 2)
        r2 = 45
        occ_angle = random.choice(ANGLES)

    bbox2 = G.draw_shape(canvas, occ_shape, c2, r2, col2, occ_angle)
    img = G.add_noise_blur(canvas, sigma, blur)

    gts = [
        {'color': main_color, 'shape': main_shape,
         'center_px': [int(c1[0]), int(c1[1])],
         'bbox': [int(b) for b in bbox1], 'radius': r1},
        {'color': occ_color, 'shape': occ_shape,
         'center_px': [int(c2[0]), int(c2[1])],
         'bbox': [int(b) for b in bbox2], 'radius': r2},
    ]
    return img, gts


def degrade_shape(image, gt, color, shape, brightness, angle, sigma):
    """Bo goc / lam khong deu bien vat bang jitter dinh + ty le + blur."""
    out = image.copy()
    col = _base_color(color, brightness)
    cx, cy = gt['center_px']
    r = int(gt['radius'] * random.uniform(0.92, 1.08))
    jitter = random.randint(3, 5)
    ang_rad = math.radians(angle)
    R = np.array([[math.cos(ang_rad), -math.sin(ang_rad)],
                  [math.sin(ang_rad), math.cos(ang_rad)]])

    if shape == 'tron':
        n = 24
        theta = np.linspace(0, 2 * math.pi, n, endpoint=False)
        radii = r + np.random.randint(-jitter, jitter + 1, n)
        pts = np.stack([radii * np.cos(theta), radii * np.sin(theta)], axis=1)
    elif shape == 'vuong':
        pts = np.array([[-r, -r], [r, -r], [r, r], [-r, r]], dtype=np.float32)
        pts += np.random.randint(-jitter, jitter + 1, pts.shape)
    else:  # tam_giac
        h = r * math.sqrt(3)
        pts = np.array([[0, -2 * h / 3],
                        [-r, h / 3],
                        [r, h / 3]], dtype=np.float32)
        pts += np.random.randint(-jitter, jitter + 1, pts.shape)

    pts = (pts @ R.T) + np.array([cx, cy])
    pts = pts.astype(np.int32).reshape(-1, 1, 2)

    # Ve hinh khong ly tuong len anh goc (pixel bien thay doi)
    cv2.fillPoly(out, [pts], col.tolist())
    # Lam mo manh toan anh de duong bien mem hon va them nhieu nhe
    out = cv2.GaussianBlur(out, (9, 9), 0)
    noise = np.random.normal(0, 10, out.shape).astype(np.float32)
    out = np.clip(out.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    out = G.add_noise_blur(out, sigma, 0)
    return out


CONDITIONS = {
    'baseline': ('Khong suy giam', degrade_none, False),
    'gradient_light': ('Anh sang khong deu', degrade_gradient, False),
    'shadow': ('Bong do', degrade_shadow, False),
    'jpeg_noise': ('Nhieu + JPEG', degrade_jpeg_noise, False),
    'perspective': ('Phoi canh nghieng', degrade_perspective, False),
    'combined': ('Ket hop cac yeu to', degrade_combined, False),
    'occlusion': ('Che khuat mot phan', None, True),
    'shape_imperfect': ('Hinh dang khong ly tuong', None, 'shape'),
}


def run_condition(name, n_images, seed_offset):
    per_image = []
    samples = []
    diffs = []
    random.seed(SEED_BASE + seed_offset)
    np.random.seed(SEED_BASE + seed_offset)

    label, degrador, special = CONDITIONS[name]

    # Tao danh sach (mau, hinh) can bang
    pairs = []
    for _ in range(n_images // (len(COLORS) * len(SHAPES))):
        for c in COLORS:
            for s in SHAPES:
                pairs.append((c, s))
    random.shuffle(pairs)

    for idx, (color, shape) in enumerate(pairs[:n_images]):
        b = random.choice(BRIGHTNESS_LEVELS)
        a = random.choice(ANGLES)
        n = random.choice(NOISES)
        bl = random.choice(BLURS)

        # Anh goc sach de kiem tra muc do suy giam
        clean, _, clean_gts = G.generate_image(idx, color, shape, b, a, n, bl,
                                               multi=False)

        if special == True:  # occlusion
            img, gts = generate_occlusion_image(color, shape, b, a, n, bl,
                                                seed_offset * 10000 + idx)
        elif special == 'shape':
            img = degrade_shape(clean, clean_gts[0], color, shape, b, a, n)
            gts = clean_gts
        else:
            img = degrador(clean, clean_gts[0])
            gts = clean_gts

        # Tu kiem tra: phai co su khac biet ro ret so voi anh goc
        def _diff(a, b):
            return float(np.mean(np.abs(a.astype(np.float32) -
                                      b.astype(np.float32))))

        diff = _diff(img, clean)
        # Voi mot so phep ngau nhien (perspective), co the gap mau bien gioi
        # nen thu lai toi da 5 lan de dam bao suy giam du manh.
        attempts = 0
        while name not in ('baseline', 'occlusion', 'shape_imperfect') and diff < 1.0 and attempts < 5:
            img = degrador(clean, clean_gts[0])
            gts = clean_gts
            diff = _diff(img, clean)
            attempts += 1

        diffs.append(diff)
        if name != 'baseline' and diff < 1.0:
            raise ValueError(
                f"Degradation '{name}' khong co tac dung cho "
                f"{color}-{shape}: mean|diff|={diff:.2f} < 1.0"
            )

        dets, _ = detect_objects(img)
        res = evaluate_image(dets, gts, max_dist_px=50)
        per_image.append(res)
        samples.append({
            'filename': f'{name}_{idx:03d}.png',
            'image': img,
            'detections': dets,
            'ground_truths': gts,
            'condition': label,
        })

    metrics = aggregate_metrics(per_image)
    metrics['condition'] = name
    metrics['label'] = label
    metrics['mean_abs_diff'] = round(float(np.mean(diffs)), 2)
    metrics['max_abs_diff'] = round(float(np.max(diffs)), 2)
    return metrics, samples


def plot_bar(results):
    names = [r['label'] for r in results]
    acc_color = [r['accuracy_color'] * 100 for r in results]
    acc_shape = [r['accuracy_shape'] * 100 for r in results]
    acc_overall = [r['accuracy_overall'] * 100 for r in results]
    recall = [r['recall_overall'] * 100 for r in results]

    x = np.arange(len(names))
    width = 0.2
    fig, ax = plt.subplots(figsize=(12, 5), dpi=300)
    ax.bar(x - 1.5 * width, acc_color, width, label='Mau')
    ax.bar(x - 0.5 * width, acc_shape, width, label='Hinh')
    ax.bar(x + 0.5 * width, acc_overall, width, label='Overall')
    ax.bar(x + 1.5 * width, recall, width, label='Recall')
    ax.set_ylabel('Accuracy / Recall (%)', fontsize=12)
    ax.set_title('Do ben vung pipeline voi cac dieu kien thuc te', fontsize=13)
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=15, ha='right', fontsize=10)
    ax.set_ylim(0, 110)
    ax.legend(fontsize=10)
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'robustness-bar.png'), dpi=300)
    plt.close(fig)


def plot_examples(samples_by_condition):
    conds = list(samples_by_condition.keys())
    n = len(conds)
    fig, axes = plt.subplots(2, n, figsize=(3 * n, 6), dpi=300)
    if n == 1:
        axes = np.array([[axes[0]], [axes[1]]])
    axes = axes.flatten()
    for k, cond in enumerate(conds):
        sample = random.choice(samples_by_condition[cond])
        annotated = draw_detections(sample['image'], sample['detections'])
        axes[k].imshow(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB))
        axes[k].set_title(f"{cond}\nDu doan", fontsize=9)
        axes[k].axis('off')

        gt_img = sample['image'].copy()
        for gt in sample['ground_truths']:
            cx, cy = gt['center_px']
            cv2.circle(gt_img, (cx, cy), 5, (0, 255, 0), -1)
            cv2.putText(gt_img, f"{gt['color']}-{gt['shape']}",
                        (cx + 8, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                        (0, 255, 0), 1)
        axes[k + n].imshow(cv2.cvtColor(gt_img, cv2.COLOR_BGR2RGB))
        axes[k + n].set_title('Ground truth', fontsize=9)
        axes[k + n].axis('off')
    for ax in axes[2 * n:]:
        ax.axis('off')
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'robustness-examples.png'), dpi=300)
    plt.close(fig)


def save_csv(results):
    path = os.path.join(OUT_DIR, 'robustness.csv')
    with open(path, 'w', newline='', encoding='utf-8') as f:
        import csv
        writer = csv.writer(f)
        writer.writerow(['condition', 'label', 'n_gt', 'n_matched',
                         'correct_both', 'accuracy_color', 'accuracy_shape',
                         'accuracy_overall', 'recall', 'precision',
                         'mean_abs_diff', 'max_abs_diff'])
        for r in results:
            writer.writerow([
                r['condition'], r['label'], r['total_gt_objects'],
                r['total_valid_matches'], r['correct_both'],
                f"{r['accuracy_color']*100:.2f}",
                f"{r['accuracy_shape']*100:.2f}",
                f"{r['accuracy_overall']*100:.2f}",
                f"{r['recall_overall']*100:.2f}",
                f"{r['precision_overall']*100:.2f}",
                f"{r['mean_abs_diff']:.2f}",
                f"{r['max_abs_diff']:.2f}",
            ])


def collect_error_examples(results, samples_by_condition):
    examples = {}
    for cond, samples in samples_by_condition.items():
        for s in samples:
            gts = s['ground_truths']
            dets = s['detections']
            # matching don gian theo tam
            used = set()
            for det in dets:
                best_i, best_d = -1, 1e9
                for i, gt in enumerate(gts):
                    if i in used:
                        continue
                    d = math.hypot(det['center_px'][0] - gt['center_px'][0],
                                   det['center_px'][1] - gt['center_px'][1])
                    if d < best_d:
                        best_d = d
                        best_i = i
                if best_i >= 0 and best_d <= 50:
                    used.add(best_i)
                    gt = gts[best_i]
                    if det['shape'] != gt['shape'] or det['color'] != gt['color']:
                        key = cond
                        if key not in examples:
                            examples[key] = []
                        examples[key].append(
                            f"{s['filename']}: {gt['color']}-{gt['shape']} "
                            f"du doan thanh {det['color']}-{det['shape']}"
                        )
            # false negatives
            for i, gt in enumerate(gts):
                if i not in used:
                    key = cond
                    if key not in examples:
                        examples[key] = []
                    examples[key].append(
                        f"{s['filename']}: {gt['color']}-{gt['shape']} "
                        f"khong phat hien duoc"
                    )
    return examples


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(FIG_DIR, exist_ok=True)

    results = []
    samples_by_condition = {}
    seed_offset = 0
    for name in CONDITIONS:
        print(f"\n>>> Dang chay dieu kien: {name}")
        metrics, samples = run_condition(name, N_PER_CONDITION, seed_offset)
        seed_offset += 1
        results.append(metrics)
        samples_by_condition[name] = samples
        print(f"  {metrics['label']}: "
              f"overall={metrics['accuracy_overall']*100:.1f}% "
              f"mau={metrics['accuracy_color']*100:.1f}% "
              f"hinh={metrics['accuracy_shape']*100:.1f}% "
              f"recall={metrics['recall_overall']*100:.1f}% "
              f"mean|diff|={metrics['mean_abs_diff']:.1f}")

    save_csv(results)
    plot_bar(results)
    plot_examples(samples_by_condition)
    error_examples = collect_error_examples(results, samples_by_condition)

    # Luu vi du loi
    with open(os.path.join(OUT_DIR, 'robustness_errors.txt'),
              'w', encoding='utf-8') as f:
        for cond, lines in error_examples.items():
            f.write(f"\n=== {cond} ===\n")
            for line in lines[:10]:
                f.write(line + '\n')

    print("\n===== BANG TOM TAT ROBUSTNESS =====")
    print(f"{'Dieu kien':<26} {'Overall':>8} {'Mau':>8} {'Hinh':>8} "
          f"{'Recall':>8} {'mean|diff|':>10} {'max|diff|':>10}")
    for r in results:
        print(f"{r['label']:<26} "
              f"{r['accuracy_overall']*100:>7.1f}% "
              f"{r['accuracy_color']*100:>7.1f}% "
              f"{r['accuracy_shape']*100:>7.1f}% "
              f"{r['recall_overall']*100:>7.1f}% "
              f"{r['mean_abs_diff']:>10.1f} "
              f"{r['max_abs_diff']:>10.1f}")
    print("===================================")
    print("Da luu:")
    print("  - output/robustness.csv")
    print("  - output/robustness_errors.txt")
    print("  - figures/robustness-bar.png")
    print("  - figures/robustness-examples.png")


if __name__ == '__main__':
    main()
