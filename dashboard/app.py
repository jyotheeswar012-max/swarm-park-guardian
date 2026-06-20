import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from simulation.environment import run_simulation
from simulation.park_map    import ZONES, HUB_POSITION

st.set_page_config(
    page_title="🌿 Swarm Park Guardian",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
<style>
body { background: #0d1117; color: #e6edf3; }
.block-container { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)

st.title("🌿 Swarm Park Guardian — Mission Dashboard")
st.caption("Autonomous multi-drone park maintenance simulation — Built by Jyotheeswar Reddy")

st.sidebar.header("⚙️ Simulation Config")
ticks   = st.sidebar.slider("Simulation Ticks", 50, 500, 200)
run_btn = st.sidebar.button("🚀 Run Simulation")

if run_btn or "sim_log" not in st.session_state:
    with st.spinner("Running drone simulation..."):
        st.session_state.sim_log = run_simulation(ticks)

log  = st.session_state.sim_log
last = log[-1]

col1, col2, col3, col4 = st.columns(4)
col1.metric("🤖 Drones Deployed", len(last["drones"]))
col2.metric("✅ Tasks Completed", last["done"])
col3.metric("📋 Queue Remaining", last["queue"])
col4.metric("🔄 Ticks Simulated", ticks)

st.divider()

st.subheader("📈 Task Completion Over Time")
df_progress = pd.DataFrame([{"tick": r["tick"], "completed": r["done"], "queued": r["queue"]} for r in log])
fig = px.line(df_progress, x="tick", y=["completed", "queued"],
              labels={"value": "Tasks", "variable": "Series"},
              color_discrete_map={"completed": "#2ea043", "queued": "#e3b341"},
              template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

st.subheader("🔋 Final Drone Battery Status")
df_drones = pd.DataFrame(last["drones"])
fig2 = px.bar(df_drones, x="id", y="battery", color="status",
              labels={"id": "Drone ID", "battery": "Battery %"},
              template="plotly_dark",
              color_discrete_map={
                  "idle": "#58a6ff", "working": "#2ea043",
                  "charging": "#e3b341", "returning": "#f85149",
                  "patrolling": "#bc8cff"
              })
st.plotly_chart(fig2, use_container_width=True)

st.subheader("🗺️ Park Zone Map")
fig3 = go.Figure()
zone_colors = {"grass": "#2ea043", "garden": "#3fb950", "paved": "#8b949e", "water": "#58a6ff"}
for zone in ZONES:
    fig3.add_shape(type="rect",
                   x0=zone["x"], y0=zone["y"],
                   x1=zone["x"]+zone["width"], y1=zone["y"]+zone["height"],
                   fillcolor=zone_colors.get(zone["type"], "#30363d"),
                   opacity=0.4, line_color="#30363d")
    fig3.add_annotation(x=zone["x"]+zone["width"]/2, y=zone["y"]+zone["height"]/2,
                        text=zone["name"], showarrow=False,
                        font=dict(color="white", size=10))
for d in last["drones"]:
    pos = d["position"]
    fig3.add_trace(go.Scatter(
        x=[pos[0]], y=[pos[1]], mode="markers+text",
        marker=dict(size=12, color="#f0883e"),
        text=[f"D{d['id']}"], textposition="top center",
        name=f"Drone {d['id']}"
    ))
fig3.add_trace(go.Scatter(
    x=[HUB_POSITION[0]], y=[HUB_POSITION[1]], mode="markers+text",
    marker=dict(size=18, color="#bc8cff", symbol="star"),
    text=["HUB"], textposition="top center", name="Hub"
))
fig3.update_layout(template="plotly_dark",
                   xaxis=dict(range=[0, 200]),
                   yaxis=dict(range=[0, 150]),
                   height=400, showlegend=False)
st.plotly_chart(fig3, use_container_width=True)

st.subheader("📋 Drone Status Table")
st.dataframe(df_drones[["id", "role", "status", "battery"]], use_container_width=True)
