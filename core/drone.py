import numpy as np
from enum import Enum

class DroneRole(Enum):
    SCOUT    = "scout"
    CLEANER  = "cleaner"
    TRIMMER  = "trimmer"
    WATERER  = "waterer"
    PATROL   = "patrol"

class DroneStatus(Enum):
    IDLE       = "idle"
    PATROLLING = "patrolling"
    WORKING    = "working"
    RETURNING  = "returning"
    CHARGING   = "charging"

class Drone:
    def __init__(self, drone_id: int, role: DroneRole, start_pos: tuple):
        self.drone_id   = drone_id
        self.role       = role
        self.position   = np.array(start_pos, dtype=float)
        self.battery    = 100.0
        self.status     = DroneStatus.IDLE
        self.task       = None
        self.path       = []
        self.speed      = 2.0
        self.drain_rate = 0.05

    def assign_task(self, task: dict):
        self.task   = task
        self.status = DroneStatus.WORKING

    def move_towards(self, target: tuple):
        target    = np.array(target, dtype=float)
        direction = target - self.position
        dist      = np.linalg.norm(direction)
        if dist < self.speed:
            self.position = target
        else:
            self.position += (direction / dist) * self.speed
        self.battery -= self.drain_rate

    def is_battery_low(self) -> bool:
        return self.battery < 20.0

    def recharge(self):
        self.battery  = min(100.0, self.battery + 5.0)
        self.status   = DroneStatus.CHARGING

    def to_dict(self) -> dict:
        return {
            "id":       self.drone_id,
            "role":     self.role.value,
            "status":   self.status.value,
            "battery":  round(self.battery, 1),
            "position": self.position.tolist(),
            "task":     self.task,
        }
