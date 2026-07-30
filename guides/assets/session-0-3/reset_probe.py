#!/usr/bin/env python3
"""Session 0-3 B-3: reset a falling object and measure the actual state."""

import math
import time

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from ros_gz_interfaces.msg import Entity
from ros_gz_interfaces.srv import ControlWorld, SetEntityPose

SET_POSE = "/world/week0_spike/set_pose"
CONTROL = "/world/week0_spike/control"
ODOM = "/spike_cube/odometry"
A = (0.25, 0.0, 0.025)

POSITION_TOL_MM = 1.0
ORIENTATION_TOL_DEG = 1.0
LINEAR_SPEED_TOL = 0.005
ANGULAR_SPEED_TOL = 0.01
QUATERNION_NORM_TOL = 0.001


class Probe(Node):
    def __init__(self):
        super().__init__("spike_b_reset_probe")
        self.set_pose = self.create_client(SetEntityPose, SET_POSE)
        self.control = self.create_client(ControlWorld, CONTROL)
        self.latest = None
        self.sequence = 0
        self.create_subscription(
            Odometry, ODOM, self.on_odom, qos_profile_sensor_data
        )
        for client, name in (
            (self.set_pose, SET_POSE),
            (self.control, CONTROL),
        ):
            if not client.wait_for_service(timeout_sec=5.0):
                raise RuntimeError(f"service not available: {name}")

    def on_odom(self, message):
        self.latest = message
        self.sequence += 1

    def wait_for(self, predicate, timeout_s, label):
        deadline = time.monotonic() + timeout_s
        while rclpy.ok() and time.monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=0.02)
            if predicate():
                return
        raise RuntimeError(f"timeout while waiting for {label}")

    def call(self, client, request, label):
        future = client.call_async(request)
        self.wait_for(future.done, 5.0, label)
        response = future.result()
        if response is None or not response.success:
            raise RuntimeError(f"{label} returned success=false")

    def lift(self):
        request = SetEntityPose.Request()
        request.entity.name = "spike_cube"
        request.entity.type = Entity.MODEL
        request.pose.position.x = A[0] + 0.10
        request.pose.position.y = A[1] + 0.08
        request.pose.position.z = 0.50
        request.pose.orientation.w = 1.0
        self.call(self.set_pose, request, "lift")

    def set_initial_pose(self):
        request = SetEntityPose.Request()
        request.entity.name = "spike_cube"
        request.entity.type = Entity.MODEL
        request.pose.position.x = A[0]
        request.pose.position.y = A[1]
        request.pose.position.z = A[2]
        request.pose.orientation.w = 1.0
        self.call(self.set_pose, request, "set initial pose")

    def reset_candidate(self):
        request = ControlWorld.Request()
        request.world_control.reset.model_only = True
        self.call(self.control, request, "model reset")
        self.set_initial_pose()


def vector_norm(vector):
    return math.sqrt(
        vector.x * vector.x + vector.y * vector.y + vector.z * vector.z
    )


def measured_values(message):
    position = message.pose.pose.position
    orientation = message.pose.pose.orientation
    dx = position.x - A[0]
    dy = position.y - A[1]
    dz = position.z - A[2]
    position_mm = 1000.0 * math.sqrt(dx * dx + dy * dy + dz * dz)

    q_norm = math.sqrt(
        orientation.x * orientation.x
        + orientation.y * orientation.y
        + orientation.z * orientation.z
        + orientation.w * orientation.w
    )
    if not math.isfinite(q_norm) or q_norm == 0.0:
        orientation_deg = float("inf")
    else:
        dot = min(1.0, max(0.0, abs(orientation.w / q_norm)))
        orientation_deg = math.degrees(2.0 * math.acos(dot))

    linear = vector_norm(message.twist.twist.linear)
    angular = vector_norm(message.twist.twist.angular)
    return position_mm, orientation_deg, linear, angular, q_norm


def values_pass(values):
    pos_mm, ori_deg, linear, angular, q_norm = values
    return (
        pos_mm <= POSITION_TOL_MM
        and ori_deg <= ORIENTATION_TOL_DEG
        and linear <= LINEAR_SPEED_TOL
        and angular <= ANGULAR_SPEED_TOL
        and abs(q_norm - 1.0) <= QUATERNION_NORM_TOL
    )


def wait_for_settled(node, timeout_s, label):
    deadline = time.monotonic() + timeout_s
    last_sequence = node.sequence
    consecutive = 0
    latest_values = None
    while rclpy.ok() and time.monotonic() < deadline:
        rclpy.spin_once(node, timeout_sec=0.02)
        if node.sequence == last_sequence or node.latest is None:
            continue
        last_sequence = node.sequence
        latest_values = measured_values(node.latest)
        consecutive = consecutive + 1 if values_pass(latest_values) else 0
        if consecutive >= 3:
            return latest_values
    raise RuntimeError(
        f"timeout while waiting for {label}; "
        f"last_values={latest_values!r}"
    )


def main():
    rclpy.init()
    node = Probe()
    all_passed = True
    try:
        node.wait_for(lambda: node.latest is not None, 3.0, "first odometry")
        for trial in range(1, 4):
            node.reset_candidate()
            wait_for_settled(node, 3.0, "pre-trial settled state")
            before_lift = node.sequence
            node.lift()
            node.wait_for(
                lambda: (
                    node.sequence > before_lift
                    and node.latest.pose.pose.position.x > A[0] + 0.08
                    and node.latest.pose.pose.position.y > A[1] + 0.06
                    and node.latest.pose.pose.position.z > 0.40
                ),
                3.0,
                "measured lifted state",
            )
            node.wait_for(
                lambda: (
                    node.latest is not None
                    and vector_norm(node.latest.twist.twist.linear) > 0.20
                ),
                3.0,
                "measured falling state",
            )
            pre_reset_speed = vector_norm(node.latest.twist.twist.linear)

            reset_started = time.monotonic()
            node.reset_candidate()
            values = wait_for_settled(node, 3.0, "post-reset settled state")
            settle_ms = (time.monotonic() - reset_started) * 1000.0
            pos_mm, ori_deg, linear, angular, q_norm = values
            passed = values_pass(values)
            all_passed = all_passed and passed
            print(
                f"trial={trial} pre_reset_speed_mps={pre_reset_speed:.6f} "
                f"settle_ms={settle_ms:.3f} "
                f"position_error_mm={pos_mm:.6f} "
                f"orientation_error_deg={ori_deg:.6f} "
                f"linear_speed_mps={linear:.6f} "
                f"angular_speed_rad_s={angular:.6f} "
                f"quaternion_norm={q_norm:.9f} "
                f"state_measured=true pass={str(passed).lower()}"
            )
    finally:
        node.destroy_node()
        rclpy.shutdown()
    raise SystemExit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
