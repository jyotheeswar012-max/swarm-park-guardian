import plotly.graph_objects as go
import streamlit as st
from simulation.park_map import ZONES, HUB_POSITION

def render_mission_map(drones: list):
    fig = go.Figure()
    zone_colors = {"grass": "#2ea043", "garden": "#3fb950", "paved": "#8b949e", "water": "#58a6ff"}
    for zone in ZONES:
        fig.add_shape(type="rect",
                      x0=zone["x"], y0=zone["y"],
                      x1=zone["x"]+zone["width"], y1=zone["y"]+zone["height"],
                      fillcolor=zone_colors.get(zone["type"], "#30363d"),
                      opacity=0.4, line_color="#30363d")
    for d in drones:
        pos = d["position"]
        fig.add_trace(go.Scatter(
            x=[pos[0]], y=[pos[1]], mode="markers+text",
            marker=dict(size=12, color="#f0883e"),
            text=[f"D{d['id']}"], textposition="top center"
        ))
    fig.update_layout(template="plotly_dark", height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
