# Live simulation statistics for traffic simulator
import tkinter as tk
from . import settings
from .export_stats import sec_to_min_sec
from .controller import compute_density, count_near_stop

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
    root.title("ATLAS Traffic - Live Stats")
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
    lane_labels.clear()
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

            # YOLO-based density & queue
            score = compute_density(i)
            count = count_near_stop(i)

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