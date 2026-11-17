"""
run.py
Chay danh gia pipeline thi giac tren tap du lieu tong hop.
Co the chay doc lap: D:\Python312\python.exe run.py
"""

import os
import sys
import json
import time
import csv
import glob
import numpy as np
import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from detect import detect_objects, draw_detections
from capture import ImageSource, list_camera_indices
from calibrate import default_transformer
from evaluate import evaluate_image, aggregate_metrics
from evaluate import save_confusion_csv, save_errors_csv


RUN_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(RUN_DIR, '..', '..', '..', 'du-lieu', 'anh-mau', 'synthetic')
DATASET_DIR = os.path.normpath(DATASET_DIR)
OUT_DIR = os.path.join(RUN_DIR, 'output')
FIG_DIR = os.path.join(RUN_DIR, 'figures')


def ensure_dataset():
    """Sinh du lieu neu thieu."""
    n_images = len(glob.glob(os.path.join(DATASET_DIR, '*.png')))
    if n_images < 150:
        print(f"Du lieu chi co {n_images} anh, sinh lai...")
        gen_path = os.path.join(RUN_DIR, 'generate_dataset.py')
        exec(open(gen_path, encoding='utf-8').read(), {'__name__': '__main__'})
    else:
        print(f"Da co {n_images} anh trong dataset.")


def load_labels():
    with open(os.path.join(DATASET_DIR, 'labels.json'), 'r', encoding='utf-8') as f:
        return json.load(f)


def run_evaluation(labels, transformer):
    per_image = []
    timings_ms = []
    sample_results = []

    for item in labels:
        fname = item['filename']
        img = cv2.imread(os.path.join(DATASET_DIR, fname))
        if img is None:
            print(f"Khong doc duoc {fname}")
            continue

        # Do thoi gian xu ly
        t0 = time.perf_counter()
        dets, _ = detect_objects(img, min_area=200, transformer=transformer)
        t1 = time.perf_counter()
        timings_ms.append((t1 - t0) * 1000)

        gts = item['objects']
        res = evaluate_image(dets, gts, max_dist_px=50)
        per_image.append(res)

        sample_results.append({
            'filename': fname,
            'image': img,
            'detections': dets,
            'ground_truths': gts,
        })

    metrics = aggregate_metrics(per_image)
    metrics['timing_ms'] = {
        'mean': round(float(np.mean(timings_ms)), 2),
        'std': round(float(np.std(timings_ms)), 2),
        'p50': round(float(np.percentile(timings_ms, 50)), 2),
        'p95': round(float(np.percentile(timings_ms, 95)), 2),
        'p99': round(float(np.percentile(timings_ms, 99)), 2),
        'n_samples': len(timings_ms),
    }
    return metrics, sample_results, timings_ms


def measure_webcam():
    """Thu mo webcam va do FPS tren 60 frame."""
    info = {'opened': False, 'fps': None, 'frame_time_ms': None, 'image_path': None}
    available = list_camera_indices(max_idx=2)
    if not available:
        print("Khong tim thay webcam.")
        return info

    idx = available[0]
    cap = cv2.VideoCapture(idx)
    if not cap.isOpened():
        print(f"Khong mo duoc webcam {idx}")
        return info

    print(f"Webcam {idx} mo thanh cong.")
    info['opened'] = True
    info['camera_index'] = idx

    # Chup 60 frame do thoi gian
    n = 60
    times = []
    last_frame = None
    for _ in range(n):
        t0 = time.perf_counter()
        ok, frame = cap.read()
        t1 = time.perf_counter()
        if ok:
            times.append((t1 - t0) * 1000)
            last_frame = frame

    if times:
        info['frame_time_ms'] = {
            'mean': round(float(np.mean(times)), 2),
            'p95': round(float(np.percentile(times, 95)), 2),
        }
        info['fps'] = round(1000.0 / max(info['frame_time_ms']['mean'], 1e-3), 1)

    # Xu ly 1 frame va luu anh co bbox
    if last_frame is not None:
        dets, _ = detect_objects(last_frame, min_area=200)
        annotated = draw_detections(last_frame, dets)
        path = os.path.join(FIG_DIR, 'webcam_sample.png')
        cv2.imwrite(path, annotated)
        info['image_path'] = path
        print(f"Da luu anh webcam mau: {path}")

    cap.release()
    return info


