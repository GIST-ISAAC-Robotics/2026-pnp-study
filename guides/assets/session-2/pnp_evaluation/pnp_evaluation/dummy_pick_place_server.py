import time

import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from pnp_interfaces.action import PickPlace
from pnp_interfaces.msg import ErrorCode


class DummyPickPlaceServer(Node):
    """Session 2 action 흐름만 보여 주는 비동작 dummy server."""

    def __init__(self):
        super().__init__('dummy_pick_place_server')
        self.declare_parameter('stage_delay_s', 0.35)
        self._stage_delay_s = float(self.get_parameter('stage_delay_s').value)
        self._action_server = ActionServer(
            self,
            PickPlace,
            '/pick_place/execute',
            execute_callback=self._execute,
            goal_callback=self._goal,
            cancel_callback=self._cancel,
            callback_group=ReentrantCallbackGroup(),
        )
        self.get_logger().info('dummy PickPlace server ready')

    def _goal(self, _request):
        return GoalResponse.ACCEPT

    def _cancel(self, _goal_handle):
        self.get_logger().info('manual cancel accepted')
        return CancelResponse.ACCEPT

    def _publish_stage(self, goal_handle, stage, progress):
        feedback = PickPlace.Feedback()
        feedback.stage = stage
        feedback.progress = float(progress)
        goal_handle.publish_feedback(feedback)
        self.get_logger().info(f'stage={stage} progress={progress:.2f}')

    def _wait_stage(self, goal_handle):
        deadline = time.monotonic() + self._stage_delay_s
        while time.monotonic() < deadline:
            if goal_handle.is_cancel_requested:
                return False
            time.sleep(0.05)
        return True

    def _execute(self, goal_handle):
        request = goal_handle.request
        stages = ['SETUP_SCENE', 'APPROACH', 'GRASP', 'LIFT']
        if not request.pick_only:
            stages.extend(['TRANSPORT', 'PLACE'])
        stages.append('CLEANUP')

        result = PickPlace.Result()
        result.success = False
        result.error_code = ErrorCode.OK

        for index, stage in enumerate(stages, start=1):
            self._publish_stage(goal_handle, stage, index / len(stages))
            if not self._wait_stage(goal_handle):
                self._publish_stage(goal_handle, 'CLEANUP', 1.0)
                result.message = 'manual cancel completed'
                goal_handle.canceled()
                return result

        result.success = True
        result.message = 'dummy pick-place completed'
        goal_handle.succeed()
        return result

    def destroy_node(self):
        self._action_server.destroy()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = DummyPickPlaceServer()
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
