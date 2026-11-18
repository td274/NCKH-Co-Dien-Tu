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
    - touches_border: bool

Cai tien so voi phien ban truoc:
    - Loc dien tich contour theo ti le so voi dien tich anh (khong con
      ngac nhien ngang tuyet doi), giu lai vat chua hoan toan nam trong khung.
    - Dac trung hinh hoc: circularity, extent, solidity, so canh xap xi
      voi epsilon = k * chu vi, giup phan biet tron/vuong/tam giac ben hon
      khi xoay, mo va nhieu nhe.
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
        {'h_min': 100, 'h_max': 140, 's_min': 80, 'v_min': 50},
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
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,
                                      (kernel_size, kernel_size))
    opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel,
                              iterations=open_iter)
    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel,
                              iterations=close_iter)
    return closed


def _shape_confidence(score, floor=0.5):
    return float(min(1.0, max(floor, score)))


def _polygon_angles(approx):
    """
    Tinh goc noi tiep (do) tai cac dinh cua da giac.
    approx: ndarray Nx1x2.
    """
    pts = approx.reshape(-1, 2)
    n = len(pts)
    if n < 3:
        return []
    angles = []
    for i in range(n):
        p0 = pts[(i - 1) % n]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        v1 = p0 - p1
        v2 = p2 - p1
        nv1 = np.linalg.norm(v1)
        nv2 = np.linalg.norm(v2)
        if nv1 < 1e-6 or nv2 < 1e-6:
            angles.append(180.0)
            continue
        cos_a = np.clip(np.dot(v1, v2) / (nv1 * nv2), -1.0, 1.0)
        angles.append(np.degrees(np.arccos(cos_a)))
    return angles


def classify_shape(contour,
                   eps_ratio=0.025,
                   circ_tol=0.82,
                   solid_tol=0.80,
                   ar_lo=0.55,
                   ar_hi=1.80,
                   extent_sq=0.65,
                   extent_tr=0.60):
    """
    Phan loai hinh dang dua tren bo dac trung hinh hoc chuan hoa.

    Cac dac trung:
        - circularity = 4*pi*A / P^2
        - extent      = A / bbox_area
        - solidity    = A / convex_hull_area
        - n_sides     = so dinh cua approxPolyDP(epsilon = eps_ratio * chu vi)
        - phan bo goc tai cac dinh (vuong co goc ~90°, tam giac co 3 goc nhon)

    Tra ve (shape, confidence).
    """
    area = cv2.contourArea(contour)
    if area < 1:
        return 'unknown', 0.0

    peri = cv2.arcLength(contour, True)
    if peri < 1e-3:
        return 'unknown', 0.0

    approx = cv2.approxPolyDP(contour, eps_ratio * peri, True)
    n_sides = len(approx)

    x, y, w, h = cv2.boundingRect(contour)
    aspect_ratio = float(w) / max(h, 1)
    bbox_area = max(w * h, 1)
    extent = area / bbox_area

    hull = cv2.convexHull(contour)
    hull_area = cv2.contourArea(hull)
    solidity = area / hull_area if hull_area > 0 else 0.0

    circularity = 4.0 * np.pi * area / (peri ** 2)

    # Tinh goc cac dinh de phan biet vuong/tam giac ben hon
    angles = _polygon_angles(approx)
    n_right = sum(1 for a in angles if 70 <= a <= 110)
    n_acute = sum(1 for a in angles if a < 60)

    # 1. Hinh tron: gan nhu hoan hao.
    if circularity >= circ_tol and solidity >= solid_tol:
        conf = 0.80 + 0.20 * min(1.0, circularity * solidity)
        return 'tron', _shape_confidence(conf, 0.85)

    # 2. Hinh vuong: circularity ~0.78, aspect ratio gan 1, hoac co goc vuong.
    square_aspect_ok = ar_lo <= aspect_ratio <= ar_hi
    square_solid_ok = solidity >= solid_tol - 0.05
    square_by_circ = (0.68 <= circularity < circ_tol and
                      square_aspect_ok and square_solid_ok)
    # Vuong that thuong co 4 goc vuong; neu mo/nhieu lam mat dinh,
    # van co the con 3 goc vuong hoac approx ra 5-6 canh nhung co >=3 goc vuong.
    square_by_angles = (n_right >= 3 and square_aspect_ok and square_solid_ok)
    # Vuong xoay 30° co extent ~0.54; chap nhan n_sides 4-6, extent >= 0.50
    # NHUNG phai co it nhat 2 goc vuong de khong nuot tam giac bi lam min.
    square_by_shape = (4 <= n_sides <= 6 and n_right >= 2 and square_aspect_ok and
                       extent >= 0.50 and square_solid_ok)
    if square_by_circ or square_by_angles or square_by_shape:
        conf = 0.50 + 0.25 * circularity + 0.25 * solidity
        return 'vuong', _shape_confidence(conf, 0.60)

    # 3. Tam giac: 3 canh ro rang va 3 goc nhon (it nhat 2 goc < 60),
    #    hoac compact (extent nho) va co goc nhon/min < 70 do lam min.
    min_angle = min(angles) if angles else 180.0
    triangle_sides_ok = (n_sides == 3 and n_acute >= 2)
    triangle_compact = (circularity < 0.68 and extent < extent_tr and
                        square_solid_ok and (n_acute >= 1 or min_angle < 70.0))
    if triangle_sides_ok or triangle_compact:
        conf = 0.50 + 0.25 * solidity + 0.25 * max(0.0, 1.0 - extent)
        return 'tam_giac', _shape_confidence(conf, 0.55)

    # 4. Fallback: chon gan nhat dua tren circularity/extent/goc.
    if n_right >= 2 and square_aspect_ok:
        return 'vuong', _shape_confidence(0.5, 0.40)
    if circularity >= 0.65:
        return 'tron', _shape_confidence(circularity, 0.40)
    if extent >= 0.55:
        return 'vuong', _shape_confidence(extent, 0.35)
    return 'tam_giac', _shape_confidence(solidity, 0.30)


