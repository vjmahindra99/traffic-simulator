# Live simulation statistics for traffic simulator
import tkinter as tk
from . import settings
from .export_stats import sec_to_min_sec

# Global variables
root = None
lbl_time = None
lbl_green = None
lbl_amb = None
lane_labels = []
dir_names = ["Right (E)", "Down (S)", "Left (W)", "Up (N)"]

# GUI window that displays live traffic simulation statistics
def start_stats_window():

    global root, lbl_time, lbl_green, lbl_amb, lane_labels

    close_stats_window() # Close previous run window
    lane_labels.clear() # Remove old objects

    # Create a new Tkinter window
    root = tk.Tk()
    root.title("Smart Traffic - Live Stats")
    root.attributes('-topmost', True) # stay above others
    root.lift() # bring window to top
    root.focus_force()

    # Fixed window size
    root.geometry("300x230")

    # Title at the top of the window
    title = tk.Label(root, text="Live Simulation Stats", font=("Arial", 14, "bold"))
    title.pack(pady=5)

    # Container for global stats
    global_frame = tk.Frame(root)
    global_frame.pack(pady=5, fill="x", padx=10)

    # Display: total simulation time
    lbl_time = tk.Label(global_frame, text="Simulation time: 00:00", anchor="w")
    lbl_time.pack(fill="x")

    # Display: current green signal index (1..4)
    lbl_green = tk.Label(global_frame, text="Current green lane: -", anchor="w")
    lbl_green.pack(fill="x")

    # Display: total ambulance-priority events
    lbl_amb = tk.Label(global_frame, text="Ambulance priority events: 0", anchor="w")
    lbl_amb.pack(fill="x")

    # Per-lane section (Right/Down/Left/Up)
    lane_frame = tk.LabelFrame(root, text="Per-lane stats")
    lane_frame.pack(pady=5, fill="both", expand=True, padx=10)

    # One label row per direction
    for name in dir_names:
        lbl = tk.Label(
            lane_frame,
            text=name + ": dens=0.00 | queue=0 | passed=0",
            anchor="w",
        )
        lbl.pack(fill="x")
        lane_labels.append(lbl)

    # Refresh the live statistics on screen every 500ms
    def update_loop():

        global root

        if root is None:
            return        
        # Time formatting (mm:ss)
        try:
            elapsed = sec_to_min_sec(settings.time_elapsed)
        except Exception:
            elapsed = "00:00"

        # Update global labels
        lbl_time.config(text="Sim time: " + elapsed)
        lbl_green.config(text="Current green lane: " + str(settings.current_green + 1))
        lbl_amb.config(text="Ambulance priority events: " + str(settings.ambulance_priority_total))

        # Compute live statistics
        for i in range(settings.no_of_signals):
            direction = settings.direction_numbers[i]
            passed = settings.vehicles[direction]["crossed"]

            # Compute density
            score = 0.0
            for lane in [0, 1, 2]:
                for v in settings.vehicles[direction][lane]:
                    # Only count vehicles not yet crossed
                    if v.crossed == 0:
                        score += settings.density_weights.get(v.vehicle_class, 1.0)

            # Count vehicles near stop line
            roi_depth = 250 # px from the stop-line into the lane
            count = 0

            for lane in [0, 1, 2]:
                for v in settings.vehicles[direction][lane]:
                    if v.crossed != 0: # Ignore vehicles already passed the junction
                        continue

                    rect = v.current_image.get_rect()

                    # Right (moving East)
                    if direction == "right":
                        right_edge = v.x + rect.width
                        if settings.stop_lines["right"] - roi_depth <= right_edge <= settings.stop_lines["right"] + 10:
                            count += 1

                    # Down (moving South)
                    elif direction == "down":
                        bottom_edge = v.y + rect.height
                        if settings.stop_lines["down"] - roi_depth <= bottom_edge <= settings.stop_lines["down"] + 10:
                            count += 1

                    # Left (moving West)
                    elif direction == "left":
                        left_edge = v.x
                        if settings.stop_lines["left"] - 10 <= left_edge <= settings.stop_lines["left"] + roi_depth:
                            count += 1

                    # Up (moving North)
                    elif direction == "up":
                        top_edge = v.y
                        if settings.stop_lines["up"] - 10 <= top_edge <= settings.stop_lines["up"] + roi_depth:
                            count += 1

            # Build label text using old-style formatting
            line_text = (dir_names[i] + ": dens=" + "%.2f" % score + " | queue=" + str(count) + " | passed=" + str(passed))

            # Update lane label
            try:
                lane_labels[i].config(text=line_text)
            except tk.TclError:
                root = None
                return

        # Live update stops when simulation ends
        if not getattr(settings, "simulation_running", True):
            lbl_time.config(text="Sim time: " + elapsed + " (ended)")
            try:
                root.destroy()
            except tk.TclError:
                pass
            root = None
            return

        # Refresh rate
        root.after(500, update_loop)

    # Start periodic refresh
    update_loop()

# Process Tk events
def pump_stats_window():

    global root
    
    if root is None:
        return
    try:
        root.update_idletasks()
        root.update()
    except tk.TclError:
        root = None

# Close stats window when simulation ends
def close_stats_window():
    
    global root
    
    if root is not None:
        try:
            root.destroy()
        except tk.TclError:
            pass
        root = None