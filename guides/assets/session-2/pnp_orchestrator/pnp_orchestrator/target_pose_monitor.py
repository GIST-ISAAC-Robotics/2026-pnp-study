#!/usr/bin/env python3

from geometry_msgs.msg import PoseStamped
import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy


class TargetPoseMonitor(Node):
    """Receive target poses and print their important fields."""

    def __init__(self) -> None:
        super().__init__('target_pose_monitor')

        self.declare_parameter('topic_name', '/perception/target_pose')

        self.topic_name = self.get_parameter('topic_name').value
        if not isinstance(self.topic_name, str) or not self.topic_name.startswith('/'):
            raise ValueError('topic_name must be an absolute ROS topic beginning with /')

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
        self.received_count = 0

        self.get_logger().info(f'READY topic={self.topic_name}')

    def _on_pose(self, message: PoseStamped) -> None:
        self.received_count += 1
        self.get_logger().info(
            'RECEIVE '
            f'count={self.received_count} frame_id={message.header.frame_id} '
            f'stamp={message.header.stamp.sec}.{message.header.stamp.nanosec:09d} '
            f'position=({message.pose.position.x:.3f},'
            f'{message.pose.position.y:.3f},{message.pose.position.z:.3f})'
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
