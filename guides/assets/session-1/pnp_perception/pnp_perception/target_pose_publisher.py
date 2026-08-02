#!/usr/bin/env python3

import math

import rclpy
from geometry_msgs.msg import PoseStamped
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy


class TargetPosePublisher(Node):
    """Publish a configurable target pose for the Session 1 ROS graph exercise."""

    def __init__(self) -> None:
        super().__init__('target_pose_publisher')

        self.declare_parameter('topic_name', '/perception/target_pose')
        self.declare_parameter('publish_rate_hz', 2.0)
        self.declare_parameter('frame_id', 'world')
        self.declare_parameter('target_x', 0.16)
        self.declare_parameter('target_y', 0.0)
        self.declare_parameter('target_z', 0.12)

        self.topic_name = self.get_parameter('topic_name').value
        self.publish_rate_hz = float(self.get_parameter('publish_rate_hz').value)
        self.frame_id = self.get_parameter('frame_id').value
        self.target = (
            float(self.get_parameter('target_x').value),
            float(self.get_parameter('target_y').value),
            float(self.get_parameter('target_z').value),
        )
        self._validate_parameters()

        qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
        )
        self.publisher = self.create_publisher(PoseStamped, self.topic_name, qos)
        self.timer = self.create_timer(1.0 / self.publish_rate_hz, self._publish_pose)
        self.published_count = 0
        self._waiting_for_clock_reported = False

        self.get_logger().info(
            'READY '
            f'topic={self.topic_name} frame_id={self.frame_id} '
            f'rate_hz={self.publish_rate_hz:.3f} '
            f'position=({self.target[0]:.3f}, {self.target[1]:.3f}, {self.target[2]:.3f})'
        )

    def _validate_parameters(self) -> None:
        if not isinstance(self.topic_name, str) or not self.topic_name.startswith('/'):
            raise ValueError('topic_name must be an absolute ROS topic beginning with /')
        if not isinstance(self.frame_id, str) or not self.frame_id:
            raise ValueError('frame_id must be a non-empty string')
        if not math.isfinite(self.publish_rate_hz) or self.publish_rate_hz <= 0.0:
            raise ValueError('publish_rate_hz must be a finite positive number')
        if not all(math.isfinite(value) for value in self.target):
            raise ValueError('target_x, target_y and target_z must be finite')
    def _publish_pose(self) -> None:
        now_ns = self.get_clock().now().nanoseconds

        # When sim time is enabled, /clock can still be zero just after startup.
        if now_ns == 0:
            if not self._waiting_for_clock_reported:
                self.get_logger().info('WAITING_FOR_SIM_TIME')
                self._waiting_for_clock_reported = True
            return

        message = PoseStamped()
        message.header.frame_id = self.frame_id
        message.header.stamp.sec = now_ns // 1_000_000_000
        message.header.stamp.nanosec = now_ns % 1_000_000_000
        message.pose.position.x = self.target[0]
        message.pose.position.y = self.target[1]
        message.pose.position.z = self.target[2]
        message.pose.orientation.w = 1.0

        self.publisher.publish(message)
        self.published_count += 1
        self.get_logger().info(
            'PUBLISH '
            f'count={self.published_count} frame_id={message.header.frame_id} '
            f'stamp={message.header.stamp.sec}.{message.header.stamp.nanosec:09d} '
            f'position=({message.pose.position.x:.3f}, '
            f'{message.pose.position.y:.3f}, {message.pose.position.z:.3f})'
        )
def main(args=None) -> None:
    rclpy.init(args=args)
    node = TargetPosePublisher()
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
