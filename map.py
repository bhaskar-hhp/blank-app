import streamlit as st
import pandas as pd
import time
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(page_title="Live Location Tracker", layout="wide")
st.title("📍 Live Location Tracker")

map_placeholder = st.empty()
coords_placeholder = st.empty()

for i in range(1000):
    # directly evaluate latitude & longitude separately
    lat = streamlit_js_eval(js_expressions="navigator.geolocation.getCurrentPosition(p => p.coords.latitude)", key=f"lat{i}")
    lon = streamlit_js_eval(js_expressions="navigator.geolocation.getCurrentPosition(p => p.coords.longitude)", key=f"lon{i}")

    if lat and lon:
        coords_placeholder.success(f"Your current location: {lat}, {lon}")

        df = pd.DataFrame([[lat, lon]], columns=["lat", "lon"])
        map_placeholder.map(df, zoom=15)
    else:
        coords_placeholder.warning("Waiting for location access... (Allow permission in browser)")

    time.sleep(2)
