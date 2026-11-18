import json, os, sys, math
import cv2, numpy as np

run_dir = r'D:\NCKH-Co-Dien-Tu\nghien-cuu\mo-phong\runs\2026-11-18-thi-giac-hsv'
sys.path.insert(0, os.path.join(run_dir, 'src'))
from detect import detect_objects, build_color_mask, preprocess_mask, COLOR_RANGES

dataset_dir = os.path.join(run_dir, '..', '..', '..', 'du-lieu', 'anh-mau', 'synthetic')
dataset_dir = os.path.normpath(dataset_dir)
labels = json.load(open(os.path.join(dataset_dir, 'labels.json'), encoding='utf-8'))

errors = []
for item in labels:
    img = cv2.imread(os.path.join(dataset_dir, item['filename']))
    dets, _ = detect_objects(img, min_area_ratio=0.0002, max_area_ratio=0.70)
    gts = item['objects']
    for det in dets:
        for gt in gts:
            dx = det['center_px'][0] - gt['center_px'][0]
            dy = det['center_px'][1] - gt['center_px'][1]
            if math.hypot(dx, dy) < 40:
                if gt['shape'] == 'vuong' and det['shape'] == 'tam_giac':
                    errors.append((item['filename'], det, gt))
    if len(errors) >= 8:
        break

for fname, det, gt in errors:
    print(fname, 'gt', gt['color'], gt['shape'], 'pred', det['color'], det['shape'])
    img = cv2.imread(os.path.join(dataset_dir, fname))
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = build_color_mask(hsv, COLOR_RANGES[gt['color']])
    mask = preprocess_mask(mask, kernel_size=5, open_iter=1, close_iter=1)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        M = cv2.moments(cnt)
        if M['m00'] == 0:
            continue
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
        if math.hypot(cx - det['center_px'][0], cy - det['center_px'][1]) < 5:
            area = cv2.contourArea(cnt)
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.025 * peri, True)
            n = len(approx)
            x, y, w, h = cv2.boundingRect(cnt)
            aspect = w / max(h, 1)
            extent = area / max(w * h, 1)
            hull = cv2.convexHull(cnt)
            hull_area = cv2.contourArea(hull)
            solidity = area / hull_area if hull_area > 0 else 0
            circ = 4 * math.pi * area / (peri ** 2)
            print(f'  area={area:.0f} peri={peri:.1f} n={n} aspect={aspect:.3f} '
                  f'extent={extent:.3f} solidity={solidity:.3f} circ={circ:.3f}')
            break
