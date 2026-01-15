# Stores traffic light timers & UI display
from .settings import default_green, default_yellow, default_red

class TrafficSignal:
    def __init__(self):
        self.green = default_green # Green light duration (adjusted by density)
        self.yellow = default_yellow # Yellow light duration
        self.red = default_red # Red light duration
        self.signal_text = "---" # Placedholder for signal timer
        self.total_green_time = 0 # Tracks total green time assigned to a signal