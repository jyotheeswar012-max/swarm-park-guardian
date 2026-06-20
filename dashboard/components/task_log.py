import streamlit as st
from core.hub import Hub

def render_task_log():
    hub  = Hub()
    data = hub.get_all_missions()
    if data:
        import pandas as pd
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    else:
        st.info("No missions logged yet.")
