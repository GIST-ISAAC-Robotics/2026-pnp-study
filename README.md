# 2026 여름 픽앤플레이스 스터디

> RGB-D 카메라로 물체를 찾고, MoveIt으로 경로를 계획하여, Gazebo에서 물체를 집어 지정 위치에 놓는 과정을
> **반복 실행 가능한 ROS 2 시스템**으로 완성한다.

GIST ISAAC Robotics · 2명 · Week 0 + 본과정 4주

---

## 확정 구성

| 구분 | 확정 | 의미 |
|---|---|---|
| 전문화 방향 | **F0 · 균형 완주형** | ROS·시뮬레이션·MoveIt·비전·평가를 모두 한 번씩 |
| 난이도 | **L2 · 표준** | 센서 입력부터 반복 평가까지, 오류 처리와 1회 재시도 포함 |
| 실행 환경 | **E2 · ROBOTIS Docker** | ROS 2 Jazzy + Gazebo Harmonic |
| 조작 API | **M3 · MoveGroupInterface C++** | 고수준 C++ API로 계획·실행·attach |
| 물체 인식 | **P1 · HSV + depth** | 색상 마스크와 깊이 영상으로 3D 위치 계산 |
| Gazebo 운반 | **T1 · Pose follower** | 손끝 자세를 따라 Gazebo 물체 pose 갱신 |

**로봇** OpenMANIPULATOR-X (팔 4-DoF + 그리퍼) · **대상** 단일 색상 큐브 · **파지** top-down

---

## 회차 구성

**Week 0** (3회 · 6~7시간)

| 회차 | 내용 |
|---|---|
| 0-1 | ROBOTIS Docker 환경 구축 |
| 0-2 | 공식 Gazebo·MoveIt smoke test |
| 0-3 | **핵심 위험 3종 spike** — RGB-D bridge · entity pose · 코드 pose goal |

**본과정** (13회 · 주 3회, Week 2만 4회)

| 주차 | 회차 | 내용 |
|---|---|---|
| Week 1 | S1~S3 | ROS 2 시스템 뼈대 — 노드·action·상태기계 골격·TF·launch |
| Week 2 | S4, S5, **S6A, S6B** | MoveIt 조작과 고정 좌표 픽앤플레이스 |
| Week 3 | S7~S9 | P1 HSV + depth 인식과 sensor-to-action 통합 |
| Week 4 | S10~S12 | 신뢰성·반복 평가·최종 정리 |

---

## 최소 완주 경로

일정이 밀렸을 때 **이것만 지키면 완주로 본다.**

| 주차 | 최소한 이것 |
|---|---|
| Week 0 | Docker 실행 · Gazebo/RViz 동시 실행 · **spike 3종 판정** |
| Week 1 | 상위 launch 하나로 실행 · action cancel/timeout · TF tree 설명 |
| Week 2 | 고정 좌표 pick-place 성공 · **grasp gate가 잘못된 파지를 거부** · T1 또는 T0 |
| Week 3 | 카메라로 찾은 좌표로 pick-place 성공 · 오류가 코드로 분류됨 |
| Week 4 | reset 후 자동 반복 · 최소 20회 평가 CSV · README로 재실행 가능 |

---

## 구현 중 되돌리지 말 것

두 차례 교차 검토에서 **명시적으로 기각한** 단순화다. 일정이 밀려도 이 방향으로 돌아가지 않는다.

| 기각한 단순화 | 실제 |
|---|---|
| "Planning Scene attach = pick 성공" | attach는 논리 상태이며 물리적 파지를 증명하지 않는다 |
| "물체 pose를 한 번 옮기면 T1 검증 끝" | one-shot과 연속 follower는 다른 검증이다 |
| "CSV에 파지 오차 열 하나면 충분" | 기록이 아니라 **T1 시작 조건**으로 걸어야 한다 |
| "모든 위치에 같은 고정 quaternion" | 자유도 4에 구속 6은 과구속이라 해가 없다 |
| "grasp 오차는 그리퍼 x·y로 계산" | 접근축이 z라는 보장이 없다. 벡터 투영으로 계산한다 |
| "action callback에서 MGI를 부르면 멈춘다" | 항상은 아니나 executor 구성에 따라 위험이 크다 |
| "인식이 늦으면 ground truth로 대체" | grasp gate와 평가기에서만 허용한다 |

