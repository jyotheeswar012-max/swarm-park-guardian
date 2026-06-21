"""
Swarm Park Guardian — Central Hub Swarm Coordinator
Author: A. Jyotheeswar Reddy, Manipal University Jaipur, 2026

Runs on: Main Hub (Raspberry Pi 5 / Intel NUC)
Implements: Greedy nearest-neighbour task allocation (Patent Claim 7)
Manages: All drones, all sub-hubs, nightly operational sequence

Patent Claims 1(e), 7 — nearest-drone task assignment.
"""

import asyncio
import logging
import math
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum

log = logging.getLogger('Coordinator')


class TaskType(Enum):
    SCOUT       = "scout"        # 1:00 AM — zone scanning
    DUST_CLEAR  = "dust_clear"   # 2:00 AM
    LEAF_COLLECT= "leaf_collect" # 2:30 AM
    GRASS_CUT   = "grass_cut"    # 3:00 AM
    DEBRIS_GRAB = "debris_grab"  # 4:00 AM
    WATER_SKIM  = "water_skim"   # 4:30 AM
    IRRIGATE    = "irrigate"     # 5:00 AM
    RETURN_HUB  = "return_hub"   # 6:00 AM


class DroneStatus(Enum):
    IDLE        = "idle"
    ASSIGNED    = "assigned"
    EN_ROUTE    = "en_route"
    WORKING     = "working"
    RETURNING   = "returning"
    CHARGING    = "charging"
    FAULT       = "fault"


@dataclass
class ParkZone:
    zone_id: str
    name: str
    centre_x: float   # metres east of main hub
    centre_y: float   # metres north of main hub
    zone_type: str    # 'lawn', 'path', 'garden', 'water'
    priority: int = 1 # 1=high, 3=low
    last_cleaned: float = 0.0


@dataclass
class MaintenanceTask:
    task_id: str
    task_type: TaskType
    zone: ParkZone
    created_at: float = field(default_factory=time.time)
    assigned_drone_id: Optional[int] = None
    completed: bool = False
    required_tool: Optional[str] = None


@dataclass
class DroneAgent:
    drone_id: int
    pos_x: float = 0.0     # metres east of hub
    pos_y: float = 0.0     # metres north of hub
    battery_pct: float = 100.0
    status: DroneStatus = DroneStatus.IDLE
    current_task: Optional[str] = None
    current_tool: str = "none"
    last_heartbeat: float = field(default_factory=time.time)


