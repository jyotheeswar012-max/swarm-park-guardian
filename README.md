<div align="center">

# 🌿 Swarm Park Guardian

### Autonomous Multi-Drone Park Maintenance System

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?logo=streamlit)](https://streamlit.io)
[![YOLOv8](https://img.shields.io/badge/Vision-YOLOv8-purple)](https://ultralytics.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Built by Jyotheeswar](https://img.shields.io/badge/Built%20by-Jyotheeswar%20Reddy-orange)](https://github.com/jyotheeswar012-max)

> A fully autonomous swarm of AI-powered drones that patrol, detect waste, trim grass, water plants, and clean water bodies in a park — coordinated by a central hub with real-time dashboard monitoring.

**[Live Demo →](#)** | **[Architecture Docs →](docs/architecture.md)** | **[Patent Concept →](docs/patent_concept.md)**

</div>

---

## 🎯 What This Does

| Drone Role | Task |
|---|---|
| 🔍 Scout | Patrol zones, detect debris/grass/waste using YOLO vision |
| 🧹 Cleaner | Collect debris, branches, and surface waste |
| ✂️ Trimmer | Trim overgrown grass zones |
| 💧 Waterer | Irrigate garden and lawn zones |
| 🛡️ Patrol | Night-time perimeter monitoring |

---

## 🏗️ Architecture

```
Park Zones → Scout Drones (YOLOv8 detection)
                    ↓
            Swarm Controller (PSO task assignment)
                    ↓
        Cleaner / Trimmer / Waterer Drones
                    ↓
             Central Hub (collect, log, recharge)
                    ↓
          Streamlit Dashboard (real-time monitoring)
```

---

## 🚀 Quick Start

```bash
git clone https://github.com/jyotheeswar012-max/swarm-park-guardian
cd swarm-park-guardian
pip install -r requirements.txt
streamlit run dashboard/app.py
```

---

## 🧪 Run Tests

```bash
pytest tests/ -v
```

---

## 🛠️ Tech Stack

- **Python 3.11** — core simulation logic
- **YOLOv8** — object detection (debris, grass, water waste)
- **PSO Algorithm** — path planning and task assignment
- **Pygame** — 2D simulation visualizer
- **Streamlit + Plotly** — live mission dashboard
- **SQLite** — mission log storage
- **Docker** — containerized deployment

---

## 🔬 Research & Patent

This project is based on an original invention concept for a **swarm-robotics park maintenance system**. See [docs/patent_concept.md](docs/patent_concept.md) for the full technical invention statement.

---

## 👨‍💻 Built by

**Jyotheeswar Reddy** — [GitHub](https://github.com/jyotheeswar012-max) · [LinkedIn](https://linkedin.com/in/a-jyotheeswar-reddy)

> 100% designed, developed, and deployed by me.
