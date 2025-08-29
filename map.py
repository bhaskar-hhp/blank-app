import streamlit as st
import pandas as pd
import time
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(page_title="Live Location Tracker", layout="wide")
st.title("📍 Live Location Tracker")

map_placeholder = st.empty()
coords_placeholder = st.empty()

# Run tracking for ~30 seconds (or until stopped manually)
for i in range(1000):  # increase if you want longer tracking
    location = streamlit_js_eval(
        js_expressions="new Promise((resolve) => navigator.geolocation.getCurrentPosition(pos => resolve(pos.coords)))",
        key=f"loc{i}"
    )

    if location:
        lat, lon = location["latitude"], location["longitude"]

        # Show text info
        coords_placeholder.success(f"Your current location: {lat}, {lon}")

        # Update map with current point
        df = pd.DataFrame([[lat, lon]], columns=["lat", "lon"])
        map_placeholder.map(df, zoom=15)

    else:
        coords_placeholder.warning("Waiting for location access...")

    time.sleep(2)  # refresh every 2 seconds
