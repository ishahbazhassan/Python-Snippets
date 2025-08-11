import random
import time

def simulate_cold_call(name):
    greetings = [
        f"Hi {name}, this is Alex from AAA Marketing.",
        f"Hey {name}, have you heard of AI tools that can boost your leads?"
    ]
    pitch = "Would you be open to a short demo call next week?"

    print(random.choice(greetings))
    time.sleep(1)
    print(pitch)

simulate_cold_call("Sarah")
