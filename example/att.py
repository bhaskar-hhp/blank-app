import streamlit as st
from streamlit_js_eval import get_geolocation # Ensure this import is correct

st.set_page_config(page_title="Location Demo", layout="centered")
st.title("📍 Auto Input Location Demo")

st.write("""
This app demonstrates how to get the user's current geographical location
using their browser's Geolocation API.
""")

# Button to trigger location fetching
if st.button("Get My Current Location"):
    st.write("Requesting location from your browser... Please allow permission when prompted.")
    
    # Fetch geolocation data
    # The get_geolocation() function will trigger a browser prompt for location permission.
    # It returns a dictionary with location data or None if permission is denied or an error occurs.
    location_data = get_geolocation()

    if location_data:
        st.success("Location obtained successfully!")
        latitude = location_data['coords']['latitude']
        longitude = location_data['coords']['longitude']
        accuracy = location_data['coords']['accuracy']
        
        st.write(f"**Latitude:** {latitude}")
        st.write(f"**Longitude:** {longitude}")
        st.write(f"**Accuracy:** Approximately {accuracy} meters")

        # You can then use these values to pre-fill a form, display on a map, etc.
        st.text_input("Detected Latitude", value=str(latitude))
        st.text_input("Detected Longitude", value=str(longitude))
        
        st.map(data=[{'latitude': latitude, 'longitude': longitude}], zoom=13)
        
    elif location_data is None:
        st.error("Failed to get location. The browser might have denied permission, or location services might be turned off.")
    else:
        # This case might occur if there's an unexpected return or error structure
        st.warning(f"Received an unexpected response for location: {location_data}")

st.markdown("---")
st.subheader("How it works:")
st.markdown("""
- When you click the button, the app uses the `get_geolocation()` function from the `streamlit-js-eval` library.
- This function executes JavaScript in your browser to call the `navigator.geolocation.getCurrentPosition()` API.
- Your browser will then ask for your permission to share your location.
- If you grant permission, the latitude and longitude are sent back to the Streamlit app.
""")

st.subheader("Alternative: IP-Based Geolocation (Server-Side)")
st.info("""
Another method is IP-based geolocation. This involves using the user's IP address to estimate their location with a server-side database or API (e.g., GeoLite2, ipinfo.io).

**Pros:**
- Doesn't require explicit browser permission for location (though privacy implications should still be considered).

**Cons:**
- Generally less accurate than browser-based GPS/Wi-Fi positioning.
- Accuracy can vary significantly (e.g., might only identify the city or ISP's location).
- Requires external databases or API subscriptions.
""")

