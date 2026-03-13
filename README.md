# ROS2 Industrial Robot Simulation

A ROS2-based simulation workspace for an industrial SCARA robot, including a conveyor belt system and robot visualization.

## ROS2 Version

**ROS2 Humble Hawksbill** (Ubuntu 22.04 LTS)

## Packages

### `scara_robot_pkg`
Visualization package for the SCARA robot. Contains the URDF model, mesh files (STL), RViz configuration, and a launch file to view the robot with interactive joint controls.

**Launch:**
```bash
ros2 launch scara_robot_pkg view_robot.launch.py
```

Opens RViz with the SCARA robot model and `joint_state_publisher_gui` for manually moving joints.

### `IFRA_ConveyorBelt`
Gazebo conveyor belt simulation plugin, split into three sub-packages:
- **`conveyorbelt_msgs`** — Custom ROS2 service/message definitions for controlling the belt
- **`conveyorbelt_gazebo`** — Gazebo plugin implementation
- **`ros2_conveyorbelt`** — ROS2 integration node and launch files

## Dependencies

```bash
sudo apt install ros-humble-gazebo-ros-pkgs \
                 ros-humble-joint-state-publisher-gui \
                 ros-humble-robot-state-publisher
```

## Build

```bash
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```
