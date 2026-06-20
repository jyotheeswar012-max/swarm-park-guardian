from simulation.environment import create_swarm
from core.swarm_controller  import SwarmController

def run():
    print("Running debris cleanup scenario...")
    drones     = create_swarm()
    controller = SwarmController(drones)

    # Pre-load heavy debris tasks
    for i in range(10):
        controller.add_task({
            "role": "cleaner",
            "location": (20 + i*10, 30),
            "type": "debris",
            "zone": "North Lawn"
        })

    for tick in range(100):
        controller.step()

    print(f"Completed: {len(controller.completed)} / 10 debris tasks")

if __name__ == "__main__":
    run()
