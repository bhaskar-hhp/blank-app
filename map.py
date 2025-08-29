import streamlit as st
import pandas as pd
import time
from streamlit_geolocation import streamlit_geolocation

st.set_page_config(page_title="Live Location Tracker", layout="wide")
st.title("📍 Live Location Tracker")

map_placeholder = st.empty()
coords_placeholder = st.empty()

for i in range(1000):
    location = streamlit_geolocation()

    if location and "latitude" in location and "longitude" in location:
        lat = location["latitude"]
        lon = location["longitude"]

        coords_placeholder.success(f"Your current location: {lat}, {lon}")

        df = pd.DataFrame([[lat, lon]], columns=["lat", "lon"])
        map_placeholder.map(df, zoom=15)
    else:
        coords_placeholder.warning("Waiting for location access... (Allow permission in browser)")

    time.sleep(2)
