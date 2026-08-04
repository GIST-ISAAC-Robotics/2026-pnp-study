import argparse
import sys
import time
import uuid

from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped
from pnp_interfaces.action import RunTrial
from pnp_interfaces.msg import ErrorCode, StageStatus, TaskStatus
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.parameter_client import AsyncParameterClient
from rclpy.utilities import remove_ros_args


STATUS_NAMES = {
    GoalStatus.STATUS_UNKNOWN: 'UNKNOWN',
    GoalStatus.STATUS_ACCEPTED: 'ACCEPTED',
    GoalStatus.STATUS_EXECUTING: 'EXECUTING',
    GoalStatus.STATUS_CANCELING: 'CANCELING',
    GoalStatus.STATUS_SUCCEEDED: 'SUCCEEDED',
    GoalStatus.STATUS_CANCELED: 'CANCELED',
    GoalStatus.STATUS_ABORTED: 'ABORTED',
}


def _pose(frame_id, x, y, z):
    pose = PoseStamped()
    pose.header.frame_id = frame_id
    pose.pose.position.x = float(x)
    pose.pose.position.y = float(y)
    pose.pose.position.z = float(z)
    pose.pose.orientation.w = 1.0
    return pose


class ScenarioRunner(Node):
    def __init__(self, options):
        super().__init__('scenario_runner')
        self._options = options
        self._action_client = ActionClient(self, RunTrial, '/task/run_trial')
        self._parameter_client = AsyncParameterClient(self, '/orchestrator')
        self._status_subscription = self.create_subscription(
            TaskStatus,
            '/task/status',
            self._status_callback,
            10,
        )
        self._active_run_id = ''
        self._last_heartbeat_at = 0.0
        self._last_heartbeat_seq = None
        self._heartbeat_samples = 0
        self._heartbeat_seq_monotonic = True
        self._feedback_stages = []

    def _spin_until(self, future, timeout_s):
        deadline = time.monotonic() + timeout_s
        while rclpy.ok() and not future.done() and time.monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=0.05)
        return future.done()

    def _target_mode(self):
        if not self._parameter_client.wait_for_services(timeout_sec=5.0):
            raise RuntimeError('orchestrator parameter service unavailable')
        future = self._parameter_client.get_parameters(['target_mode'])
        if not self._spin_until(future, 5.0):
            raise RuntimeError('target_mode query timed out')
        response = future.result()
        if not response.values:
            raise RuntimeError('target_mode response was empty')
        return response.values[0].string_value

    def _status_callback(self, message):
        if self._active_run_id and message.run_id == self._active_run_id:
            if (
                self._last_heartbeat_seq is not None
                and message.heartbeat_seq <= self._last_heartbeat_seq
            ):
                self._heartbeat_seq_monotonic = False
            self._last_heartbeat_at = time.monotonic()
            self._last_heartbeat_seq = message.heartbeat_seq
            self._heartbeat_samples += 1

    def _feedback_callback(self, feedback_message):
        feedback = feedback_message.feedback
        self._feedback_stages.append(feedback.outer_stage)
        self.get_logger().info(
            f'FEEDBACK outer_stage={feedback.outer_stage} '
            f'progress={feedback.progress:.2f}'
        )

    def _profile_is_valid(self, target_mode):
        return (
            self._options.runner_profile == 'week2_baseline'
            and target_mode == 'fixed'
        ) or (
            self._options.runner_profile == 'perception_evaluation'
            and target_mode == 'perception'
        )

    def _print_profile_rejection(self, target_mode):
        print(
            'PROFILE_CHECK=REJECT '
            f'runner_profile={self._options.runner_profile} '
            f'target_mode={target_mode} '
            f'error_code={ErrorCode.INVALID_TARGET_MODE} '
            'attempt_allocated=false reset_called=false action_sent=false'
        )

    def _goal(self):
        goal = RunTrial.Goal()
        goal.run_id = self._options.run_id
        goal.seed = self._options.seed
        goal.object_id = 'cube_1'
        goal.task_scope = (
            RunTrial.Goal.PICK_LIFT_ONLY
            if self._options.scope == 'lift'
            else (
                RunTrial.Goal.FULL_PICK_PLACE
                if self._options.scope == 'full'
                else 99
            )
        )
        if goal.task_scope == RunTrial.Goal.FULL_PICK_PLACE:
            goal.place_pose = _pose('world', 0.12, 0.12, 0.18)
        return goal

    def _expected_mask(self, target_mode):
        mask = (
            StageStatus.PLANNING
            | StageStatus.VERIFY_PICK
            | StageStatus.TRANSPORT
            | StageStatus.CLEANUP
        )
        if self._options.scope == 'full':
            mask |= StageStatus.PLACE
        if target_mode == 'perception':
            mask |= StageStatus.DETECTION | StageStatus.TF
        return mask

    def _expectation_matches(self, received, result, effective_error, target_mode):
        expectation = self._options.expect
        if expectation == 'no-result':
            return not received
        if not received or result is None:
            return False
        if expectation == 'success':
            expected_mask = self._expected_mask(target_mode)
            source_stamp_ns = (
                result.perception_source_stamp.sec * 1_000_000_000
                + result.perception_source_stamp.nanosec
            )
            source_contract_ok = (
                target_mode == 'perception'
                and result.perception_source_accepted
                and result.perception_source_frame == 'camera_optical_frame'
                and source_stamp_ns > 0
            ) or (
                target_mode == 'fixed'
                and not result.perception_source_accepted
                and not result.perception_source_frame
                and source_stamp_ns == 0
            )
            return (
                result.trial_completed
                and result.pipeline_success
                and result.error_code == ErrorCode.OK
                and source_contract_ok
                and result.transport_prepare_attempted
                and result.stage_status.reached_mask == expected_mask
                and result.stage_status.succeeded_mask == expected_mask
                and abs(result.planning_time_ms - 12.5) < 0.01
                and result.outer_input_retry_count == 0
                and result.planning_replan_count == 0
                and result.verify_pick_recheck_count == 0
                and self._heartbeat_samples >= 2
                and self._heartbeat_seq_monotonic
            )
        if expectation == 'coded-failure':
            return (
                result.trial_completed
                and not result.pipeline_success
                and result.error_code == ErrorCode.PLANNING_FAILED
                and result.stage_status.reached_mask
                == StageStatus.PLANNING | StageStatus.CLEANUP
                and result.stage_status.succeeded_mask == StageStatus.CLEANUP
                and abs(result.planning_time_ms - 12.5) < 0.01
            )
        if expectation == 'invalid-scope':
            return (
                result.trial_completed
                and not result.pipeline_success
                and result.error_code == ErrorCode.INVALID_TASK_SCOPE
                and result.stage_status.reached_mask == 0
                and result.stage_status.succeeded_mask == 0
            )
        if expectation == 'canceled':
            return (
                not result.trial_completed
                and not result.pipeline_success
                and effective_error == ErrorCode.TASK_CANCELED
            )
        if expectation == 'heartbeat-timeout':
            return (
                not result.trial_completed
                and not result.pipeline_success
                and effective_error == ErrorCode.TASK_HEARTBEAT_TIMEOUT
            )
        if expectation == 'execution-timeout':
            return (
                not result.trial_completed
                and not result.pipeline_success
                and result.error_code == ErrorCode.EXECUTION_TIMEOUT
                and effective_error == ErrorCode.EXECUTION_TIMEOUT
            )
        return False

    def run(self):
        if (
            self._options.run_trial_cancel_timeout
            < self._options.pick_place_cancel_timeout
            + self._options.cancel_margin
        ):
            print('STARTUP_CHECK=FAIL reason=cancel-timeout-invariant')
            return 2
        print(
            'STARTUP_CHECK=PASS '
            f'outer_cancel_timeout={self._options.run_trial_cancel_timeout:.1f} '
            f'inner_cancel_timeout={self._options.pick_place_cancel_timeout:.1f} '
            f'margin={self._options.cancel_margin:.1f}'
        )

        target_mode = self._target_mode()
        print(
            f'PROFILE_CHECK runner_profile={self._options.runner_profile} '
            f'target_mode={target_mode}'
        )
        if not self._profile_is_valid(target_mode):
            self._print_profile_rejection(target_mode)
            matched = self._options.expect == 'profile-rejected'
            print(f'EXPECTATION={"PASS" if matched else "FAIL"}')
            return 0 if matched else 2
        if self._options.expect == 'profile-rejected':
            print('EXPECTATION=FAIL reason=profile-was-accepted')
            return 2

        if not self._action_client.wait_for_server(timeout_sec=5.0):
            print('ACTION_SERVER=UNAVAILABLE name=/task/run_trial')
            return 2
        goal = self._goal()
        self._active_run_id = goal.run_id
        self._last_heartbeat_at = time.monotonic()
        send_future = self._action_client.send_goal_async(
            goal,
            feedback_callback=self._feedback_callback,
        )
        if not self._spin_until(send_future, 5.0):
            print('GOAL_RESPONSE=TIMEOUT')
            return 2
        goal_handle = send_future.result()
        if not goal_handle.accepted:
            print('GOAL_RESPONSE=REJECTED')
            matched = self._options.expect == 'goal-rejected'
            print(f'EXPECTATION={"PASS" if matched else "FAIL"}')
            return 0 if matched else 2
        print(
            f'GOAL_RESPONSE=ACCEPTED run_id={goal.run_id} '
            f'task_scope={goal.task_scope}'
        )

        result_future = goal_handle.get_result_async()
        accepted_at = time.monotonic()
        cancel_sent_at = None
        initiating_error = ErrorCode.OK
        while rclpy.ok() and not result_future.done():
            now = time.monotonic()
            rclpy.spin_once(self, timeout_sec=0.05)
            if (
                cancel_sent_at is None
                and self._options.cancel_after >= 0.0
                and now - accepted_at >= self._options.cancel_after
            ):
                goal_handle.cancel_goal_async()
                cancel_sent_at = now
                initiating_error = ErrorCode.TASK_CANCELED
                print('CANCEL_SENT reason=manual')
            if (
                cancel_sent_at is None
                and now - self._last_heartbeat_at
                > self._options.task_status_timeout
            ):
                goal_handle.cancel_goal_async()
                cancel_sent_at = now
                initiating_error = ErrorCode.TASK_HEARTBEAT_TIMEOUT
                print(
                    'CANCEL_SENT reason=heartbeat-timeout '
                    f'last_seq={self._last_heartbeat_seq}'
                )
            if (
                cancel_sent_at is not None
                and now - cancel_sent_at
                > self._options.run_trial_cancel_timeout
            ):
                print(
                    'RESULT run_trial_result_received=false '
                    'trial_completed=false pipeline_success=false '
                    f'effective_error_code={initiating_error} next_state=SAFE_STOP'
                )
                matched = self._expectation_matches(
                    False, None, initiating_error, target_mode
                )
                print(f'EXPECTATION={"PASS" if matched else "FAIL"}')
                return 0 if matched else 2
            if now - accepted_at > self._options.result_timeout:
                print('RESULT_TIMEOUT=TRUE')
                return 2

        wrapped_result = result_future.result()
        result = wrapped_result.result
        status_name = STATUS_NAMES.get(wrapped_result.status, str(wrapped_result.status))
        effective_error = (
            initiating_error
            if initiating_error != ErrorCode.OK
            else result.error_code
        )
        source_stamp_ns = (
            result.perception_source_stamp.sec * 1_000_000_000
            + result.perception_source_stamp.nanosec
        )
        print(
            'RESULT run_trial_result_received=true '
            f'action_status={status_name} '
            f'trial_completed={str(result.trial_completed).lower()} '
            f'pipeline_success={str(result.pipeline_success).lower()} '
            f'error_code={result.error_code} '
            f'effective_error_code={effective_error}'
        )
        print(
            f'STAGES reached={result.stage_status.reached_mask} '
            f'succeeded={result.stage_status.succeeded_mask} '
            f'planning_time_ms={result.planning_time_ms:.1f}'
        )
        print(
            'FLAGS '
            f'perception_source_accepted={str(result.perception_source_accepted).lower()} '
            f'perception_source_frame={result.perception_source_frame or "-"} '
            f'perception_source_stamp_ns={source_stamp_ns} '
            f'transport_prepare_attempted={str(result.transport_prepare_attempted).lower()} '
            f'heartbeat_samples={self._heartbeat_samples} '
            'heartbeat_seq_monotonic='
            f'{str(self._heartbeat_seq_monotonic).lower()} '
            f'heartbeat_seq={self._last_heartbeat_seq}'
        )
        print(
            'RETRIES '
            f'outer_input={result.outer_input_retry_count} '
            f'planning_replan={result.planning_replan_count} '
            f'verify_pick_recheck={result.verify_pick_recheck_count}'
        )
        matched = self._expectation_matches(
            True, result, effective_error, target_mode
        )
        print(f'EXPECTATION={"PASS" if matched else "FAIL"}')
        return 0 if matched else 2


