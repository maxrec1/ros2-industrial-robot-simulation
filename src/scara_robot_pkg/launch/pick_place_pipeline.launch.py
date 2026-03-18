#!/usr/bin/python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    scara_pkg = get_package_share_directory('scara_robot_pkg')
    moveit_pkg = get_package_share_directory('scara_moveit_config')

    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(scara_pkg, 'launch', 'scara_conveyor_gazebo.launch.py')
        ),
        launch_arguments={'launch_rviz': 'False'}.items(),
    )

    moveit_launch = TimerAction(
        period=6.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(moveit_pkg, 'launch', 'demo_with_controllers.launch.py')
                ),
                launch_arguments={
                    'use_gazebo_controllers': 'True',
                    'rviz_tutorial': 'False',
                    'db': 'False',
                }.items(),
            )
        ],
    )

    pick_place_config = os.path.join(scara_pkg, 'config', 'pick_place_joints.yaml')
    pick_place_cycle = TimerAction(
        period=14.0,
        actions=[
            Node(
                package='scara_robot_pkg',
                executable='pick_place_cycle',
                output='screen',
                parameters=[{'config_path': pick_place_config}],
            )
        ],
    )

    return LaunchDescription([
        gazebo_launch,
        moveit_launch,
        pick_place_cycle,
    ])
