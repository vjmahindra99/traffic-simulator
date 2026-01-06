# Simulation logic & density functions
import math
import time
import random
from . import settings
from .vehicle import Vehicle
from .traffic_signal import TrafficSignal

# Initialize all traffic light signal objects
def init_signals():

    for _ in range(settings.no_of_signals):
        settings.signals.append(TrafficSignal())

# Density calculation
def compute_density(dir_index):
    
    direction = settings.direction_numbers[dir_index]
    score = 0.0
    
    for lane in [0, 1, 2]:
        for v in settings.vehicles[direction][lane]:
            if v.crossed == 0:
                score += settings.density_weights.get(v.vehicle_class, 1.0)
    return score

# Scan all directions to determine where is the ambulance located
def find_ambulance_dir():

    roi_depth = 1000 # px

    for dir_index in range(settings.no_of_signals):
        direction = settings.direction_numbers[dir_index]

        for lane in [0, 1, 2]:
            for v in settings.vehicles[direction][lane]:
                # Only care about ambulances that haven't crossed
                if v.crossed != 0 or v.vehicle_class != "ambulance":
                    continue

                rect = v.current_image.get_rect()

                # East (moving right)
                if direction == "right":
                    right_edge = v.x + rect.width
                    if settings.stop_lines["right"] - roi_depth <= right_edge <= settings.stop_lines["right"] + 10:
                        return dir_index

                # South (moving down)
                elif direction == "down":
                    bottom_edge = v.y + rect.height
                    if settings.stop_lines["down"] - roi_depth <= bottom_edge <= settings.stop_lines["down"] + 10:
                        return dir_index

                # West (moving left)
                elif direction == "left":
                    left_edge = v.x
                    if settings.stop_lines["left"] - 10 <= left_edge <= settings.stop_lines["left"] + roi_depth:
                        return dir_index

                # North (moving up)
                elif direction == "up":
                    top_edge = v.y
                    if settings.stop_lines["up"] - 10 <= top_edge <= settings.stop_lines["up"] + roi_depth:
                        return dir_index
    return None

# Count vehicles at stop line (ROI style)
def count_near_stop(dir_index):
    
    direction = settings.direction_numbers[dir_index]
    count = 0
    roi_depth = 250 # px

    for lane in [0, 1, 2]:
        for v in settings.vehicles[direction][lane]:
            if v.crossed != 0:
                continue  # vehicles already passed junction

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

# Use density to calculate the green light timer
def compute_green_time(dir_index):
    
    density = compute_density(dir_index)
    
    if density == 0:
        raw = settings.default_minimum
    else:
        raw = math.ceil(density * settings.base_time_per_weight)
    
    green_time = max(settings.default_minimum, min(settings.default_maximum, raw))
    
    print("[density] dir = " + str(dir_index) + " density = " + ("%.2f" % density) + " -> green = " + str(green_time) + "s")

    return green_time

# Which lane to give priority
def choose_next_green(current_index):
    
    best_dir = None
    best_score = -1.0

    for i in range(settings.no_of_signals):
        score = compute_density(i)
        if score > best_score and i != current_index:
            best_score = score
            best_dir = i

    if best_dir is None or best_score == 0:
        best_dir = (current_index + 1) % settings.no_of_signals

    print("[scheduler] next green: lane " + str(best_dir + 1) + " (score = " + ("%.2f" % best_score) + ")")
    
    return best_dir

