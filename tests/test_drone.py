import pytest
from core.drone import Drone, DroneRole, DroneStatus

def test_drone_creation():
    d = Drone(1, DroneRole.CLEANER, (0, 0))
    assert d.battery == 100.0
    assert d.status  == DroneStatus.IDLE

def test_assign_task():
    d = Drone(1, DroneRole.CLEANER, (0, 0))
    d.assign_task({"type": "debris", "location": (10, 10)})
    assert d.status == DroneStatus.WORKING
    assert d.task is not None

def test_battery_drain():
    d = Drone(1, DroneRole.CLEANER, (0, 0))
    d.move_towards((100, 100))
    assert d.battery < 100.0

def test_recharge():
    d = Drone(1, DroneRole.CLEANER, (0, 0))
    d.battery = 15.0
    d.recharge()
    assert d.battery == 20.0

def test_battery_low():
    d = Drone(1, DroneRole.CLEANER, (0, 0))
    d.battery = 10.0
    assert d.is_battery_low() is True
