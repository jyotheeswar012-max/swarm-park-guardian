from core.drone            import Drone, DroneRole
from core.swarm_controller import SwarmController

def make_controller():
    drones = [
        Drone(1, DroneRole.CLEANER, (0, 0)),
        Drone(2, DroneRole.TRIMMER, (0, 0)),
    ]
    return SwarmController(drones)

def test_task_assignment():
    ctrl = make_controller()
    ctrl.add_task({"role": "cleaner", "location": (10, 10), "type": "debris"})
    ctrl.assign_tasks()
    assert ctrl.drones[0].task is not None

def test_step_runs():
    ctrl = make_controller()
    ctrl.add_task({"role": "cleaner", "location": (5, 5), "type": "debris"})
    for _ in range(10):
        ctrl.step()

def test_completed_grows():
    ctrl = make_controller()
    ctrl.add_task({"role": "cleaner", "location": (1, 1), "type": "debris"})
    for _ in range(30):
        ctrl.step()
    assert len(ctrl.completed) >= 1
