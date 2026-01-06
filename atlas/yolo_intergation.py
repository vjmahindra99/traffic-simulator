# YOLO intergration settings for ATLAS simulator
import os
import torch
import pygame
import threading
import numpy as np
from ultralytics import YOLO
import pygame.surfarray as surfarray
from . import settings

# Global YOLO state
_model = None
_model_lock = threading.Lock()

# One entry per signal direction index
# 0: right, 1: down, 2: left, 3: up
_lane_density = [0.0] * settings.no_of_signals
_lane_queue = [0] * settings.no_of_signals

# Map YOLO class IDs -> class names used
yolo_class_id_to_name = {
    0: "ambulance",
    1: "bike",
    2: "bus",
    3: "car",
    4: "rickshaw",
    5: "truck",
}
vehicle_classes = set(settings.density_weights.keys())

# Lane band helpers
_lane_bands = {}

# Right-moving lanes: y-band based on spawn rows
_right_y_min = min(settings.y["right"]) - 40
_right_y_max = max(settings.y["right"]) + 40

# Down-moving lanes: x-band based on spawn columns
_down_x_min = min(settings.x["down"]) - 40
_down_x_max = max(settings.x["down"]) + 40

# Left-moving lanes: y-band
_left_y_min = min(settings.y["left"]) - 40
_left_y_max = max(settings.y["left"]) + 40

# Up-moving lanes: x-band
_up_x_min = min(settings.x["up"]) - 40
_up_x_max = max(settings.x["up"]) + 40

# Initialize YOLO model
def init_yolo(model_path: str | None = None, device: str | None = None):

    global _model

    with _model_lock:
        if _model is not None:
            return

        # Path to YOLO model
        if model_path is None:
            model_path = os.path.join(settings.base_path, "assets", "YOLO model", "pygame_model.pt")

        _model = YOLO(model_path)
        
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        _model.to(device)

        print("[YOLO] Loaded model from:", model_path, "on device:", device)

# Run YOLO on Pygame
def update_yolo_from_surface(surface: pygame.Surface):

    global _lane_density, _lane_queue

    if _model is None:
        return

    # Convert Pygame surface -> numpy array (H, W, 3)
    frame = surfarray.array3d(surface)
    frame = np.transpose(frame, (1, 0, 2)) # (H, W, 3)
    frame_bgr = frame[..., ::-1]

    # Run YOLO
    results = _model(frame_bgr, verbose=False)[0]

    dens = [0.0] * settings.no_of_signals
    q = [0] * settings.no_of_signals

    # ROI depths (in pixels)
    roi_depth_density = 1000 # for density
    roi_depth_queue = 500 # for queue near stop-line

    stop = settings.stop_lines

    if results.boxes is None:
        with _model_lock:
            _lane_density = dens
            _lane_queue = q
        return

    # Bounding boxes
    boxes = results.boxes.xyxy.cpu().numpy() # (N, 4)
    cls_ids = results.boxes.cls.cpu().numpy().astype(int) # (N,)

    for box, cls_id in zip(boxes, cls_ids):
        x1, y1, x2, y2 = box

        class_name = yolo_class_id_to_name.get(cls_id)
        if class_name is None or class_name not in vehicle_classes:
            continue

        weight = settings.density_weights.get(class_name, 1.0)

        cx = 0.5 * (x1 +x2)
        cy = 0.5 * (y1 +y2)

        right_edge = x2
        left_edge = x1
        bottom_edge = y2
        top_edge = y1

        dir_index = None

        # Direction 0 (right, moving East)
        if (
            _right_y_min <= cy <= _right_y_max
            and stop["right"] - roi_depth_density <= right_edge <= stop["right"] + 10
        ):
            dir_index = 0

        # Direction 1 (down, moving South)
        elif (
            _down_x_min <= cx <= _down_x_max
            and stop["down"] - roi_depth_density <= bottom_edge <= stop["down"] + 10
        ):
            dir_index = 1

        # Direction 2 (left, moving West)
        elif (
            _left_y_min <= cy <= _left_y_max
            and stop["left"] - 10 <= left_edge <= stop["left"] + roi_depth_density
        ):
            dir_index = 2

        # Direction 3 (up, moving North)
        elif (
            _up_x_min <= cx <= _up_x_max
            and stop["up"] - 10 <= top_edge <= stop["up"] + roi_depth_density
        ):
            dir_index = 3

        if dir_index is None:
            continue

        # Accumulate density
        dens[dir_index] += weight

        # Queue length (no of cars at stop line)
        if dir_index == 0: # right
            if stop["right"] - roi_depth_queue <= right_edge <= stop["right"] + 10:
                q[0] += 1

        elif dir_index == 1: # down
            if stop["down"] - roi_depth_queue <= bottom_edge <= stop["down"] + 10:
                q[1] += 1

        elif dir_index == 2: # left
            if stop["left"] - 10 <= left_edge <= stop["left"] + roi_depth_queue:
                q[2] += 1

        elif dir_index == 3: # up
            if stop["up"] - 10 <= top_edge <= stop["up"] + roi_depth_queue:
                q[3] += 1

    with _model_lock:
        _lane_density = dens
        _lane_queue = q

# Retrieve number of vehicles from each lane
def get_lane_density(dir_index: int) -> float:
    with _model_lock:
        return float(_lane_density[dir_index])

# Retrieve number of vehicles at stop line
def get_lane_queue(dir_index: int) -> int:
    with _model_lock:
        return int(_lane_queue[dir_index])