from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

from moveit_configs_utils import MoveItConfigsBuilder


def generate_launch_description():
    moveit_config = (
        MoveItConfigsBuilder("cobot", package_name="cobot_moveit_config")
        .robot_description_semantic(file_path="config/cobot.srdf")
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .to_moveit_configs()
    )

    move_group_configuration = {
        "publish_robot_description_semantic": True,
        "allow_trajectory_execution": True,
        "capabilities": ParameterValue("", value_type=str),
        "disable_capabilities": ParameterValue("", value_type=str),
        "publish_planning_scene": True,
        "publish_geometry_updates": False,
        "publish_state_updates": True,
        "publish_transforms_updates": True,
        "monitor_dynamics": False,
    }

    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        arguments=[
            "--ros-args",
            "--log-level",
            "moveit.moveit.ros.occupancy_map_monitor:=fatal",
        ],
        parameters=[
            moveit_config.to_dict(),
            move_group_configuration,
        ],
    )

    return LaunchDescription([move_group_node])
