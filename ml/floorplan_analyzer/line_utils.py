import cv2
import numpy as np

def detect_contours(image_bgr):
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    valid = []
    for cnt in contours:
        if len(cnt) >= 3 and cv2.contourArea(cnt) > 50:  # filter tiny noise
            valid.append(cnt)
    return valid

def calculate_area(contour, px_per_unit=None):
    pixel_area = cv2.contourArea(contour.astype(np.float32))
    if px_per_unit:
        return round(pixel_area / (px_per_unit ** 2), 2)
    return None
