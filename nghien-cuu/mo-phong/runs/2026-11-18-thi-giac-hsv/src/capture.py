"""
capture.py
Nguon anh: webcam hoac thu muc anh tren dia.
"""

import os
import cv2
import glob


class ImageSource:
    """Nguon anh dong nhat cho ca webcam va thu muc."""

    def __init__(self, source=0):
        """
        source:
            - int: chi so webcam (0, 1, ...)
            - str: duong dan thu muc chua anh hoac file video
        """
        self.source = source
        self._cap = None
        self._files = []
        self._idx = 0
        self.is_live = False

        if isinstance(source, int):
            self._cap = cv2.VideoCapture(source)
            if self._cap.isOpened():
                self.is_live = True
            else:
                self._cap = None
                raise RuntimeError(f"Khong mo duoc webcam index={source}")
        elif isinstance(source, str):
            if os.path.isdir(source):
                exts = ('*.png', '*.jpg', '*.jpeg', '*.bmp')
                for e in exts:
                    self._files.extend(glob.glob(os.path.join(source, e)))
                self._files.sort()
            elif os.path.isfile(source):
                self._cap = cv2.VideoCapture(source)
                self.is_live = True
            else:
                raise FileNotFoundError(f"Khong tim thay nguon: {source}")

    def read(self):
        """Doc mot frame/anhh. Tra ve (success, image_bgr)."""
        if self._cap is not None:
            ok, frame = self._cap.read()
            return ok, frame
        if self._files:
            if self._idx < len(self._files):
                img = cv2.imread(self._files[self._idx])
                self._idx += 1
                return img is not None, img
            return False, None
        return False, None

    def get_files(self):
        """Tra ve danh sach file anh neu nguon la thu muc."""
        return self._files

    def release(self):
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


def list_camera_indices(max_idx=3):
    """Kiem tra cac chi so webcam co mo duoc."""
    available = []
    for i in range(max_idx):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available.append(i)
        cap.release()
    return available
