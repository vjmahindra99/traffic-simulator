# Simulation logic & density functions for fixed-timer traffic lights
import time
import random
from . import settings
from .vehicle import Vehicle
from .traffic_signal import TrafficSignal

# Count vehicles waiting near the stop line (ROI check)
def count_near_stop(dir_index):
    
    direction = settings.direction_numbers[dir_index]
    count = 0
    roi_depth = 500 # px

    for lane in [0, 1, 2]:
        for v in settings.vehicles[direction][lane]:

            if v.crossed != 0:
                continue # ignore vehicles that already passed intersection

            rect = v.current_image.get_rect()

            # East (moving right)
            if direction == "right":
                right_edge = v.x + rect.width
                if settings.stop_lines["right"] - roi_depth <= right_edge <= settings.stop_lines["right"] + 10:
                    count += 1

            # South (moving down)
            elif direction == "down":
                bottom_edge = v.y + rect.height
                if settings.stop_lines["down"] - roi_depth <= bottom_edge <= settings.stop_lines["down"] + 10:
                    count += 1

            # West (moving left)
            elif direction == "left":
                left_edge = v.x
                if settings.stop_lines["left"] - 10 <= left_edge <= settings.stop_lines["left"] + roi_depth:
                    count += 1

            # North (moving up)
            elif direction == "up":
                top_edge = v.y
                if settings.stop_lines["up"] - 10 <= top_edge <= settings.stop_lines["up"] + roi_depth:
                    count += 1
    return count

# Green light timer
fixed_green_time = 60  # seconds

# Yellow light timer
fixed_yellow_time = settings.default_yellow

# Signal initialization
def init_signals():
    settings.signals.clear()
    for _ in range(settings.no_of_signals):
        settings.signals.append(TrafficSignal())

# Fixed-time signal controller
def signal_controller():

    while settings.simulation_running:

        # Ensure current_green is within range
        current = settings.current_green % settings.no_of_signals

        # Set fixed green & yellow for this phase
        settings.signals[current].green = fixed_green_time
        settings.signals[current].yellow = fixed_yellow_time

        # Green phase
        settings.current_yellow = 0

        while settings.signals[current].green > 0 and settings.simulation_running:
            
            # AGlobal simulation timer
            settings.time_elapsed += 1

            # Show remaining green time on the current lane
            settings.signals[current].signal_text = settings.signals[current].green
            settings.signals[current].green -= 1

            # Other lanes display '---'
            for i in range(settings.no_of_signals):
                if i != current:
                    settings.signals[i].signal_text = "---"

            time.sleep(1)

        if not settings.simulation_running:
            return

        # Once green is done, set to 0
        settings.signals[current].green = 0

        # Mark when the current lane finished its green phase
        finished_lane = current
        settings.lane_last_green_end[finished_lane] = settings.time_elapsed

        # Yellow phase
        settings.current_yellow = 1

        while settings.signals[current].yellow > 0 and settings.simulation_running:
            settings.time_elapsed += 1
            settings.signals[current].signal_text = settings.signals[current].yellow
            settings.signals[current].yellow -= 1
            time.sleep(1)

        if not settings.simulation_running:
            return

        settings.current_yellow = 0
        settings.signals[current].signal_text = "stop"

        # Next lane (fixed rotation)
        next_green = (current + 1) % settings.no_of_signals

        # Time taken for this next lane to finally turn green
        last_end = settings.lane_last_green_end[next_green]
        wait_before_green = settings.time_elapsed - last_end
        settings.lane_wait_before_green_sum[next_green] += wait_before_green
        settings.lane_wait_before_green_count[next_green] += 1

        # How many vehicles are waiting in that lane when it turns green
        queue_now = count_near_stop(next_green)
        settings.queue_at_green_sum[next_green] += queue_now
        settings.queue_at_green_count[next_green] += 1

        # Move to next lane
        settings.current_green = next_green

        time.sleep(0.5)

# Vehicle generator
def generate_vehicles():

    while settings.simulation_running:

        vehicle_type = random.randint(0, 4) # Random choice of vehicle class

        # Bikes only use lane 0
        if vehicle_type == 4:
            lane_number = 0
        else:
            # Other vehicles use lanes 1 or 2
            lane_number = random.randint(0, 1) + 1

        # Vehicles turn probability
        will_turn = 0
        if lane_number == 2:
            temp = random.randint(0, 4)
            if temp <= 2:
                will_turn = 1
            else:
                will_turn = 0

        # Equal probability for each vehicle spawn direction
        temp = random.randint(0, 999)
        thresholds = [250, 500, 750, 1000]
        if temp < thresholds[0]:
            direction_number = 0
        elif temp < thresholds[1]:
            direction_number = 1
        elif temp < thresholds[2]:
            direction_number = 2
        else:
            direction_number = 3

        # Vehicle object
        Vehicle(
            lane_number,
            settings.vehicle_types[vehicle_type],
            direction_number,
            settings.direction_numbers[direction_number],
            will_turn,
        )

        # Check flag again during delay so it stops quickly
        for _ in range(3):  # 3 * 0.50 = 1.5s total
            if not settings.simulation_running:
                return
            
            time.sleep(0.50) # Delay for every vehicle spawn