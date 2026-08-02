# Week 0 spike 결과와 동결값 (Session 0-3)

- 수행일: 2026-08-02
- 담당: `leejinh0225` (메인 PC)
- 결과: **부분 완료**
- Week 0 Gate 판정: **조건부 통과**
- 미완료 확인: RGB-depth registration 캡처·두 사람 확인, Session 5의 IK mode 재동결

## 1. spike A — RGB-D

| 항목 | 실제 값 |
|---|---|
| 사용한 world | Gazebo Sim 8.11.0 vendor의 `sensors_demo.sdf` |
| Gazebo topic | `/rgbd_camera/image`, `/rgbd_camera/depth_image`, `/rgbd_camera/camera_info`, `/rgbd_camera/points`, `/rgbd_camera/performance_metrics` |
| ROS bridge topic | image·depth·CameraInfo·points 4개 (`performance_metrics` 제외) |
| RGB | `/rgbd_camera/image` · 320×240 · `rgb8` |
| depth | `/rgbd_camera/depth_image` · 320×240 · `32FC1` |
| CameraInfo | `/rgbd_camera/camera_info` · RGB/depth 공용 topic |
| intrinsics 기준값 | `fx=fy=277.191356`, `cx=160`, `cy=120`; 이번 회차의 CameraInfo 전문은 별도 로그로 보존하지 못함 |
| registration | 같은 RGB-D sensor·해상도·CameraInfo 경로는 확인했으나, 경계 3점 육안 비교 캡처가 증빙으로 남지 않음 |
| optical frame | `rgbd_camera_optical_frame`; depth probe의 실제 `frame_id`로 확인 |
| depth 단위 | `32FC1` canonical depth이므로 REP-118에 따라 m |
| depth 통계 | valid 43464, NaN 0, inf 33336, zero 0, negative 0; min 0.115979m, max 9.240039m, center 1.949998m |
| 5분 유지 최초 결과 | RGB 약 12.701Hz, depth 약 12.710Hz였으나 `min=-2.427s`, Zenoh timestamp 거부 RGB 206건·depth 226건으로 무효 |
| 시간 보정 | Windows Time 서비스 시작·강제 동기화 전 WSL/컨테이너가 Windows보다 약 0.7~0.85초 뒤짐; 보정 뒤 약 0.09~0.22초 차이로 감소 |
| 5분 유지 재시험 | RGB 14.047Hz, depth 14.048Hz; min 0.055s/0.056s, max 0.107s, timestamp 오류 각 0건 |
| 역투영 조합 | `/rgbd_camera/image` + `/rgbd_camera/camera_info` + `rgbd_camera_optical_frame`; registration 캡처 뒤 최종 확정 |
| 판정 | `sensor_path_status=deferred`; live 수신과 단위·frame·5분 안정성은 확인, registration 증빙은 Week 3 진입 전에 보완 |

### A의 실패와 해결 증빙

최초 5분 측정은 평균 Hz 숫자만 보면 그럴듯했지만 음수 간격과 timestamp 거부가 섞였으므로 폐기했다.
Windows Time 서비스가 정지해 있었고 WSL·container 시각 차이가 Zenoh 허용치 500ms를 넘은 것이 원인이었다.
실행 중이던 router·Gazebo·MoveIt을 종료하고 Windows 시간을 동기화한 뒤 모든 Zenoh 세션을 다시 시작했다.
재시험에서는 두 topic 모두 5분간 timestamp 오류 0건과 양수 간격을 유지했다.

## 2. spike B — pose 추종과 reset

### 2.1 B-1 one-shot

| 항목 | 실제 값 |
|---|---|
| world 이름 | `week0_spike` |
| gz/ROS 서비스 | `/world/week0_spike/set_pose` |
| ROS 경로 | `ros_gz_bridge` direct service bridge |
| A → B → A | 세 호출 `success=True`; 실제 y 좌표 `0.00 → 0.10 → 0.00` |
| wall elapsed | 442ms / 363ms / 359ms |
| 비고 | 기존 `/usr/bin/time`은 image에 없어서 실패; Bash 내장 `time`과 `TIMEFORMAT`으로 재시험 |

이 값은 매번 `ros2 service call` CLI를 새로 실행한 wall elapsed이며 순수 transport RTT로 해석하지 않는다.

### 2.2 B-2 연속 추종

