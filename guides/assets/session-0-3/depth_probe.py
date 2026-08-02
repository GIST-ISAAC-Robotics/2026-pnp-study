#!/usr/bin/env python3
"""Print statistics from one ROS 2 32FC1 depth image."""

import math
import struct
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image


class DepthProbe(Node):
    def __init__(self):
        super().__init__("depth_probe")
        self.done = False
        self.passed = False
        self.create_subscription(
            Image,
            "/rgbd_camera/depth_image",
            self.on_depth,
            qos_profile_sensor_data,
        )

    def fail(self, reason):
        print(f"DEPTH_PROBE_FAIL reason={reason}")
        self.done = True

    def on_depth(self, msg):
        if self.done:
            return

        if msg.encoding.upper() != "32FC1":
            self.fail(f"encoding={msg.encoding} expected=32FC1")
            return

        row_bytes = msg.width * 4
        expected_size = msg.step * msg.height
        if msg.step < row_bytes:
            self.fail(f"step={msg.step} row_bytes={row_bytes}")
            return
        if len(msg.data) < expected_size:
            self.fail(f"data_bytes={len(msg.data)} expected_at_least={expected_size}")
            return

        endian = ">" if msg.is_bigendian else "<"
        values = []
        raw = memoryview(msg.data)
        for row in range(msg.height):
            start = row * msg.step
            chunk = raw[start : start + row_bytes]
            values.extend(struct.unpack(f"{endian}{msg.width}f", chunk))

        finite_positive = [value for value in values if math.isfinite(value) and value > 0.0]
        nan_count = sum(math.isnan(value) for value in values)
        inf_count = sum(math.isinf(value) for value in values)
        zero_count = sum(value == 0.0 for value in values)
        negative_count = sum(math.isfinite(value) and value < 0.0 for value in values)
        center = values[(msg.height // 2) * msg.width + (msg.width // 2)]

        print(
            "DEPTH_PROBE "
            f"width={msg.width} height={msg.height} encoding={msg.encoding} "
            f"frame_id={msg.header.frame_id}"
        )
        print(
            "DEPTH_VALUES "
            f"valid={len(finite_positive)} nan={nan_count} inf={inf_count} "
            f"zero={zero_count} negative={negative_count}"
        )
        if finite_positive:
            print(
                "DEPTH_RANGE_M "
                f"min={min(finite_positive):.6f} "
                f"max={max(finite_positive):.6f} "
                f"center={center:.6f}"
            )
            self.passed = True
        else:
            print(f"DEPTH_RANGE_M no_positive_finite_values center={center}")

        self.done = True


def main():
    rclpy.init()
    node = DepthProbe()
    deadline = time.monotonic() + 15.0
    while rclpy.ok() and not node.done and time.monotonic() < deadline:
        rclpy.spin_once(node, timeout_sec=1.0)

    if not node.done:
        node.fail("no_depth_message_within_15s")

    passed = node.passed
    node.destroy_node()
    rclpy.shutdown()
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
