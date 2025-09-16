# Autonomous Vessel Simulator

This project is a Python-based simulator for developing and testing autonomous navigation algorithms for a marine vessel. It uses the Pygame library to create a 2D world with a realistic geographic coordinate system, allowing for the rapid prototyping of control logic before deployment on physical hardware.

The codebase is intentionally modular, separating the simulation environment (`world`), the vessel's physics (`vessel`), and the navigation logic (`controller`) to ensure the control code can be easily transferred to a real-world platform like a Raspberry Pi.

## Current Status

The simulator is functional with a physics model and a modular controller supporting multiple modes. The navigation is based on a PID controller for heading adjustments and a track-following algorithm for waypoints. The control scheme has been unified to use the arrow keys across all modes for intuitive operation.

## Features Implemented

* **Modular Architecture:** Code is split into `main.py`, `world.py`, `vessel.py`, and `controller.py`.
* **Geographic Coordinate System:** The world is based on real Latitude and Longitude coordinates.
* **Dynamic Camera:** The view follows the vessel and supports zooming.
* **Visual Feedback:** Includes a dynamic scale bar, a continuous vessel track line, breadcrumbs, and a heading indicator.
* **Track-Following Navigation:** The waypoint mode now calculates Cross-Track Error (XTE) to stay on the planned route.
* **Multiple Control Modes:** A unified control scheme for robust operation.
    * **Manual (M):** Direct control via arrow keys.
    * **Semi-Auto (S):** Set-and-hold thrust/rudder via arrow keys.
    * **Autohelm (A):** Maintain an adjustable heading and speed via arrow keys.
    * **Waypoint (W):** Navigate a route with adjustable speed via arrow keys.

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
Up / Down Arrows	Manual	Apply forward / reverse thrust.
Up / Down Arrows	Semi-Auto	Increase / Decrease target thrust.
Up / Down Arrows	Autohelm / Waypoint	Increase / Decrease target speed.
Left / Right Arrows	Manual	Apply port / starboard rudder.
Left / Right Arrows	Semi-Auto	Adjust target rudder port / starboard.
Left / Right Arrows	Autohelm	Adjust target heading.
Left Mouse Click	Any	Add a waypoint at the cursor's location.
Mouse Wheel	Any	Zoom the map in or out.