| 항목 | 실제 값 |
|---|---|
| 조건 | 10Hz × 5초, 1-in-flight, latest-wins |
| generated / sent / completed | 50 / 50 / 50 |
| failures / dropped / timeout | 0 / 0 / 0 |
| max inflight / max backlog | 1 / 1 |
| RTT | 평균 1.596ms / 최대 3.131ms |
| 정지 후 최종 A pose | `final_completed=True`, error 0.015mm |
| 판정 | `pass=True`; T1 연속 경로 가능 |

### 2.3 B-3 reset

| 항목 | 동결값 |
|---|---|
| `reset_backend` | `control_model_only_then_set_pose_A` |
| backend 명령 | `/world/week0_spike/control` → `/world/week0_spike/set_pose` |
| backend 제한 | 비원자적 2단계·모든 model 속도 reset; 최종 robot world에서 atomic adapter 재검증 필요 |
| `reset_state_source` | `/spike_cube/odometry` (`nav_msgs/msg/Odometry`, 50Hz) |
| `reset_position_tolerance_mm` | 1.0 |
| `reset_orientation_tolerance_deg` | 1.0 |
| `linear_speed_threshold_mps` | 0.005 |
| `angular_speed_threshold_rad_s` | 0.01 |
| `quaternion_norm_tolerance` | 0.001 |

| 회차 | reset 전 속도 (m/s) | settle (ms) | position error (mm) | orientation error (°) | linear speed (m/s) | angular speed (rad/s) | state measured | 판정 |
|---|---:|---:|---:|---:|---:|---:|---|---|
| 1 | 0.337985 | 59.868 | 0.386895 | 0 | 0.001 | 0 | true | 통과 |
| 2 | 0.337993 | 59.894 | 0.377103 | 0 | 0.001 | 0 | true | 통과 |
| 3 | 0.328194 | 60.078 | 0.367304 | 0 | 0.001 | 0 | true | 통과 |

세 회차의 quaternion norm은 모두 1.0이었고 `pass=true`였다.

## 3. spike C — IK mode

| 항목 | 실제 값 |
|---|---|
| `robotis_commit` | `32975f87efdb089e82c9ad103f068ef532aabfd2` |
| `effective_kinematics_parameters` | `/root/ros2_ws/src/open_manipulator/open_manipulator_moveit_config/config/open_manipulator_x/kinematics.yaml` |
| config SHA-256 | `f4e894d980e5e9838850b3f1383a069bdbcc7af259c0cf7fbd734daeff3d3a8a` |
| solver | `kdl_kinematics_plugin/KDLKinematicsPlugin` |
| mode A actual parameter | `position_only_ik=True` |
| mode B actual parameter | `position_only_ik=False` |
| `planning_frame` | `world` |
| `arm_base_frame` | `link1` |
| `eef_frame` | `end_effector_link` |
| `world_frame` | `world` |
| `sensor_source_frame` | `rgbd_camera_optical_frame` |
| 접근축 | `+X_tool` |
| 선언한 position 제한 | 5mm |
| 선언한 orientation 제한 | 2° (full-pose) |
| 선언한 tilt 제한 | 10° |

시간 동기화와 전체 process 재시작 뒤 얻은 최종 재시험값은 다음과 같다. 관련 로그의 Zenoh timestamp 오류는 모두 0건이었다.

| 점 | mode | plan | execute | position error (mm) | orientation error (°) | actual tool tilt (°) | 판정 |
|---|---|---|---|---:|---:|---:|---|
| p1 `(0.16, 0.00, 0.12)` | position-only | OK | OK | 4.243 | 9.311 (참고) | 9.293 | 통과 |
| p2 `(0.17, 0.05, 0.12)` | position-only | OK | OK | 3.449 | 13.560 (참고) | 13.524 | tilt 실패 |
| p3 `(0.17, -0.05, 0.12)` | position-only | OK | OK | 4.911 | 14.010 (참고) | 14.004 | tilt 실패 |
| p1 | full-pose | FAIL | — | — | — | — | plan 실패 `99999` |
| p2 | full-pose | FAIL | — | — | — | — | plan 실패 `99999` |
| p3 | full-pose | FAIL | — | — | — | — | plan 실패 `99999` |

