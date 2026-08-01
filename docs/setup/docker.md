# Docker 개발 환경과 공식 smoke test (Session 0-1·0-2)

- 수행일: 2026-07-29 (S0-1) · 2026-07-31 (S0-2)
- 담당: `leejinh0225` (메인 PC)
- 결과: **Session 0-1·0-2 완료**
- 다음 회차: Session 0-3 · 핵심 위험 3종 spike

## 1. Windows / WSL host

| 항목 | 실제 값 |
|---|---|
| Windows | Microsoft Windows 11 Home · `10.0.26200` (build `26200`) |
| WSL | `2.7.11.0` · kernel `6.18.33.2-microsoft-standard-WSL2` |
| WSLg | `1.0.73.2` · `DISPLAY=:0` · X11 socket 확인 |
| 배포판 | WSL2 · Ubuntu `24.04.4 LTS` |
| systemd | `running` |
| GPU 1 | NVIDIA GeForce RTX 5070 Laptop GPU · Windows driver `32.0.16.1074` |
| GPU 2 | AMD Radeon(TM) 610M · Windows driver `32.0.21036.8001` |
| GUI 전제 | WSLg/X11 및 container RViz 표시 성공 |

## 2. Docker

| 항목 | 실제 값 |
|---|---|
| 방식 | Docker Engine in WSL |
| Client / Server | Docker Engine Community `29.6.2` / `29.6.2` |
| API | `1.55` |
| Compose | Docker Compose plugin `v5.3.1` (`docker compose`) |
| hello-world | 성공 · `hello-world:latest` image 확인 |
| container | `open_manipulator` · `Up` 확인 |

`docker` 그룹이 root급 권한을 부여한다는 점을 확인하고 개인 개발용 WSL에서 사용했다.

## 3. ROBOTIS 공식 환경

| 항목 | 실제 값 |
|---|---|
| 저장소 | <https://github.com/ROBOTIS-GIT/open_manipulator> |
| branch | `jazzy` |
| commit | `32975f87efdb089e82c9ad103f068ef532aabfd2` |
| commit 날짜 | 2026-06-26 |
| commit 제목 | `Merge pull request #374 from ROBOTIS-GIT/main` |
| image | `robotis/open-manipulator:5.0.0` |
| image digest | `sha256:d2e2f0545cc71c9710430c5e959f6321296b59114ea237f0bf4608d739b60059` |

## 4. 시작·진입과 Zenoh router

WSL host에서 container를 시작하고 작업 shell에 진입한다.

```bash
cd ~/open_manipulator
./docker/container.sh start
./docker/container.sh enter
```

`rmw_zenoh_cpp`의 ROS graph discovery를 위해 **별도 container shell**을 router 전용으로 유지한다.

```bash
# 새 WSL 터미널
cd ~/open_manipulator
./docker/container.sh enter
ros2 run rmw_zenoh_cpp rmw_zenohd
```

정상 실행 중에는 마지막 명령이 종료되지 않고 해당 shell의 프롬프트가 돌아오지 않는다. 다른 container shell에서 다음을 확인한다.

```bash
pgrep -af '[r]mw_zenohd'
ros2 node list
```

`container.sh stop`은 container를 중지·제거하므로 router도 함께 종료한다. **모든 `stop → start` 또는 container 재생성 뒤 위 router 절차를 다시 실행한다.**

## 5. Host ↔ Container 경로

| WSL host | Container | 용도 |
|---|---|---|
| `~/open_manipulator/docker/workspace` | `/workspace` | 영속 프로젝트 공간 |
| `.../workspace/2026-pnp-study` | `/workspace/2026-pnp-study` | 스터디 저장소 |
| `~/open_manipulator` | `/root/ros2_ws/src/open_manipulator/` | ROBOTIS 공식 소스 |
| `/tmp/.X11-unix` | `/tmp/.X11-unix` | X11/WSLg |
| `/dev`, `/dev/shm` | `/dev`, `/dev/shm` | 장치·공유 메모리 |

## 6. Container 확인 결과

