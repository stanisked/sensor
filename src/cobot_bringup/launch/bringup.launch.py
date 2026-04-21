import os

from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command


def generate_launch_description():

    urdf_file = os.path.join(
        get_package_share_directory('cobot_description'),
        'urdf',
        'cobot.urdf'
    )

    controller_config = os.path.join(
        get_package_share_directory('cobot_bringup'),
        'config',
        'controllers.yaml'
    )

    robot_description = ParameterValue(
        Command(['cat ', urdf_file]),
        value_type=str
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}],
        output='screen'
    )

    ros2_control_node = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[
            {'robot_description': robot_description},
            controller_config
        ],
        output='screen'
    )

    return LaunchDescription([
        robot_state_publisher,
        ros2_control_node
    ])
