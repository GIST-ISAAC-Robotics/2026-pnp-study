import math
import threading
import time

from geometry_msgs.msg import PoseStamped
from pnp_interfaces.action import PickPlace, RunTrial
from pnp_interfaces.msg import ErrorCode, StageStatus, TaskStatus
from pnp_orchestrator.state_machine import (
    ExplicitStateMachine,
    ORCHESTRATOR_TRANSITIONS,
    OrchestratorState,
    TransitionError,
)
import rclpy
from rclpy.action import ActionClient, ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.clock import Clock, ClockType
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

KNOWN_ERROR_CODES = {
    ErrorCode.OK,
    ErrorCode.NO_DETECTION,
    ErrorCode.STALE_DETECTION,
    ErrorCode.INVALID_DEPTH,
    ErrorCode.RGBD_REGISTRATION_ERROR,
    ErrorCode.TF_ERROR,
    ErrorCode.OUT_OF_WORKSPACE,
    ErrorCode.INVALID_TARGET_MODE,
    ErrorCode.INVALID_TASK_SCOPE,
    ErrorCode.PLANNING_FAILED,
    ErrorCode.IK_UNREACHABLE_POSE,
    ErrorCode.EXECUTION_TIMEOUT,
    ErrorCode.SCENE_SYNC_FAILED,
    ErrorCode.VERIFY_PICK_FAILED,
    ErrorCode.VERIFY_PLACE_FAILED,
    ErrorCode.STALE_GROUND_TRUTH,
    ErrorCode.GRASP_NOT_ELIGIBLE,
    ErrorCode.TRANSPORT_FAILED,
    ErrorCode.RESET_FAILED,
    ErrorCode.TASK_HEARTBEAT_TIMEOUT,
    ErrorCode.EVALUATION_DATA_MISSING,
    ErrorCode.TASK_CANCELED,
    ErrorCode.INTERNAL_ERROR,
}
ALL_STAGE_BITS = (
    StageStatus.DETECTION
    | StageStatus.TF
    | StageStatus.PLANNING
    | StageStatus.VERIFY_PICK
    | StageStatus.TRANSPORT
    | StageStatus.PLACE
    | StageStatus.CLEANUP
)


def _pose(frame_id, x, y, z):
    pose = PoseStamped()
    pose.header.frame_id = frame_id
    pose.pose.position.x = float(x)
    pose.pose.position.y = float(y)
    pose.pose.position.z = float(z)
    pose.pose.orientation.w = 1.0
    return pose


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
    quaternion_norm = math.sqrt(sum(value * value for value in values[3:]))
    return abs(quaternion_norm - 1.0) <= 1.0e-3


