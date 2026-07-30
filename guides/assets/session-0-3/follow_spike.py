#!/usr/bin/env python3
"""Session 0-3 B-2: 10 Hz x 5 s, 1-in-flight and latest-wins."""

import math
import statistics
import time

import rclpy
from geometry_msgs.msg import Pose
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from ros_gz_interfaces.msg import Entity
from ros_gz_interfaces.srv import SetEntityPose

SERVICE = "/world/week0_spike/set_pose"
MODEL = "spike_cube"
RATE_HZ = 10.0
DURATION = 5.0
TOTAL = int(RATE_HZ * DURATION)
TIMEOUT_S = 0.5
A = (0.25, 0.0, 0.025)


class Follower(Node):
    def __init__(self):
        super().__init__("spike_b_follower")
        self.cli = self.create_client(SetEntityPose, SERVICE)
        if not self.cli.wait_for_service(timeout_sec=5.0):
            raise RuntimeError(f"service not available: {SERVICE}")

        self.inflight = None
        self.inflight_started = None
        self.timeout_counted = False
        self.pending = None
        self.sample_index = 0
        self.generated = 0
        self.sent = 0
        self.completed = 0
        self.failures = 0
        self.dropped = 0
        self.timeouts = 0
        self.max_inflight = 0
        self.max_backlog = 0
        self.rtts_ms = []
        self.actual = None
        self.odom_sequence = 0
        self.last_send_odom_sequence = 0

        self.create_subscription(
            Odometry,
            "/spike_cube/odometry",
            self.on_odom,
            qos_profile_sensor_data,
        )
        self.timer = self.create_timer(1.0 / RATE_HZ, self.on_tick)
        self.watch = self.create_timer(0.05, self.on_watchdog)

    def target(self, elapsed):
        angle = 2.0 * math.pi * elapsed / DURATION
        pose = Pose()
        pose.position.x = A[0] + 0.03 * (1.0 - math.cos(angle))
        pose.position.y = A[1] + 0.05 * math.sin(angle)
        pose.position.z = A[2]
        pose.orientation.w = 1.0
        return pose

    def on_tick(self):
        if self.sample_index >= TOTAL:
            self.timer.cancel()
            return

        self.sample_index += 1
        self.generated += 1
        pose = self.target(self.sample_index / RATE_HZ)
        if self.inflight is not None:
            if self.pending is not None:
                self.dropped += 1
            self.pending = pose
            self.max_backlog = max(self.max_backlog, 2)
            return
        self.send(pose)

    def send(self, pose):
        request = SetEntityPose.Request()
        request.entity.name = MODEL
        request.entity.type = Entity.MODEL
        request.pose = pose

        self.sent += 1
        self.last_send_odom_sequence = self.odom_sequence
        self.inflight_started = time.monotonic()
        self.timeout_counted = False
        self.inflight = self.cli.call_async(request)
        self.inflight.add_done_callback(self.on_done)
        self.max_inflight = max(self.max_inflight, 1)
        self.max_backlog = max(self.max_backlog, 1)

    def on_done(self, future):
        self.rtts_ms.append(
            (time.monotonic() - self.inflight_started) * 1000.0
        )
        self.completed += 1
        try:
            response = future.result()
            if response is None or not response.success:
                self.failures += 1
        except Exception as exc:
            self.failures += 1
            self.get_logger().error(f"service future failed: {exc!r}")

        self.inflight = None
        self.inflight_started = None
        if self.pending is not None:
            next_pose, self.pending = self.pending, None
            self.send(next_pose)

    def on_watchdog(self):
        if (
            self.inflight is not None
            and not self.timeout_counted
            and time.monotonic() - self.inflight_started > TIMEOUT_S
        ):
            self.timeouts += 1
            self.timeout_counted = True
            # Keep the outstanding future. Clearing it would violate
            # the 1-in-flight contract.

    def on_odom(self, message):
        self.actual = message.pose.pose
        self.odom_sequence += 1

    def report(self):
        final_completed = (
            self.generated == TOTAL
            and self.completed == self.sent
            and self.inflight is None
            and self.pending is None
        )
        final_error_mm = float("inf")
        if self.actual is not None:
            dx = self.actual.position.x - A[0]
            dy = self.actual.position.y - A[1]
            dz = self.actual.position.z - A[2]
            final_error_mm = 1000.0 * math.sqrt(dx * dx + dy * dy + dz * dz)

        mean_ms = (
            statistics.mean(self.rtts_ms) if self.rtts_ms else float("nan")
        )
        max_ms = max(self.rtts_ms) if self.rtts_ms else float("nan")
        passed = (
            final_completed
            and self.failures == 0
            and self.timeouts == 0
            and self.max_inflight <= 1
            and self.max_backlog <= 2
            and final_error_mm <= 1.0
        )
        print(
            f"generated={self.generated} sent={self.sent} "
            f"completed={self.completed} failures={self.failures} "
            f"dropped={self.dropped} timeouts={self.timeouts} "
            f"max_inflight={self.max_inflight} "
            f"max_backlog={self.max_backlog}"
        )
        print(f"rtt_mean_ms={mean_ms:.3f} rtt_max_ms={max_ms:.3f}")
        print(
            f"final_completed={final_completed} "
            f"final_error_mm={final_error_mm:.3f} pass={passed}"
        )
        return passed


def main():
    rclpy.init()
    node = Follower()
    passed = False
    try:
        deadline = time.monotonic() + DURATION + 3.0
        while rclpy.ok() and time.monotonic() < deadline:
            rclpy.spin_once(node, timeout_sec=0.05)
            if (
                node.sample_index == TOTAL
                and node.inflight is None
                and node.pending is None
                and node.actual is not None
                and node.odom_sequence >= node.last_send_odom_sequence + 2
            ):
                break
    finally:
        passed = node.report()
        node.destroy_node()
        rclpy.shutdown()
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
