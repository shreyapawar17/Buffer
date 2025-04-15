import speech_recognition as sr
import time
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import folium
import webbrowser
import os
from datetime import datetime


class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False


class SOSWordDetector:
    def __init__(self):
        self.root = TrieNode()


    def insert(self, word):
        node = self.root
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True


    def is_sos_word(self, word):
        node = self.root
        for char in word.lower():
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end_of_word


# ✅ Step 1: Initialize SOS words
print("✅ Initializing SOS words")
sos_detector = SOSWordDetector()
sos_words = ["Help", "Danger", "Emergency", "Save", "Fire", "Attack"]


for word in sos_words:
    sos_detector.insert(word)


# 👤 Step 2: Identify the User (Simplified - in a real app, you'd have login/registration)
CURRENT_USER_ID = "woman_user_123"  # Replace with actual user identification
CURRENT_USER_GENDER = "female"      # Replace with actual user gender


# ⏱️ SOS Tracking State
is_sos_active = False
sos_start_time = None
sos_last_location = None
TRACKING_DURATION = 60 * 5  # Track for 5 minutes after SOS
LOCATION_UPDATE_INTERVAL = 10 # Update location every 10 seconds


def get_current_location():
    geolocator = Nominatim(user_agent="sos_app")
    try:
        pune_location = geolocator.geocode("Pune, Maharashtra, India", exactly_one=True, timeout=5)
        if pune_location:
            return pune_location.latitude, pune_location.longitude
        else:
            print("⚠️ Could not determine current location (simulating Pune).")
            return 18.5204, 73.8567 # Default to Pune coordinates
    except Exception as e:
        print(f"⚠️ Error getting location: {e} (simulating Pune).")
        return 18.5204, 73.8567 # Default to Pune coordinates


# 📞 Function to simulate sending SOS alert (replace with actual implementation)
def send_sos_alert(user_id, user_gender, location, spoken_word):
    global is_sos_active, sos_start_time, sos_last_location
    print("🚨 SOS Alert Triggered!")
    print(f"👤 User ID: {user_id}")
    print(f"🚺 User Gender: {user_gender}")
    print(f"⚠️ SOS Word Detected: '{spoken_word}'")
    if location:
        latitude, longitude = location
        print(f"📍 Initial Location: Latitude {latitude:.6f}, Longitude {longitude:.6f}")
        sos_last_location = location
        # In a real app, you would:
        # 1. Send SMS/Notifications to emergency contacts with user info, initial location, and SOS word.
        # 2. Potentially initiate a call to emergency services or contacts.
        # 3. Record audio and upload it to a secure server.
        # 4. Update UI to show SOS triggered and tracking is active.
    else:
        print("⚠️ Location could not be determined, but SOS triggered with user info.")


    is_sos_active = True
    sos_start_time = time.time()


# 📍 Function to track location during SOS
def track_location():
    global sos_last_location
    if is_sos_active:
        current_location = get_current_location()
        if current_location != sos_last_location:
            sos_last_location = current_location
            if current_location:
                latitude, longitude = current_location
                print(f"🛰️ Tracking Location: Latitude {latitude:.6f}, Longitude {longitude:.6f} (at {time.strftime('%H:%M:%S')})")
                # In a real app, you would:
                # 1. Send updated location to emergency contacts periodically.
                # 2. Store the location history on a server.
            else:
                print("⚠️ Could not get updated location.")


# 🎤 Step 3: Recognize speech and trigger/continue alert and tracking
def detect_speech_and_alert():
    global is_sos_active, sos_start_time


    if is_sos_active:
        if time.time() - sos_start_time >= TRACKING_DURATION:
            print("🛑 SOS tracking duration ended.")
            is_sos_active = False
            sos_start_time = None
            return
        else:
            print(f"📡 SOS tracking active for {int(time.time() - sos_start_time)} seconds. Listening for stop command...")
            recognizer = sr.Recognizer()
            try:
                mic = sr.Microphone()
                with mic as source:
                    recognizer.adjust_for_ambient_noise(source)
                    print("🎧 Adjusted for ambient noise")
                    print("👂 Listening for stop command (up to 10 seconds)...")
                    audio = recognizer.listen(source, phrase_time_limit=10)
                    text = recognizer.recognize_google(audio)
                    print(f"🗣️ You said: {text}")
                    if "stop" in text.lower():
                        print("✅ 'Stop' command detected. Ending SOS tracking.")
                        is_sos_active = False
                        sos_start_time = None
                        return
            except sr.WaitTimeoutError:
                print("⏳ No 'stop' command heard.")
            except sr.UnknownValueError:
                print("😕 Could not understand audio for stop command.")
            except sr.RequestError as e:
                print(f"⚠️ Could not connect to speech recognition service for stop command: {e}")
            return # If SOS is active, we prioritize listening for the stop command


    print("🎙️ Starting speech detection for SOS trigger")
    recognizer = sr.Recognizer()


    try:
        mic = sr.Microphone()
    except Exception as e:
        print(f"⚠️ Microphone initialization failed: {e}")
        return


    print("🎙️ Listening for SOS words... Speak now.")
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        print("🎧 Adjusted for ambient noise")
        print("⌛ Speak for up to 30 seconds...")
        try:
            audio = recognizer.listen(source, phrase_time_limit=30)
            print("🎧 Audio captured")
        except sr.WaitTimeoutError:
            print("⏳ No speech detected.")
            return


    try:
        text = recognizer.recognize_google(audio)
        print(f"🗣️ You said: {text}")


        for word in text.split():
            if sos_detector.is_sos_word(word):
                print("🚨 SOS Word Detected! Triggering alert and starting tracking.")
                current_location = get_current_location()
                send_sos_alert(CURRENT_USER_ID, CURRENT_USER_GENDER, current_location, word)
                return


        print("✅ No SOS word found.")
    except sr.UnknownValueError:
        print("😕 Could not understand audio.")
    except sr.RequestError as e:
        print(f"⚠️ Could not connect to speech recognition service: {e}")


# Run the function in a loop
print("🚀 Running detection now...")
while True:
    detect_speech_and_alert()
    if is_sos_active:
        track_location()
        time.sleep(LOCATION_UPDATE_INTERVAL)
    else:
        time.sleep(5) # Adjust the delay between listening attempts when SOS is not active

