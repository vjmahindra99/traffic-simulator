# Global constants & parameters
import os
import pygame

# Base path of fixed_atlas folder
base_path = os.path.dirname(__file__)

default_red = 150 # Default red light timer
default_yellow = 3 # Yellow light timer
default_green = 20 # Green light timer, adjusted by density
default_minimum = 10 # Minimum green light timer
default_maximum = 60 # Maximum green timer
no_of_signals = 4 # Number of signal lights

signals = []

# Directions (north = up, south = down, = east = Right, west = Left)
# Direction index -> name
direction_numbers = {0: "right", 1: "down", 2: "left", 3: "up"}

# [Reverse] Direction name -> index (for wait-time stats)
direction_index = {"right": 0, "down": 1, "left": 2, "up": 3}

# Vehicle types
vehicle_types = {0: "car", 1: "bus", 2: "truck", 3: "rickshaw", 4: "bike"}

# Average speed of each vehicles
speeds = {
    "car": 2.25,
    "bus": 1.8,
    "truck": 1.8,
    "rickshaw": 2.0,
    "bike": 2.5,
}

# Weight of each vehicle
density_weights = {
    "car": 1.0,
    "bus": 2.0,
    "truck": 2.0,
    "rickshaw": 0.8,
    "bike": 0.5,
}

base_time_per_weight = 1.5

# Stop simulation when more than [amount of vehicles] have crossed
vehicle_limit = 250

# Lane wait stats: per direction index (0: right, 1: down, 2: left, 3: up)
lane_wait_sum = [0.0, 0.0, 0.0, 0.0] # total wait time
lane_wait_count = [0, 0, 0, 0] # number of vehicles counted

# Lane waiting time before green light
lane_wait_before_green_sum = [0.0, 0.0, 0.0, 0.0]
lane_wait_before_green_count = [0, 0, 0, 0]
lane_last_green_end = [0, 0, 0, 0]

# Average queue size at start of green (per lane)
queue_at_green_sum   = [0.0, 0.0, 0.0, 0.0] # total vehicles waiting when green starts
queue_at_green_count = [0,   0,   0,   0] # how many times each lane turned green

# Coordinates of start
base_x = {
    "right": [0, 0, 0],
    "down": [755, 727, 697],
    "left": [1400, 1400, 1400],
    "up": [602, 627, 657],
}

base_y = {
    "right": [348, 370, 398],
    "down": [0, 0, 0],
    "left": [498, 466, 436],
    "up": [800, 800, 800],
}

# Stop lines for each lane
stop_lines = {"right": 590, "down": 330, "left": 800, "up": 535}
default_stop = {"right": 580, "down": 320, "left": 810, "up": 545}

base_stops = {
    "right": [580, 580, 580],
    "down": [320, 320, 320],
    "left": [810, 810, 810],
    "up": [545, 545, 545],
}

x = {d: coords[:] for d, coords in base_x.items()}
y = {d: coords[:] for d, coords in base_y.items()}
stops = {d: coords[:] for d, coords in base_stops.items()}

# Intersection centre used for turns
mid = {
    "right": {"x": 705, "y": 445},
    "down": {"x": 695, "y": 450},
    "left": {"x": 695, "y": 425},
    "up": {"x": 695, "y": 400},
}

rotation_angle = 3

gap = 15 # Stopping gap
gap2 = 15 # Moving gap

# Data structure to keep vehicles
vehicles = {
    "right": {0: [], 1: [], 2: [], "crossed": 0},
    "down": {0: [], 1: [], 2: [], "crossed": 0},
    "left": {0: [], 1: [], 2: [], "crossed": 0},
    "up": {0: [], 1: [], 2: [], "crossed": 0},
}

# Signal light positions & ui counters
signal_coords = [(530, 230), (810, 230), (810, 570), (530, 570)]
signal_timer_coords = [(530, 210), (810, 210), (810, 550), (530, 550)]
vehicle_count_coords = [(480, 210), (880, 210), (880, 550), (480, 550)]

# Global simulation state variables
current_green = 0 # which lane is green light currently
current_yellow = 0 # 0 = green/red, 1 = yellow
time_elapsed = 0 # simulator start timer
sim_time = 300 # maximum simulation duration

# Reset simulation function
def reset_for_new_run():
    
    global signals
    global lane_wait_sum, lane_wait_count
    global lane_wait_before_green_sum, lane_wait_before_green_count, lane_last_green_end
    global queue_at_green_sum, queue_at_green_count
    global vehicles, x, y, stops
    global current_green, current_yellow, time_elapsed, simulation_running
    global simulation
    global last_ambulance_spawn_time

    # Reset counters
    signals = []

    lane_wait_sum = [0.0, 0.0, 0.0, 0.0]
    lane_wait_count = [0, 0, 0, 0]

    lane_wait_before_green_sum = [0.0, 0.0, 0.0, 0.0]
    lane_wait_before_green_count = [0, 0, 0, 0]
    lane_last_green_end = [0, 0, 0, 0]

    queue_at_green_sum   = [0.0, 0.0, 0.0, 0.0]
    queue_at_green_count = [0,   0,   0,   0]

    # Reset vehicle data
    vehicles = {
        "right": {0: [], 1: [], 2: [], "crossed": 0},
        "down":  {0: [], 1: [], 2: [], "crossed": 0},
        "left":  {0: [], 1: [], 2: [], "crossed": 0},
        "up":    {0: [], 1: [], 2: [], "crossed": 0},
    }

    # Reset spawn coordinates & stops to base values
    x = {d: coords[:] for d, coords in base_x.items()}
    y = {d: coords[:] for d, coords in base_y.items()}
    stops = {d: coords[:] for d, coords in base_stops.items()}

    # Simulation state variables
    current_green = 0
    current_yellow = 0
    time_elapsed = 0

    # Controls background threads and timers
    simulation_running = True

    # Reset ambulance timing
    last_ambulance_spawn_time = 0.0

    # PyGame sprite group for vehicles
    simulation = pygame.sprite.Group()

# Initialise mutable state once at import
reset_for_new_run()