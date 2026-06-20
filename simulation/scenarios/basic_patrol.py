from simulation.environment import run_simulation

def run():
    print("Running basic patrol scenario...")
    log = run_simulation(ticks=100)
    final = log[-1]
    print(f"Ticks: {final['tick']} | Done: {final['done']} | Queue: {final['queue']}")
    for d in final["drones"]:
        print(f"  Drone {d['id']} ({d['role']}) — {d['status']} — Battery: {d['battery']}%")

if __name__ == "__main__":
    run()
