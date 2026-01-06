# 🚦Traffic Density-Based Simulator

# **Summary**<br>
A Python-based traffic intersection simulator comparing fixed-time and adaptive signal control using real-time vehicle density.

# **Description**<br>
<p align="justify">
This project is an interactive traffic simulator designed to evaluate and compare fixed-time and density-based adaptive traffic signal control systems. The simulator models realistic vehicle movement across multiple lanes and directions dynamically generating traffic flow and managing signal phases in real time.
</p>

<p align="justify">
An adaptive control algorithm adjusts green signal durations based on real-time vehicle density that enables more traffic throughput efficiently. Thus, reducing waiting times compared to traditional fixed timer systems. Vehicle counts, signal timings and performance metrics (total vehciles passed intersection and average delay) are continuously tracked and visualized during the simulation
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/5027e66f-cf53-4e74-8e45-8e04e9e95651"
       width="500" />
  <br>
  <em>Traffic Simulator – Main Menu</em>
</p>

<p align="justify">
The system is implementated using Python and Pygame framework featuring a graphical user interface, animated vehicles and configurable signal parameters. Simulation results can be exported as Excel format for further analysis making the project suitable for academic studies, traffic engineering research and intelligent transportation system (ITS) experimentation.
</p>

# **🔍 Purpose of Multi-Mode Design**
<p align="justify">
  The simulator provides a direct and fair comparison between fixed-time, rule-based adaptive and vision-based adaptive traffic systems using metrics such as vehicle throughput, waiting time and signal utilization.
</p>

# **Simulation Modes**

<p align="justify">
  <strong>🚦 Classic — Fixed-Time Mode</strong><br>
  Classic mode uses a fixed-time traffic signal system where aeach direction is assigned to a predefined green, yellow and red durations (eg. 60 seconds). Signal changes follow a cyclic sequence and do not react to traffic demand. This mode represents conventional traffic light systems commonly used in real-world intersections. This serves as a baseline for performance comparison.
</p>

<p align="justify">
  <strong>🧠 Smart — Rule-Based Density Mode</strong><br>
  Smart mode implements a rule-based adaptive signal control system that adjusts green signal durations according to simulated vehicle density on each lane. Vehicle counts are monitored in real time and predefined rules allocate longer green times to lanes with higher congestions. This mode improves efficiency compared to fixed-time control while remaining lightweight and independent of computer vision models.
</p>

<p align="justify">
  <strong>🤖 ATLAS — YOLO-Based Density Mode</strong><br>
  ATLAS mode is an advanced adaptive traffic control system that determines signal timings using YOLO-based vehicle detection. real-time object detection is used to estimate lane density by identifying and counting vehicles that enables high responsive allocation based on actual traffic conditions. This mode represents an AI-driven smart traffic system bridging Deep Learning and traffic simulation to achieve optimal intersection throughput.
</p>
