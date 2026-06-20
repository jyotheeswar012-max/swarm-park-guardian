from simulation.environment import run_simulation

def run():
    print("Running multi-zone scenario (300 ticks)...")
    log = run_simulation(ticks=300)
    final = log[-1]
    print(f"Final — Done: {final['done']} | Queue: {final['queue']}")

if __name__ == "__main__":
    run()
