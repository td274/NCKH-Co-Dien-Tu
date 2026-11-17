"""
evaluate.py
So sanh du doan voi ground truth, tinh ma tran nham lan va do chinh xac.
"""

import json
import csv
import os
import numpy as np
from collections import defaultdict


COLORS = ['do', 'vang', 'xanh']
SHAPES = ['tron', 'vuong', 'tam_giac']


def distance(p1, p2):
    return np.hypot(p1[0] - p2[0], p1[1] - p2[1])


def match_detections_to_gt(detections, ground_truths, max_dist_px=40):
    """
    Greedy matching dua tren khoang cach tam pixel.
    Tra ve: list cac tuple (det, gt) va cac FP/FN.
    """
    used_gt = set()
    matches = []
    for det in detections:
        best_i = -1
        best_d = float('inf')
        for i, gt in enumerate(ground_truths):
            if i in used_gt:
                continue
            d = distance(det['center_px'], gt['center_px'])
            if d < best_d:
                best_d = d
                best_i = i
        if best_i >= 0 and best_d <= max_dist_px:
            used_gt.add(best_i)
            matches.append((det, ground_truths[best_i], best_d))
        else:
            matches.append((det, None, best_d))  # false positive

    # False negatives
    for i, gt in enumerate(ground_truths):
        if i not in used_gt:
            matches.append((None, gt, None))

    return matches


def build_confusion_matrix(predictions, truths, labels):
    """predictions, truths: list nhan tuong ung."""
    n = len(labels)
    label_to_idx = {l: i for i, l in enumerate(labels)}
    cm = np.zeros((n, n), dtype=int)
    for p, t in zip(predictions, truths):
        if t in label_to_idx and p in label_to_idx:
            cm[label_to_idx[t], label_to_idx[p]] += 1
    return cm


def evaluate_image(detections, ground_truths, max_dist_px=40):
    """Danh gia mot anh, tra ve cac chi so va ca sai."""
    matches = match_detections_to_gt(detections, ground_truths, max_dist_px)

    pred_colors = []
    true_colors = []
    pred_shapes = []
    true_shapes = []
    errors = []
    correct_both = 0

    for det, gt, dist in matches:
        if det is None:
            # FN
            errors.append({
                'type': 'FN',
                'gt_color': gt['color'],
                'gt_shape': gt['shape'],
                'reason': 'Khong phat hien duoc vat'
            })
            continue
        if gt is None:
            # FP
            errors.append({
                'type': 'FP',
                'pred_color': det['color'],
                'pred_shape': det['shape'],
                'reason': 'Phat hien du vat'
            })
            continue

        pred_colors.append(det['color'])
        true_colors.append(gt['color'])
        pred_shapes.append(det['shape'])
        true_shapes.append(gt['shape'])

        is_correct = (det['color'] == gt['color'] and det['shape'] == gt['shape'])
        if is_correct:
            correct_both += 1
        else:
            errors.append({
                'type': 'MISMATCH',
                'gt_color': gt['color'],
                'gt_shape': gt['shape'],
                'pred_color': det['color'],
                'pred_shape': det['shape'],
                'distance_px': float(dist),
                'reason': f"Du doan {det['color']}-{det['shape']} thay vi {gt['color']}-{gt['shape']}"
            })

    cm_color = build_confusion_matrix(pred_colors, true_colors, COLORS)
    cm_shape = build_confusion_matrix(pred_shapes, true_shapes, SHAPES)

    # So cap matched hop le
    n_valid = len([m for m in matches if m[0] is not None and m[1] is not None])
    n_total_gt = len(ground_truths)

    return {
        'cm_color': cm_color,
        'cm_shape': cm_shape,
        'errors': errors,
        'n_valid_matches': n_valid,
        'n_total_gt': n_total_gt,
        'correct_both': correct_both,
    }


def aggregate_metrics(per_image_results):
    """Tong hop ma tran nham lan va accuracy tu nhieu anh."""
    cm_color = np.zeros((3, 3), dtype=int)
    cm_shape = np.zeros((3, 3), dtype=int)
    all_errors = []
    total_gt = 0
    total_valid = 0

    for r in per_image_results:
        cm_color += r['cm_color']
        cm_shape += r['cm_shape']
        all_errors.extend(r['errors'])
        total_gt += r['n_total_gt']
        total_valid += r['n_valid_matches']

    accuracy_color = float(np.trace(cm_color) / max(cm_color.sum(), 1))
    accuracy_shape = float(np.trace(cm_shape) / max(cm_shape.sum(), 1))
    # Accuracy tong: ty le vat dung ca mau va hinh tren tong so vat GT
    correct_both = sum(r.get('correct_both', 0) for r in per_image_results)
    accuracy_overall = float(correct_both / max(total_gt, 1))

    return {
        'cm_color': cm_color.tolist(),
        'cm_shape': cm_shape.tolist(),
        'accuracy_color': round(accuracy_color, 4),
        'accuracy_shape': round(accuracy_shape, 4),
        'accuracy_overall': round(accuracy_overall, 4),
        'total_gt_objects': total_gt,
        'total_valid_matches': total_valid,
        'correct_both': correct_both,
        'all_errors': all_errors,
    }


def save_confusion_csv(cm, labels, path):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        header = ['GT \\ Pred'] + labels
        writer.writerow(header)
        for i, row in enumerate(cm):
            writer.writerow([labels[i]] + [int(x) for x in row])


def save_errors_csv(errors, path):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['type', 'gt_color', 'gt_shape',
                                               'pred_color', 'pred_shape',
                                               'distance_px', 'reason'])
        writer.writeheader()
        for e in errors:
            writer.writerow(e)
