import openrouteservice
from openrouteservice import convert
import folium
from folium.plugins import HeatMap
import networkx as nx
from geopy.geocoders import Nominatim
from datetime import datetime
import webbrowser
import random

# OpenRouteService API Key
ORS_API_KEY = '5b3ce3597851110001cf6248fc9983571fcc4f99be09c0202832e14a'
client = openrouteservice.Client(key=ORS_API_KEY)

# --- Time-based risk multipliers ---
time_risk_multipliers = {
    (0, 6): 0.6,
    (6, 18): 1.2,
    (18, 24): 0.8
}


# --- Simulate user-reported unsafe areas (intensity 0-1) ---
unsafe_reports = [
    {"lat": 18.5250, "lon": 73.8600, "intensity": 0.8, "description": "Reported dimly lit after 9 PM"},
    {"lat": 18.5170, "lon": 73.8560, "intensity": 0.6, "description": "Few people around, poor lighting"},
    {"lat": 18.5290, "lon": 73.8530, "intensity": 0.4, "description": "Isolated area"},
    
]

# --- Simulate safe spaces ---
safe_spaces = [
    # ... (your existing safe_spaces list) ...
]

# --- Simulate safe bus routes ---
safe_bus_routes = [
    # ... (your existing safe_bus_routes list) ...
]

# --- Simulate safe taxi pickup points ---
safe_taxi_stands = [
    # ... (your existing safe_taxi_stands list) ...
]


def get_risk_multiplier():
    """Get the risk multiplier based on the current hour."""
    hour = datetime.now().hour
    for (start, end), mult in time_risk_multipliers.items():
        if start <= hour < end:
            return mult
    return 1.0

def get_coordinates(place_name):
    """Get the latitude and longitude of a place by its name using geopy."""
    geolocator = Nominatim(user_agent="safe_route_app", timeout=10) # Increased timeout
    try:
        location = geolocator.geocode(place_name)
        if location:
            return location.latitude, location.longitude
        return None, None
    except Exception as e:
        print(f"Error geocoding '{place_name}': {e}")
        return None, None

def fetch_routes(start, end, alternatives=3):
    """Fetch alternative routes between start and end using OpenRouteService."""
    try:
        routes = client.directions(
            coordinates=[start, end],
            profile='foot-walking',
            format='geojson',
            optimize_waypoints=True,
            alternative_routes={"share_factor": 0.5, "target_count": alternatives}
        )
        return routes
    except Exception as e:
        print(f"Error fetching routes from OpenRouteService: {e}")
        return None

def build_route_graph(route_geojson):
    """Build a graph from the route coordinates with random safety scores."""
    G = nx.DiGraph()
    coords = route_geojson['features'][0]['geometry']['coordinates']
    for i in range(len(coords) - 1):
        u = tuple(coords[i])
        v = tuple(coords[i + 1])
        dist = ((u[0] - v[0])**2 + (u[1] - v[1])**2) ** 0.5

        # Introducing variation in safety scores based on position (e.g., proximity to unsafe zones)
        safety_score = random.randint(5, 10)  # Simulate safety score based on position
        # Add more variation by considering proximity to unsafe areas
        for report in unsafe_reports:
            if abs(report['lat'] - u[1]) < 0.005 and abs(report['lon'] - u[0]) < 0.005: # Adjusted tolerance
                safety_score -= 3  # Decrease safety score near unsafe reports
        G.add_edge(u, v, distance=dist, safety=safety_score)
    return G

def score_route(graph):
    """Calculate the score of the route based on its safety and time-based risk multipliers."""
    multiplier = get_risk_multiplier()
    score = 0
    for u, v, data in graph.edges(data=True):
        # Lower weight for higher safety & time safety
        score += data['distance'] * ((10 - data['safety']) / 10) / multiplier
    return score

def display_map(routes, start_coords, end_coords, scores):
    """Display the routes on a Folium map with unsafe heatmaps, safe spaces, and crime hotspots."""
    # Define Pune's coordinates for map initialization
    pune_coords = (18.5204, 73.8567)  # Pune city center coordinates

    # Update the folium map to use Pune's coordinates
    fmap = folium.Map(location=pune_coords, zoom_start=13)  # Adjust zoom level to suit Pune city

    # Add start and end markers
    folium.Marker(location=start_coords[::-1], popup="Start (Pune)", icon=folium.Icon(color="green")).add_to(fmap)
    folium.Marker(location=end_coords[::-1], popup="Destination", icon=folium.Icon(color="red")).add_to(fmap)

    if routes and 'features' in routes:
        # Show all route options
        for i, feature in enumerate(routes['features']):
            coords = feature['geometry']['coordinates']
            path = [(lat, lon) for lon, lat in coords]
            color = "blue" if i == scores.index(min(scores)) else "gray"
            folium.PolyLine(path, color=color, weight=5, tooltip=f"Route {i+1} Score: {scores[i]:.2f}").add_to(fmap)

    # Unsafe areas as heatmap
    heat_data = [[r["lat"], r["lon"], r["intensity"]] for r in unsafe_reports]
    HeatMap(heat_data, radius=20).add_to(fmap)

    # Safe spaces (focused around Pune)
    for space in safe_spaces:
        folium.Marker([space["lat"], space["lon"]], popup=space["name"], icon=folium.Icon(color="orange")).add_to(fmap)

    # --- Add Crime Hotspots ---
    for report in unsafe_reports:
        print(f"Attempting to add marker at: {report['lat']}, {report['lon']} with intensity: {report.get('intensity', 0)}") # Enhanced print
        folium.CircleMarker(
            location=[report["lat"], report["lon"]],
            radius=report.get('intensity', 0) * 10,   # Use .get() with default
            color='red',
            fill=True,
            fill_color='darkred',
            fill_opacity=0.6,
            popup=report.get("description", "Unsafe Area") # Use .get() with default
        ).add_to(fmap)

    folium.LayerControl().add_to(fmap)
    fmap.save("interactive_safe_routes.html")
    webbrowser.open("interactive_safe_routes.html")

def main():
    """Main function to get user input, evaluate routes, and display the safest route from Pune."""
    print("🏁 Safe Route Finder (OpenRouteService + Safety Graph)\n")
    destination = input("Enter your destination: ")

    # Hardcode Pune coordinates as the starting point
    pune_latitude = 18.5204
    pune_longitude = 73.8567

    dst_lat, dst_lon = get_coordinates(destination)

    if not all([pune_latitude, pune_longitude, dst_lat, dst_lon]):
        print("❌ Could not find destination coordinates.")
        return

    start_coords = (pune_longitude, pune_latitude)
    end_coords = (dst_lon, dst_lat)

    routes = fetch_routes(start_coords, end_coords)

    if routes is None:
        print("❌ Could not fetch routes.")
        return

    route_scores = []

    print("\n🔍 Evaluating route safety...")

    if 'features' in routes:
        for feature in routes['features']:
            G = build_route_graph({"features": [feature]})
            score = score_route(G)
            route_scores.append(score)

        if route_scores:
            best_index = route_scores.index(min(route_scores))
            print(f"\n✅ Best route is Route {best_index+1} with safety score {route_scores[best_index]:.2f}")
            print("--- Unsafe Reports Data ---")
            print(unsafe_reports)  # This line was added
            display_map(routes, (pune_latitude, pune_longitude), (dst_lat, dst_lon), route_scores)
        else:
            print("⚠️ No valid routes found to score.")
    else:
        print("⚠️ No routes found.")

if __name__ == "__main__":
    main()
