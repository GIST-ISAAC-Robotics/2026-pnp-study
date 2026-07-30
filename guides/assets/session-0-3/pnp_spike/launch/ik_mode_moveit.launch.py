#!/usr/bin/env python3
"""MoveIt launch wrapper with an explicit position_only_ik argument."""

import os
from pathlib import Path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from moveit_configs_utils import MoveItConfigsBuilder


def _as_bool(value):
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes", "on"}:
        return True
    if normalized in {"false", "0", "no", "off"}:
        return False
    raise RuntimeError(
        f"position_only_ik must be true or false, got {value!r}"
    )


def _launch_setup(context):
    position_only = _as_bool(
        LaunchConfiguration("position_only_ik").perform(context)
    )
    use_sim = LaunchConfiguration("use_sim")
    start_rviz = LaunchConfiguration("start_rviz")
    warehouse_path = LaunchConfiguration("warehouse_sqlite_path")

    moveit_config = (
        MoveItConfigsBuilder(
            robot_name="open_manipulator_x",
            package_name="open_manipulator_moveit_config",
        )
        .robot_description_semantic(
            str(Path("config") / "open_manipulator_x"
                / "open_manipulator_x.srdf")
        )
        .joint_limits(
            str(Path("config") / "open_manipulator_x" / "joint_limits.yaml")
        )
        .trajectory_execution(
            str(Path("config") / "open_manipulator_x"
                / "moveit_controllers.yaml")
        )
        .robot_description_kinematics(
            str(Path("config") / "open_manipulator_x" / "kinematics.yaml")
        )
        .to_moveit_configs()
    )
    moveit_config.robot_description_kinematics[
        "robot_description_kinematics"
    ]["arm"]["position_only_ik"] = position_only

    warehouse_config = {
        "warehouse_plugin": "warehouse_ros_sqlite::DatabaseConnection",
        "warehouse_host": warehouse_path,
    }
    move_group = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            moveit_config.to_dict(),
            warehouse_config,
            {
                "use_sim_time": use_sim,
                "publish_robot_description_semantic": True,
            },
        ],
    )

    rviz_config = PathJoinSubstitution(
        [
            FindPackageShare("open_manipulator_moveit_config"),
            "config",
            "moveit.rviz",
        ]
    )
    rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2_moveit",
        output="log",
        condition=IfCondition(start_rviz),
        arguments=["-d", rviz_config],
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.planning_pipelines,
            moveit_config.joint_limits,
            warehouse_config,
            {"use_sim_time": use_sim},
        ],
    )
    return [move_group, rviz]


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("position_only_ik", default_value="true"),
            DeclareLaunchArgument("start_rviz", default_value="true"),
            DeclareLaunchArgument("use_sim", default_value="true"),
            DeclareLaunchArgument(
                "warehouse_sqlite_path",
                default_value=os.path.expanduser(
                    "~/.ros/warehouse_ros.sqlite"
                ),
            ),
            OpaqueFunction(function=_launch_setup),
        ]
    )
