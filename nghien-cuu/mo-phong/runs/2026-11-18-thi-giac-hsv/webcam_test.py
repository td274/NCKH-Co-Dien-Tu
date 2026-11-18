"""
webcam_test.py
Thu mo webcam, do FPS/frame-time tren 60 frame, luu anh co bbox.
"""

import os
import sys
import time
import json
import numpy as np
import cv2

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from detect import detect_objects, draw_detections
from capture import list_camera_indices


RUN_DIR = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(RUN_DIR, 'figures')
OUT_DIR = os.path.join(RUN_DIR, 'output')


def test_webcam():
    info = {'opened': False, 'fps': None, 'frame_time_ms': None,
            'image_path': None, 'camera_index': None}
    available = list_camera_indices(max_idx=2)
    print(f"Camera co san: {available}")
    if not available:
        print("Khong tim thay webcam.")
        return info

    idx = available[0]
    cap = cv2.VideoCapture(idx)
    if not cap.isOpened():
        print(f"Khong mo duoc webcam {idx}")
        return info

    info['opened'] = True
    info['camera_index'] = idx
    print(f"Webcam {idx} mo thanh cong.")

    n = 60
    times = []
    last_frame = None
    for i in range(n):
        t0 = time.perf_counter()
        ok, frame = cap.read()
        t1 = time.perf_counter()
        if ok:
            times.append((t1 - t0) * 1000)
            last_frame = frame
        else:
            print(f"Frame {i} doc that bai")

    if times:
        info['frame_time_ms'] = {
            'mean': round(float(np.mean(times)), 2),
            'std': round(float(np.std(times)), 2),
            'p95': round(float(np.percentile(times, 95)), 2),
        }
        info['fps'] = round(1000.0 / max(info['frame_time_ms']['mean'], 1e-3), 1)
        print(f"Frame time mean: {info['frame_time_ms']['mean']} ms, P95: {info['frame_time_ms']['p95']} ms, FPS: {info['fps']}")

    if last_frame is not None:
        dets, _ = detect_objects(last_frame, min_area_ratio=0.0002,
                                  max_area_ratio=0.70)
        annotated = draw_detections(last_frame, dets)
        path = os.path.join(FIG_DIR, 'webcam_sample.png')
        cv2.imwrite(path, annotated)
        info['image_path'] = path
        print(f"Da luu anh webcam mau: {path}, {len(dets)} vat phat hien")

    cap.release()
    return info


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    info = test_webcam()
    with open(os.path.join(OUT_DIR, 'webcam_info.json'), 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()
