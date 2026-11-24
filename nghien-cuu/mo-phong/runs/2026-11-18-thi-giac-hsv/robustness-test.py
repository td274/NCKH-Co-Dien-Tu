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


# --- Tham so phep thu bong do (ban tang cuong) ---
# Ban cu chi lam toi 50-70 % mot ellipse nho dat tren vat, dat mean|diff| ~ 3,5/255
# (~1,4 %) -> khong chung minh duoc gi. Ban nay: bong do (cast shadow) lon, mo dan,
# phu 20-40 % dien tich vat, alpha 0,45-0,60, va tu dong tang cuong cho toi khi
# mean|diff| >= 20/255. Khong dat thi bao loi, khong am tham bo qua.
SHADOW_ALPHA_RANGE = (0.45, 0.60)
SHADOW_COVER_RANGE = (0.20, 0.40)   # ty le dien tich vat bi bong che
SHADOW_MIN_DIFF = 20.0              # mean|diff| toi thieu tren toan anh (0-255)

# Nhat ky ty le che phu thuc te, de bao cao trung thuc.
SHADOW_COVERAGE_LOG = []


def _object_mask(image, gt):
    """Mask vat dua tren do bao hoa S (nen xam S~0, vat mau S cao).

    Dung S thay vi so sanh voi nen vi S khong doi khi nhan ca anh voi gradient
    hay khi vat bi bong lam toi (ca hai chi nhan kenh BGR voi cung he so).
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    mask = ((sat > 60) & (val > 25)).astype(np.uint8) * 255

    cx, cy = gt['center_px']
    pad = int(gt['radius'] * 1.8)
    roi = np.zeros_like(mask)
    cv2.rectangle(roi, (cx - pad, cy - pad), (cx + pad, cy + pad), 255, -1)
    mask = cv2.bitwise_and(mask, roi)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE,
                            np.ones((5, 5), np.uint8))
    return mask


def degrade_shadow(image, gt, require_min=True):
    """Bong do lon, mo dan: che 20-40 % dien tich vat, alpha 0,45-0,60.

    require_min=True: tu kiem tra mean|diff| >= SHADOW_MIN_DIFF; neu chua dat thi
    tang alpha va kich thuoc bong qua tung vong; khong dat sau 12 vong thi raise.
    require_min=False (dung trong 'combined'): van giu rang buoc che phu va
    alpha, nhung khong doi hoi mean|diff| >= 20 so voi anh trung gian —
    do manh tong cua dieu kien combined do gradient quyet dinh.
    """
    obj = _object_mask(image, gt)
    obj_area = cv2.countNonZero(obj)
    if obj_area < 50:
        raise ValueError(
            f"Khong xac dinh duoc mask vat ({obj_area} px) -> khong dat duoc "
            f"rang buoc che phu cua phep thu bong do"
        )

    h, w = image.shape[:2]
    cx, cy = gt['center_px']
    r = float(gt['radius'])
    base = image.astype(np.float32)

    last_cov, last_diff = None, None
    n_rounds = 12 if require_min else 1
    for escalation in range(n_rounds):
        alpha = min(0.85, random.uniform(*SHADOW_ALPHA_RANGE) + 0.06 * escalation)
        scale = min(3.4, 2.2 + 0.12 * escalation)
        rx = int(r * scale * random.uniform(0.95, 1.15))
        ry = int(r * scale * random.uniform(0.85, 1.05))

        # Tim vi tri dat bong sao cho che dung 20-40 % dien tich vat.
        # Bong lon hon vat nhieu nen phai day tam bong ra xa (toi ~1,15 lan
        # ban kinh ellipse) moi chi phu mot phan vat; phan con lai roi tren nen.
        placed = False
        for _ in range(400):
            ang = random.uniform(0, 2 * math.pi)
            dist = random.uniform(0.8 * r, 1.15 * rx)
            ex = int(cx + dist * math.cos(ang))
            ey = int(cy + dist * math.sin(ang))
            # Giu phan lon ellipse trong khung hinh (tranh bong bi cat cut
            # lam giam gia tri do manh mot cach gia tao)
            ex = min(max(ex, int(0.4 * rx)), w - int(0.4 * rx))
            ey = min(max(ey, int(0.4 * ry)), h - int(0.4 * ry))
            angle = random.randint(0, 180)
            m = np.zeros((h, w), dtype=np.uint8)
            cv2.ellipse(m, (ex, ey), (rx, ry), angle, 0, 360, 255, -1)
            cov = cv2.countNonZero(cv2.bitwise_and(m, obj)) / obj_area
            if SHADOW_COVER_RANGE[0] <= cov <= SHADOW_COVER_RANGE[1]:
                placed = True
                break
        if not placed:
            continue

        # Bong mo dan: blur manh theo kich thuoc bong
        ksize = int(max(rx, ry) * 0.45) | 1
        sigma = max(rx, ry) * 0.28
        soft = cv2.GaussianBlur(m.astype(np.float32) / 255.0,
                                (ksize, ksize), sigma)
        soft = np.clip(soft, 0.0, 1.0)
        factor = (1.0 - alpha * soft)[..., np.newaxis]
        out = np.clip(base * factor, 0, 255).astype(np.uint8)

        diff = float(np.mean(np.abs(out.astype(np.float32) - base)))
        last_cov, last_diff = cov, diff
        if not require_min or diff >= SHADOW_MIN_DIFF:
            SHADOW_COVERAGE_LOG.append(cov)
            return out

    raise ValueError(
        f"Phep thu bong do khong du manh: mean|diff|={last_diff} < "
        f"{SHADOW_MIN_DIFF} (che phu={last_cov}). Tang cuong them hoac sua "
        f"gia thiet, khong duoc bo qua."
    )


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
    img = degrade_shadow(img, gt, require_min=False)
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

# Muc suy giam toi thieu bat buoc (mean|diff| tren toan anh, thang 0-255).
# Chi dat nguong cho cac phep co the dat mot cach trung thuc: bong do va ket hop
# deu phai >= 20. Cac phep hinh hoc (phoi canh) chi dich duong bien nen
# mean|diff| khong the lon — van giu nguong toi thieu 1.0 de bat loi "khong tac dung".
MIN_DIFF = {
    'shadow': SHADOW_MIN_DIFF,
    'combined': SHADOW_MIN_DIFF,
}
DEFAULT_MIN_DIFF = 1.0


def wilson_ci(k, n, z=1.96):
    """Khoang tin cay Wilson 95 % cho mot ty le k/n."""
    if n <= 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denom
    half = z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n)) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def run_condition(name, n_images, seed_offset):
    per_image = []
    samples = []
    diffs = []
    random.seed(SEED_BASE + seed_offset)
    np.random.seed(SEED_BASE + seed_offset)

    label, degrador, special = CONDITIONS[name]
    SHADOW_COVERAGE_LOG.clear()
    min_diff = MIN_DIFF.get(name, DEFAULT_MIN_DIFF)

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
        while (name not in ('baseline', 'occlusion', 'shape_imperfect', 'shadow')
               and diff < DEFAULT_MIN_DIFF and attempts < 5):
            img = degrador(clean, clean_gts[0])
            gts = clean_gts
            diff = _diff(img, clean)
            attempts += 1

        diffs.append(diff)
        if name != 'baseline' and diff < min_diff:
            raise ValueError(
                f"Degradation '{name}' khong du manh cho "
                f"{color}-{shape}: mean|diff|={diff:.2f} < {min_diff:.1f}"
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
            'errors': res['errors'],
        })

    metrics = aggregate_metrics(per_image)
    metrics['condition'] = name
    metrics['label'] = label
    metrics['mean_abs_diff'] = round(float(np.mean(diffs)), 2)
    metrics['max_abs_diff'] = round(float(np.max(diffs)), 2)

    # Khoang tin cay Wilson 95 % cho tung ty le (n=36 thi CI rat rong)
    cm_c = np.asarray(metrics['cm_color'])
    cm_s = np.asarray(metrics['cm_shape'])
    n_gt = metrics['total_gt_objects']
    n_pred = metrics['total_predictions']
    n_valid = metrics['total_valid_matches']
    rates = {
        'accuracy_color': (int(np.trace(cm_c)), int(cm_c.sum())),
        'accuracy_shape': (int(np.trace(cm_s)), int(cm_s.sum())),
        'accuracy_overall': (metrics['correct_both'], n_gt),
        'recall': (n_valid, n_gt),
        'precision': (n_valid, n_pred),
    }
    metrics['ci95'] = {
        k: [round(v, 4) for v in wilson_ci(kk, nn)]
        for k, (kk, nn) in rates.items()
    }

    # Ty le che phu bong thuc te (chi co y nghia voi shadow / combined)
    if SHADOW_COVERAGE_LOG:
        metrics['shadow_cover_pct'] = round(
            100.0 * float(np.mean(SHADOW_COVERAGE_LOG)), 1)
    else:
        metrics['shadow_cover_pct'] = ''
    return metrics, samples


def plot_bar(results):
    names = [r['label'] for r in results]
    acc_color = np.array([r['accuracy_color'] * 100 for r in results])
    acc_shape = np.array([r['accuracy_shape'] * 100 for r in results])
    acc_overall = np.array([r['accuracy_overall'] * 100 for r in results])
    recall = np.array([r['recall_overall'] * 100 for r in results])

    def _err(values, key):
        lo = np.array([r['ci95'][key][0] for r in results]) * 100
        hi = np.array([r['ci95'][key][1] for r in results]) * 100
        return np.vstack([values - lo, hi - values])

    errs = [_err(acc_color, 'accuracy_color'),
            _err(acc_shape, 'accuracy_shape'),
            _err(acc_overall, 'accuracy_overall'),
            _err(recall, 'recall')]

    x = np.arange(len(names))
    width = 0.2
    fig, ax = plt.subplots(figsize=(12, 5), dpi=300)
    ebar = dict(ecolor='#333333', elinewidth=0.9, capsize=3)
    ax.bar(x - 1.5 * width, acc_color, width, yerr=errs[0],
           error_kw=ebar, label='Mau')
    ax.bar(x - 0.5 * width, acc_shape, width, yerr=errs[1],
           error_kw=ebar, label='Hinh')
    ax.bar(x + 0.5 * width, acc_overall, width, yerr=errs[2],
           error_kw=ebar, label='Overall')
    ax.bar(x + 1.5 * width, recall, width, yerr=errs[3],
           error_kw=ebar, label='Recall')
    ax.set_ylabel('Accuracy / Recall (%)', fontsize=12)
    ax.set_title('Do ben vung pipeline voi cac dieu kien thuc te\n'
                 '(bong do tang cuong; thanh sai so = CI Wilson 95 %, '
                 'n = 36 anh/dieu kien, che khuat 72 object)',
                 fontsize=12)
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
    fig, axes = plt.subplots(2, n, figsize=(2.35 * n, 4.8), dpi=300)
    if n == 1:
        axes = np.array([[axes[0]], [axes[1]]])
    axes = axes.flatten()
    for k, cond in enumerate(conds):
        # Uu tien chon ca sai de hinh vi du phan anh dung diem gay
        bad = [s for s in samples_by_condition[cond] if s.get('errors')]
        sample = random.choice(bad) if bad else random.choice(
            samples_by_condition[cond])
        tag = 'ca sai' if bad else 'ca dung'
        annotated = draw_detections(sample['image'], sample['detections'])
        axes[k].imshow(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB))
        axes[k].set_title(f"{cond}\nDu doan ({tag})", fontsize=10)
        axes[k].axis('off')

        gt_img = sample['image'].copy()
        for gt in sample['ground_truths']:
            cx, cy = gt['center_px']
            cv2.circle(gt_img, (cx, cy), 5, (0, 255, 0), -1)
            cv2.putText(gt_img, f"{gt['color']}-{gt['shape']}",
                        (cx + 8, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                        (0, 255, 0), 1)
        axes[k + n].imshow(cv2.cvtColor(gt_img, cv2.COLOR_BGR2RGB))
        axes[k + n].set_title('Ground truth', fontsize=10)
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
                         'mean_abs_diff', 'max_abs_diff',
                         'accuracy_color_ci95_lo', 'accuracy_color_ci95_hi',
                         'accuracy_shape_ci95_lo', 'accuracy_shape_ci95_hi',
                         'accuracy_overall_ci95_lo', 'accuracy_overall_ci95_hi',
                         'recall_ci95_lo', 'recall_ci95_hi',
                         'precision_ci95_lo', 'precision_ci95_hi',
                         'shadow_cover_pct'])
        for r in results:
            ci = r['ci95']
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
                f"{ci['accuracy_color'][0]*100:.2f}",
                f"{ci['accuracy_color'][1]*100:.2f}",
                f"{ci['accuracy_shape'][0]*100:.2f}",
                f"{ci['accuracy_shape'][1]*100:.2f}",
                f"{ci['accuracy_overall'][0]*100:.2f}",
                f"{ci['accuracy_overall'][1]*100:.2f}",
                f"{ci['recall'][0]*100:.2f}",
                f"{ci['recall'][1]*100:.2f}",
                f"{ci['precision'][0]*100:.2f}",
                f"{ci['precision'][1]*100:.2f}",
                r['shadow_cover_pct'],
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
    print(f"{'Dieu kien':<24} {'Overall':>8} {'CI95 overall':>15} "
          f"{'Mau':>7} {'Hinh':>7} {'Recall':>8} {'Prec':>7} "
          f"{'mean|diff|':>10} {'cover':>7}")
    for r in results:
        ci = r['ci95']['accuracy_overall']
        cover = (f"{r['shadow_cover_pct']:.1f}%"
                 if r['shadow_cover_pct'] != '' else '-')
        print(f"{r['label']:<24} "
              f"{r['accuracy_overall']*100:>7.1f}% "
              f"{ci[0]*100:>6.1f}-{ci[1]*100:<6.1f} "
              f"{r['accuracy_color']*100:>6.1f}% "
              f"{r['accuracy_shape']*100:>6.1f}% "
              f"{r['recall_overall']*100:>7.1f}% "
              f"{r['precision_overall']*100:>6.1f}% "
              f"{r['mean_abs_diff']:>10.1f} "
              f"{cover:>7}")
    print("===================================")
    print("Da luu:")
    print("  - output/robustness.csv")
    print("  - output/robustness_errors.txt")
    print("  - figures/robustness-bar.png")
    print("  - figures/robustness-examples.png")


if __name__ == '__main__':
    main()
