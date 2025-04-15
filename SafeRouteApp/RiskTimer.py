import heapq
import time
import threading
import random
import winsound  # Windows-specific sound module


# Min-heap for risk timers
risk_timer_heap = []


# Challenge words dictionary (Hash Map)
challenge_words = ["rescue", "safety", "secure", "escape", "protect", "shield", "guardian"]


# Simulated alert function
def send_alert():
    print("\n🚨 ALERT: No response received! Sending alert to emergency contacts...")


# Challenge to confirm safety
def challenge_user():
    word = random.choice(challenge_words)
    print(f"\n🛡️  Type this word within 10 seconds to confirm you're safe: {word}")
   
    def get_input():
        nonlocal user_input
        user_input = input("Your input: ")


    user_input = ""
    input_thread = threading.Thread(target=get_input)
    input_thread.start()
    input_thread.join(timeout=10)


    if user_input.strip().lower() == word:
        print("✅ Safety Confirmed!")
    else:
        send_alert()


# Monitor and trigger challenge after timer expires
def risk_timer_monitor():
    while risk_timer_heap:
        current_time = time.time()
        timer, destination = heapq.heappop(risk_timer_heap)
        wait_time = max(0, timer - current_time)
        time.sleep(wait_time)
        print(f"\n⏰ Time's up for destination: {destination}")


        # 🔔 Play buzzer (Windows only)
        print("🔊 Buzzer sounding...")
        winsound.Beep(1000, 700)  # frequency (Hz), duration (ms)
        winsound.Beep(1000, 700)
       
        challenge_user()


# Function to set a risk timer
def set_risk_timer(destination, minutes):
    trigger_time = time.time() + minutes * 60  # Convert minutes to seconds
    heapq.heappush(risk_timer_heap, (trigger_time, destination))
    print(f"🧭 Risk timer set for '{destination}' in {minutes} minutes.")


# Example usage
if __name__ == "__main__":
    print("🔐 Risk Timer + Safety Challenge System")


    # Set risk timer
    destination = input("Enter your destination: ")
    minutes = float(input("Set risk timer (in minutes, use small value like 0.1 for demo): "))
    set_risk_timer(destination, minutes)


    # Start monitoring in background
    monitor_thread = threading.Thread(target=risk_timer_monitor)
    monitor_thread.start()
