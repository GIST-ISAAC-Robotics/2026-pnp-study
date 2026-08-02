# 진행 상황과 실행 로그

> **현재 단계:** Week 1 진입 준비 완료 — Session 1 실행 가이드 준비
>
> **다음 Gate:** Week 1 Gate — Session 1~3 시스템 뼈대 검증
>
> **마지막 업데이트:** 2026-08-02

이 문서는 스터디 진행 상황의 단일 기록 원본이다. 회차 종료 시 최신 항목을 위에 추가하고, 성공뿐 아니라 실패·축소·보류 판정도 증빙과 함께 남긴다.

## 단계별 현황

| 단계 | 상태 | 현재 결과 / 진입 조건 |
|---|---|---|
| 커리큘럼·저장소 준비 | **완료** | `curriculum.md` v3.5.5 문서 계약 확정, README·Pages·문서 경로·ignore 규칙 정리 |
| Week 0 — 환경·위험 제거 | **완료** | Gate 조건부 통과와 두 사람 확인 완료; C의 Session 5 `final` 재동결 조건은 6A 전까지 추적 |
| Week 1 — ROS 2 시스템 뼈대 | 대기 | Session 1 실행 가이드 준비 완료; 실제 회차 시작 시 `진행 중`으로 변경 |
| Week 2 — MoveIt 조작 | 대기 | Week 1 Gate 통과 후 시작 |
| Week 3 — RGB-D 인식 통합 | 대기 | Week 2 Gate 통과 후 시작 |
| Week 4 — 신뢰성·평가·정리 | 대기 | Week 3 Gate 통과 후 시작 |
| 최종 시연·회고 | 대기 | 반복 평가와 문서·영상 완료 |

상태 표기는 `대기`, `진행 중`, `완료`, `보류`, `차단` 중 하나를 사용한다.

## 다음 작업

- [x] Session 0-1: ROBOTIS Docker 환경 구축
- [x] Session 0-2: 공식 Gazebo·MoveIt smoke test
- [x] Session 0-3: RGB-D, pose 추종/reset, pose goal·IK mode spike 실행과 조건부 Gate 판정
- [x] `docs/setup/docker.md`에 S0-1 환경 기록
- [x] S0-2 종료 시 `docs/setup/docker.md`에 공식 smoke test 결과 추가
- [x] `docs/setup/week0_spike.md`에 동결값과 Gate 판정 기록
- [x] RGB-depth registration 경계 3점과 CameraInfo 실제값 확인
- [x] Week 0 조건부 Gate와 fallback 두 사람 확인
- [ ] Session 1: ROS graph와 데이터 흐름 실습
- [ ] Session 5에서 IK workspace·tool offset 재시험 후 `ik_mode_status=final` 재동결 (6A 진입 전)

