from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def _launch_file(package_name: str, file_name: str) -> PythonLaunchDescriptionSource:
    return PythonLaunchDescriptionSource(
        PathJoinSubstitution(
            [FindPackageShare(package_name), 'launch', file_name]
        )
    )


def generate_launch_description() -> LaunchDescription:
    world = LaunchConfiguration('world')
    start_rviz = LaunchConfiguration('start_rviz')
    params_file = LaunchConfiguration('params_file')

    default_params_file = PathJoinSubstitution(
        [FindPackageShare('pnp_bringup'), 'config', 'common.yaml']
    )

    gazebo = IncludeLaunchDescription(
        _launch_file(
            'open_manipulator_bringup',
            'open_manipulator_x_gazebo.launch.py',
        ),
        launch_arguments={'world': world}.items(),
    )

    moveit = IncludeLaunchDescription(
        _launch_file(
            'open_manipulator_moveit_config',
            'open_manipulator_x_moveit.launch.py',
        ),
        launch_arguments={
            'use_sim': 'true',
            'start_rviz': start_rviz,
        }.items(),
    )

    session1_nodes = IncludeLaunchDescription(
        _launch_file('pnp_bringup', 'core_skeleton.launch.py'),
        launch_arguments={'params_file': params_file}.items(),
    )

    orchestrator = Node(
        package='pnp_orchestrator',
        executable='orchestrator',
        name='pnp_orchestrator',
        output='screen',
        parameters=[{'use_sim_time': True}],
    )

    dummy_pick_place_server = Node(
        package='pnp_evaluation',
        executable='dummy_pick_place_server',
        name='dummy_pick_place_server',
        output='screen',
        parameters=[{'use_sim_time': True}],
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                'world',
                default_value='empty_world',
                description=(
                    'ROBOTIS world name without the .sdf extension'
                ),
            ),
            DeclareLaunchArgument(
                'start_rviz',
                default_value='true',
                description='Start the MoveIt RViz window',
            ),
            DeclareLaunchArgument(
                'params_file',
                default_value=default_params_file,
                description='Shared parameters for the Session 1 nodes',
            ),
            gazebo,
            session1_nodes,
            orchestrator,
            dummy_pick_place_server,
            TimerAction(period=3.0, actions=[moveit]),
        ]
    )
