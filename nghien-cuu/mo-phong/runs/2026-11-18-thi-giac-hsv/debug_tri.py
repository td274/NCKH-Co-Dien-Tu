import json, os, sys, math
import cv2, numpy as np

run_dir = r'D:\NCKH-Co-Dien-Tu\nghien-cuu\mo-phong\runs\2026-11-18-thi-giac-hsv'
sys.path.insert(0, os.path.join(run_dir, 'src'))
from detect import detect_objects, build_color_mask, preprocess_mask, COLOR_RANGES, _polygon_angles

dataset_dir = os.path.join(run_dir, '..', '..', '..', 'du-lieu', 'anh-mau', 'synthetic')
dataset_dir = os.path.normpath(dataset_dir)
labels = json.load(open(os.path.join(dataset_dir, 'labels.json'), encoding='utf-8'))

for item in labels:
    if 'tam_giac' not in item['filename']:
        continue
    img = cv2.imread(os.path.join(dataset_dir, item['filename']))
    dets, _ = detect_objects(img, min_area_ratio=0.0002, max_area_ratio=0.70)
    for det, gt in zip(dets, item['objects']):
        if gt['shape'] == 'tam_giac' and det['shape'] == 'vuong':
            print('FILE', item['filename'])
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            mask = build_color_mask(hsv, COLOR_RANGES[gt['color']])
            mask = preprocess_mask(mask, kernel_size=5, open_iter=1, close_iter=1)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area < 1000:
                    continue
                M = cv2.moments(cnt)
                cx = int(M['m10']/M['m00']); cy=int(M['m01']/M['m00'])
                if math.hypot(cx-det['center_px'][0], cy-det['center_px'][1])>5:
                    continue
                peri = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.025 * peri, True)
                angles = _polygon_angles(approx)
                x,y,w,h = cv2.boundingRect(cnt)
                aspect = w/max(h,1)
                extent = area/max(w*h,1)
                hull = cv2.convexHull(cnt)
                hull_area = cv2.contourArea(hull)
                solidity = area/hull_area if hull_area>0 else 0
                circ = 4*math.pi*area/(peri**2)
                print('n', len(approx), 'angles', angles,
                      'n_right', sum(1 for a in angles if 70<=a<=110),
                      'n_acute', sum(1 for a in angles if a<60))
                print(f'aspect={aspect:.3f} extent={extent:.3f} solidity={solidity:.3f} circ={circ:.3f}')
            break
