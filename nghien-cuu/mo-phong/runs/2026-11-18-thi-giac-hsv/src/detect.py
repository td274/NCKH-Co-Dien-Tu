"""
detect.py
Pipeline phat hien va phan loai mau + hinh dang bang OpenCV.

Dau vao: anh BGR (numpy array HxWx3)
Dau ra: list cac dict, moi dict chua:
    - center_px: (cx, cy) pixel
    - center_mm: (x_mm, y_mm) neu transformer duoc truyen vao
    - color: 'do' | 'vang' | 'xanh'
    - shape: 'tron' | 'vuong' | 'tam_giac'
    - confidence: float [0,1]
    - bbox: (x,y,w,h)
    - area: float (pixel^2)
"""

import cv2
import numpy as np


COLOR_RANGES = {
    'do': [
        {'h_min': 0, 'h_max': 10, 's_min': 100, 'v_min': 50},
        {'h_min': 170, 'h_max': 180, 's_min': 100, 'v_min': 50},
    ],
    'vang': [
        {'h_min': 20, 'h_max': 40, 's_min': 100, 'v_min': 50},
    ],
    'xanh': [
        {'h_min': 70, 'h_max': 100, 's_min': 80, 'v_min': 50},
    ],
}


def build_color_mask(hsv, ranges):
    """Tao mask tu danh sach cac khoang HSV."""
    mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
    for r in ranges:
        lower = np.array([r['h_min'], r['s_min'], r['v_min']])
        upper = np.array([r['h_max'], 255, 255])
        mask |= cv2.inRange(hsv, lower, upper)
    return mask


def preprocess_mask(mask, kernel_size=5, open_iter=1, close_iter=1):
    """Morphology mo/dong de loai nhieu va no lo."""
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=open_iter)
    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel, iterations=close_iter)
    return closed


def classify_shape(contour, aspect_ratio_tol=0.25):
    """
    Phan loai hinh dang dua tren approxPolyDP + dac trung hinh hoc.
    Tra ve (shape, confidence).
    """
    area = cv2.contourArea(contour)
    if area < 50:
        return 'unknown', 0.0

    peri = cv2.arcLength(contour, True)
    if peri < 1e-3:
        return 'unknown', 0.0

    # So canh xap xi
    approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
    n_sides = len(approx)

    # Bao hinh chu nhat
    x, y, w, h = cv2.boundingRect(contour)
    aspect_ratio = float(w) / max(h, 1)

    # Dac trung tron
    hull = cv2.convexHull(contour)
    hull_area = cv2.contourArea(hull)
    solidity = area / hull_area if hull_area > 0 else 0
    circularity = 4 * np.pi * area / (peri ** 2)

    if n_sides >= 8 or (solidity > 0.85 and circularity > 0.65):
        # Tron
        conf = min(1.0, circularity * solidity)
        return 'tron', float(conf)

    if n_sides == 4:
        # Vuong / chu nhat
        ar_ok = abs(aspect_ratio - 1.0) <= aspect_ratio_tol
        if ar_ok:
            conf = 0.7 + 0.3 * solidity
            return 'vuong', float(min(1.0, conf))
        else:
            return 'vuong', float(0.4)

    if n_sides == 3:
        conf = 0.7 + 0.3 * solidity
        return 'tam_giac', float(min(1.0, conf))

    # Truong hop khac: chon gan nhat dua tren circularity
    if circularity > 0.6:
        return 'tron', float(circularity)
    if n_sides == 5 or n_sides == 6:
        return 'vuong', 0.3
    return 'tam_giac', 0.2


def detect_objects(image_bgr, min_area=200, max_area=None,
                   transformer=None, debug=False):
    """
    Phat hien cac vat the trong anh BGR.

    Args:
        image_bgr: numpy array HxWx3
        min_area: dien tich toi thieu (px^2)
        max_area: dien tich toi da (px^2), None = khong gioi han
        transformer: doi tuong co ham transform(points_px) -> points_mm
        debug: neu True, tra ve them mask dict

    Returns:
        detections: list[dict]
        debug_info: dict (chi khi debug=True)
    """
    if image_bgr is None or image_bgr.size == 0:
        return [], {}

    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    detections = []
    all_masks = {}

    for color_name, ranges in COLOR_RANGES.items():
        mask = build_color_mask(hsv, ranges)
        mask = preprocess_mask(mask, kernel_size=5, open_iter=1, close_iter=1)
        all_masks[color_name] = mask

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < min_area:
                continue
            if max_area is not None and area > max_area:
                continue

            M = cv2.moments(cnt)
            if M['m00'] < 1e-6:
                continue
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])

            shape, conf_shape = classify_shape(cnt)
            if shape == 'unknown':
                continue

            # Confidence tong hop: do tin cay hinh dang + ty le dien tich contour
            # so voi bounding box (phan tach tot)
            x, y, w, h = cv2.boundingRect(cnt)
            bbox_area = max(w * h, 1)
            extent = area / bbox_area
            confidence = float(conf_shape * 0.7 + extent * 0.3)

            det = {
                'center_px': (cx, cy),
                'color': color_name,
                'shape': shape,
                'confidence': round(confidence, 3),
                'bbox': (x, y, w, h),
                'area': float(area),
                'contour': cnt,
            }
            if transformer is not None:
                pts = np.array([[cx, cy]], dtype=np.float32)
                mm = transformer.transform(pts)
                det['center_mm'] = tuple(mm[0])
            detections.append(det)

    if debug:
        return detections, all_masks
    return detections, {}


def draw_detections(image_bgr, detections, thickness=2):
    """Ve bounding box va nhan len anh."""
    out = image_bgr.copy()
    color_map_bgr = {
        'do': (0, 0, 255),
        'vang': (0, 255, 255),
        'xanh': (255, 0, 0),
    }
    for det in detections:
        x, y, w, h = det['bbox']
        c = color_map_bgr.get(det['color'], (128, 128, 128))
        cv2.rectangle(out, (x, y), (x + w, y + h), c, thickness)
        label = f"{det['color']}-{det['shape']} {det['confidence']:.2f}"
        cv2.putText(out, label, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, c, 2)
        cx, cy = det['center_px']
        cv2.circle(out, (cx, cy), 4, (0, 255, 0), -1)
    return out
