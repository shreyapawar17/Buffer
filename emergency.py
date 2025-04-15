import geopy.distance
from geopy.geocoders import Nominatim
import folium
import webbrowser
import heapq  # Import the heapq module


# Sample data (replace with actual data from a reliable source and user-specific data)
police_stations = [
    {"name": "Shivajinagar Police Station", "lat": 18.5387, "lon": 73.8573, "contact": "020-25511111"},
    {"name": "Deccan Gymkhana Police Station", "lat": 18.5178, "lon": 73.8441, "contact": "020-25652222"},
    {"name": "Swargate Police Station", "lat": 18.5033, "lon": 73.8601, "contact": "020-24453333"},
    {"name": "Kothrud Police Station", "lat": 18.5085, "lon": 73.8183, "contact": "020-25384444"},
    {"name": "Yerwada Police Station", "lat": 18.5670, "lon": 73.8778, "contact": "020-26685555"},
    # ... more stations with contact numbers
]


women_help_centers = [
    {"name": "Bharosa Cell", "lat": 18.5204, "lon": 73.8567},
    {"name": "Swayam Siddha Mahila Manch", "lat": 18.5132, "lon": 73.8552},
    {"name": "Aadhar Mahila Mandal", "lat": 18.5356, "lon": 73.8723},
    # ... more centers
]


emergency_contacts = [
    {"name": "Police Control Room", "number": "100"},
    {"name": "Women Helpline", "number": "1091"},
    {"name": "National Emergency Number", "number": "112"},
]


# Simulate user's trusted contacts (replace with actual user data)
trusted_contacts = [
    {"name": "Family Member 1", "number": "9876543210", "lat": 18.5250, "lon": 73.8600},
    {"name": "Friend 1", "number": "8765432109", "lat": 18.5150, "lon": 73.8500},
    {"name": "Friend 2", "number": "7654321098", "lat": 18.5300, "lon": 73.8700},
    # ... more trusted contacts with potential locations (if available)
]


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculates the distance between two coordinates."""
    return geopy.distance.geodesic((lat1, lon1), (lat2, lon2)).km


def find_nearest_locations(user_lat, user_lon, locations, num_results=3):
    """Finds the nearest locations using a priority queue (min-heap)."""
    distances = []
    for location in locations:
        distance = calculate_distance(user_lat, user_lon, location["lat"], location["lon"])
        heapq.heappush(distances, (distance, location))


    nearest_locations = []
    for _ in range(min(num_results, len(distances))):
        nearest_locations.append(heapq.heappop(distances)[1])


    return nearest_locations


def get_user_location():
    """Gets the user's location using geocoding."""
    geolocator = Nominatim(user_agent="emergency_app")
    try:
        location = geolocator.geocode("Pune") #default location, replace with actual user location.
        if location:
            return location.latitude, location.longitude
        else:
            print("Could not get location. Using Pune's default location.")
            return 18.5204, 73.8567 #Pune's general coordinates.
    except Exception as e:
        print(f"Error getting location: {e}. Using Pune's default location.")
        return 18.5204, 73.8567


def display_map(user_lat, user_lon, nearest_police, nearest_help_centers, nearest_trusted):
    """Displays the locations on a map using Folium."""
    map_pune = folium.Map(location=[user_lat, user_lon], zoom_start=12)


    folium.Marker([user_lat, user_lon], popup="Your Location", icon=folium.Icon(color="red")).add_to(map_pune)


    # Police Stations
    police_group = folium.FeatureGroup(name="Nearest Police Stations")
    for station in nearest_police:
        popup_content = f"<b>{station['name']}</b><br>Contact: {station.get('contact', 'N/A')}"
        folium.Marker([station["lat"], station["lon"]], popup=popup_content, icon=folium.Icon(color="blue")).add_to(police_group)
        distance = calculate_distance(user_lat, user_lon, station['lat'], station['lon'])
        folium.CircleMarker(
            location=[station["lat"], station["lon"]],
            radius=5,
            color="blue",
            fill=False,
            tooltip=f"Approx. {distance:.2f} km away"
        ).add_to(police_group)
    police_group.add_to(map_pune)


    # Women Help Centers
    help_center_group = folium.FeatureGroup(name="Nearest Women Help Centers")
    for center in nearest_help_centers:
        folium.Marker([center["lat"], center["lon"]], popup=center["name"], icon=folium.Icon(color="green")).add_to(help_center_group)
        distance = calculate_distance(user_lat, user_lon, center['lat'], center['lon'])
        folium.CircleMarker(
            location=[center["lat"], center["lon"]],
            radius=5,
            color="green",
            fill=False,
            tooltip=f"Approx. {distance:.2f} km away"
        ).add_to(help_center_group)
    help_center_group.add_to(map_pune)


    # Trusted Contacts
    trusted_group = folium.FeatureGroup(name="Nearest Trusted Contacts")
    for contact in nearest_trusted:
        if "lat" in contact and "lon" in contact:
            popup_content = f"<b>{contact['name']}</b><br>Contact: {contact.get('number', 'N/A')}"
            folium.Marker([contact["lat"], contact["lon"]], popup=popup_content, icon=folium.Icon(color="purple")).add_to(trusted_group)
            distance = calculate_distance(user_lat, user_lon, contact['lat'], contact['lon'])
            folium.CircleMarker(
                location=[contact["lat"], contact["lon"]],
                radius=5,
                color="purple",
                fill=False,
                tooltip=f"Approx. {distance:.2f} km away"
            ).add_to(trusted_group)
        else:
            print(f"Warning: Location data not available for {contact['name']}")
    trusted_group.add_to(map_pune)


    # Layer Control
    folium.LayerControl().add_to(map_pune)


    map_pune.save("pune_emergency_map.html")
    webbrowser.open("pune_emergency_map.html")


def main():
    """Main function to execute the emergency contact and location finding."""
    user_lat, user_lon = get_user_location()


    nearest_police = find_nearest_locations(user_lat, user_lon, police_stations)
    nearest_help_centers = find_nearest_locations(user_lat, user_lon, women_help_centers)


    # Find nearest trusted contacts (assuming they have location data)
    nearest_trusted = find_nearest_locations(user_lat, user_lon, trusted_contacts)


    print("Nearest Police Stations:")
    for station in nearest_police:
        distance = calculate_distance(user_lat, user_lon, station['lat'], station['lon'])
        print(f"- {station['name']}: {distance:.2f} km, Contact: {station.get('contact', 'N/A')}")


    print("\nNearest Women Help Centers:")
    for center in nearest_help_centers:
        distance = calculate_distance(user_lat, user_lon, center['lat'], center['lon'])
        print(f"- {center['name']}: {distance:.2f} km")


    print("\nNearest Trusted Contacts:")
    for contact in nearest_trusted:
        if "lat" in contact and "lon" in contact:
            distance = calculate_distance(user_lat, user_lon, contact['lat'], contact['lon'])
            print(f"- {contact['name']}: {distance:.2f} km, Contact: {contact.get('number', 'N/A')}")
        else:
            print(f"- {contact['name']}: Contact: {contact.get('number', 'N/A')} (Location unavailable)")


    print("\nEmergency Contacts:")
    for contact in emergency_contacts:
        print(f"- {contact['name']}: {contact['number']}")


    display_map(user_lat, user_lon, nearest_police, nearest_help_centers, nearest_trusted)


if __name__ == "__main__":
    main()
