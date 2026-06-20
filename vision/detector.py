import random

TASK_TYPES = ["debris", "grass", "water_waste", "branch"]

class MockDetector:
    """
    Simulates YOLO detection output for park zones.
    In production, replace with: model = YOLO('yolov8n.pt')
    """
    def __init__(self, detection_rate=0.3):
        self.detection_rate = detection_rate

    def detect(self, zone: dict) -> list:
        detections = []
        if random.random() < self.detection_rate:
            task_type = random.choice(TASK_TYPES)
            x = zone["x"] + random.uniform(0, zone["width"])
            y = zone["y"] + random.uniform(0, zone["height"])
            detections.append({
                "type":       task_type,
                "confidence": round(random.uniform(0.7, 0.99), 2),
                "location":   (round(x, 1), round(y, 1)),
                "zone":       zone["name"],
            })
        return detections

class YOLODetector:
    """Production-ready YOLO detector — swap in when real hardware is ready."""
    def __init__(self, model_path="yolov8n.pt"):
        from ultralytics import YOLO
        self.model = YOLO(model_path)

    def detect(self, frame) -> list:
        results = self.model(frame)
        detections = []
        for r in results:
            for box in r.boxes:
                detections.append({
                    "type":       self.model.names[int(box.cls)],
                    "confidence": float(box.conf),
                    "location":   box.xywh[0][:2].tolist(),
                })
        return detections