def signal_controller():

    # Decides green time based on density
    # Green light ends early if no vehicles on lane for 3s
    # then yellow light & chooses next lane by density

    no_vehicle_timeout = 3  # Seconds of empty roi before cutting green light early

    while settings.simulation_running:
        
        # Compute adaptive green time for current lane
        settings.signals[settings.current_green].green = compute_green_time(settings.current_green)
        settings.signals[settings.current_green].yellow = settings.default_yellow

        # Green light phase
        settings.current_yellow = 0
        no_vehicle_seconds = 0

        while settings.signals[settings.current_green].green > 0:
            if not settings.simulation_running:
                return

            # Ambulance priority
            amb_dir = find_ambulance_dir()
            # If an ambulance is waiting on a different lane, cut current green early
            if amb_dir is not None and amb_dir != settings.current_green:
                print("[AMBULANCE] detected on lane",
                    amb_dir + 1,
                    "- cutting current green early from lane",
                    settings.current_green + 1)
                break

            waiting_near = count_near_stop(settings.current_green)
            
            if waiting_near == 0:
                no_vehicle_seconds += 1
            else:
                no_vehicle_seconds = 0

            if no_vehicle_seconds >= no_vehicle_timeout:
                print("[early cut] lane " + str(settings.current_green + 1) +
                      ": no vehicles near stop line for " + str(no_vehicle_timeout) +
                      "s, ending green early")
                break

            settings.time_elapsed += 1
            settings.signals[settings.current_green].signal_text = settings.signals[settings.current_green].green
            settings.signals[settings.current_green].green -= 1
            settings.signals[settings.current_green].total_green_time += 1

            # Other lanes stay red
            for i in range(settings.no_of_signals):
                if i != settings.current_green:
                    settings.signals[i].signal_text = "---"

            time.sleep(1)

        settings.signals[settings.current_green].green = 0

        # Yellow light phase
        settings.current_yellow = 1
        while settings.signals[settings.current_green].yellow > 0:
            settings.time_elapsed += 1
            settings.signals[settings.current_green].signal_text = settings.signals[settings.current_green].yellow
            settings.signals[settings.current_green].yellow -= 1
            time.sleep(1)

        settings.current_yellow = 0
        settings.signals[settings.current_green].signal_text = "stop"

        # Mark when the current lane finished its green + yellow
        finished_lane = settings.current_green
        settings.lane_last_green_end[finished_lane] = settings.time_elapsed

        # Next lane choice (with ambulance priority)
        amb_dir = find_ambulance_dir()
        if amb_dir is not None:
            next_green = amb_dir
            print("[AMBULANCE] Giving priority to lane", amb_dir + 1)
            settings.ambulance_priority_total += 1
            settings.ambulance_priority_per_lane[amb_dir] += 1
        else:
            next_green = choose_next_green(settings.current_green)

        # Time taken for next lane to turn green light
        last_end = settings.lane_last_green_end[next_green]
        if last_end > 0:
            wait_before_green = settings.time_elapsed - last_end
            settings.lane_wait_before_green_sum[next_green] += wait_before_green
            settings.lane_wait_before_green_count[next_green] += 1

        # Count vehicles near the stop line for the lane that is about to get green
        queue_now = count_near_stop(next_green)
        settings.queue_at_green_sum[next_green] += queue_now
        settings.queue_at_green_count[next_green] += 1
        settings.current_green = next_green

# Generate vehicles while simulation runs
def generate_vehicles():

    while settings.simulation_running:

        now = time.time()
        if not settings.simulation_running:
            return

        # Ambulance spawn chance
        time_since_last_amb = now - settings.last_ambulance_spawn_time
        can_spawn_ambulance = time_since_last_amb >= settings.ambulance_cooldown

        # Ambulance spawn probability
        roll = random.randint(1, 100)

        if can_spawn_ambulance and roll <= 5:
            vehicle_type = 0  # ambulance
            settings.last_ambulance_spawn_time = now
            print("[SPAWN] Ambulance spotted!")
        else:
            vehicle_type = random.randint(1, 5)  # normal vehicles

        # Bikes only use lane 0
        if vehicle_type == 1:
            lane_number = 0
        else:
            lane_number = random.randint(0, 1) + 1 # Others use lanes 1 or 2

        # Vehicles turn probability
        will_turn = 0
        if lane_number == 2:
            temp = random.randint(0, 5)
            will_turn = 1 if temp <= 2 else 0

        # Equal probability for each vehicle spawn
        temp = random.randint(0, 999)
        a = [250, 500, 750, 1000]
        if temp < a[0]:
            direction_number = 0
        elif temp < a[1]:
            direction_number = 1
        elif temp < a[2]:
            direction_number = 2
        else:
            direction_number = 3

        # Vehicle object variables
        Vehicle(
            lane_number,
            settings.vehicle_types[vehicle_type],
            direction_number,
            settings.direction_numbers[direction_number],
            will_turn,
        )
        
        # Check flag again after sleep so it stops quickly
        for _ in range(3):  # 3 * 0.50 = 1.5s total
            if not settings.simulation_running:
                return
        
        time.sleep(0.50) # Delay for every vehicle spawn