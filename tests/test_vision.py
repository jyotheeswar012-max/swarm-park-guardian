from vision.detector    import MockDetector
from simulation.park_map import ZONES

def test_detector_returns_list():
    det = MockDetector(detection_rate=1.0)
    result = det.detect(ZONES[0])
    assert isinstance(result, list)

def test_detection_has_required_keys():
    det = MockDetector(detection_rate=1.0)
    result = det.detect(ZONES[0])
    assert len(result) > 0
    keys = result[0].keys()
    assert "type" in keys
    assert "location" in keys
    assert "confidence" in keys

def test_zero_detection_rate():
    det = MockDetector(detection_rate=0.0)
    result = det.detect(ZONES[0])
    assert result == []