| 항목 | 명령 | 실제 출력 |
|---|---|---|
| ROS distro | `echo $ROS_DISTRO` | `jazzy` |
| ros2 CLI | `ros2 --help` | 성공 |
| colcon | `command -v colcon` | `/usr/bin/colcon` |
| colcon-core | package 확인 | `0.20.1+upstream-1` |
| Gazebo | `gz sim --version` | Gazebo Sim `8.11.0` |
| MoveIt | `ros2 pkg list \| grep -ci moveit` | `24` |
| RMW 환경 변수 | `echo $RMW_IMPLEMENTATION` | `rmw_zenoh_cpp` |
| 실제 RMW | `ros2 doctor --report` | `middleware name: rmw_zenoh_cpp` |
| ROS domain | `echo $ROS_DOMAIN_ID` | `30` |
| Zenoh router | `pgrep -af '[r]mw_zenohd'` | launcher와 `rmw_zenohd` process 확인 |
| ROS graph 조회 | `ros2 node list` | 경고 없이 종료 코드 `0` |

## 7. Volume 보존

- 절차: `/workspace/keep_me.txt` 생성 → `stop` → `start` → `enter` → host/container 양쪽에서 `cat`
- 기록 내용: `session 0-1 volume test 2026-07-28T18:20:42+00:00`
- 결과: **보존됨**
- 스터디 저장소: `/workspace/2026-pnp-study/.git` 확인
- 추가 shell: 같은 container와 `/workspace` 내용 확인

## 8. GUI

| 항목 | 결과 |
|---|---|
| Host WSLg/X11 | 성공 · `DISPLAY=:0`, X11 socket 확인 |
| Container `rviz2` | 성공 |
| OpenGL | `4.5 (GLSL 4.5)` |
| software rendering | 불필요 |

`QStandardPaths: XDG_RUNTIME_DIR not set`은 root container가 `/tmp/runtime-root`를 사용하는 경고이고, `Stereo is NOT SUPPORTED`는 입체 렌더링 미지원 안내다. 두 메시지 모두 일반 RViz 표시를 막지 않았다.

## 9. 발생 문제와 해결

### Zenoh router 미실행 경고

- 증상: `ros2 pkg list`, `ros2 doctor --report`, `rviz2`에서 `Unable to connect to a Zenoh router after 1 attempt(s)` 경고
- 최초 원인: `RMW_IMPLEMENTATION=rmw_zenoh_cpp`였지만 `rmw_zenohd`를 시작하지 않음
- 재발 원인: D-3의 `container.sh stop → start`가 실행 중이던 router를 container와 함께 종료했으나, router용 터미널 창은 남아 있어 실행 중으로 오인
- 해결: container 시작·재시작 뒤 별도 container shell에서 `ros2 run rmw_zenoh_cpp rmw_zenohd` 재실행
- 검증: `rmw_zenohd` process 확인, 별도 shell의 `ros2 node list` 종료 코드 `0`, RViz OpenGL 초기화 성공
- 가이드 반영: [Session 0-1 일일 실행 가이드](../../guides/2026-07-28-session-0-1-docker-setup.html)에 router 전용 shell과 재시작 규칙 추가

## 10. 재현 명령 요약

```bash
# WSL host
cd ~/open_manipulator
./docker/container.sh start

# container 작업 shell
./docker/container.sh enter

# 별도 WSL 터미널 → router 전용 container shell
cd ~/open_manipulator
./docker/container.sh enter
ros2 run rmw_zenoh_cpp rmw_zenohd
```

## 11. Session 0-2 · 공식 Gazebo·MoveIt smoke test

### 11.1 실행 환경과 명령

Session 0-1에서 확정한 ROBOTIS `jazzy` commit
`32975f87efdb089e82c9ad103f068ef532aabfd2`, image
`robotis/open-manipulator:5.0.0`, `rmw_zenoh_cpp`, `ROS_DOMAIN_ID=30` 환경을
그대로 사용했다. router를 별도 container shell에서 계속 실행한 뒤 Gazebo와 MoveIt을
순서대로 올렸다.

```bash
# T0 · router
ros2 run rmw_zenoh_cpp rmw_zenohd

# T1 · Gazebo
ros2 launch open_manipulator_bringup open_manipulator_x_gazebo.launch.py

# T2 · MoveIt + RViz
ros2 launch open_manipulator_moveit_config \
  open_manipulator_x_moveit.launch.py use_sim:=true
```

### 11.2 준비 gate

