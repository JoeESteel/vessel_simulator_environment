Autonomous Vessel Simulator
This project is a Python-based simulator for developing and testing autonomous navigation algorithms for a marine vessel. It uses the Pygame library to create a 2D world with a realistic geographic coordinate system, allowing for the rapid prototyping of control logic before deployment on physical hardware.

The codebase is intentionally modular, separating the simulation environment (world), the vessel's physics (vessel), and the navigation logic (controller) to ensure the control code can be easily transferred to a real-world platform like a Raspberry Pi.

Current Status
The simulator is functional with a physics model and a modular controller supporting multiple modes. The navigation is based on a PID controller for heading adjustments. Recent bug fixes have corrected issues with navigational heading calculations and autopilot/waypoint steering logic.

Features Implemented
Modular Architecture: Code is split into main.py, world.py, vessel.py, and controller.py for clarity and portability.

Geographic Coordinate System: The world is based on real Latitude and Longitude coordinates, centered on the Southampton area.

Dynamic Camera: The view follows the vessel and supports zooming with the mouse wheel.

Visual Feedback: Includes a dynamic scale bar, a continuous vessel track line, and periodic breadcrumbs.

Multiple Control Modes:

Manual (M): Direct, real-time control of thrust and rudder.

Semi-Auto (S): Set and hold specific thrust and rudder percentages.

Autohelm (A): Maintain a target heading. The target can be set automatically to the current heading on activation and then adjusted.

Waypoint (W): Navigate through a sequence of waypoints set by clicking on the map.

Project Setup and Execution
1. Prerequisites
Python 3.8+

Git

2. Setup
Clone the Repository:

git clone <your-repository-url>
cd <your-repository-name>

Create and Activate a Virtual Environment:

# Create the venv
python -m venv venv
# Activate it (on Windows Git Bash)
source venv/Scripts/activate

Install Dependencies:

pip install pygame

3. Running the Simulator
The project uses a src directory. To ensure the relative imports work correctly, you must run the application as a module from the root directory of the project.

python -m src.main

Simulator Controls
Key(s)

Mode(s)

Action

M

Any

Switch to Manual mode.

S

Any

Switch to Semi-Auto mode.

A

Any

Switch to Autohelm mode (sets target to current heading).

W

Any

Switch to Waypoint mode.

Up / Down Arrows

Manual

Apply forward / reverse thrust.

Left / Right Arrows

Manual

Apply port / starboard rudder.

Left / Right Arrows

Autohelm

Adjust target heading by +/- 0.5 degrees.

Q / A

Semi-Auto

Increase / Decrease target thrust percentage.

Z / X

Semi-Auto

Increase / Decrease target rudder percentage.

Left Mouse Click

Any

Add a waypoint at the cursor's location.

Mouse Wheel

Any

Zoom the map in or out.

Roadmap & Next Steps
The following features are planned for the next development phase to enhance the navigation capabilities and user feedback.

1. Implement Track-Following Logic
The current Waypoint mode uses a direct "go-to" approach, constantly pointing the vessel at the next waypoint. This is simple but inefficient, as it doesn't account for drift from wind or current and can lead to "S" curves when arriving at waypoints.

The next evolution is to implement a Track-Following mode.

Concept: The controller will calculate the ideal straight line (the "track" or "leg") between the last waypoint and the active one.

Cross-Track Error (XTE): The primary metric will be the vessel's perpendicular distance from this line, known as the Cross-Track Error.

Control Objective: The PID controller's goal will be to derive a heading that minimizes both the XTE (getting back to the line) and the heading error (pointing along the line). This will result in much smoother and more robust navigation that actively corrects for drift.

2. Enhanced UI & Visualization
To support the new navigation mode and provide better insight, the UI will be updated.

Display XTE: The on-screen data will be updated to show the current Cross-Track Error in meters when in a navigation mode.

Active Leg Highlighting: The current route leg (from the last waypoint to the next) will be drawn in a brighter, distinct color to make the intended path obvious.

Heading & Bearing Lines:

A "heading line" will be drawn from the front of the vessel to visualize its current heading.

A "bearing line" will be drawn from the vessel directly to the active waypoint, making it easy to see the difference between the vessel's heading and the direct bearing to the target.