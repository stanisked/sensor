#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    package_dir = get_package_share_directory('cobot_camera')
    config_file = os.path.join(package_dir, 'config', 'camera_config.yaml')

    return LaunchDescription([
        DeclareLaunchArgument(
            'config_file',
            default_value=config_file,
            description='Camera config file path'
        ),
        Node(
            package='cobot_camera',
            executable='camera_driver',
            name='camera_driver',
            parameters=[LaunchConfiguration('config_file')],
            output='screen',
        ),
    ])