---

## 성공의 정의

T1은 실제 접촉으로 물체를 집지 않으므로, 단일 성공률은 파지 품질과 무관해진다. 성공을 셋으로 나눠 기록한다.

| 지표 | 의미 |
|---|---|
| `pipeline_success` | 시스템 단계가 오류 없이 끝남 |
| `grasp_plausible_success` | 실제였다면 잡혔을 기하 조건을 만족 |
| `place_success` | 물체가 목표 영역에 최종 위치 |

최종 `success`는 **셋을 모두 만족**할 때만 참이다.

---

## 패키지 구조

```text
pick_place_ws/src/
├── pnp_interfaces/      # PickPlace.action
├── pnp_simulation/      # worlds · models · config · launch
├── pnp_perception/      # detector_node.py · depth_projector.py
├── pnp_manipulation/    # MoveGroupInterface action server (C++)
├── pnp_transport/       # pose_follower.py
├── pnp_orchestrator/    # orchestrator.py · state_machine.py
├── pnp_evaluation/      # scenario_runner.py · evaluator.py
└── pnp_bringup/         # launch · config · rviz
```

ROBOTIS 공식 패키지는 복사하지 않고 dependency로 사용한다. 수정이 필요하면 fork와 commit을 명시한다.

---

## 브랜치 전략

```text
main
├── feature/s01-ros-skeleton
├── feature/s04-move-group
├── feature/s07-rgbd
└── fix/tf-timeout
```

회차를 끝낼 때 Pull Request로 합친다. 본과정 중 `main`에 실험 코드를 바로 밀어 넣지 않는다.

---

## 끝까지 지킬 원칙

- 모든 프로젝트 노드는 `use_sim_time:=true`
- 물체 ID는 Gazebo와 Planning Scene에서 동일하게 사용
- Ground truth는 grasp gate·평가기·Week 2 기준선에서만 사용 (perception·orchestrator 입력 금지)
- **파지 적합성을 통과하지 못하면 T1을 시작하지 않음**
- Gazebo world는 Session 5에서 만든 최종 골격 하나만 유지
- MoveGroupInterface는 action callback 안에서 직접 blocking 호출하지 않음
- 단일 물체를 완성하기 전 다물체로 확장하지 않음
- 기능 수보다 반복 실행 가능성을 우선

---

## 문서

- [`curriculum.md`](./curriculum.md) — 회차별 실행 커리큘럼 (목표·실습·완료 기준·실패 시 전환)

### 읽는 법

문서가 길다. 처음부터 다 읽지 않는다.

| 등급 | 항목 | 읽는 시점 |
|---|---|---|
| **필수** | 목표 · 실습 · 완료 기준 | 해당 회차 직전 |
| **권장** | 배우는 개념 · 산출물 · 실패 시 | 설명 시간과 막혔을 때 |
| **여유 시** | 시간이 남을 때 · 확장 메뉴 | Gate를 여유 있게 통과했을 때만 |

---

## 이번 범위가 아닌 것

실물 팔 · sim-to-real · MTC/MoveItPy 전체 재구현 · DetachableJoint 물리 연결 · 마찰 기반 물리 파지 ·
YOLO 학습 · 6-DoF pose estimation · PCL 전체 파이프라인 · 강화학습 · LeRobot · Isaac Lab ·
다수의 임의 형상 물체 · BehaviorTree.CPP · Navigation · SLAM

본과정을 완주한 뒤의 확장 메뉴에만 남긴다.