class Orchestrator(Node):
    def __init__(self):
        super().__init__('orchestrator')
        self.declare_parameter('target_mode', 'fixed')
        self.declare_parameter('task_status_rate_hz', 2.0)
        self.declare_parameter('pick_place_action_timeout_s', 15.0)
        self.declare_parameter('pick_place_cancel_timeout_s', 5.0)
        self.declare_parameter('pause_heartbeat_after_s', -1.0)

        self._target_mode = self.get_parameter('target_mode').value
        self._cancel_timeout = float(
            self.get_parameter('pick_place_cancel_timeout_s').value
        )
        status_rate_hz = float(
            self.get_parameter('task_status_rate_hz').value
        )
        self._action_timeout = float(
            self.get_parameter('pick_place_action_timeout_s').value
        )
        self._pause_heartbeat_after_s = float(
            self.get_parameter('pause_heartbeat_after_s').value
        )
        if self._target_mode not in ('fixed', 'perception'):
            raise ValueError('target_mode must be fixed or perception')
        if (
            status_rate_hz <= 0.0
            or self._action_timeout <= 0.0
            or self._cancel_timeout <= 0.0
        ):
            raise ValueError(
                'status rate, action timeout and cancel timeout must be positive'
            )

        self._callback_group = ReentrantCallbackGroup()
        self._status_publisher = self.create_publisher(TaskStatus, '/task/status', 10)
        self._steady_clock = Clock(clock_type=ClockType.STEADY_TIME)
        self._status_timer = self.create_timer(
            1.0 / status_rate_hz,
            self._publish_status,
            callback_group=self._callback_group,
            clock=self._steady_clock,
        )
        self._inner_client = ActionClient(
            self,
            PickPlace,
            '/pick_place/execute',
            callback_group=self._callback_group,
        )
        self._action_server = ActionServer(
            self,
            RunTrial,
            '/task/run_trial',
            execute_callback=self._execute,
            goal_callback=self._goal_callback,
            cancel_callback=self._cancel_callback,
            callback_group=self._callback_group,
        )

        self._reservation_lock = threading.Lock()
        self._goal_reserved = False
        self._safe_stop = False
        self._active_run_id = ''
        self._active_started_at = 0.0
        self._status_error_code = ErrorCode.OK
        self._heartbeat_seq = 0
        self._state_machine = ExplicitStateMachine(
            OrchestratorState.IDLE,
            ORCHESTRATOR_TRANSITIONS,
        )
        self.get_logger().info(
            'READY action=/task/run_trial inner=/pick_place/execute '
            f'target_mode={self._target_mode} '
            f'task_status_rate_hz={status_rate_hz:.1f}'
        )

    def _goal_callback(self, goal_request):
        del goal_request
        with self._reservation_lock:
            if self._safe_stop or self._goal_reserved:
                self.get_logger().warning('GOAL_REJECTED reason=busy-or-safe-stop')
                return GoalResponse.REJECT
            self._goal_reserved = True
        return GoalResponse.ACCEPT

    def _cancel_callback(self, goal_handle):
        self.get_logger().warning(
            f'CANCEL_ACCEPTED run_id={goal_handle.request.run_id}'
        )
        return CancelResponse.ACCEPT

    def _publish_status(self):
        if (
            self._active_run_id
            and self._pause_heartbeat_after_s >= 0.0
            and time.monotonic() - self._active_started_at
            >= self._pause_heartbeat_after_s
        ):
            return
        self._heartbeat_seq += 1
        message = TaskStatus()
        message.run_id = self._active_run_id
        message.outer_stage = self._state_machine.state.value
        message.heartbeat_seq = self._heartbeat_seq
        message.error_code = self._status_error_code
        message.message = 'safe stop' if self._safe_stop else 'alive'
        self._status_publisher.publish(message)

    def _move(self, state, goal_handle=None, progress=0.0):
        self._state_machine.move(state)
        if goal_handle is not None:
            feedback = RunTrial.Feedback()
            feedback.outer_stage = state.value
            feedback.progress = float(progress)
            goal_handle.publish_feedback(feedback)
        self.get_logger().info(
            f'STATE run_id={self._active_run_id} '
            f'outer_stage={state.value} error_code={self._status_error_code} '
            f'target_mode={self._target_mode}'
        )

    def _finish_before_inner(self, goal_handle, result, error_code, message):
        result.trial_completed = True
        result.pipeline_success = False
        result.error_code = error_code
        result.message = message
        self._status_error_code = error_code
        if self._state_machine.state != OrchestratorState.COMPLETE:
            self._move(OrchestratorState.COMPLETE, goal_handle, 1.0)
        goal_handle.abort()
        return result

    def _validate_request(self, request):
        if not request.run_id or not request.object_id:
            return ErrorCode.INVALID_TASK_SCOPE, 'run_id and object_id are required'
        if request.task_scope not in (
            RunTrial.Goal.PICK_LIFT_ONLY,
            RunTrial.Goal.FULL_PICK_PLACE,
        ):
            return ErrorCode.INVALID_TASK_SCOPE, 'unknown task_scope'
        if request.task_scope == RunTrial.Goal.PICK_LIFT_ONLY:
            if request.place_pose.header.frame_id:
                return ErrorCode.INVALID_TASK_SCOPE, 'lift-only place_pose must be empty'
        elif not _pose_is_valid(request.place_pose):
            return ErrorCode.INVALID_TASK_SCOPE, 'full-scope place_pose is invalid'
        return ErrorCode.OK, 'valid'

    def _inner_feedback(self, feedback_message):
        feedback = feedback_message.feedback
        self.get_logger().info(
            f'INNER_FEEDBACK run_id={self._active_run_id} '
            f'inner_stage={feedback.inner_stage} progress={feedback.progress:.2f}'
        )

    def _copy_inner_result(self, outer_result, inner_result, outer_sensor_bits):
        outer_result.transport_prepare_attempted = (
            inner_result.transport_prepare_attempted
        )
        outer_result.stage_status.reached_mask = (
            inner_result.stage_status.reached_mask | outer_sensor_bits
        )
        outer_result.stage_status.succeeded_mask = (
            inner_result.stage_status.succeeded_mask | outer_sensor_bits
        )
        outer_result.planning_replan_count = inner_result.planning_replan_count
        outer_result.verify_pick_recheck_count = (
            inner_result.verify_pick_recheck_count
        )
        outer_result.planning_time_ms = inner_result.planning_time_ms
        outer_result.error_code = (
            inner_result.error_code
            if inner_result.error_code in KNOWN_ERROR_CODES
            else ErrorCode.INTERNAL_ERROR
        )
        outer_result.message = inner_result.message

    def _stage_contract_ok(self, request, result):
        reached = result.stage_status.reached_mask
        succeeded = result.stage_status.succeeded_mask
        if reached & ~ALL_STAGE_BITS or succeeded & ~reached:
            return False
        required = (
            StageStatus.PLANNING
            | StageStatus.VERIFY_PICK
            | StageStatus.TRANSPORT
            | StageStatus.CLEANUP
        )
        forbidden = 0
        if request.task_scope == RunTrial.Goal.FULL_PICK_PLACE:
            required |= StageStatus.PLACE
        else:
            forbidden |= StageStatus.PLACE
        if self._target_mode == 'perception':
            required |= StageStatus.DETECTION | StageStatus.TF
        else:
            forbidden |= StageStatus.DETECTION | StageStatus.TF
        if reached & forbidden or succeeded & forbidden:
            return False
        if result.pipeline_success:
            return (
                result.error_code == ErrorCode.OK
                and succeeded & required == required
            )
        return True

    def _execute(self, goal_handle):
        request = goal_handle.request
        result = RunTrial.Result()
        result.error_code = ErrorCode.OK
        self._active_run_id = request.run_id
        self._active_started_at = time.monotonic()
        self._status_error_code = ErrorCode.OK
        self._state_machine = ExplicitStateMachine(
            OrchestratorState.IDLE,
            ORCHESTRATOR_TRANSITIONS,
        )
        try:
            self._move(OrchestratorState.SELECT_TARGET, goal_handle, 0.05)
            error_code, message = self._validate_request(request)
            if error_code != ErrorCode.OK:
                return self._finish_before_inner(
                    goal_handle, result, error_code, message
                )

            outer_sensor_bits = 0
            if self._target_mode == 'fixed':
                self._move(OrchestratorState.LOAD_FIXED_TARGET, goal_handle, 0.15)
                object_pose = _pose('world', 0.16, 0.0, 0.12)
                result.perception_source_accepted = False
            else:
                self._move(OrchestratorState.DETECT, goal_handle, 0.12)
                result.perception_source_accepted = True
                result.perception_source_stamp = self.get_clock().now().to_msg()
                result.perception_source_frame = 'camera_optical_frame'
                outer_sensor_bits |= StageStatus.DETECTION
                self._move(OrchestratorState.TRANSFORM, goal_handle, 0.20)
                outer_sensor_bits |= StageStatus.TF
                object_pose = _pose('world', 0.16, 0.0, 0.12)

            self._move(OrchestratorState.VALIDATE, goal_handle, 0.28)
            if not _pose_is_valid(object_pose):
                return self._finish_before_inner(
                    goal_handle,
                    result,
                    ErrorCode.OUT_OF_WORKSPACE,
                    'dummy object pose validation failed',
                )

            self._move(OrchestratorState.CALL_MANIPULATION, goal_handle, 0.35)
            if not self._inner_client.wait_for_server(timeout_sec=5.0):
                return self._finish_before_inner(
                    goal_handle,
                    result,
                    ErrorCode.INTERNAL_ERROR,
                    'PickPlace server unavailable',
                )

            inner_goal = PickPlace.Goal()
            inner_goal.run_id = request.run_id
            inner_goal.object_id = request.object_id
            inner_goal.task_scope = request.task_scope
            inner_goal.object_pose = object_pose
            inner_goal.pick_pose = _pose('world', 0.16, 0.0, 0.16)
            inner_goal.place_pose = request.place_pose
            inner_goal.grasp_frame = 'end_effector_link'
            send_future = self._inner_client.send_goal_async(
                inner_goal,
                feedback_callback=self._inner_feedback,
            )
            while not send_future.done():
                time.sleep(0.02)
            inner_handle = send_future.result()
            if not inner_handle.accepted:
                return self._finish_before_inner(
                    goal_handle,
                    result,
                    ErrorCode.INTERNAL_ERROR,
                    'PickPlace goal rejected',
                )

            result_future = inner_handle.get_result_async()
            inner_started_at = time.monotonic()
            cancel_sent_at = None
            cancel_initiating_error = ErrorCode.OK
            cancel_timed_out = False
            while not result_future.done():
                if goal_handle.is_cancel_requested and cancel_sent_at is None:
                    inner_handle.cancel_goal_async()
                    cancel_sent_at = time.monotonic()
                    cancel_initiating_error = ErrorCode.TASK_CANCELED
                    self._status_error_code = cancel_initiating_error
                    self.get_logger().warning(
                        f'INNER_CANCEL_SENT run_id={request.run_id} '
                        'reason=outer-cancel '
                        f'error_code={cancel_initiating_error} '
                        f'target_mode={self._target_mode}'
                    )
                if (
                    cancel_sent_at is None
                    and time.monotonic() - inner_started_at
                    > self._action_timeout
                ):
                    inner_handle.cancel_goal_async()
                    cancel_sent_at = time.monotonic()
                    cancel_initiating_error = ErrorCode.EXECUTION_TIMEOUT
                    self._status_error_code = cancel_initiating_error
                    self.get_logger().warning(
                        f'INNER_CANCEL_SENT run_id={request.run_id} '
                        'reason=execution-timeout '
                        f'error_code={cancel_initiating_error} '
                        f'target_mode={self._target_mode}'
                    )
                if (
                    cancel_sent_at is not None
                    and not cancel_timed_out
                    and time.monotonic() - cancel_sent_at > self._cancel_timeout
                ):
                    cancel_timed_out = True
                    self._safe_stop = True
                    self._status_error_code = ErrorCode.INTERNAL_ERROR
                    self._move(OrchestratorState.SAFE_STOP, goal_handle, 0.99)
                    self.get_logger().error(
                        f'SAFE_STOP run_id={request.run_id} '
                        'reason=inner-cancel-terminal-timeout'
                    )
                time.sleep(0.05)

            wrapped_result = result_future.result()
            inner_result = wrapped_result.result
            self._copy_inner_result(result, inner_result, outer_sensor_bits)

            if cancel_timed_out:
                result.trial_completed = False
                result.pipeline_success = False
                result.error_code = ErrorCode.INTERNAL_ERROR
                result.message = 'inner cancel terminal was not confirmed in time'
                goal_handle.abort()
                return result

            if cancel_sent_at is not None:
                result.trial_completed = False
                result.pipeline_success = False
                result.error_code = cancel_initiating_error
                result.message = (
                    'manual cancel confirmed inner-to-outer'
                    if cancel_initiating_error == ErrorCode.TASK_CANCELED
                    else 'PickPlace execution timeout cancel was confirmed'
                )
                self._move(OrchestratorState.COMPLETE, goal_handle, 1.0)
                if cancel_initiating_error == ErrorCode.TASK_CANCELED:
                    goal_handle.canceled()
                else:
                    goal_handle.abort()
                return result

            cleanup_ok = bool(
                result.stage_status.succeeded_mask & StageStatus.CLEANUP
            )
            result.trial_completed = cleanup_ok
            result.pipeline_success = bool(inner_result.pipeline_success)
            if not self._stage_contract_ok(request, result):
                result.trial_completed = False
                result.pipeline_success = False
                result.error_code = ErrorCode.INTERNAL_ERROR
                result.message = 'stage mask or scope invariant failed'

            self._move(OrchestratorState.COMPLETE, goal_handle, 1.0)
            if result.pipeline_success and result.error_code == ErrorCode.OK:
                goal_handle.succeed()
            else:
                goal_handle.abort()
            self.get_logger().info(
                f'RESULT run_id={request.run_id} '
                f'trial_completed={result.trial_completed} '
                f'pipeline_success={result.pipeline_success} '
                f'error_code={result.error_code} '
                f'target_mode={self._target_mode} '
                f'reached={result.stage_status.reached_mask} '
                f'succeeded={result.stage_status.succeeded_mask}'
            )
            return result
        except TransitionError as error:
            self._safe_stop = True
            self._status_error_code = ErrorCode.INTERNAL_ERROR
            result.trial_completed = False
            result.pipeline_success = False
            result.error_code = ErrorCode.INTERNAL_ERROR
            result.message = str(error)
            goal_handle.abort()
            return result
        finally:
            if not self._safe_stop:
                if self._state_machine.state == OrchestratorState.COMPLETE:
                    self._move(OrchestratorState.IDLE)
                self._active_run_id = ''
                self._status_error_code = ErrorCode.OK
            with self._reservation_lock:
                self._goal_reserved = self._safe_stop

    def destroy_node(self):
        self._action_server.destroy()
        self._inner_client.destroy()
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