세부 명령·완료 기준·실패 시 전환은 [curriculum.md의 Week 0](./curriculum.md#6-week-0--환경-구축과-위험-제거)을 따른다.

## 회차 로그

### 2026-08-02 — Session 0-3 · 핵심 위험 3종 spike와 Week 0 Gate

- **상태:** 완료 — Week 0 Gate 조건부 통과와 두 사람 확인 완료
- **목표:** RGB-D 입력·registration 계약, ROS 경로의 entity pose 추종과 actual pose/twist reset, 코드 pose goal과 IK mode를 검증하고 Week 0 Gate를 판정
- **수행:** Gazebo `sensors_demo.sdf`의 image·depth·CameraInfo·points를 ROS로 bridge하고 32FC1 depth 통계와 optical frame을 확인했다. `week0_spike.sdf`에서 B-1 A→B→A, B-2 10Hz×5초 1-in-flight 추종, B-3 낙하 중 복합 reset을 수행했다. C에서는 실제 `position_only_ik` true/false를 각각 확인하고 세 안전점과 도달 불가능 목표를 코드로 실행했다. 반복된 Zenoh timestamp 오류는 모든 process를 종료한 뒤 Windows Time 서비스를 시작·강제 동기화하고 전체 topology를 재기동해 A 5분 측정과 C 두 mode를 다시 수행했다.
- **결과:** A depth는 320×240 `32FC1`, `frame_id=rgbd_camera_optical_frame`, center 1.949998m였고 시간 보정 뒤 5분 실측은 RGB 14.047Hz·depth 14.048Hz, timestamp 오류 각 0건이었다. 보완 확인에서 실제 CameraInfo와 하단 RGBD image/depth의 상자·작은 물체·원뿔 경계 정합을 확인해 `sensor_path_status=live`로 확정했다. B-1 세 호출과 실제 A→B→A가 성공했고, B-2는 50/50 완료·failure/drop/timeout 0·평균 RTT 1.596ms·최종 오차 0.015mm였다. B-3는 세 trial 모두 actual state 측정과 네 threshold를 통과했다. C 재시험에서 position-only는 세 점 모두 plan/execute 성공했지만 tilt는 p1 9.293°만 10° 이내였고, full-pose는 세 점 모두 plan 실패했다. `ik_mode=position-only`, `ik_mode_status=provisional`, 검증점 p1 `(0.16, 0, 0.12)`로 동결했다.
- **문제:** 최초 A 5분 로그에는 음수 간격 `-2.427s`와 Zenoh timestamp 거부 RGB 206건·depth 226건이 있었고, 최초 C 로그에도 같은 오류가 섞였다. 진단 당시 Windows Time 서비스가 정지돼 WSL/container가 Windows보다 약 0.7~0.85초 뒤져 500ms 제한을 넘었다. 가이드의 B-1은 존재하지 않는 `/usr/bin/time`을 사용했고, A-5-5의 미터 단위 근거와 C-4·C-5의 실제 판정·기록 절차도 부족했다.
- **결정:** Windows 시간 동기화와 전체 process 재시작 뒤 오류 0건인 재시험 로그를 최종값으로 채택하고 최초 실패 로그도 보존한다. B는 T1과 복합 reset backend를 유지하되 비원자성은 최종 robot world에서 재검증한다. A는 실제 CameraInfo와 registration 경계 정합을 보완 확인해 live 경로로 닫고, C는 Session 5에서 tool offset·workspace grid를 재검증해 `final`로 재동결하기 전 6A 진입을 금지한다. 가이드는 REP-118 단위 근거, Bash 내장 `time`, C-4 로그 판정과 C-5 frame 확인 명령으로 보강한다.
- **다음:** Session 1을 계획대로 시작한다. C의 `final` 재동결은 Session 5에서 완료하며, 그 전에는 Session 6A에 진입하지 않는다.
- **증빙:** [Week 0 spike 결과와 동결값](./docs/setup/week0_spike.md), [Session 0-3 실행 가이드](./guides/2026-07-31-session-0-3-week0-spikes.html), container 영속 로그 `/workspace/week0_spike/logs/`

### 2026-07-31 — Session 0-2 · 공식 Gazebo·MoveIt smoke test

- **상태:** 완료
- **목표:** 공식 OpenMANIPULATOR-X 시뮬레이션에서 Gazebo·RViz 동시 유지, arm·gripper 동작, 네 토픽과 sim time, joint state 일치, 2회 재현을 확인
- **수행:** Zenoh router를 별도 shell에 유지한 채 `open_manipulator_x_gazebo.launch.py`와 `open_manipulator_x_moveit.launch.py use_sim:=true`를 실행했다. controller 3개와 MoveIt action server를 확인하고 RViz에서 arm `home`·`init`, gripper `open`·`close`를 계획·실행했다. `/joint_states`, `/tf`, `/tf_static`, `/clock`, sim time과 clean stop을 확인하고 같은 smoke test를 2회 수행했다.
- **결과:** controller 3개가 모두 `active`, arm·gripper의 모든 plan/execute가 `SUCCEEDED`, action server는 arm·gripper 각각 1개였다. 2회차 실측은 `/tf` 약 `20 Hz`, `/clock` 약 `200 Hz`, `/joint_states` 305초 유지 후 `99.617 Hz`였고 시간 간격은 모두 양수였다. gripper 좌우 관절은 open 약 `0.01892`, close 약 `-0.00992`로 일치했다. MoveIt·Gazebo 로그의 Zenoh timestamp 오류는 각각 0건이었으며, 종료 뒤 router만 남긴 상태에서 `ros2 node list --no-daemon`이 빈 출력임을 확인하고 router까지 종료했다. 운영 판정은 **2회 재현 완료**다.
- **문제:** Step 0-4에서 container의 Git 사용자와 저장소 소유자가 다르다고 판정되어 branch·commit 확인 명령 두 개가 `fatal: detected dubious ownership`으로 실패했다. 따라서 해당 단계에서는 실제 Git 출력값을 얻지 못하고 Session 0-1에서 동결한 기준값을 참조했다. 별도로 1회차에서 메인 PC에만 Zenoh `incoming timestamp ... exceeding delta 500ms` 오류와 `ros2 topic hz`의 음수 간격이 반복됐고 팀원 PC에서는 같은 오류가 발생하지 않았다. Windows 외부 시각 오차 약 `2.87 s`, WSL 시각 offset 약 `2.50 s`를 확인해 공통 ROS·router 설정이 아니라 해당 PC의 Windows↔WSL 시각 동기화 문제로 분리했다.
- **결정:** Git 오류는 `/root/ros2_ws/src/open_manipulator` 경로 하나만 `safe.directory`로 등록한 뒤 두 `rev-parse` 명령을 재실행하는 복구 절차를 가이드에 추가하고, 모든 저장소를 허용하는 wildcard는 사용하지 않는다. Windows 시간을 동기화하고 WSL을 정상 종료·재기동한 뒤 외부 시각 오차를 ms 단위로 낮췄다. 팀 공통 환경은 변경하지 않으며 같은 오류가 특정 PC에서만 나타날 때 해당 PC의 NTP offset을 먼저 확인한다. 기능이 정상 동작한 1회차와 시간 보정 뒤 전체 기준을 통과한 2회차를 Session 0-2의 두 재현으로 확정한다.
- **다음:** Session 0-3에서 RGB-D topic/registration, pose 추종·reset backend, 코드 pose goal·IK mode의 핵심 위험 3종을 검증하고 `docs/setup/week0_spike.md`를 작성
- **증빙:** [Docker 개발 환경과 S0-2 결과](./docs/setup/docker.md), [Session 0-2 실행 가이드](./guides/2026-07-29-session-0-2-gazebo-moveit-smoke-test.html)

### 2026-07-29 — Session 0-1 · ROBOTIS Docker 환경 구축

- **상태:** 완료
- **목표:** ROBOTIS 공식 `jazzy` Docker 환경에 진입하고 `/workspace` 보존, 실제 middleware와 RViz GUI를 검증
- **수행:** Windows 11 + WSL2 Ubuntu 24.04.4에 Docker Engine/Compose를 구성하고 ROBOTIS `jazzy` 저장소와 `robotis/open-manipulator:5.0.0` container를 실행했다. 두 번째 shell, container 제거 전후 volume, ROS 2/colcon/Gazebo/MoveIt, Zenoh router와 RViz를 순서대로 확인
- **결과:** ROBOTIS commit `32975f8`, Docker `29.6.2`, Compose `v5.3.1`, ROS 2 Jazzy, Gazebo Sim `8.11.0`, MoveIt package `24`개, `RMW_IMPLEMENTATION=rmw_zenoh_cpp`, 실제 RMW `rmw_zenoh_cpp`, `ROS_DOMAIN_ID=30`을 확인했다. `/workspace/keep_me.txt`와 스터디 저장소가 container 제거 후에도 보존됐고 RViz는 OpenGL `4.5`로 표시됐다.
- **문제:** Zenoh router를 시작하지 않았을 때 D-2에서 `Unable to connect to a Zenoh router` 경고가 발생했다. router를 켠 뒤에도 D-3의 `container.sh stop → start`가 router process를 종료했으나 터미널 창은 남아 있어 실행 중으로 오인했고, D-5 RViz에서 같은 경고가 재발했다.
- **결정:** `rmw_zenoh_cpp` 사용 시 별도 container shell을 router 전용으로 유지하고, 모든 container 시작·재시작 뒤 `ros2 run rmw_zenoh_cpp rmw_zenohd`를 다시 실행한다. `pgrep`와 경고 없는 `ros2 node list`로 생존을 확인하도록 일일 가이드를 보정했다.
- **다음:** Session 0-2에서 공식 Gazebo·MoveIt launch, arm planning/execution, gripper open/close, `/clock`과 2회 재실행을 검증
- **증빙:** [Docker 개발 환경 기록](./docs/setup/docker.md), [Session 0-1 실행 가이드](./guides/2026-07-28-session-0-1-docker-setup.html)

### 2026-07-28 — 커리큘럼 v3.5.5 참조·구조 일관성 검토

- **상태:** 완료
- **수행:** `curriculum.md` v3.5.4 전문과 README·`docs/README.md`·`progress.md`를 다시 교차 검토해 절 참조, 회차 귀속, 권장 패키지 트리, 표 서식과 기존 계약의 일관성을 확인
- **결과:** §4.4의 `ik_mode` 목표 생성 규칙 참조를 Session 5로 교정하고, Session 4의 「완료 기준에 추가」를 기본 완료 기준 뒤로 이동했다. §4.1 트리에 `pnp_evaluation/test/`를 반영하고, Session 8의 optical frame 동결 회차를 프레임 고정표와 같은 Session 5·7로 맞췄으며, `runner_profile` 용도표에 6A 분리 시험을 명시하고 §12의 불필요한 구분선을 제거했다. 오류 코드 표와 `ErrorCode.msg`, 일곱 최종 실행 구성 필드, cancel 예산 불변식, 표본 축소 표, `docs/README.md` 경로표는 모순 없음을 재확인했다. HTML/Pages 파일은 검토·수정 범위에서 제외했다.
- **문제:** ROS 구현 전이므로 각 계약의 runtime 검증은 해당 회차에서 수행해야 함
- **결정:** 실행 명세 v3.5.5를 Week 0 기준으로 사용
- **다음:** Session 0-1에서 Docker 환경 구축 시작
- **증빙:** [curriculum.md](./curriculum.md), [README](./README.md), [문서 산출물 경로](./docs/README.md)

### 2026-07-28 — 커리큘럼 v3.5.4 최종 문서 경로·존재성 계약 검토

- **상태:** 완료
- **수행:** `curriculum.md`를 처음부터 끝까지 다시 읽고 최소 완료 세트, 회차별 산출물, `docs/README.md` 경로표, Session 12 최종화 책임과 평가 artifact 존재성 계약을 교차 검토
- **결과:** `docs/system_architecture.md`를 시스템 구조도·상태 전이도·오류 코드 표의 단일 원본으로, `docs/frames.md`를 TF tree 원본으로 연결했다. S0-2 smoke test와 S5·S7·S9 frame/world 갱신, 누락됐던 S9 통합 산출물의 경로를 복구했다. 최종 README의 Known issues·축소 사유·후속 확장 경로, `PICK_LIFT_ONLY`의 final GT 비필수 계약, `week0_spike.md`의 실제 최초 작성 회차도 교정했다. HTML/Pages 파일은 검토·수정 범위에서 제외했다.
- **문제:** ROS 구현 전이므로 각 전문 문서의 실제 내용과 runtime 산출물은 해당 회차에서 검증해야 함
- **결정:** 실행 명세 v3.5.4를 Week 0 기준으로 사용
- **다음:** Session 0-1에서 Docker 환경 구축 시작
- **증빙:** [curriculum.md](./curriculum.md), [README](./README.md), [문서 산출물 경로](./docs/README.md)

### 2026-07-28 — 커리큘럼 v3.5.3 batch 산출물·문서 정책 회귀 검토

- **상태:** 완료
- **수행:** `curriculum.md` 전체와 README·`docs/README.md`의 문서 정책, batch 중단·재시작, reset 실패 row, Week 2/4 CSV 계약을 처음부터 끝까지 교차 검토
- **결과:** 회차 일지로 오인되던 ROS graph 전문 문서를 `docs/system_architecture.md`로 정리하고, 정의 없이 한 번 쓰인 batch 식별자 표현 대신 batch별 새 출력 디렉터리와 `batch_summary.yaml` schema를 확정했다. Session 11 산출물 누락, `TASK_CANCELED` 중단 열거, reset 실패 완료 기준, Week 2 reset/final-GT audit 필드도 교정했다. HTML/Pages 파일은 검토·수정 범위에서 제외했다.
- **문제:** ROS 구현 전이므로 runner가 실제 파일을 생성하고 schema를 지키는지는 아직 runtime 검증하지 못함
- **결정:** 실행 명세 v3.5.3을 Week 0 기준으로 사용
- **다음:** Session 0-1에서 Docker 환경 구축 시작
- **증빙:** [curriculum.md](./curriculum.md), [README](./README.md), [문서 산출물 경로](./docs/README.md)

### 2026-07-27 — 커리큘럼 v3.5.2 전수 계약·저장소 회귀 검토

- **상태:** 완료
- **수행:** `curriculum.md` 처음부터 끝까지 producer/consumer, 상태기계, interface, reset·transport·평가 CSV와 README·`docs/README.md`·`progress.md` 기록 체계를 재검토
- **결과:** reset 명령과 actual state 측정 경로를 분리하고 `state_measured`를 추가했다. gripper exact-close 모순, official world argument의 `.sdf` 중복 위험, terminal 뒤 지연 GT 재사용, fixed-bag의 최종 P2 오인, manual cancel code 누락을 교정했다. HTML/Pages 파일은 검토·수정 범위에서 제외했다.
- **문제:** ROS 구현 전이므로 compile·Gazebo runtime 동작은 아직 검증하지 못함
- **결정:** 실행 명세 v3.5.2를 Week 0 기준으로 사용. runtime에서 동결할 값은 `progress.md`와 지정 전문 문서에 증빙 링크와 함께 기록
- **다음:** Session 0-1에서 Docker 환경 구축 시작
- **증빙:** [curriculum.md](./curriculum.md), [README](./README.md), [문서 산출물 경로](./docs/README.md)

### 2026-07-27 — 커리큘럼 v3.5.1 교차 계약 재검토

- **상태:** 완료
- **수행:** RGB-D 관측점→물체 중심 변환, 고정 object orientation과 reset 검증, 6A outer/inner action 경로, Planning Scene 소유권, 중단 batch 규칙을 처음부터 다시 추적
- **결과:** sensor surface·tag 원점이 collision object 중심으로 오인될 여지를 제거하고, reset orientation 응답→CSV, `RunTrial → PickPlace` scope 전파와 static/dynamic scene 경계를 문서 전체에서 일치시킴. 문서 계약 교정만 완료했으며 ROS 구현은 아직 미착수
- **다음:** Session 0-1에서 Docker 환경 구축 시작
- **증빙:** [curriculum.md](./curriculum.md), [문서 산출물 경로](./docs/README.md)

### 2026-07-27 — 커리큘럼 v3.5.0 계약 개정

- **상태:** 완료
- **수행:** transport control·task scope·Planning Scene 소유권·cleanup·평가 threshold의 문서 계약을 전면 교정하고 `docs/` 경로표와 `.gitignore` 추가
- **결과:** T0 one-shot과 pick verify의 service 호출 계약, lift-only/full 평가 분리, evaluator·simulation·manipulation 소유권을 문서상 확정. ROS 구현은 Week 0 전으로 아직 미착수
- **다음:** Session 0-1에서 Docker 환경 구축 시작
- **증빙:** [curriculum.md](./curriculum.md), [문서 산출물 경로](./docs/README.md)

### 2026-07-27 — 커리큘럼과 저장소 구조 확정

- **상태:** 완료
- **수행:** `curriculum.md` v3.4.0 최종 검토, README 구성, GitHub Pages 커리큘럼 뷰어와 진행 로그 체계 정리
- **결과:** 실행 기준은 `curriculum.md`, 진행 기록은 `progress.md`, 과거 비교 문서는 의사결정 아카이브로 역할을 분리
- **다음:** Session 0-1에서 Docker 환경 구축 시작
- **증빙:** [curriculum.md](./curriculum.md), [커리큘럼 웹 뷰](https://gist-isaac-robotics.github.io/2026-pnp-study/)

## 로그 작성 형식

새 기록은 `회차 로그` 바로 아래에 역순으로 추가한다.

```markdown
### YYYY-MM-DD — Session N · 짧은 제목

- **상태:** 완료 | 진행 중 | 보류 | 차단
- **목표:** 이번 회차에서 검증하려던 것
- **수행:** 실제로 실행한 핵심 작업
- **결과:** 수치, 성공/실패, Gate 판정
- **문제:** 원인과 재현 조건. 없으면 `없음`
- **결정:** 동결값, fallback, 다음 회차 이관 사항
- **다음:** 담당자와 다음 행동
- **증빙:** commit, 실행 로그, 영상, rosbag, CSV, 문서 링크
```

## 기록 원칙

- “동작함” 대신 실행 횟수, 성공률, timeout, 오차 등 확인 가능한 값을 쓴다.
- 실패 기록을 지우지 않는다. 수정 후에는 이전 실패와 해결 결과를 연결한다.
- 회차 종료 조건을 못 채웠다면 `완료`로 표시하지 않는다.
- Gate 판정과 fallback은 두 사람이 확인하고 근거 파일을 링크한다.
- 비밀키·토큰·개인정보와 대용량 원본 파일은 기록하지 않는다.
