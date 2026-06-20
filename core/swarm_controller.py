from core.drone import Drone, DroneRole, DroneStatus

class SwarmController:
    def __init__(self, drones: list):
        self.drones      = drones
        self.task_queue  = []
        self.completed   = []
        self.tick        = 0

    def add_task(self, task: dict):
        self.task_queue.append(task)

    def _find_available_drone(self, role: DroneRole):
        for d in self.drones:
            if d.role == role and d.status == DroneStatus.IDLE:
                return d
        return None

    def assign_tasks(self):
        unassigned = []
        for task in self.task_queue:
            role  = DroneRole(task["role"])
            drone = self._find_available_drone(role)
            if drone:
                drone.assign_task(task)
            else:
                unassigned.append(task)
        self.task_queue = unassigned

    def step(self):
        self.tick += 1
        self.assign_tasks()
        for drone in self.drones:
            if drone.is_battery_low() and drone.status != DroneStatus.CHARGING:
                drone.status = DroneStatus.RETURNING
            if drone.status == DroneStatus.CHARGING:
                drone.recharge()
                if drone.battery >= 95:
                    drone.status = DroneStatus.IDLE
            elif drone.status == DroneStatus.WORKING and drone.task:
                target = drone.task.get("location", (0, 0))
                drone.move_towards(target)
                dist = ((drone.position[0] - target[0])**2 +
                        (drone.position[1] - target[1])**2) ** 0.5
                if dist < 2.0:
                    self.completed.append(drone.task)
                    drone.task   = None
                    drone.status = DroneStatus.IDLE
            elif drone.status == DroneStatus.RETURNING:
                drone.move_towards((0, 0))
                dist = (drone.position[0]**2 + drone.position[1]**2) ** 0.5
                if dist < 2.0:
                    drone.status = DroneStatus.CHARGING

    def get_status(self) -> list:
        return [d.to_dict() for d in self.drones]