class SwarmCoordinator:
    """
    Central brain of the system.
    Runs the nightly 1AM–7AM autonomous maintenance cycle.
    Assigns tasks using greedy nearest-neighbour (Patent Claim 7).
    Sends heartbeats to all drones every second.
    """

    # Nightly schedule — aligned with patent Section 5 operational sequence
    NIGHTLY_SCHEDULE = [
        ("01:00", TaskType.SCOUT),
        ("02:00", TaskType.DUST_CLEAR),
        ("02:30", TaskType.LEAF_COLLECT),
        ("03:00", TaskType.GRASS_CUT),
        ("04:00", TaskType.DEBRIS_GRAB),
        ("04:30", TaskType.WATER_SKIM),
        ("05:00", TaskType.IRRIGATE),
        ("06:00", TaskType.RETURN_HUB),
    ]

    TOOL_FOR_TASK = {
        TaskType.SCOUT:        "none",
        TaskType.DUST_CLEAR:   "none",          # uses permanent dust blaster
        TaskType.LEAF_COLLECT: "leaf_basket",
        TaskType.GRASS_CUT:    "blade",
        TaskType.DEBRIS_GRAB:  "arm",
        TaskType.WATER_SKIM:   "net",
        TaskType.IRRIGATE:     "none",          # uses permanent irrigation port
        TaskType.RETURN_HUB:   "none",
    }

    def __init__(self, park_zones: List[ParkZone]):
        self.zones = {z.zone_id: z for z in park_zones}
        self.drones: Dict[int, DroneAgent] = {}
        self.task_queue: List[MaintenanceTask] = []
        self.completed_tasks: List[MaintenanceTask] = []
        self._task_counter = 0
        self._running = False

    # ------------------------------------------------------------------
    # DRONE REGISTRY
    # ------------------------------------------------------------------
    def register_drone(self, drone_id: int, start_x: float = 0, start_y: float = 0):
        self.drones[drone_id] = DroneAgent(drone_id=drone_id, pos_x=start_x, pos_y=start_y)
        log.info(f"Registered Drone {drone_id}")

    def update_drone_telemetry(self, drone_id: int, pos_x: float, pos_y: float,
                                battery_pct: float, status: DroneStatus):
        if drone_id in self.drones:
            d = self.drones[drone_id]
            d.pos_x = pos_x
            d.pos_y = pos_y
            d.battery_pct = battery_pct
            d.status = status
            d.last_heartbeat = time.time()

    # ------------------------------------------------------------------
    # TASK GENERATION — scout results trigger task creation
    # ------------------------------------------------------------------
    def add_task(self, task_type: TaskType, zone_id: str) -> MaintenanceTask:
        zone = self.zones[zone_id]
        self._task_counter += 1
        task = MaintenanceTask(
            task_id=f"T{self._task_counter:04d}",
            task_type=task_type,
            zone=zone,
            required_tool=self.TOOL_FOR_TASK[task_type]
        )
        self.task_queue.append(task)
        log.info(f"Task {task.task_id} queued: {task_type.value} @ {zone.name}")
        return task

    # ------------------------------------------------------------------
    # GREEDY NEAREST-NEIGHBOUR ASSIGNMENT — Patent Claim 7
    # ------------------------------------------------------------------
    def assign_tasks(self) -> List[Tuple[int, MaintenanceTask]]:
        """
        For each unassigned task, find the nearest idle drone
        using Euclidean distance to task zone centre.
        Time complexity: O(tasks × drones) — acceptable for <20 drones.
        """
        assignments = []
        unassigned = [t for t in self.task_queue if not t.assigned_drone_id and not t.completed]
        available_drones = [
            d for d in self.drones.values()
            if d.status == DroneStatus.IDLE and d.battery_pct > 25.0
        ]

        used_drone_ids = set()

        for task in sorted(unassigned, key=lambda t: t.zone.priority):
            best_drone = None
            best_dist  = float('inf')

            for drone in available_drones:
                if drone.drone_id in used_drone_ids:
                    continue
                dist = math.sqrt(
                    (drone.pos_x - task.zone.centre_x) ** 2 +
                    (drone.pos_y - task.zone.centre_y) ** 2
                )
                if dist < best_dist:
                    best_dist  = dist
                    best_drone = drone

            if best_drone:
                task.assigned_drone_id = best_drone.drone_id
                best_drone.status = DroneStatus.ASSIGNED
                best_drone.current_task = task.task_id
                used_drone_ids.add(best_drone.drone_id)
                assignments.append((best_drone.drone_id, task))
                log.info(
                    f"Assigned {task.task_id} ({task.task_type.value}) "
                    f"→ Drone {best_drone.drone_id} [dist={best_dist:.1f}m]"
                )

        return assignments

    def mark_task_complete(self, task_id: str):
        for task in self.task_queue:
            if task.task_id == task_id:
                task.completed = True
                task.zone.last_cleaned = time.time()
                self.completed_tasks.append(task)
                self.task_queue.remove(task)
                if task.assigned_drone_id and task.assigned_drone_id in self.drones:
                    self.drones[task.assigned_drone_id].status = DroneStatus.IDLE
                    self.drones[task.assigned_drone_id].current_task = None
                log.info(f"Task {task_id} marked complete")
                break

    # ------------------------------------------------------------------
    # HEARTBEAT — sent to all drones every second
    # ------------------------------------------------------------------
    async def heartbeat_loop(self):
        """Broadcast hub heartbeat. Drones lost-comm if no beat for 5s."""
        while self._running:
            for drone in self.drones.values():
                # In real deployment: send UDP packet to drone's IP
                drone.last_heartbeat = time.time()
            await asyncio.sleep(1)

    # ------------------------------------------------------------------
    # NIGHTLY CYCLE RUNNER
    # ------------------------------------------------------------------
    async def run_nightly_cycle(self):
        """Execute the full 1AM–7AM autonomous maintenance sequence."""
        self._running = True
        log.info("=" * 60)
        log.info("NIGHTLY MAINTENANCE CYCLE STARTED")
        log.info("=" * 60)
        asyncio.create_task(self.heartbeat_loop())

        for phase_time, task_type in self.NIGHTLY_SCHEDULE:
            log.info(f"[{phase_time}] Phase: {task_type.value.upper()}")

            if task_type == TaskType.SCOUT:
                # Scout phase: assign all zones to scout drone
                for zone_id in self.zones:
                    self.add_task(TaskType.SCOUT, zone_id)
            elif task_type == TaskType.RETURN_HUB:
                log.info("All drones returning to sub-hubs for recharge")
                for drone in self.drones.values():
                    drone.status = DroneStatus.RETURNING
            else:
                # Add task for each relevant zone
                for zone_id, zone in self.zones.items():
                    if self._task_relevant_for_zone(task_type, zone):
                        self.add_task(task_type, zone_id)

            assignments = self.assign_tasks()
            log.info(f"  {len(assignments)} tasks assigned to drones")

            # Wait for phase completion (in real system: await drone callbacks)
            await asyncio.sleep(2)

        self._running = False
        log.info("NIGHTLY CYCLE COMPLETE — all drones at sub-hubs")
        self._print_summary()

    def _task_relevant_for_zone(self, task_type: TaskType, zone: ParkZone) -> bool:
        ZONE_TASK_MAP = {
            TaskType.DUST_CLEAR:   ['path', 'lawn'],
            TaskType.LEAF_COLLECT: ['lawn', 'path', 'garden'],
            TaskType.GRASS_CUT:    ['lawn', 'garden'],
            TaskType.DEBRIS_GRAB:  ['lawn', 'garden', 'path'],
            TaskType.WATER_SKIM:   ['water'],
            TaskType.IRRIGATE:     ['garden', 'lawn'],
        }
        allowed = ZONE_TASK_MAP.get(task_type, [])
        return zone.zone_type in allowed

    def _print_summary(self):
        log.info("--- SESSION SUMMARY ---")
        log.info(f"Total tasks completed: {len(self.completed_tasks)}")
        for t in self.completed_tasks:
            log.info(f"  {t.task_id} | {t.task_type.value:<14} | Zone: {t.zone.name}")
