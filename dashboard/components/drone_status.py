import streamlit as st
import pandas as pd

def render_drone_status(drones: list):
    df = pd.DataFrame(drones)
    st.dataframe(df[["id", "role", "status", "battery"]], use_container_width=True)
