import json, os, sys, math
import cv2, numpy as np

run_dir = r'D:\NCKH-Co-Dien-Tu\nghien-cuu\mo-phong\runs\2026-11-18-thi-giac-hsv'
sys.path.insert(0, os.path.join(run_dir, 'src'))
from detect import detect_objects, classify_shape, _polygon_angles

dataset_dir = os.path.join(run_dir, '..', '..', '..', 'du-lieu', 'anh-mau', 'synthetic')
dataset_dir = os.path.normpath(dataset_dir)
labels = json.load(open(os.path.join(dataset_dir, 'labels.json'), encoding='utf-8'))

for item in labels:
    if '0140_single_vang_tam_giac' not in item['filename']:
        continue
    img = cv2.imread(os.path.join(dataset_dir, item['filename']))
    dets, masks = detect_objects(img, min_area_ratio=0.0002, max_area_ratio=0.70, debug=True)
    print('det', dets)
    for det, gt in zip(dets, item['objects']):
        cnt = det['contour']
        area = cv2.contourArea(cnt)
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.025 * peri, True)
        angles = _polygon_angles(approx)
        x, y, w, h = cv2.boundingRect(cnt)
        aspect = w / max(h, 1)
        extent = area / max(w * h, 1)
        hull = cv2.convexHull(cnt)
        hull_area = cv2.contourArea(hull)
        solidity = area / hull_area if hull_area > 0 else 0
        circ = 4 * math.pi * area / (peri ** 2)
        print('gt', gt)
        print('n', len(approx), 'angles', angles,
              'n_right', sum(1 for a in angles if 70 <= a <= 110),
              'n_acute', sum(1 for a in angles if a < 60))
        print(f'aspect={aspect:.3f} extent={extent:.3f} solidity={solidity:.3f} circ={circ:.3f}')
    break
