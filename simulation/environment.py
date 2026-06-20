from core.drone            import Drone, DroneRole
from core.swarm_controller import SwarmController
from vision.detector       import MockDetector
from simulation.park_map   import ZONES, HUB_POSITION

ROLE_MAP = {
    "debris":     DroneRole.CLEANER,
    "grass":      DroneRole.TRIMMER,
    "water_waste":DroneRole.CLEANER,
    "branch":     DroneRole.CLEANER,
}

def create_swarm(n=8):
    roles = [
        DroneRole.SCOUT,
        DroneRole.CLEANER,
        DroneRole.CLEANER,
        DroneRole.TRIMMER,
        DroneRole.TRIMMER,
        DroneRole.WATERER,
        DroneRole.PATROL,
        DroneRole.PATROL,
    ]
    return [Drone(i+1, roles[i % len(roles)], HUB_POSITION) for i in range(n)]

def run_simulation(ticks=200):
    drones     = create_swarm()
    controller = SwarmController(drones)
    detector   = MockDetector(detection_rate=0.4)
    log        = []

    for tick in range(ticks):
        if tick % 5 == 0:
            for zone in ZONES:
                hits = detector.detect(zone)
                for h in hits:
                    controller.add_task({
                        "role":     ROLE_MAP.get(h["type"], DroneRole.CLEANER).value,
                        "location": h["location"],
                        "type":     h["type"],
                        "zone":     h["zone"],
                    })
        controller.step()
        log.append({
            "tick":   tick,
            "drones": controller.get_status(),
            "queue":  len(controller.task_queue),
            "done":   len(controller.completed),
        })

    return log