- position-only 실행 종료 코드: 0
- full-pose 실행 종료 코드: 1
- 도달 불가능 목표: 두 mode 모두 `expected_fail=true`, code 99999
- 재시험 전에도 같은 형태였으나 timestamp 오류가 섞여 있었다. 오류 0건인 재시험에서도 full-pose 세 점이 모두 실패했으므로 현재 목표·offset 조합의 실제 실패로 판정한다.

### C-4 동결

```text
ik_mode=position-only
ik_mode_status=provisional
validated_points=p1 (0.16, 0.00, 0.12)
rerun_condition=Session 5에서 tool_frame_offset과 workspace grid를 재검증해 final로 재동결; final 전 6A 진입 금지
```

## 4. 세 spike 결과와 계획 변경

| spike | 결과 | 계획 변경 |
|---|---|---|
| A | 5분 재시험 성공, registration 증빙 미완료 | `sensor_path_status=deferred`; Week 3 진입 전에 경계 3점 캡처로 registration 확정 |
| B | B-1·B-2·B-3 성공 | T1 유지; reset backend의 비원자성은 최종 robot world에서 재검증 |
| C | `position-only / provisional`, 안전점 p1 검증 | Session 5에서 tool offset·grid 재시험 후 `final` 재동결; 그 전 6A 금지 |

## 5. Week 0 Gate 판정

- 판정: **조건부 통과**
- 통과 근거: Docker·Gazebo·MoveIt 환경, B의 one-shot·연속 추종·actual pose/twist reset 3회, C의 코드 기반 안전점 1개가 검증됐다.
- 조건 1: RGB-depth 경계 3점 registration 캡처와 CameraInfo 실제값을 Week 3 진입 전에 보존한다.
- 조건 2: Session 5에서 IK workspace·tool offset을 재검증하고 `ik_mode_status=final`로 재동결하기 전에는 Session 6A에 진입하지 않는다.
- 조건 3: Gate 판정과 fallback을 두 사람이 확인한다. 현재 두 번째 확인자는 미기록이다.

## 6. 증빙 파일과 hash

원본 로그는 container의 영속 `/workspace/week0_spike/logs/`에 있다. 대용량 Zenoh 오류 로그는 저장소에 복사하지 않고 경로와 SHA-256을 남긴다.

| 로그 | SHA-256 | 용도 |
|---|---|---|
| `depth_probe.log` | `928d75ff2757cbcff2b0ad589ef65b222f34840949d6086a26ace34d8e3fb659` | depth 단위·invalid·frame |
| `spike_b1.log` | `0ad2004980be89f1da60c5f587419af57f744bd799ff2414f6d03d096b14eea1` | B-1 A→B→A |
| `spike_b2_055403.log` | `59b66c406d2f707007c4d94976592bb6199430215198a40aa83093836d9c2631` | B-2 연속 추종 |
| `spike_b3_055711.log` | `032921ea21001c70dd34890682c15517403dda03f76603363f6ac555efaf9a26` | B-3 reset 3회 |
| `rgb_hz_5min_retest.log` | `0112d88625b7efa393c08779988efe6251165a4d224dabd431dd731966b51a9c` | 시간 보정 후 RGB 5분 |
| `depth_hz_5min_retest.log` | `aef6f7ba54d568f3fa5dfcf603fd449baab25318820b32e23ef2996daa9d9582` | 시간 보정 후 depth 5분 |
| `ik_position_only_retest.log` | `d46dd5573d7d3895475322675fa8dad40362b0b3127cfa1e82cbd2907dfaffdf` | position-only 최종 재시험 |
| `ik_full_pose_retest.log` | `e623e703795dfa84a1331f947cf72d985e809541ac828b6178799c203157194f` | full-pose 최종 재시험 |

관련 생성 파일 hash:

| 파일 | SHA-256 |
|---|---|
| `/workspace/week0_spike/worlds/week0_spike.sdf` | `64bd5f3563c8cfb2d547d1ea7542041a5a8d8613d64c5c32130e7e1023f56640` |
| `/workspace/week0_spike/scripts/follow_spike.py` | `841dc16c7e1c56599f5e1ad53cae6c3027baa4c953c446fe02b167f73c4ca268` |
| `/workspace/week0_spike/scripts/reset_probe.py` | `17680c6c5d6d641de5d46d64dbde77ff6a5ef376170e2c2029a594183bcdfbe5` |
