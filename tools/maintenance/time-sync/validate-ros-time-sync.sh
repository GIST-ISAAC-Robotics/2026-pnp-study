#!/usr/bin/env bash

# Re-run the Session 1 ROS/Zenoh time path after host clock maintenance.

set -eo pipefail

source /opt/ros/jazzy/setup.bash
source /workspace/pick_place_ws/install/setup.bash

set -u

workspace=/workspace/pick_place_ws
router_log="$workspace/time_sync_fix_router.log"
gazebo_log="$workspace/time_sync_fix_gazebo.log"
bridge_log="$workspace/time_sync_fix_bridge.log"
clock_log="$workspace/time_sync_fix_clock.log"
core_log="$workspace/time_sync_fix_validation.log"

router_pid=''
gazebo_pid=''
bridge_pid=''

cleanup() {
    set +e
    for pid in "$bridge_pid" "$gazebo_pid" "$router_pid"; do
        if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
            kill -INT "$pid" 2>/dev/null || true
        fi
    done
    sleep 2
    for pid in "$bridge_pid" "$gazebo_pid" "$router_pid"; do
        if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
            kill -TERM "$pid" 2>/dev/null || true
        fi
    done
    wait 2>/dev/null || true
}
trap cleanup EXIT

: > "$router_log"
: > "$gazebo_log"
: > "$bridge_log"
: > "$clock_log"
: > "$core_log"

ros2 run rmw_zenoh_cpp rmw_zenohd > "$router_log" 2>&1 &
router_pid=$!
sleep 3

gz sim -s -r \
    /opt/ros/jazzy/opt/gz_sim_vendor/share/gz/gz-sim8/worlds/empty.sdf \
    > "$gazebo_log" 2>&1 &
gazebo_pid=$!

ros2 run ros_gz_bridge parameter_bridge \
    '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock' \
    > "$bridge_log" 2>&1 &
bridge_pid=$!
sleep 5

timeout 10 ros2 topic echo \
    /clock \
    rosgraph_msgs/msg/Clock \
    --once > "$clock_log" 2>&1

set +e
timeout --signal=INT --kill-after=10 60 \
    ros2 launch pnp_bringup core_skeleton.launch.py \
    > "$core_log" 2>&1
launch_exit=$?
set -e

publish_count=$(grep -c 'PUBLISH count=' "$core_log" || true)
receive_count=$(grep -c 'RECEIVE count=' "$core_log" || true)
timestamp_errors=$(
    { grep -h 'exceeding delta 500ms' \
        "$router_log" "$bridge_log" "$clock_log" "$core_log" || true; } \
        | wc -l
)

printf 'CLOCK_OK=%s\n' "$(grep -c '^clock:$' "$clock_log" || true)"
printf 'PUBLISH=%s\n' "$publish_count"
printf 'RECEIVE=%s\n' "$receive_count"
printf 'TIMESTAMP_ERRORS=%s\n' "$timestamp_errors"
printf 'LAUNCH_EXIT=%s\n' "$launch_exit"

if [[ "$publish_count" -lt 100 ]]; then
    echo 'VALIDATION=FAIL reason=insufficient-publish-count'
    exit 1
fi
if [[ "$publish_count" -ne "$receive_count" ]]; then
    echo 'VALIDATION=FAIL reason=publish-receive-mismatch'
    exit 1
fi
if [[ "$timestamp_errors" -ne 0 ]]; then
    echo 'VALIDATION=FAIL reason=zenoh-timestamp-errors'
    exit 1
fi

echo 'VALIDATION=PASS'
