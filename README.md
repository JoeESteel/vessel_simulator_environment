Autonomous Vessel Simulator
This project is a 2D simulation environment built with Pygame to develop and test autonomous navigation algorithms for a marine surface vessel. The simulator operates in a realistic latitude/longitude coordinate system and provides the foundation for building complex autonomous behaviors.

Features
Geographical Coordinate System: The world is based on real latitude and longitude, centered on Southampton, UK.

Modular Architecture: The code is cleanly separated into four main modules:

world.py: The simulation environment, graphics, and camera.

vessel.py: The vessel's physics model and state.

controller.py: The "brain" containing all control logic.

main.py: The main application orchestrator.

Dynamic Camera: The view follows the vessel, with mouse-wheel zooming.

Multiple Control Modes:

(M)anual: Direct keyboard control of thrust and rudder.

(A)utohelm: Automatically maintains a target heading and speed (currently hardcoded, future work to make adjustable).

(W)aypoint: Navigates a sequence of waypoints set by the user.

Visual Tracking: Displays a continuous track line of the vessel's exact path and periodic "breadcrumbs" to mark its progress over time.

Project Structure
The project is organized within a src directory to keep the source code neatly separated from project-level files.

vessel_simulator_environment/
├── .gitignore
├── README.md
├── venv/
└── src/
    ├── __init__.py  (can be empty)
    ├── main.py
    ├── world.py
    ├── vessel.py
    └── controller.py

Setup and Installation
Follow these steps to set up your local development environment.

1. Prerequisites
Python 3.8+

Git

2. Clone the Repository
Open a terminal (like Git Bash) and clone the repository to your local machine:

git clone <your-repository-url>
cd vessel_simulator_environment

3. Create and Activate Virtual Environment
It is highly recommended to use a virtual environment to manage project dependencies.

# Create the virtual environment
python -m venv venv

# Activate the environment
# On Windows (Git Bash)
source venv/Scripts/activate
# On macOS/Linux
source venv/bin/activate

You will know the environment is active when you see (venv) at the beginning of your terminal prompt.

4. Install Dependencies
Install the required Python packages using pip.

pip install pygame

How to Run the Simulator
With your virtual environment activated, run the simulator from the root directory of the project using the following command:

python -m src.main

This will launch the Pygame window and start the simulation.

Controls
Camera Zoom: Use the Mouse Wheel to zoom in and out.

Mode Switching:

M Key: Switch to Manual mode.

A Key: Switch to Autohelm mode.

W Key: Switch to Waypoint mode.

Manual Mode Controls:

Up Arrow: Apply forward thrust.

Down Arrow: Apply reverse thrust.

Left Arrow: Steer left (port).

Right Arrow: Steer right (starboard).

Waypoint Mode Controls:

Left Mouse Click: Add a new waypoint at the cursor's location. The vessel will immediately start navigating towards the first waypoint in the list.