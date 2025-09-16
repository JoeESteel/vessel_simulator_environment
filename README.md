# Autonomous Vessel Simulator

This project is a Python-based simulator for developing and testing autonomous navigation algorithms for a marine vessel. It uses the Pygame library to create a 2D world with a realistic geographic coordinate system, allowing for the rapid prototyping of control logic before deployment on physical hardware.

The codebase is intentionally modular, separating the simulation environment (`world`), the vessel's physics (`vessel`), and the navigation logic (`controller`) to ensure the control code can be easily transferred to a real-world platform like a Raspberry Pi.

## Current Status

The simulator is highly functional with a tunable physics model reflecting vessel momentum, and a modular controller supporting multiple modes. The navigation logic now uses PID controllers for both heading and speed, along with a sophisticated, tiered approach for waypoint arrival.

## Features Implemented

* **Modular Architecture:** Code is split into `main.py`, `world.py`, `vessel.py`, and `controller.py`.
* **Realistic Physics:** The vessel model includes proportional drag and momentum for a more authentic feel. Top speed is configurable (~10 kts).
* **PID Control:** Separate PID controllers for heading and speed ensure precise, stable control without overshooting targets.
* **Advanced Waypoint Navigation:**
    * Uses a "go-to" strategy with tiered rudder control (hard, normal, and PID-based) for efficient turning.
    * Features an automatic speed limiter when approaching waypoints to prevent fly-by errors.
* **Full Waypoint Management:**
    * Add waypoints with a mouse click.
    * Clear the entire route.
    * Remove the most recently added waypoint.
* **Enhanced UI & Visualization:**
    * Displays Cross-Track Error (XTE) from the planned route.
    * Renders waypoint numbers, the active route leg, and the arrival circle.
    * Includes a heading line, vessel track, and a dynamic scale bar.
* **Unified Control Scheme:** The arrow keys are used consistently across all modes for intuitive operation.

## Project Setup and Execution

### 1. Prerequisites

* Python 3.8+
* Git

### 2. Setup

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd <your-repository-name>
    ```

2.  **Create and Activate a Virtual Environment:**
    ```bash
    # Create the venv
    python -m venv venv
    # Activate it (on Windows with Git Bash)
    source venv/Scripts/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### 3. Running the Simulator

Run the application as a module from the **root directory** of the project.

```bash
python -m src.main


Simulator Controls
Key(s)	Mode(s)	Action
M, S, A, W	Any	Switch to Manual, Semi-Auto, Autohelm, Waypoint mode.
C	Any	Clear all waypoints.
Backspace	Any	Remove the last waypoint.
Up / Down Arrows	Manual	Apply forward / reverse thrust.
Up / Down Arrows	Semi-Auto	Increase / Decrease target thrust.
Up / Down Arrows	Autohelm / Waypoint	Increase / Decrease target speed.
Left / Right Arrows	Manual	Apply port / starboard rudder.
Left / Right Arrows	Semi-Auto	Adjust target rudder port / starboard.
Left / Right Arrows	Autohelm	Adjust target heading.
Left Mouse Click	Any	Add a waypoint at the cursor's location.
Mouse Wheel	Any	Zoom the map in or out.