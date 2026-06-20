# Demo Walkthrough

## Step 1 — Run the dashboard
```bash
streamlit run dashboard/app.py
```

## Step 2 — Configure simulation
- Use the sidebar to set ticks (50–500)
- Click "🚀 Run Simulation"

## Step 3 — Interpret results
- **Task Completion chart** — shows how quickly drones clear the queue
- **Battery chart** — shows drone health at end of mission
- **Park map** — shows final drone positions and zones
- **Status table** — shows every drone role, status and battery

## Step 4 — Run the Pygame visualizer
```bash
python simulation/visualizer.py
```
Watch drones move in real-time across the park map.

## Step 5 — Run unit tests
```bash
pytest tests/ -v
```

## What to show recruiters
1. Live Streamlit dashboard with dynamic charts
2. Pygame animated simulation
3. Patent concept doc in docs/
4. Clean modular code structure
5. 11 passing unit tests
