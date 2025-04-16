# RiskTimer.py
import heapq, time, random, threading

risk_timer_heap = []
challenge_words = ["rescue", "safety", "secure", "escape", "protect", "shield", "guardian"]
challenge_data = {}

def set_risk_timer(destination, minutes):
    trigger_time = time.time() + minutes * 60
    heapq.heappush(risk_timer_heap, (trigger_time, destination))
    print(f"🧭 Risk timer set for '{destination}' in {minutes} minutes.")

def get_challenge_data():
    return challenge_data

def risk_timer_monitor():
    while True:
        if risk_timer_heap:
            current_time = time.time()
            timer, destination = heapq.heappop(risk_timer_heap)
            wait_time = max(0, timer - current_time)
            time.sleep(wait_time)

            # Trigger challenge
            challenge_word = random.choice(challenge_words)
            challenge_data.clear()
            challenge_data.update({
                'destination': destination,
                'word': challenge_word,
                'timestamp': time.time(),
                'alert_sent': False,
                'active': True
            })
        else:
            time.sleep(1)

# Start background thread
threading.Thread(target=risk_timer_monitor, daemon=True).start()