def _parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--runner-profile',
        choices=('week2_baseline', 'perception_evaluation'),
        default='week2_baseline',
    )
    parser.add_argument(
        '--scope',
        choices=('lift', 'full', 'invalid'),
        default='full',
    )
    parser.add_argument(
        '--expect',
        choices=(
            'success',
            'coded-failure',
            'invalid-scope',
            'canceled',
            'heartbeat-timeout',
            'execution-timeout',
            'no-result',
            'goal-rejected',
            'profile-rejected',
        ),
        default='success',
    )
    parser.add_argument('--cancel-after', type=float, default=-1.0)
    parser.add_argument('--task-status-timeout', type=float, default=2.0)
    parser.add_argument('--run-trial-cancel-timeout', type=float, default=7.0)
    parser.add_argument('--pick-place-cancel-timeout', type=float, default=5.0)
    parser.add_argument('--cancel-margin', type=float, default=2.0)
    parser.add_argument('--result-timeout', type=float, default=20.0)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--run-id', default=f'session2-{uuid.uuid4().hex[:8]}')
    return parser


def main(args=None):
    argv = sys.argv if args is None else args
    options = _parser().parse_args(remove_ros_args(args=argv)[1:])
    rclpy.init(args=argv)
    node = ScenarioRunner(options)
    try:
        return_code = node.run()
    except (RuntimeError, ValueError) as error:
        node.get_logger().error(str(error))
        return_code = 2
    finally:
        node.destroy_node()
        rclpy.shutdown()
    raise SystemExit(return_code)


if __name__ == '__main__':
    main()