def plot_confusion(cm, labels, title, path):
    fig, ax = plt.subplots(figsize=(5, 4), dpi=300)
    im = ax.imshow(cm, cmap='Blues')
    ax.set_xticks(np.arange(len(labels)))
    ax.set_yticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_yticklabels(labels, fontsize=11)
    ax.set_xlabel('Du doan', fontsize=12)
    ax.set_ylabel('Ground truth', fontsize=12)
    ax.set_title(title, fontsize=13)

    for i in range(len(labels)):
        for j in range(len(labels)):
            text = ax.text(j, i, int(cm[i, j]), ha='center', va='center',
                           color='white' if cm[i, j] > cm.max() / 2 else 'black',
                           fontsize=11)

    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    fig.savefig(path, dpi=300)
    plt.close(fig)


def plot_samples(samples, n=4):
    fig, axes = plt.subplots(2, n, figsize=(12, 6), dpi=300)
    axes = axes.flatten()
    for k, sample in enumerate(samples[:n]):
        img = sample['image']
        dets = sample['detections']
        annotated = draw_detections(img, dets)
        annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
        axes[k].imshow(annotated_rgb)
        axes[k].set_title(sample['filename'][:30], fontsize=9)
        axes[k].axis('off')

        # Ve ground truth overlay
        gt_img = img.copy()
        for gt in sample['ground_truths']:
            cx, cy = gt['center_px']
            cv2.circle(gt_img, (cx, cy), 5, (0, 255, 0), -1)
            cv2.putText(gt_img, f"{gt['color']}-{gt['shape']}",
                        (cx + 8, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                        (0, 255, 0), 1)
        axes[k + n].imshow(cv2.cvtColor(gt_img, cv2.COLOR_BGR2RGB))
        axes[k + n].set_title('Ground truth', fontsize=9)
        axes[k + n].axis('off')

    for ax in axes[len(samples):]:
        ax.axis('off')
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'sample_detections.png'), dpi=300)
    plt.close(fig)


def save_outputs(metrics, timings_ms):
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(FIG_DIR, exist_ok=True)

    # JSON metrics
    with open(os.path.join(OUT_DIR, 'metrics.json'), 'w', encoding='utf-8') as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    # CSV confusion
    save_confusion_csv(np.array(metrics['cm_color']), ['do', 'vang', 'xanh'],
                       os.path.join(OUT_DIR, 'confusion_color.csv'))
    save_confusion_csv(np.array(metrics['cm_shape']), ['tron', 'vuong', 'tam_giac'],
                       os.path.join(OUT_DIR, 'confusion_shape.csv'))

    # CSV errors
    save_errors_csv(metrics['all_errors'],
                    os.path.join(OUT_DIR, 'error_cases.csv'))

    # CSV timing
    with open(os.path.join(OUT_DIR, 'timing_ms.csv'), 'w',
              newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['sample', 'time_ms'])
        for i, t in enumerate(timings_ms):
            writer.writerow([i + 1, round(t, 3)])


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(FIG_DIR, exist_ok=True)

    ensure_dataset()
    labels = load_labels()
    print(f"So anh nhan: {len(labels)}")

    transformer = default_transformer()
    print("Transformer gia dinh 300x200 mm tu 4 diem moc.")

    metrics, samples, timings_ms = run_evaluation(labels, transformer)
    print("Da danh gia xong.")

    # Luu truoc khi webcam de neu webcam loi van co ket qua
    save_outputs(metrics, timings_ms)

    # Kiem tra webcam
    webcam_info = measure_webcam()
    metrics['webcam'] = webcam_info

    # Cap nhat metrics sau webcam
    with open(os.path.join(OUT_DIR, 'metrics.json'), 'w', encoding='utf-8') as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    # Figures
    plot_confusion(np.array(metrics['cm_color']), ['do', 'vang', 'xanh'],
                   'Ma tran nham lan - Mau sac',
                   os.path.join(FIG_DIR, 'confusion_color.png'))
    plot_confusion(np.array(metrics['cm_shape']), ['tron', 'vuong', 'tam_giac'],
                   'Ma tran nham lan - Hinh dang',
                   os.path.join(FIG_DIR, 'confusion_shape.png'))
    plot_samples(samples, n=4)

    # In tom tat
    print("\n===== KET QUA TOM TAT =====")
    print(f"So anh: {len(labels)}")
    print(f"Tong so vat GT: {metrics['total_gt_objects']}")
    print(f"Do chinh xac mau: {metrics['accuracy_color']*100:.1f}%")
    print(f"Do chinh xac hinh: {metrics['accuracy_shape']*100:.1f}%")
    print(f"Do chinh xac tong: {metrics['accuracy_overall']*100:.1f}%")
    print(f"Thoi gian xu ly trung binh: {metrics['timing_ms']['mean']:.2f} ms")
    print(f"Thoi gian xu ly P95: {metrics['timing_ms']['p95']:.2f} ms")
    print(f"Webcam mo duoc: {metrics['webcam']['opened']}")
    print("===========================")


if __name__ == '__main__':
    main()
