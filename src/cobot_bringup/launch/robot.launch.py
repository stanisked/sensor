#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    cobot_bringup_dir = get_package_share_directory('cobot_bringup')
    cobot_driver_dir = get_package_share_directory('cobot_driver')
    cobot_camera_dir = get_package_share_directory('cobot_camera')
    ldlidar_dir = get_package_share_directory('ldlidar_stl_ros2')

    camera_config = os.path.join(cobot_camera_dir, 'config', 'camera_config.yaml')
    
    # Get port configuration from environment or use defaults
    wheel_port = os.environ.get('WHEEL_PORT', '/dev/ttyCH341_motors')
    lidar_port = os.environ.get('LIDAR_PORT', '/dev/ttyUSB0')
    camera_url = os.environ.get('CAMERA_URL', 'http://192.168.1.100:81/stream')

    return LaunchDescription([
        # Wheel driver node
        Node(
            package='cobot_driver',
            executable='wheel_driver',
            name='wheel_driver',
            parameters=[{
                'port': wheel_port,
                'baud': 115200,
            }],
            output='screen',
        ),

        # Camera driver node
        Node(
            package='cobot_camera',
            executable='camera_driver',
            name='camera_driver',
            parameters=[{
                'camera_url': camera_url,
                'frame_rate': 30,
                'frame_id': 'camera',
            }],
            output='screen',
        ),

        # LDROBOT LiDAR (D500 / STL-27L)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(ldlidar_dir, 'launch', 'stl27l.launch.py')
            ),
            launch_arguments={
                'port_name': lidar_port,
            }.items(),
        ),
    ])
