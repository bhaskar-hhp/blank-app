import streamlit as st
from streamlit_js_eval import get_geolocation
from geopy.geocoders import Nominatim # Import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

st.set_page_config(page_title="Location Demo", layout="centered")
st.title("📍 Auto Input Location Demo")

st.write("""
This app demonstrates how to get the user's current geographical location
using their browser's Geolocation API and then reverse geocodes it to find the address.
""")

st.info("You might need to install the `geopy` library: `pip install geopy`")

# Initialize Nominatim geolocator
# It's good practice to specify a unique user_agent
geolocator = Nominatim(user_agent="streamlit_location_app_v1")

# Button to trigger location fetching
if st.button("Get My Current Location & Address"):
    st.write("Requesting location from your browser... Please allow permission when prompted.")
    
    location_data = get_geolocation()

    if location_data and 'coords' in location_data:
        st.success("Coordinates obtained successfully!")
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

        st.write("Attempting to find address (reverse geocoding)...")
        try:
            # Use geopy to reverse geocode the coordinates
            # timeout is important for services that might be slow
            location_address_info = geolocator.reverse((latitude, longitude), exactly_one=True, language='en', timeout=10)
            
            if location_address_info:
                st.success("Address found!")
                st.write(f"**Full Address:** {location_address_info.address}")
                
                # You can access specific parts if available, e.g.:
                # city = location_address_info.raw.get('address', {}).get('city')
                # country = location_address_info.raw.get('address', {}).get('country')
                # if city:
                #     st.write(f"**City:** {city}")
                # if country:
                #     st.write(f"**Country:** {country}")
            else:
                st.warning("Could not find address for the given coordinates.")
        
        except GeocoderTimedOut:
            st.error("Reverse geocoding service timed out. Please try again.")
        except GeocoderUnavailable:
            st.error("Reverse geocoding service is unavailable. Please try again later.")
        except Exception as e:
            st.error(f"An error occurred during reverse geocoding: {e}")
        
    elif location_data is None:
        st.error("Failed to get location. The browser might have denied permission, or location services might be turned off.")
    else:
        st.warning(f"Received an unexpected response for location: {location_data}")

st.markdown("---")
st.subheader("How it works:")
st.markdown("""
- When you click the button, the app uses the `get_geolocation()` function from `streamlit-js-eval`.
- This function executes JavaScript in your browser to call `navigator.geolocation.getCurrentPosition()`.
- Your browser asks for permission to share your location.
- If granted, latitude and longitude are sent back to the Streamlit app.
- The app then uses the `geopy` library with the Nominatim service to convert these coordinates into a human-readable address (reverse geocoding).
""")
st.markdown("""
**Note on Nominatim Usage Policy:**
Nominatim is a free service provided by OpenStreetMap. Please be mindful of their usage policy to avoid overloading their servers (e.g., no more than 1 request per second, provide a valid User-Agent). For heavy usage, consider hosting your own instance or using a commercial geocoding provider.
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

