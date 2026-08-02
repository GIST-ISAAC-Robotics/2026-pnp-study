from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution


def generate_launch_description() -> LaunchDescription:
    params_file = LaunchConfiguration('params_file')
    default_params_file = PathJoinSubstitution(
        [FindPackageShare('pnp_bringup'), 'config', 'common.yaml']
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                'params_file',
                default_value=default_params_file,
                description='Absolute path to the shared Session 1 parameter YAML',
            ),
            Node(
                package='pnp_orchestrator',
                executable='target_pose_monitor',
                name='target_pose_monitor',
                output='screen',
                parameters=[params_file],
            ),
            Node(
                package='pnp_perception',
                executable='target_pose_publisher',
                name='target_pose_publisher',
                output='screen',
                parameters=[params_file],
            ),
        ]
    )
