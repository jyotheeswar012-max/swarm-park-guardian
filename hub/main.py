"""
Swarm Park Guardian — Main Hub Entry Point
Author: A. Jyotheeswar Reddy, Manipal University Jaipur, 2026

Run this on the Main Hub computer to start the nightly cycle.
Usage: python hub/main.py
"""

import asyncio
import logging
from hub.coordinator import SwarmCoordinator, ParkZone
from hub.sub_hub_controller import SubHubController

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(name)-16s %(levelname)-8s %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger('MainHub')


# --- Define your park layout here ---
# Coordinates in metres from main hub position
PARK_ZONES = [
    ParkZone("Z01", "North Lawn",    centre_x=  0, centre_y= 40, zone_type="lawn",   priority=1),
    ParkZone("Z02", "East Garden",   centre_x= 60, centre_y= 30, zone_type="garden", priority=1),
    ParkZone("Z03", "Central Plaza", centre_x=  0, centre_y=  0, zone_type="path",   priority=2),
    ParkZone("Z04", "South Lawn",    centre_x=  0, centre_y=-40, zone_type="lawn",   priority=1),
    ParkZone("Z05", "Pond Area",     centre_x= 60, centre_y=-30, zone_type="water",  priority=2),
    ParkZone("Z06", "West Path",     centre_x=-50, centre_y=  0, zone_type="path",   priority=3),
]

# --- Sub-hubs ---
SUB_HUB_IDS = [1, 2, 3, 4]   # 4 sub-hubs at corners of park


async def main():
    log.info("="*60)
    log.info(" SWARM PARK GUARDIAN — MAIN HUB BOOT")
    log.info(" Inventor: A. Jyotheeswar Reddy, MUJ 2026")
    log.info("="*60)

    # Initialise sub-hubs
    sub_hubs = [SubHubController(hub_id=i) for i in SUB_HUB_IDS]
    log.info(f"Initialised {len(sub_hubs)} sub-hubs")

    # Emerge all sub-hubs
    log.info("Emerging sub-hubs from underground...")
    for sh in sub_hubs:
        sh.emerge()

    # Initialise swarm coordinator
    coordinator = SwarmCoordinator(park_zones=PARK_ZONES)

    # Register drones (in real system: drones connect via MAVLink/UDP)
    for drone_id in range(1, 8):   # 7 drones
        coordinator.register_drone(drone_id, start_x=0, start_y=0)
    log.info(f"Registered {len(coordinator.drones)} drones")

    # Run nightly maintenance cycle
    await coordinator.run_nightly_cycle()

    # Retract all sub-hubs before dawn
    log.info("Retracting sub-hubs underground before 7 AM...")
    for sh in sub_hubs:
        sh.retract()

    log.info("All sub-hubs hidden. Park ready for visitors.")


if __name__ == "__main__":
    asyncio.run(main())