def detect_objects(image_bgr,
                   min_area_ratio=0.0002,
                   max_area_ratio=0.70,
                   transformer=None,
                   debug=False):
    """
    Phat hien cac vat the trong anh BGR.

    Args:
        image_bgr: numpy array HxWx3
        min_area_ratio: ti le dien tich toi thieu so voi dien tich anh
        max_area_ratio: ti le dien tich toi da so voi dien tich anh
        transformer: doi tuong co ham transform(points_px) -> points_mm
        debug: neu True, tra ve them mask dict

    Returns:
        detections: list[dict]
        debug_info: dict (chi khi debug=True)
    """
    if image_bgr is None or image_bgr.size == 0:
        return [], {}

    h_img, w_img = image_bgr.shape[:2]
    img_area = h_img * w_img
    min_area = max(1, int(min_area_ratio * img_area))
    max_area = int(max_area_ratio * img_area) if max_area_ratio is not None else None

    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    detections = []
    all_masks = {}

    # Kich thuoc kernel morphology ty le nho voi kich thuoc anh.
    kernel_size = max(3, int(min(h_img, w_img) / 80) | 1)

    for color_name, ranges in COLOR_RANGES.items():
        mask = build_color_mask(hsv, ranges)
        mask = preprocess_mask(mask, kernel_size=kernel_size,
                               open_iter=1, close_iter=1)
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

            x, y, w, h = cv2.boundingRect(cnt)
            bbox_area = max(w * h, 1)
            extent = area / bbox_area
            confidence = float(conf_shape * 0.7 + extent * 0.3)

            touches_border = (x <= 0 or y <= 0 or
                              x + w >= w_img - 1 or y + h >= h_img - 1)

            det = {
                'center_px': (cx, cy),
                'color': color_name,
                'shape': shape,
                'confidence': round(confidence, 3),
                'bbox': (x, y, w, h),
                'area': float(area),
                'contour': cnt,
                'touches_border': bool(touches_border),
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
        if det.get('touches_border'):
            label += " *"
        cv2.putText(out, label, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, c, 2)
        cx, cy = det['center_px']
        cv2.circle(out, (cx, cy), 4, (0, 255, 0), -1)
    return out
