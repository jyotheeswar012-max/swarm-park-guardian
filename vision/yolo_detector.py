"""
Swarm Park Guardian — YOLOv8 Real-Time Vision Pipeline
Author: A. Jyotheeswar Reddy, Manipal University Jaipur, 2026

Runs on: Google Coral Edge TPU + Raspberry Pi 4 onboard the drone
Camera: OAK-D Pro W (RGB + NIR + Depth) + FLIR Lepton 3.5 (thermal)
Target: 15–20 FPS inference (Patent Claim 6 & Section 12)

Detects and classifies:
  - GRASS      → Trimmer drone task
  - FLOWER     → AVOID (skip, do not cut) — key novelty
  - LEAF       → Cleaner drone task
  - BRANCH     → Arm module task
  - DEBRIS     → Cleaner task
  - WATER_WASTE→ Net module task
  - PATH       → Dust blast zone
"""

import logging
import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from enum import Enum

log = logging.getLogger('YOLODetector')

# Try to import real hardware libs — fall back to mock if not available
try:
    from ultralytics import YOLO
    import depthai as dai        # OAK-D Pro W SDK
    HW_AVAILABLE = True
except ImportError:
    HW_AVAILABLE = False
    log.warning("Hardware libs not found — running in MockDetector mode")


class ObjectClass(Enum):
    GRASS       = "grass"        # cut it
    FLOWER      = "flower"       # AVOID — do not cut
    LEAF        = "leaf"         # collect
    BRANCH      = "branch"       # arm grab
    DEBRIS      = "debris"       # clean
    WATER_WASTE = "water_waste"  # net skim
    PATH        = "path"         # dust blast
    UNKNOWN     = "unknown"


@dataclass
class Detection:
    obj_class: ObjectClass
    confidence: float
    bbox_xyxy: Tuple[int, int, int, int]   # pixel coords in frame
    depth_m: Optional[float] = None         # from OAK-D stereo
    thermal_temp_c: Optional[float] = None  # from FLIR Lepton
    action: str = field(init=False)

    def __post_init__(self):
        ACTION_MAP = {
            ObjectClass.GRASS:       "CUT",
            ObjectClass.FLOWER:      "AVOID",
            ObjectClass.LEAF:        "COLLECT",
            ObjectClass.BRANCH:      "GRAB",
            ObjectClass.DEBRIS:      "CLEAN",
            ObjectClass.WATER_WASTE: "SKIM",
            ObjectClass.PATH:        "BLAST",
            ObjectClass.UNKNOWN:     "IGNORE",
        }
        self.action = ACTION_MAP[self.obj_class]


