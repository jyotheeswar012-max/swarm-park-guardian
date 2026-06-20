# System Architecture

## Overview
The Swarm Park Guardian consists of 4 main layers:

1. **Vision Layer** — YOLOv8-based detection of park issues per zone
2. **Coordination Layer** — PSO-based task assignment via SwarmController
3. **Execution Layer** — Individual drone agents with roles and battery management
4. **Monitoring Layer** — Real-time Streamlit dashboard with SQLite logging

## Data Flow
1. Scout drones scan zones every 5 ticks
2. Detections feed into the task queue
3. SwarmController assigns tasks by role matching
4. Drones navigate via PSO waypoints
5. Completed tasks are logged to SQLite
6. Dashboard polls state every tick

## Scalability
- Swap MockDetector → YOLODetector for real camera feeds
- Swap Pygame sim → ROS 2 + Gazebo for real drone hardware
- Swap SQLite → PostgreSQL for production logging

## Component Diagram
```
[Park Zones]
     |
     v
[MockDetector / YOLODetector]  <-- vision/detector.py
     |
     v
[Task Queue]  <-- core/swarm_controller.py
     |
     v
[Drone Agents]  <-- core/drone.py
     |
     v
[Central Hub + SQLite Log]  <-- core/hub.py
     |
     v
[Streamlit Dashboard]  <-- dashboard/app.py
```
