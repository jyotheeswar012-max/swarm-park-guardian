TASK_TO_ROLE = {
    "debris":     "cleaner",
    "grass":      "trimmer",
    "water_waste":"cleaner",
    "branch":     "cleaner",
}

def classify_task(detection: dict) -> str:
    """Map a detected object type to the drone role that should handle it."""
    return TASK_TO_ROLE.get(detection.get("type", ""), "cleaner")
