import json, os, sys, math
import cv2, numpy as np

run_dir = r'D:\NCKH-Co-Dien-Tu\nghien-cuu\mo-phong\runs\2026-11-18-thi-giac-hsv'
sys.path.insert(0, os.path.join(run_dir, 'src'))
from detect import detect_objects, build_color_mask, preprocess_mask, COLOR_RANGES, _polygon_angles

dataset_dir = os.path.join(run_dir, '..', '..', '..', 'du-lieu', 'anh-mau', 'synthetic')
dataset_dir = os.path.normpath(dataset_dir)
labels = json.load(open(os.path.join(dataset_dir, 'labels.json'), encoding='utf-8'))

for item in labels:
    if 'vuong_b100_a30_n0' not in item['filename']:
        continue
    img = cv2.imread(os.path.join(dataset_dir, item['filename']))
    dets, _ = detect_objects(img, min_area_ratio=0.0002, max_area_ratio=0.70)
    for det in dets:
        print(item['filename'], det)
    # find red contour features
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = build_color_mask(hsv, COLOR_RANGES[item['objects'][0]['color']])
    mask = preprocess_mask(mask, kernel_size=5, open_iter=1, close_iter=1)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 1000:
            continue
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.025 * peri, True)
        angles = _polygon_angles(approx)
        print('area', area, 'n_sides', len(approx), 'angles', angles,
              'n_right', sum(1 for a in angles if 70 <= a <= 110),
              'n_acute', sum(1 for a in angles if a < 60))
    break
