#!/usr/bin/env python3

import math
import threading
import time

from pnp_interfaces.action import PickPlace
from pnp_interfaces.msg import ErrorCode, StageStatus
import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node


def _pose_is_valid(pose, require_frame=True):
    if require_frame and not pose.header.frame_id:
        return False
    values = (
        pose.pose.position.x,
        pose.pose.position.y,
        pose.pose.position.z,
        pose.pose.orientation.x,
        pose.pose.orientation.y,
        pose.pose.orientation.z,
        pose.pose.orientation.w,
    )
    if not all(math.isfinite(value) for value in values):
        return False
    norm = math.sqrt(sum(value * value for value in values[3:]))
    return abs(norm - 1.0) <= 1.0e-3


class DummyPickPlaceServer(Node):
    def __init__(self):
        super().__init__('dummy_pick_place_server')
        self.declare_parameter('behavior', 'success')
        self.declare_parameter('stage_delay_s', 0.20)
        self.declare_parameter('cancel_delay_s', 4.90)
        self.declare_parameter('ignore_cancel_s', 10.0)
        self._behavior = self.get_parameter('behavior').value
        self._stage_delay_s = float(self.get_parameter('stage_delay_s').value)
        self._cancel_delay_s = float(self.get_parameter('cancel_delay_s').value)
        self._ignore_cancel_s = float(self.get_parameter('ignore_cancel_s').value)
        if self._behavior not in (
            'success',
            'coded_failure',
            'boundary_cancel',
            'ignore_cancel',
        ):
            raise ValueError('unsupported dummy behavior')

        self._callback_group = ReentrantCallbackGroup()
        self._reservation_lock = threading.Lock()
        self._goal_reserved = False
        self._action_server = ActionServer(
            self,
            PickPlace,
            '/pick_place/execute',
            execute_callback=self._execute,
            goal_callback=self._goal_callback,
            cancel_callback=self._cancel_callback,
            callback_group=self._callback_group,
        )
        self.get_logger().info(
            f'READY action=/pick_place/execute behavior={self._behavior}'
        )

    def _goal_callback(self, goal_request):
        del goal_request
        with self._reservation_lock:
            if self._goal_reserved:
                self.get_logger().warning('GOAL_REJECTED reason=duplicate-active-goal')
                return GoalResponse.REJECT
            self._goal_reserved = True
        return GoalResponse.ACCEPT

    def _cancel_callback(self, goal_handle):
        self.get_logger().warning(
            f'CANCEL_ACCEPTED run_id={goal_handle.request.run_id}'
        )
        return CancelResponse.ACCEPT

    def _feedback(self, goal_handle, stage, progress):
        feedback = PickPlace.Feedback()
        feedback.inner_stage = stage
        feedback.progress = float(progress)
        goal_handle.publish_feedback(feedback)
        self.get_logger().info(
            f'STATE run_id={goal_handle.request.run_id} '
            f'inner_stage={stage} progress={progress:.2f}'
        )

    def _delay(self, goal_handle, duration=None):
        deadline = time.monotonic() + (
            self._stage_delay_s if duration is None else duration
        )
        while time.monotonic() < deadline:
            if goal_handle.is_cancel_requested:
                return False
            time.sleep(0.02)
        return True

    @staticmethod
    def _reach(result, bit):
        result.stage_status.reached_mask |= bit

    @staticmethod
    def _succeed(result, bit):
        result.stage_status.reached_mask |= bit
        result.stage_status.succeeded_mask |= bit

    def _cancel_result(self, goal_handle, result):
        self._feedback(goal_handle, 'CLEANUP', 0.95)
        self._reach(result, StageStatus.CLEANUP)
        if self._behavior == 'boundary_cancel':
            time.sleep(self._cancel_delay_s)
        elif self._behavior == 'ignore_cancel':
            time.sleep(self._ignore_cancel_s)
            result.pipeline_success = False
            result.error_code = ErrorCode.INTERNAL_ERROR
            result.message = 'dummy intentionally missed cancel terminal budget'
            goal_handle.abort()
            return result
        else:
            time.sleep(0.10)

        self._succeed(result, StageStatus.CLEANUP)
        result.pipeline_success = False
        result.error_code = ErrorCode.TASK_CANCELED
        result.message = 'dummy cancel terminal confirmed'
        goal_handle.canceled()
        return result

    def _request_error(self, request):
        if not request.run_id or not request.object_id:
            return 'run_id and object_id are required'
        if request.task_scope not in (
            PickPlace.Goal.PICK_LIFT_ONLY,
            PickPlace.Goal.FULL_PICK_PLACE,
        ):
            return 'unknown task_scope'
        if not _pose_is_valid(request.object_pose):
            return 'object_pose is invalid'
        if not _pose_is_valid(request.pick_pose):
            return 'pick_pose is invalid'
        if request.task_scope == PickPlace.Goal.PICK_LIFT_ONLY:
            if request.place_pose.header.frame_id:
                return 'lift-only place_pose must be empty'
        elif not _pose_is_valid(request.place_pose):
            return 'full-scope place_pose is invalid'
        if not request.grasp_frame:
            return 'grasp_frame is required'
        return ''

    def _execute(self, goal_handle):
        request = goal_handle.request
        result = PickPlace.Result()
        result.error_code = ErrorCode.OK
        try:
            request_error = self._request_error(request)
            if request_error:
                result.error_code = ErrorCode.INVALID_TASK_SCOPE
                result.message = request_error
                goal_handle.abort()
                return result

            stages = (
                ('SETUP_SCENE', 0.08),
                ('PLAN_PICK', 0.18),
                ('EXECUTE_PICK', 0.32),
                ('PREPARE_TRANSPORT', 0.46),
                ('ATTACH_OBJECT', 0.56),
                ('LIFT', 0.66),
                ('VERIFY_PICK', 0.76),
            )
            for stage, progress in stages:
                self._feedback(goal_handle, stage, progress)
                if stage == 'PLAN_PICK':
                    self._reach(result, StageStatus.PLANNING)
                    result.planning_time_ms = 12.5
                    if self._behavior == 'coded_failure':
                        time.sleep(self._stage_delay_s)
                        self._feedback(goal_handle, 'CLEANUP', 0.95)
                        self._succeed(result, StageStatus.CLEANUP)
                        result.pipeline_success = False
                        result.error_code = ErrorCode.PLANNING_FAILED
                        result.message = 'dummy coded planning failure'
                        goal_handle.abort()
                        return result
                elif stage == 'PREPARE_TRANSPORT':
                    result.transport_prepare_attempted = True
                    self._reach(result, StageStatus.TRANSPORT)
                elif stage == 'LIFT':
                    self._succeed(result, StageStatus.PLANNING)
                    self._succeed(result, StageStatus.TRANSPORT)
                elif stage == 'VERIFY_PICK':
                    self._succeed(result, StageStatus.VERIFY_PICK)

                if not self._delay(goal_handle):
                    return self._cancel_result(goal_handle, result)

            if request.task_scope == PickPlace.Goal.FULL_PICK_PLACE:
                for stage, progress in (
                    ('PLAN_PLACE', 0.82),
                    ('EXECUTE_PLACE', 0.88),
                ):
                    self._feedback(goal_handle, stage, progress)
                    self._reach(result, StageStatus.PLACE)
                    if not self._delay(goal_handle):
                        return self._cancel_result(goal_handle, result)
                self._succeed(result, StageStatus.PLACE)

            self._feedback(goal_handle, 'CLEANUP', 0.95)
            self._succeed(result, StageStatus.CLEANUP)
            if not self._delay(goal_handle):
                return self._cancel_result(goal_handle, result)

            self._feedback(goal_handle, 'RETURN_RESULT', 1.0)
            result.pipeline_success = True
            result.error_code = ErrorCode.OK
            result.message = 'dummy requested scope completed'
            goal_handle.succeed()
            self.get_logger().info(
                f'RESULT run_id={request.run_id} pipeline_success=true '
                f'reached={result.stage_status.reached_mask} '
                f'succeeded={result.stage_status.succeeded_mask}'
            )
            return result
        finally:
            with self._reservation_lock:
                self._goal_reserved = False

    def destroy_node(self):
        self._action_server.destroy()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = DummyPickPlaceServer()
    executor = MultiThreadedExecutor(num_threads=3)
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
