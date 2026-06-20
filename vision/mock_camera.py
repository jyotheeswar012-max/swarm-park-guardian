import random
from simulation.park_map import ZONES

def get_mock_frame(zone_name: str) -> dict:
    """Returns a simulated camera frame dict for a given zone."""
    zone = next((z for z in ZONES if z["name"] == zone_name), ZONES[0])
    return {
        "zone":      zone["name"],
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "pixels":    [[random.randint(0, 255) for _ in range(3)] for _ in range(10)],
    }
