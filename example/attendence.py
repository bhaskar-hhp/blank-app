import streamlit as st
from streamlit_javascript import st_javascript

st.title("📍 Location Fetch Test")

coords = st_javascript("""await new Promise((resolve, reject) => {
    navigator.geolocation.getCurrentPosition(
        (position) => resolve(position.coords.latitude + "," + position.coords.longitude),
        (err) => resolve("ERROR: " + err.message)
    );
});""", key="get_location")

if coords:
    if "ERROR" in coords:
        st.error(coords)
    else:
        st.success(f"Your Location: {coords}")
else:
    st.warning("Waiting for location permission...")
