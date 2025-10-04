import sys
import cv2
import numpy as np
import warnings
import torch

from ocr_utils import perform_ocr, auto_estimate_scale
from line_utils import detect_contours, calculate_area
from export_utils import save_pth, export_json_from_pth
from fuzzy_wuzzy import correct_labels

warnings.filterwarnings("ignore", message=".*pin_memory.*")

def main(image_path, pth_file, json_file, min_conf=0.4):
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: could not load image {image_path}")
        return

    # OCR
    labels = perform_ocr(image, min_conf=min_conf)
    labels = correct_labels(labels)

    # Contours
    contours = detect_contours(image)

    # Scale estimation
    auto_scale = auto_estimate_scale(labels)
    px_per_unit = auto_scale if auto_scale else None

    # Areas
    areas = []
    for i, cnt in enumerate(contours):
        area_units = calculate_area(cnt, px_per_unit)
        areas.append({
            "contour_id": i,
            "area_pixels": float(cv2.contourArea(cnt)),
            "area_units": area_units
        })

    results = {
        "labels": labels,
        "contours": len(contours),
        "areas": areas,
        "scale_px_per_unit": px_per_unit
    }

    # Save
    save_pth(results, pth_file)
    export_json_from_pth(pth_file, json_file)

    print(f"✅ Saved results to {pth_file} and {json_file}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python main.py <image_path> <output.pth> <output.json>")
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
