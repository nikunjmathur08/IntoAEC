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

def main(image_path, pth_file, json_file, min_conf=0.4, pixels_per_unit=None, scale_unit="meters"):
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

    # Scale: use provided or auto-estimate
    if pixels_per_unit is not None:
        px_per_unit = pixels_per_unit
        scale_source = "user_provided"
        print(f"✅ Using user-provided scale: {px_per_unit:.2f} pixels per {scale_unit}")
    else:
        auto_scale = auto_estimate_scale(labels)
        px_per_unit = auto_scale if auto_scale else None
        scale_source = "ocr_estimated" if auto_scale else "none"
        if auto_scale:
            print(f"⚠️  Using OCR-estimated scale: {px_per_unit:.2f}")
        else:
            print("⚠️  No scale available - measurements will be in pixels only")

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
        "scale_px_per_unit": px_per_unit,
        "scale_unit": scale_unit,
        "scale_source": scale_source
    }

    # Save
    save_pth(results, pth_file)
    export_json_from_pth(pth_file, json_file)

    print(f"✅ Saved results to {pth_file} and {json_file}")
    if px_per_unit:
        print(f"   Scale: {px_per_unit:.2f} pixels per {scale_unit} ({scale_source})")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python main.py <image_path> <output.pth> <output.json> [min_conf] [pixels_per_unit] [scale_unit]")
        print("Example: python main.py floor.jpg output.pth output.json 0.4 10.5 meters")
    else:
        min_conf = float(sys.argv[4]) if len(sys.argv) > 4 else 0.4
        pixels_per_unit = float(sys.argv[5]) if len(sys.argv) > 5 else None
        scale_unit = sys.argv[6] if len(sys.argv) > 6 else "meters"
        main(sys.argv[1], sys.argv[2], sys.argv[3], min_conf, pixels_per_unit, scale_unit)
