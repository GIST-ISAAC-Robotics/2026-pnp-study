import copy
import time

import rclpy
from geometry_msgs.msg import PoseStamped
from rclpy.action import (
    ActionClient,
    ActionServer,
    CancelResponse,
    GoalResponse,
)
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from pnp_interfaces.action import PickPlace, RunTrial
from pnp_interfaces.msg import ErrorCode
from pnp_orchestrator.state_machine import (
    ExplicitStateMachine,
    ORCHESTRATOR_TRANSITIONS,
    OrchestratorState,
)


class Orchestrator(Node):
    """RunTrial을 PickPlace로 연결하는 학습용 최소 orchestrator."""

    def __init__(self):
        super().__init__('pnp_orchestrator')
        group = ReentrantCallbackGroup()
        self._latest_target = None
        self._target_subscription = self.create_subscription(
            PoseStamped,
            '/perception/target_pose',
            self._target_callback,
            10,
            callback_group=group,
        )
        self._pick_place_client = ActionClient(
            self,
            PickPlace,
            '/pick_place/execute',
            callback_group=group,
        )
        self._run_trial_server = ActionServer(
            self,
            RunTrial,
            '/task/run_trial',
            execute_callback=self._execute,
            goal_callback=self._goal,
            cancel_callback=self._cancel,
            callback_group=group,
        )
        self.get_logger().info('RunTrial orchestrator ready')

    def _target_callback(self, message):
        self._latest_target = copy.deepcopy(message)

    def _goal(self, _request):
        return GoalResponse.ACCEPT

    def _cancel(self, _goal_handle):
        self.get_logger().info('outer manual cancel accepted')
        return CancelResponse.ACCEPT

    def _feedback(self, goal_handle, stage, progress):
        message = RunTrial.Feedback()
        message.stage = stage
        message.progress = float(progress)
        goal_handle.publish_feedback(message)
        self.get_logger().info(f'stage={stage} progress={progress:.2f}')

    @staticmethod
    def _pose_valid(message):
        return bool(message.header.frame_id) and message.pose.orientation.w != 0.0

    def _execute(self, goal_handle):
        request = goal_handle.request
        result = RunTrial.Result()
        result.success = False
        result.error_code = ErrorCode.OK
        machine = ExplicitStateMachine(
            OrchestratorState.IDLE,
            ORCHESTRATOR_TRANSITIONS,
        )

        machine.move(OrchestratorState.SELECT_TARGET)
        self._feedback(goal_handle, machine.state.value, 0.15)
        object_pose = (
            copy.deepcopy(self._latest_target)
            if request.use_perception
            else copy.deepcopy(request.fixed_object_pose)
        )
        if object_pose is None or not self._pose_valid(object_pose):
            machine.move(OrchestratorState.FAILED)
            result.error_code = ErrorCode.TARGET_UNAVAILABLE
            result.message = 'target pose is unavailable'
            goal_handle.abort()
            return result

        machine.move(OrchestratorState.TRANSFORM)
        self._feedback(goal_handle, machine.state.value, 0.30)
        # Session 2에서는 frame을 바꾸지 않고 action 연결만 확인한다.
        pick_pose = copy.deepcopy(object_pose)
        pick_pose.pose.position.z += 0.08

        if not self._pick_place_client.wait_for_server(timeout_sec=5.0):
            machine.move(OrchestratorState.FAILED)
            result.error_code = ErrorCode.INTERNAL_ERROR
            result.message = 'PickPlace server is unavailable'
            goal_handle.abort()
            return result

        inner_goal = PickPlace.Goal()
        inner_goal.run_id = request.run_id
        inner_goal.object_pose = object_pose
        inner_goal.pick_pose = pick_pose
        inner_goal.place_pose = request.place_pose
        inner_goal.pick_only = False

        machine.move(OrchestratorState.CALL_PICK_PLACE)
        self._feedback(goal_handle, machine.state.value, 0.40)

        def forward_feedback(message):
            inner = message.feedback
            self._feedback(goal_handle, inner.stage, 0.40 + inner.progress * 0.50)

        send_future = self._pick_place_client.send_goal_async(
            inner_goal,
            feedback_callback=forward_feedback,
        )
        while not send_future.done():
            time.sleep(0.05)
        inner_handle = send_future.result()
        if inner_handle is None or not inner_handle.accepted:
            machine.move(OrchestratorState.FAILED)
            result.error_code = ErrorCode.INTERNAL_ERROR
            result.message = 'PickPlace goal was rejected'
            goal_handle.abort()
            return result

        inner_result_future = inner_handle.get_result_async()
        cancel_sent = False
        while not inner_result_future.done():
            if goal_handle.is_cancel_requested and not cancel_sent:
                inner_handle.cancel_goal_async()
                cancel_sent = True
            time.sleep(0.05)

        wrapped = inner_result_future.result()
        inner_result = wrapped.result
        if cancel_sent or goal_handle.is_cancel_requested:
            result.message = 'manual cancel completed'
            goal_handle.canceled()
            return result

        if not inner_result.success:
            machine.move(OrchestratorState.FAILED)
            result.error_code = inner_result.error_code
            result.message = inner_result.message
            goal_handle.abort()
            return result

        machine.move(OrchestratorState.DONE)
        self._feedback(goal_handle, machine.state.value, 1.0)
        result.success = True
        result.message = 'RunTrial completed'
        goal_handle.succeed()
        return result

    def destroy_node(self):
        self._run_trial_server.destroy()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = Orchestrator()
    executor = MultiThreadedExecutor(num_threads=4)
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
