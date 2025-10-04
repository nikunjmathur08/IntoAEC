import easyocr
import numpy as np
import cv2

reader = easyocr.Reader(["en"], gpu=False)

def perform_ocr(image, min_conf=0.3):
    results = reader.readtext(image)
    labels = []
    for (bbox, text, conf) in results:
        if conf >= min_conf:
            pts = np.array(bbox).astype(int).tolist()
            x, y = int(pts[0][0]), int(pts[0][1])
            labels.append({
                "text": text,
                "confidence": float(conf),
                "position": {"x": x, "y": y},
                "bbox": pts
            })
    return labels

def auto_estimate_scale(labels):
    """Try to detect numeric values (dimensions) from OCR results to use as scale."""
    for lbl in labels:
        text = lbl["text"].replace(" ", "")
        if text.replace(".", "").isdigit():
            try:
                return float(text)
            except:
                continue
    return None
