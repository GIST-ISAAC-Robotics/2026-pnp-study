import argparse
import time
import uuid

import rclpy
from action_msgs.msg import GoalStatus
from rclpy.action import ActionClient
from rclpy.node import Node

from pnp_interfaces.action import RunTrial


def _pose(frame_id, x, y, z):
    from geometry_msgs.msg import PoseStamped

    message = PoseStamped()
    message.header.frame_id = frame_id
    message.pose.position.x = x
    message.pose.position.y = y
    message.pose.position.z = z
    message.pose.orientation.w = 1.0
    return message


class ScenarioRunner(Node):
    def __init__(self, options):
        super().__init__('session2_scenario_runner')
        self._options = options
        self._client = ActionClient(self, RunTrial, '/task/run_trial')

    def _feedback(self, message):
        feedback = message.feedback
        print(f'FEEDBACK stage={feedback.stage} progress={feedback.progress:.2f}')

    def run(self):
        if not self._client.wait_for_server(timeout_sec=5.0):
            raise RuntimeError('RunTrial server is unavailable')

        goal = RunTrial.Goal()
        goal.run_id = self._options.run_id
        goal.use_perception = False
        goal.fixed_object_pose = _pose('world', 0.16, 0.00, 0.12)
        goal.place_pose = _pose('world', 0.12, 0.12, 0.12)

        send_future = self._client.send_goal_async(
            goal,
            feedback_callback=self._feedback,
        )
        rclpy.spin_until_future_complete(self, send_future)
        goal_handle = send_future.result()
        if goal_handle is None or not goal_handle.accepted:
            raise RuntimeError('RunTrial goal was rejected')

        accepted_at = time.monotonic()
        cancel_sent = False
        result_future = goal_handle.get_result_async()
        while rclpy.ok() and not result_future.done():
            rclpy.spin_once(self, timeout_sec=0.05)
            if (
                self._options.cancel_after >= 0.0
                and not cancel_sent
                and time.monotonic() - accepted_at >= self._options.cancel_after
            ):
                goal_handle.cancel_goal_async()
                cancel_sent = True
                print('CANCEL_SENT reason=manual')

        wrapped = result_future.result()
        status_name = {
            GoalStatus.STATUS_SUCCEEDED: 'SUCCEEDED',
            GoalStatus.STATUS_CANCELED: 'CANCELED',
            GoalStatus.STATUS_ABORTED: 'ABORTED',
        }.get(wrapped.status, str(wrapped.status))
        result = wrapped.result
        print(
            f'RESULT status={status_name} success={str(result.success).lower()} '
            f'error_code={result.error_code} message={result.message}'
        )
        return 0 if status_name in {'SUCCEEDED', 'CANCELED'} else 1


def _parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cancel-after', type=float, default=-1.0)
    parser.add_argument('--run-id', default=f'session2-{uuid.uuid4().hex[:8]}')
    return parser


def main(args=None):
    options, ros_args = _parser().parse_known_args(args)
    rclpy.init(args=ros_args)
    node = ScenarioRunner(options)
    try:
        return node.run()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    raise SystemExit(main())
