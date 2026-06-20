<div align="center">

# 🌿 Swarm Park Guardian

### Autonomous Multi-Drone Park Maintenance System

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?logo=streamlit)](https://streamlit.io)
[![YOLOv8](https://img.shields.io/badge/Vision-YOLOv8-purple)](https://ultralytics.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Invention](https://img.shields.io/badge/Original-Invention-gold)](docs/patent_concept.md)
[![Built by Jyotheeswar](https://img.shields.io/badge/Built%20by-A.%20Jyotheeswar%20Reddy-orange)](https://github.com/jyotheeswar012-max)

> **My original invention.** A fleet of AI-powered drones that autonomously patrol, detect waste, trim grass, water plants, and clean water bodies in a park — coordinated by a central hub. Every season. Zero human intervention.

**[🌍 Live Website →](https://jyotheeswar012-max.github.io/swarm-park-guardian)** &nbsp;|
**[📊 Dashboard →](#)** &nbsp;|
**[📄 Patent Concept →](docs/patent_concept.md)**

</div>

---

## 💡 The Idea

I came up with this idea as a solution to one real problem: **parks need constant maintenance but human labour is expensive, inconsistent, and unavailable at night.**

My solution: a swarm of specialised drones that work as a single unit — scouting, cleaning, trimming, watering, and patrolling — all coordinated by a central hub that handles recharging and waste collection through a pipe system.

---

## 🤖 Drone Fleet

| Drone | Role |
|---|---|
| 🔍 Scout | Patrols all zones, detects debris/grass/waste via YOLOv8 |
| 🧹 Cleaner | Collects dust, branches, litter — pipes waste to hub |
| ✂️ Trimmer | Detects and trims overgrown grass with precision |
| 💧 Waterer | Irrigates gardens, cleans water body surfaces |
| 🛡️ Patrol | Night-time perimeter + LED light-show formation |

---

## 🏗️ System Architecture

```
Park Zones
    ↓
Scout Drones (YOLOv8 detection)
    ↓
Central Hub (PSO task assignment)
    ↓
Cleaner / Trimmer / Waterer Drones
    ↓
Hub (waste collection via pipes + solar recharge)
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

## 🔬 Research & Patent

This is an original invention. See [docs/patent_concept.md](docs/patent_concept.md) for the full technical invention statement and patent claims.

---

## 👨‍💻 Inventor

**A. Jyotheeswar Reddy** — [GitHub](https://github.com/jyotheeswar012-max) · [LinkedIn](https://linkedin.com/in/a-jyotheeswar-reddy) · Mumbai, India 🇮🇳

> 100% my original idea, designed and developed by me.