| 항목 | 결과 |
|---|---|
| 필수 토픽 | `/clock`, `/joint_states`, `/tf`, `/tf_static` 모두 publisher 확인 |
| controller | `joint_state_broadcaster`, `arm_controller`, `gripper_controller` 모두 `active` |
| MoveIt node | `/move_group`, `/rviz2_moveit` 확인 |
| sim time | `move_group=true`, `rviz2_moveit=true`, `robot_state_publisher=false` |
| action server | `/arm_controller/follow_joint_trajectory` 1개, `/gripper_controller/gripper_cmd` 1개 |
| RViz | MotionPlanning `Status: Ok`, RobotModel 표시 |

`robot_state_publisher=false`는 공식 Gazebo launch가 해당 노드에 `use_sim_time`을
명시하지 않는 현재 구성의 예상값이다. `/tf` 수신과 RViz 상태가 정상이므로 임의로
변경하지 않았다.

### 11.3 arm·gripper 실행 결과

RViz MotionPlanning에서 매 동작의 Start State를 `<current>`로 두고 Plan 성공 뒤
Execute를 눌렀다.

| 동작 | 결과 | 완료 직후 관절값 |
|---|---|---|
| arm `home` | plan/execute `SUCCEEDED` | `joint2=-1.00002`, `joint3=0.70004`, `joint4=0.29996` |
| arm `init` | plan/execute `SUCCEEDED` | `joint1~4` 절댓값 최대 약 `4.5e-5` |
| gripper `open` | plan/execute `SUCCEEDED` | left=`0.018919`, right=`0.018919` |
| gripper `close` | plan/execute `SUCCEEDED` | left=`-0.009917`, right=`-0.009917` |

Gazebo의 joint state를 RViz가 같은 자세로 표시했고, gripper right mimic joint가 left와
같은 값으로 움직였다.

### 11.4 토픽·시간과 5분 유지

| 항목 | 2회차 실측 |
|---|---|
| `/tf` | 약 `19.98~20.00 Hz`, interval `0.047~0.060 s` |
| `/clock` | 약 `200.00 Hz`, interval `0.003~0.007 s` |
| `/joint_states` 유지 | `2026-07-31 03:12:36~03:17:41 KST`, 총 `305 s` |
| `/joint_states` 최종 | `99.617 Hz`, 최근 10,000 sample interval `0.004~0.021 s` |
| Gazebo Zenoh timestamp 오류 | `0` |
| MoveIt Zenoh timestamp 오류 | `0` |
| GUI | Gazebo·RViz 동시 생존, RViz MotionPlanning `Status: Ok` |

`ros2 topic hz`를 정해진 시간 뒤 종료할 때의 wait-set invalid-context 한 줄은
`Ctrl+C` 또는 `timeout`으로 context를 종료하면서 생긴 측정 종료 메시지다. 실행 중
timestamp 역행이나 topic 단절로 판정하지 않았다.

### 11.5 두 차례 재현 판정

| 회차 | 판정 | 근거 |
|---|---|---|
| 1회차 | **성공으로 확정** | Gazebo·RViz, controller, arm·gripper와 topic 흐름이 동작했다. 메인 PC의 host clock skew 때문에 Zenoh timestamp 오류가 섞였지만 팀원 PC에서는 같은 오류가 없었고 공통 launch·router 문제는 아니었다. |
| 2회차 | **성공** | 시간 보정 뒤 전체 준비 gate, 네 동작, 네 토픽, sim time, 305초 유지, joint state 일치와 clean stop을 통과했고 timestamp 오류는 0건이었다. |

운영 결정에 따라 기능이 정상 동작한 1회차와 시간 보정 뒤 전체 기준을 통과한 2회차를
Session 0-2의 두 재현으로 인정한다.

### 11.6 Step 0-4 Git 소유권 보호 오류

- 증상: 기준 환경 재확인에서 branch와 commit을 읽는 두 `git -C ... rev-parse`
  명령이 `fatal: detected dubious ownership in repository at
  '/root/ros2_ws/src/open_manipulator'`로 실패함
- 원인: container에서 Git 명령을 실행한 사용자와 저장소 소유자가 다르다고 Git이
  판단해 보안상 저장소 접근을 거부함
- 영향: 해당 Step 0-4에서는 branch와 commit의 실제 출력값을 얻지 못함.
  Session 0-1에서 이미 검증·동결한 `jazzy`,
  `32975f87efdb089e82c9ad103f068ef532aabfd2`를 기준값으로 유지했으며
  `ros2 control list_controllers --help | head`의 `usage:` 출력은 정상 도움말로 판정함
