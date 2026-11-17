"""
calibrate.py
Chuyen doi toa do pixel -> mm bang ma tran homography tu 4 diem moc.

Gia dinh: mat phang vat nam ngang, camera nhin thang xuong.
Vi chua co ban thi nghiem that, dung kich thuoc gia dinh 300x200 mm
voi 4 goc vung chup lam moc.
"""

import numpy as np
import cv2


class PixelToWorldTransformer:
    """Anh xa pixel (u,v) -> he toa do the gioi (x,y) mm bang homography."""

    def __init__(self, image_points_px, world_points_mm):
        """
        image_points_px: list 4 diem [[u,v], ...] theo thu tu tuong ung
        world_points_mm: list 4 diem [[x,y], ...] theo thu tu tuong ung
        """
        self.image_points = np.array(image_points_px, dtype=np.float32)
        self.world_points = np.array(world_points_mm, dtype=np.float32)
        assert len(self.image_points) >= 4
        assert len(self.world_points) == len(self.image_points)

        self.H, self.status = cv2.findHomography(
            self.image_points, self.world_points, method=cv2.RANSAC
        )
        if self.H is None:
            raise ValueError("Khong tinh duoc ma tran homography")

    def transform(self, points_px):
        """
        points_px: ndarray Nx2 [[u,v], ...]
        Tra ve: ndarray Nx2 [[x_mm, y_mm], ...]
        """
        pts = np.asarray(points_px, dtype=np.float32).reshape(-1, 1, 2)
        world = cv2.perspectiveTransform(pts, self.H)
        return world.reshape(-1, 2)

    def get_reprojection_error(self):
        """Tinh sai so tai cac diem moc (mm)."""
        pred = self.transform(self.image_points)
        err = np.linalg.norm(pred - self.world_points, axis=1)
        return {
            'errors_mm': err.tolist(),
            'mean_mm': float(np.mean(err)),
            'max_mm': float(np.max(err)),
        }


def default_transformer():
    """Transformer mac dinh gia dinh vung 300x200 mm."""
    return PixelToWorldTransformer(
        image_points_px=[[100, 100], [500, 100], [500, 400], [100, 400]],
        world_points_mm=[[0, 0], [300, 0], [300, 200], [0, 200]]
    )
