import torch
import json

def save_pth(results, filename):
    torch.save(results, filename)

def load_pth(filename):
    return torch.load(filename, weights_only=False)

def export_json_from_pth(pth_file, json_file):
    results = load_pth(pth_file)
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
