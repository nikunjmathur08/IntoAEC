from rapidfuzz import fuzz, process

# Extended dictionary of common floor plan labels
KNOWN_LABELS = [
    "Living Room", "Bedroom", "Bedroom 1", "Bedroom 2", "Bedroom 3", "Bedroom 4",
    "Bathroom", "Bathroom 1", "Bathroom 2", "Kitchen", "Dining Room", "Hallway",
    "Closet", "Walk-in Closet", "Entry", "Porch", "Front Porch", "Balcony", "Garage",
    "Storage", "Utilities", "Sitting Room", "Office", "Study", "Pantry", "Laundry",
    "Stairs", "Lobby", "Corridor", "Master Bedroom", "Guest Room", "Playroom"
]

def correct_labels(labels, threshold=75):
    """
    Correct OCR labels using fuzzy matching against known room names.
    Adds `corrected_text` and `fuzzy_score` to each label.
    """
    corrected = []
    for lbl in labels:
        text = lbl.get("text", "").strip()
        if not text:
            lbl["corrected_text"] = text
            lbl["fuzzy_score"] = 0
            corrected.append(lbl)
            continue

        best_match, score, _ = process.extractOne(
            text, KNOWN_LABELS, scorer=fuzz.ratio
        )
        if score >= threshold:
            lbl["corrected_text"] = best_match
            lbl["fuzzy_score"] = score
        else:
            lbl["corrected_text"] = text
            lbl["fuzzy_score"] = score
        corrected.append(lbl)
    return corrected
