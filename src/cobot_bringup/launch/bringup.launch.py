from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command

import os

def generate_launch_description():

    # Пути
    description_pkg = get_package_share_directory('cobot_description')
    bringup_pkg = get_package_share_directory('cobot_bringup')

    urdf_file = os.path.join(description_pkg, 'urdf', 'cobot.urdf')
    controllers_file = os.path.join(bringup_pkg, 'config', 'controllers.yaml')

    # Читаем URDF
    with open(urdf_file, 'r') as f:
        robot_description = f.read()

    # robot_state_publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description
        }]
    )

    # ros2_control_node
    control_node = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[
            {'robot_description': robot_description},
            controllers_file
        ],
        output='screen',
    )

    return LaunchDescription([
        robot_state_publisher_node,
        control_node,
    ])
