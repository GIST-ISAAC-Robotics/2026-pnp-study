# Docker 개발 환경 (Session 0-1)

- 수행일: 2026-07-29
- 담당: `leejinh0225` (메인 PC)
- 결과: **완료**
- 다음 회차: Session 0-2 · 공식 Gazebo·MoveIt smoke test

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

인증 코드·토큰·개인 이메일 등 비밀값은 기록하지 않았다.
