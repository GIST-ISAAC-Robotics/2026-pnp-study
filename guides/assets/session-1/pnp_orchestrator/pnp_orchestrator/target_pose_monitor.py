#!/usr/bin/env python3

import math

import rclpy
from geometry_msgs.msg import PoseStamped
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from rclpy.time import Time


class TargetPoseMonitor(Node):
    """Accept valid target poses and explain why invalid poses are rejected."""

    def __init__(self) -> None:
        super().__init__('target_pose_monitor')

        self.declare_parameter('topic_name', '/perception/target_pose')
        self.declare_parameter('expected_frame', 'world')
        self.declare_parameter('max_age_sec', 0.5)
        self.declare_parameter('future_tolerance_sec', 0.05)
        self.declare_parameter('workspace_min_x', 0.10)
        self.declare_parameter('workspace_max_x', 0.40)
        self.declare_parameter('workspace_min_y', -0.20)
        self.declare_parameter('workspace_max_y', 0.20)
        self.declare_parameter('workspace_min_z', 0.05)
        self.declare_parameter('workspace_max_z', 0.30)

        self.topic_name = self.get_parameter('topic_name').value
        self.expected_frame = self.get_parameter('expected_frame').value
        self.max_age_sec = float(self.get_parameter('max_age_sec').value)
        self.future_tolerance_sec = float(
            self.get_parameter('future_tolerance_sec').value
        )
        self.bounds = {
            'x': (
                float(self.get_parameter('workspace_min_x').value),
                float(self.get_parameter('workspace_max_x').value),
            ),
            'y': (
                float(self.get_parameter('workspace_min_y').value),
                float(self.get_parameter('workspace_max_y').value),
            ),
            'z': (
                float(self.get_parameter('workspace_min_z').value),
                float(self.get_parameter('workspace_max_z').value),
            ),
        }
        self._validate_parameters()

        qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
        )
        self.subscription = self.create_subscription(
            PoseStamped,
            self.topic_name,
            self._on_pose,
            qos,
        )
        self.accepted_count = 0
        self.rejected_count = 0

        self.get_logger().info(
            'READY '
            f'topic={self.topic_name} expected_frame={self.expected_frame} '
            f'max_age_sec={self.max_age_sec:.3f} '
            f'workspace=x[{self.bounds["x"][0]:.3f},{self.bounds["x"][1]:.3f}] '
            f'y[{self.bounds["y"][0]:.3f},{self.bounds["y"][1]:.3f}] '
            f'z[{self.bounds["z"][0]:.3f},{self.bounds["z"][1]:.3f}]'
        )

    def _validate_parameters(self) -> None:
        if not isinstance(self.topic_name, str) or not self.topic_name.startswith('/'):
            raise ValueError('topic_name must be an absolute ROS topic beginning with /')
        if not isinstance(self.expected_frame, str) or not self.expected_frame:
            raise ValueError('expected_frame must be a non-empty string')
        if not math.isfinite(self.max_age_sec) or self.max_age_sec <= 0.0:
            raise ValueError('max_age_sec must be a finite positive number')
        if (
            not math.isfinite(self.future_tolerance_sec)
            or self.future_tolerance_sec < 0.0
        ):
            raise ValueError('future_tolerance_sec must be finite and non-negative')
        for axis, (minimum, maximum) in self.bounds.items():
            if not math.isfinite(minimum) or not math.isfinite(maximum):
                raise ValueError(f'workspace {axis} bounds must be finite')
            if minimum > maximum:
                raise ValueError(f'workspace_min_{axis} must be <= workspace_max_{axis}')

    def _reject(self, reason: str, detail: str) -> None:
        self.rejected_count += 1
        self.get_logger().warning(
            f'REJECT count={self.rejected_count} reason={reason} {detail}'
        )

    def _on_pose(self, message: PoseStamped) -> None:
        if message.header.frame_id != self.expected_frame:
            self._reject(
                'FRAME_MISMATCH',
                f'expected={self.expected_frame} actual={message.header.frame_id}',
            )
            return

        stamp_ns = Time.from_msg(message.header.stamp).nanoseconds
        if stamp_ns == 0:
            self._reject('ZERO_STAMP', 'timestamp=0.000000000')
            return

        age_sec = (self.get_clock().now().nanoseconds - stamp_ns) / 1_000_000_000.0
        if age_sec < -self.future_tolerance_sec:
            self._reject(
                'FUTURE_TIMESTAMP',
                f'age_sec={age_sec:.3f} tolerance_sec={self.future_tolerance_sec:.3f}',
            )
            return
        if age_sec > self.max_age_sec:
            self._reject(
                'STALE_TIMESTAMP',
                f'age_sec={age_sec:.3f} max_age_sec={self.max_age_sec:.3f}',
            )
            return

        coordinates = {
            'x': message.pose.position.x,
            'y': message.pose.position.y,
            'z': message.pose.position.z,
        }
        if not all(math.isfinite(value) for value in coordinates.values()):
            self._reject('NON_FINITE_POSITION', f'position={coordinates}')
            return

        outside = [
            axis
            for axis, value in coordinates.items()
            if not self.bounds[axis][0] <= value <= self.bounds[axis][1]
        ]
        if outside:
            self._reject(
                'OUT_OF_WORKSPACE',
                'position=('
                f'{coordinates["x"]:.3f},{coordinates["y"]:.3f},{coordinates["z"]:.3f}) '
                f'outside={",".join(outside)}',
            )
            return

        self.accepted_count += 1
        self.get_logger().info(
            'ACCEPT '
            f'count={self.accepted_count} frame_id={message.header.frame_id} '
            f'age_sec={age_sec:.3f} '
            f'position=({coordinates["x"]:.3f},'
            f'{coordinates["y"]:.3f},{coordinates["z"]:.3f})'
        )


def main(args=None) -> None:
    rclpy.init(args=args)
    node = TargetPoseMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
