"""
generate_dataset.py
Sinh tap du lieu anh tong hop 3 mau x 3 hinh cho pipeline thi giac.
"""

import os
import json
import csv
import random
import math
import numpy as np
import cv2


BASE_COLORS = {
    'do': np.array([0, 0, 200], dtype=np.uint8),
    'vang': np.array([0, 200, 200], dtype=np.uint8),
    'xanh': np.array([200, 0, 0], dtype=np.uint8),
}
SHAPES = ['tron', 'vuong', 'tam_giac']
COLORS = list(BASE_COLORS.keys())
IMG_W, IMG_H = 640, 480


def random_center(margin=100, existing=None, min_dist=120):
    """Chon tam ngau nhien, tranh chong lan voi cac vat da co."""
    for _ in range(50):
        cx = random.randint(margin, IMG_W - margin)
        cy = random.randint(margin, IMG_H - margin)
        if existing is None:
            return (cx, cy)
        ok = True
        for ex, ey in existing:
            if math.hypot(cx - ex, cy - ey) < min_dist:
                ok = False
                break
        if ok:
            return (cx, cy)
    return (random.randint(margin, IMG_W - margin),
            random.randint(margin, IMG_H - margin))


def draw_shape(canvas, shape, center, radius, color_bgr, angle=0):
    """Ve hinh len canvas, tra ve bbox."""
    cx, cy = center
    if shape == 'tron':
        cv2.circle(canvas, (cx, cy), radius, color_bgr.tolist(), -1)
        return (cx - radius, cy - radius, 2 * radius, 2 * radius)

    if shape == 'vuong':
        pts = np.array([
            [-radius, -radius],
            [radius, -radius],
            [radius, radius],
            [-radius, radius]
        ], dtype=np.float32)
    else:  # tam_giac
        h = radius * math.sqrt(3)
        pts = np.array([
            [0, -2 * h / 3],
            [-radius, h / 3],
            [radius, h / 3]
        ], dtype=np.float32)

    # Xoay
    ang_rad = math.radians(angle)
    R = np.array([[math.cos(ang_rad), -math.sin(ang_rad)],
                  [math.sin(ang_rad), math.cos(ang_rad)]])
    pts = pts @ R.T
    pts = pts + np.array([cx, cy])
    pts = pts.astype(np.int32)
    cv2.fillPoly(canvas, [pts], color_bgr.tolist())

    x, y, w, h = cv2.boundingRect(pts)
    return (x, y, w, h)


def add_noise_blur(img, sigma, blur_ksize):
    """Them nhieu Gauss va Gaussian blur."""
    if sigma > 0:
        noise = np.random.normal(0, sigma, img.shape).astype(np.float32)
        img = np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    if blur_ksize > 0:
        img = cv2.GaussianBlur(img, (blur_ksize * 2 + 1, blur_ksize * 2 + 1), 0)
    return img


def generate_image(index, color, shape, brightness, angle, sigma, blur,
                   multi=False):
    """Sinh mot anh va ground truth."""
    # Nen xam nhat ngau nhien
    bg_gray = random.randint(220, 250)
    canvas = np.full((IMG_H, IMG_W, 3), bg_gray, dtype=np.uint8)

    base = BASE_COLORS[color].astype(np.float32)
    color_bgr = np.clip(base * brightness, 0, 255).astype(np.uint8)

    gts = []
    centers = []

    n_objects = 2 if multi else 1
    for _ in range(n_objects):
        # Neu multi, mau/hinh thu hai co the khac de tao kho khan
        if multi and len(gts) == 1:
            c2 = random.choice([c for c in COLORS if c != color])
            s2 = random.choice([s for s in SHAPES if s != shape])
            cb = BASE_COLORS[c2].astype(np.float32)
            cb = np.clip(cb * brightness, 0, 255).astype(np.uint8)
        else:
            c2, s2, cb = color, shape, color_bgr

        center = random_center(existing=centers)
        centers.append(center)
        radius = random.randint(35, 55)
        bbox = draw_shape(canvas, s2, center, radius, cb, angle)
        gts.append({
            'color': c2,
            'shape': s2,
            'center_px': [int(center[0]), int(center[1])],
            'bbox': [int(b) for b in bbox],
            'radius': radius,
        })

    img = add_noise_blur(canvas, sigma, blur)

    suffix = 'multi' if multi else 'single'
    fname = f"{index:04d}_{suffix}_{color}_{shape}_b{int(brightness*100):03d}_a{angle:02d}_n{sigma}_r{blur}.png"
    return img, fname, gts


def main():
    # Ghi vao du-lieu chung cua repo, khong phai trong thu muc run.
    repo_root = os.path.normpath(os.path.join(os.path.dirname(__file__),
                                              '..', '..', '..', '..'))
    out_dir = os.path.join(repo_root, 'nghien-cuu', 'du-lieu', 'anh-mau', 'synthetic')
    os.makedirs(out_dir, exist_ok=True)

    random.seed(42)
    np.random.seed(42)

    brightness_levels = [0.7, 1.0, 1.3]
    angles = [0, 15, 30]
    noises = [0, 8, 15]
    blurs = [0, 1]

    images = []
    idx = 0

    # Sinh anh don: 3 mau x 3 hinh x 3 sang x 3 goc x 2 noise x 1 blur = 162
    for color in COLORS:
        for shape in SHAPES:
            for b in brightness_levels:
                for a in angles:
                    for n in noises:
                        for bl in [0]:
                            img, fname, gts = generate_image(
                                idx, color, shape, b, a, n, bl, multi=False)
                            images.append((img, fname, gts))
                            idx += 1

    # Sinh anh voi blur nhe: 18 anh
    for _ in range(18):
        color = random.choice(COLORS)
        shape = random.choice(SHAPES)
        b = random.choice(brightness_levels)
        a = random.choice(angles)
        n = random.choice([5, 10])
        bl = 1
        img, fname, gts = generate_image(
            idx, color, shape, b, a, n, bl, multi=False)
        images.append((img, fname, gts))
        idx += 1

    # Sinh anh 2 vat: 12 anh
    for _ in range(12):
        color = random.choice(COLORS)
        shape = random.choice(SHAPES)
        b = random.choice(brightness_levels)
        a = random.choice(angles)
        n = random.choice([0, 5, 10])
        bl = random.choice([0, 1])
        img, fname, gts = generate_image(
            idx, color, shape, b, a, n, bl, multi=True)
        images.append((img, fname, gts))
        idx += 1

    # Ghi anh va nhan
    labels = []
    for img, fname, gts in images:
        cv2.imwrite(os.path.join(out_dir, fname), img)
        labels.append({'filename': fname, 'objects': gts})

    # Ghi JSON
    with open(os.path.join(out_dir, 'labels.json'), 'w', encoding='utf-8') as f:
        json.dump(labels, f, ensure_ascii=False, indent=2)

    # Ghi CSV tom tat
    with open(os.path.join(out_dir, 'labels_summary.csv'), 'w',
              newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['filename', 'n_objects', 'colors', 'shapes'])
        for item in labels:
            objs = item['objects']
            writer.writerow([
                item['filename'],
                len(objs),
                '+'.join([o['color'] for o in objs]),
                '+'.join([o['shape'] for o in objs]),
            ])

    print(f"Da sinh {len(images)} anh tai {out_dir}")


if __name__ == '__main__':
    main()