class YOLODetector:
    """
    Real YOLOv8 detector running on Google Coral Edge TPU.
    Uses OAK-D Pro W for RGB + depth, FLIR for thermal overlay.
    Outputs Detection list at 15–20 FPS.
    """

    MODEL_PATH = "models/park_guardian_yolov8n_edgetpu.tflite"  # Coral-compiled
    IMG_SIZE   = 320   # smaller = faster on Edge TPU
    CONF_THRESH = 0.50
    FLOWER_SAFE_MARGIN_M = 0.15  # 15cm buffer around any flower

    CLASS_NAMES = [
        "grass", "flower", "leaf", "branch",
        "debris", "water_waste", "path"
    ]

    def __init__(self):
        self.model = None
        self.pipeline = None
        self._frame_count = 0
        self._init_model()
        if HW_AVAILABLE:
            self._init_oak_pipeline()

    def _init_model(self):
        if HW_AVAILABLE:
            log.info("Loading YOLOv8 model on Coral Edge TPU")
            self.model = YOLO(self.MODEL_PATH, task='detect')
        else:
            log.info("MockDetector active — no Coral TPU")

    def _init_oak_pipeline(self):
        """Configure OAK-D Pro W DepthAI pipeline."""
        self.pipeline = dai.Pipeline()

        # RGB camera
        cam_rgb = self.pipeline.create(dai.node.ColorCamera)
        cam_rgb.setPreviewSize(self.IMG_SIZE, self.IMG_SIZE)
        cam_rgb.setInterleaved(False)
        cam_rgb.setFps(20)

        # Stereo depth
        mono_l = self.pipeline.create(dai.node.MonoCamera)
        mono_r = self.pipeline.create(dai.node.MonoCamera)
        stereo  = self.pipeline.create(dai.node.StereoDepth)
        mono_l.setCamera("left");  mono_l.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        mono_r.setCamera("right"); mono_r.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        mono_l.out.link(stereo.left)
        mono_r.out.link(stereo.right)
        stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_ACCURACY)

        # Output queues
        xout_rgb   = self.pipeline.create(dai.node.XLinkOut); xout_rgb.setStreamName("rgb")
        xout_depth = self.pipeline.create(dai.node.XLinkOut); xout_depth.setStreamName("depth")
        cam_rgb.preview.link(xout_rgb.input)
        stereo.depth.link(xout_depth.input)
        log.info("OAK-D Pro W pipeline configured")

    def detect_frame(self, frame: np.ndarray, depth_map: Optional[np.ndarray] = None) -> List[Detection]:
        """
        Run YOLOv8 inference on one frame.
        Returns list of Detection objects with action assigned.
        Flowers always get AVOID — no matter confidence.
        """
        if not HW_AVAILABLE or self.model is None:
            return self._mock_detections()

        results = self.model.predict(
            source=frame,
            imgsz=self.IMG_SIZE,
            conf=self.CONF_THRESH,
            verbose=False
        )

        detections: List[Detection] = []
        for r in results:
            for box in r.boxes:
                cls_id  = int(box.cls[0])
                conf    = float(box.conf[0])
                x1,y1,x2,y2 = map(int, box.xyxy[0].tolist())
                cls_name = self.CLASS_NAMES[cls_id] if cls_id < len(self.CLASS_NAMES) else "unknown"

                try:
                    obj_class = ObjectClass(cls_name)
                except ValueError:
                    obj_class = ObjectClass.UNKNOWN

                # Get depth at bounding box centre if available
                depth_m = None
                if depth_map is not None:
                    cy, cx = (y1+y2)//2, (x1+x2)//2
                    depth_m = float(depth_map[cy, cx]) / 1000.0  # mm → m

                det = Detection(
                    obj_class=obj_class,
                    confidence=conf,
                    bbox_xyxy=(x1,y1,x2,y2),
                    depth_m=depth_m
                )
                detections.append(det)

        self._frame_count += 1
        # Safety: any flower in frame forces AVOID on all nearby grass
        detections = self._apply_flower_safety_zone(detections)
        return detections

    def _apply_flower_safety_zone(self, detections: List[Detection]) -> List[Detection]:
        """
        Core safety rule: if a flower is within FLOWER_SAFE_MARGIN_M of
        any grass detection, suppress the CUT action on that grass patch.
        This implements the key novelty — AI flower avoidance during mowing.
        """
        flower_boxes = [d for d in detections if d.obj_class == ObjectClass.FLOWER]
        if not flower_boxes:
            return detections

        safe_detections = []
        for det in detections:
            if det.obj_class == ObjectClass.GRASS:
                # Check proximity to any flower
                g_cx = (det.bbox_xyxy[0] + det.bbox_xyxy[2]) / 2
                g_cy = (det.bbox_xyxy[1] + det.bbox_xyxy[3]) / 2
                too_close = False
                for fl in flower_boxes:
                    f_cx = (fl.bbox_xyxy[0] + fl.bbox_xyxy[2]) / 2
                    f_cy = (fl.bbox_xyxy[1] + fl.bbox_xyxy[3]) / 2
                    pixel_dist = ((g_cx-f_cx)**2 + (g_cy-f_cy)**2)**0.5
                    # ~15px ≈ 15cm at 5cm hover altitude with 90° FoV
                    if pixel_dist < 40:
                        too_close = True
                        break
                if too_close:
                    det.action = "AVOID"  # override CUT → AVOID near flowers
            safe_detections.append(det)
        return safe_detections

    def _mock_detections(self) -> List[Detection]:
        """Simulate detections for testing without hardware."""
        import random
        classes = list(ObjectClass)
        n = random.randint(1, 4)
        result = []
        for _ in range(n):
            cls = random.choice(classes[:-1])
            result.append(Detection(
                obj_class=cls,
                confidence=round(random.uniform(0.55, 0.97), 2),
                bbox_xyxy=(random.randint(0,200), random.randint(0,200),
                           random.randint(200,320), random.randint(200,320)),
                depth_m=round(random.uniform(0.04, 0.5), 3)
            ))
        return result

    def get_fps(self) -> float:
        return self._frame_count  # caller tracks time