- 후속 가이드 조치: 같은 오류가 발생하면 정확한 저장소 경로만 신뢰 대상으로 등록한 뒤
  두 `rev-parse` 명령을 다시 실행하도록 Step 0-4에 복구 절차를 추가함

```bash
git config --global --add safe.directory /root/ros2_ws/src/open_manipulator
git -C /root/ros2_ws/src/open_manipulator rev-parse --abbrev-ref HEAD
git -C /root/ros2_ws/src/open_manipulator rev-parse HEAD
```

모든 저장소를 허용하는 `safe.directory '*'`는 사용하지 않는다. 이는 ROS, controller,
Gazebo 또는 MoveIt 동작 실패가 아니라 Git의 저장소 소유권 보호 기능에 따른 사전 확인
실패다.

### 11.7 메인 PC에서만 발생한 시각 동기화 문제

- 증상: Zenoh가 `incoming timestamp ... exceeding delta 500ms is rejected`를
  반복 출력하고 `ros2 topic hz`의 최소 interval이 약 `-2.49 s`로 표시됨
- 범위: 메인 실습 PC에서만 재현됐으며 팀원 PC에는 동일 오류가 없었음
- 원인 분리: Windows의 `time.windows.com` 대비 오차 약 `-2.87 s`, WSL NTP offset
  약 `-2.50 s`를 확인. router 중복이나 Gazebo·MoveIt 중복 process는 없었음
- 조치: Windows 「날짜 및 시간」에서 시간을 동기화한 뒤 MoveIt → Gazebo → router
  순서로 정상 종료하고 `wsl --shutdown` 후 재기동
- 결과: 동기화 직후 외부 시각 오차 약 `2~3 ms`, 시험 종료 뒤 재확인 약 `68 ms`.
  Windows↔WSL 비교도 명령 실행 지연을 포함해 약 `93 ms`였고 WSL NTP 동기화 상태는
  `yes`

같은 오류가 특정 PC에서만 발생하면 팀 공통 ROS 설정을 바꾸기 전에 해당 PC에서 다음을
확인한다.

```powershell
w32tm /stripchart /computer:time.windows.com /samples:5 /dataonly
```

오차가 Zenoh 기준 `500 ms`를 넘거나 topic interval이 음수라면 실행 중인 작업을 먼저
clean stop하고 Windows 시간을 동기화한다. 그 뒤 `wsl --shutdown`으로 WSL 시계를
재생성하고 container와 router부터 다시 시작한다. `wsl --shutdown`은 모든 WSL shell과
container process를 끊으므로 실행 중간에 바로 사용하지 않는다. 정상 기준은 외부 시각
오차가 충분히 `500 ms` 아래이고, topic interval이 모두 양수이며, 새 로그에 timestamp
오류가 반복되지 않는 것이다.

### 11.8 관찰된 비차단 경고

- MoveIt의 `Cannot infer URDF/SRDF` 뒤 `/robot_description` topic fallback
- `/recognize_objects` action server 미사용 안내
- RViz 내부 node의 동일 이름 경고 — 실제 RViz process는 1개
- Gazebo physics engine의 mimic constraint 미지원 안내 — ros2_control joint state에서
  left/right 값 일치 확인
- SIGINT clean stop 때 launch가 자식 process의 exit code `-2`를 기록하는 종료 로그

위 메시지만으로 실패 판정하지 않았고 node·controller·action server·관절값과 실제 GUI
동작을 함께 확인했다.

### 11.9 clean stop

1. MoveIt·RViz에 SIGINT
2. Gazebo launch에 SIGINT
3. router가 살아 있는 동안 `ros2 node list --no-daemon`이 빈 출력이고
   `gz sim`, `move_group`, `rviz2` process가 없는지 확인
4. 이번 회차에서 띄운 router에 SIGINT
5. router·Gazebo·MoveIt·RViz·robot_state_publisher·bridge process가 모두 없는지 확인

최종 확인을 통과했다. `ros2 node list --no-daemon`의 완전한 빈 출력은 다른 ROS 작업이
없는 이 격리 환경에서 정상이다. 다른 작업이 함께 실행 중이라면 전체가 비어야 하는 것이
아니라 `/move_group`, `/rviz2_moveit`, `/controller_manager`,
`/robot_state_publisher`가 사라졌는지를 판정한다.

인증 코드·토큰·개인 이메일 등 비밀값은 기록하지 않았다.
