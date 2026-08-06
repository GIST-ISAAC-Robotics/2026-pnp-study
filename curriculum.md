# 2026 여름 픽앤플레이스 스터디
## 최종 실행 커리큘럼 v4.0.1 — ROS 2 · Gazebo · MoveIt · RGB-D 개념 순회형

> **기간:** 시작 전 Week 0 + 본과정 4주  
> **인원:** 2명  
> **개정일:** 2026-08-05
>
> **운영 권장:** 주 3회, 회차당 2~3시간 (Week 2만 4회차) + 회차 사이 개인 작업 1인당 주 2시간 상한
> **환경:** Windows + WSL2 + ROBOTIS 공식 Docker 환경  
> **로봇:** OpenMANIPULATOR-X 시뮬레이션 모델  
> **최종 목표:** ROS 2·Gazebo·MoveIt·RGB-D가 연결되는 전체 흐름을 한 번 완주하고, 각 구성 요소의 역할과 연결 방법을 설명할 수 있다.

---

# Quick Start

이 문서는 완성형 로봇 제품의 품질보증 규격이 아니라 **핵심 개념을 직접 연결해 보는 실행 커리큘럼**이다. 회차마다 정상 경로를 먼저 실행하고, 그 회차의 개념을 이해하는 데 꼭 필요한 대표 확인만 수행한다.

다음 원칙을 모든 본과정 회차에 적용한다.

- 같은 기능을 여러 회차에서 반복 검증하지 않는다. 구현이나 환경이 바뀌었을 때만 다시 확인한다.
- 일부러 잘못된 입력·통신 단절·경계 timeout을 만드는 시험은 회차 목표에 직접 필요한 경우에만 한 번 수행한다.
- 정상 결과가 재현되면 다음 개념으로 이동한다. 모든 예외를 닫느라 전체 파이프라인 완주를 늦추지 않는다.
- 실패하면 원인과 다음 행동을 짧게 기록하되, 해당 회차의 핵심이 아니면 별도 신뢰성 과제로 이관한다.
- 정량 평가는 성능 보증이 아니라 결과를 읽는 연습으로 사용한다.

## Week 0에서 고정한 값

Week 0에서 확인한 다음 값은 본과정에서 재사용한다. 관련 환경·world·MoveIt 설정이 바뀌지 않았다면 같은 검증을 매주 반복하지 않는다.

| 고정 항목 | 기록 위치 | 본과정에서 다시 확인하는 때 |
|---|---|---|
| `ik_mode`와 `ik_mode_status` | `docs/setup/week0_spike.md` | Session 5에서 최종 world의 대표 3점으로 한 번 재확인 |
| `planning_frame`·`eef_frame` | `docs/setup/week0_spike.md` | Session 3 TF tree 작성 때 이름과 연결 확인 |
| `reset_backend`·`reset_state_source` | `docs/setup/week0_spike.md` | Session 5 최종 world에서 한 번 확인 |
| RGB-depth 해상도·CameraInfo·optical frame | `docs/setup/week0_spike.md` | Session 7 실제 project world에서 한 번 확인 |
| T1/T0 transport 경로 | `docs/setup/week0_spike.md` | Session 6B 실제 pick-place와 연결할 때 확인 |

## 프레임 고정표

| 의미 | 고정 규칙 |
|---|---|
| `planning_frame` | 런타임 `getPlanningFrame()` 결과. 목표 pose와 TF 변환의 기준 |
| `arm_base_frame` | 공식 모델의 `link1`. base yaw를 설명할 때 사용 |
| `eef_frame` | `end_effector_link` |
| `grasp_frame` | 프로젝트가 정한 접근축 기준 frame |
| `camera_optical_frame` | Session 7에서 project world의 실제 이름 확인 |
| `world_frame` | 공식 모델의 `world` |

공식 URDF에는 `base_link`가 없으므로 이름을 추측해 사용하지 않는다. 목표 pose는 `planning_frame`, 카메라 관측은 실제 optical frame, 로봇 밑면 설명은 `link1`을 구분한다.

## 경로와 완료 표기

| 코드 | 의미 |
|---|---|
| `F0` | ROS·Gazebo·MoveIt·비전·평가를 한 번씩 경험하는 균형 완주형 |
| `L2` | P1 인식과 T1 운반을 연결한 표준 경로 |
| `L1-fallback` | P2 또는 T0를 사용해 전체 흐름을 완주한 축소 경로 |
| `P1` | HSV + registered depth 인식 |
| `P2` | live sensor를 이용하는 단순 대체 인식 경로. 고정 bag은 개발 입력일 뿐 최종 시연 경로가 아님 |
| `T1` | 집은 동안 EE pose를 따라 물체 pose를 연속 갱신 |
| `T0` | lift/place 시점에만 물체 pose를 한 번 갱신 |

최종 결과에는 다음 다섯 값만 필수로 기록한다.

```text
completion_level: L2 | L1-fallback
perception_mode: P1 | P2
transport_mode: T1 | T0
ik_mode: position-only | full-pose
ik_mode_status: final
```

## 최소 완주 경로

| 주차 | 최소한 이것 |
|---|---|
| Week 0 | 환경·RGB-D·reset·IK·transport 가능성 확인 |
| Week 1 | topic과 action 데이터 흐름, 간단한 상태기계, TF·controller·상위 launch |
| Week 2 | 고정 좌표 pick-place, Planning Scene, 간단한 grasp check, T1 또는 T0 |
| Week 3 | RGB-D 위치를 TF로 변환해 pick-place에 연결 |
| Week 4 | 간단한 오류 정리, 5회 자동 반복, CSV·README·시연 |

## 목차

- [1. 확정 구성](#1-확정-구성)
- [2. 최종 결과물과 성공 기준](#2-최종-결과물과-성공-기준)
- [3. 핵심 용어](#3-처음-등장하는-핵심-용어)
- [4. 시스템 구조와 인터페이스](#4-시스템-구조)
- [5. 운영 규칙](#5-운영-규칙)
- [6. Week 0](#6-week-0--환경-구축과-위험-제거)
- [7. Week 1](#7-week-1--ros-2-시스템-뼈대)
- [8. Week 2](#8-week-2--moveit-조작과-고정-좌표-픽앤플레이스)
- [9. Week 3](#9-week-3--p1-hsv--depth-인식)
- [10. Week 4](#10-week-4--통합-평가-최종-정리)
- [11. 축소 순서](#11-전체-일정-지연-시-축소-순서)
- [12. 진단표](#12-예상-문제와-진단-순서)
- [13. Gate 요약](#13-week별-gate-요약)
- [14. 확장 메뉴](#14-확장-메뉴)
- [15. 최종 체크리스트](#15-최종-체크리스트)
- [16. 공식 참고 자료](#16-공식-참고-자료)
- [17. 한 줄 결론](#17-한-줄-결론)
- [18. 개정 이력](#18-개정-이력)

---

# 1. 확정 구성

| 구분 | 확정 내용 | 이번 스터디에서의 의미 |
|---|---|---|
| 전체 방향 | **F0 · 개념 순회형** | 각 기술을 깊게 최적화하기보다 전체 연결을 경험 |
| 기본 완료 | **L2**, 필요 시 **L1-fallback** | 표준 경로를 우선하되 fallback으로 완주 가능 |
| 실행 환경 | **ROBOTIS 공식 Docker 환경** | 환경 구축보다 ROS·MoveIt 실습에 집중 |
| 조작 API | **MoveGroupInterface C++** | 고수준 계획·실행 API를 직접 사용 |
| 물체 인식 | **P1 · HSV + depth** | 색상 영역과 depth로 3차원 위치 계산 |
| Gazebo 운반 | **T1**, 불안정하면 **T0** | 시뮬레이션 물체 운반 원리를 경험 |
| 파지 형태 | **Top-down grasp** | 단순한 한 방향 파지로 범위 제한 |
| 기본 대상 | **단일 색상 큐브** | 다물체·임의 형상은 확장 항목 |
| 신뢰성 시험 | **대표 사례만 필수** | 정상 경로 완주를 방해하는 대규모 fault injection은 선택 |
| 실물 팔 | **범위 제외** | 시뮬레이션 완주 뒤 후속 프로젝트에서 검토 |

## 1.1 이번 구성의 의도

핵심은 다음 흐름을 직접 연결하고 각 화살표의 의미를 설명하는 것이다.

```text
Docker 실행
→ ROS 2 노드·topic·action 구성
→ Gazebo world와 로봇 실행
→ RGB-D에서 물체 위치 계산
→ TF로 planning frame에 변환
→ MoveIt으로 pick-place 계획·실행
→ Gazebo 물체 운반
→ 간단한 결과 기록과 반복
```

정상 경로가 한 바퀴 돌기 전에 대규모 예외 처리·성능 최적화·완전한 평가 자동화를 먼저 만들지 않는다.

## 1.2 이번에 하지 않는 것

- 실제 로봇팔 제작과 sim-to-real
- 모든 잘못된 입력 조합과 통신 장애를 닫는 방어 프로그래밍
- heartbeat·중첩 cancel deadline·`SAFE_STOP` 상태의 완전한 구현
- production 수준의 fault injection matrix와 batch 무결성 감사
- 30회 이상 통계 평가를 필수화하는 것
- MTC·MoveItPy 기반 전체 재구현
- DetachableJoint·마찰 기반 물리 파지
- YOLO·6-DoF pose estimation·PCL 전체 파이프라인
- 강화학습·Navigation·SLAM
- 다수의 임의 형상 물체

필요하면 §14의 확장 메뉴에서 별도 실험한다.

## 1.3 전체 일정표

Week 0 이후 본과정은 Session 6을 6A·6B로 나눈 **13회**다.

| 구간 | 회차 | 핵심 결과 |
|---|---|---|
| Week 0 | S0-1~S0-3 | 공식 환경과 주요 기술 위험 확인 |
| Week 1 | S1~S3 | ROS 데이터 흐름, action·상태기계, TF·controller·상위 launch |
| Week 2 | S4·S5·S6A·S6B | 고정 좌표 조작, grasp check, transport/place |
| Week 3 | S7~S9 | registered RGB-D 인식과 sensor-to-action 통합 |
| Week 4 | S10~S12 | 간단한 복구, 5회 평가, 문서·시연 정리 |

---

# 2. 최종 결과물과 성공 기준

## 2.1 최종 시연

하나의 상위 launch와 하나의 trial 명령으로 다음 흐름을 실행한다.

```text
시뮬레이션 시작
→ RGB-D에서 큐브 위치 계산
→ camera pose를 planning frame으로 변환
→ pick 계획·실행
→ 큐브 운반
→ place 실행
→ 결과 출력·CSV 기록
```

## 2.2 최소 결과물

- 실행 가능한 ROS 2 workspace와 상위 launch
- Gazebo world, 단일 큐브, RGB-D sensor
- MoveGroupInterface 기반 조작 노드
- perception·orchestrator·simulation·evaluation의 최소 노드
- 설치·빌드·실행·종료 방법이 있는 README
- 시스템 구조도와 TF tree
- 최종 5회 trial의 간단한 CSV
- 최종 시연 영상
- 다섯 최종 실행 구성 필드와 사용한 fallback 이유

다음 항목은 권장이지만 필수는 아니다.

- 대표 성공·실패 rosbag2 각 1개
- 인식 debug 이미지
- 10회 이상 추가 반복
- CI build 또는 lint

## 2.3 성공의 정의

각 trial에는 다음 네 항목만 기록한다.

| 항목 | 의미 |
|---|---|
| `detection_ok` | sensor 입력으로 목표 위치를 얻음 |
| `grasp_check_ok` | 물체 중심과 grasp 목표가 동결한 간단한 허용 범위 안에 있음 |
| `place_ok` | 최종 물체 위치가 place zone 안에 있음 |
| `success` | 위 세 항목과 pick-place 실행이 모두 성공 |

Planning Scene attach나 T1 시작 자체를 pick 성공으로 간주하지 않는다. 다만 이를 증명하기 위해 복잡한 다중 지표와 stage mask를 만들지는 않는다. grasp 직전 중심 오차와 최종 물체 위치를 한 번씩 확인하면 충분하다.

### Ground truth 사용 범위

| 용도 | 허용 여부 |
|---|---|
| grasp check와 place 결과 확인 | 허용 |
| T1/T0 물체 운반 | 허용 |
| perception 오차를 보는 선택 분석 | 허용 |
| pick pose 생성·보정 | 금지 |
| orchestrator의 sensor 대체 입력 | 금지 |

GT가 실행 pose에 섞이지 않는다는 원칙은 유지한다. 이 원칙은 인식과 평가의 차이를 배우기 위한 것이며, 별도 artifact 존재성 계약까지 구현할 필요는 없다.

## 2.4 최종 평가 규모

- 필수: 같은 설정에서 **5회** 자동 실행
- 시간이 부족하면: 3회까지 축소하고 이유 기록
- 시간이 남으면: 10회로 확대
- 성공률은 성능 보증 수치가 아니라 어떤 단계가 자주 막히는지 읽는 자료로 사용

최소 성공률을 사전에 강제하지 않는다. 실패가 있어도 원인이 설명되고 전체 흐름을 경험했다면 학습 목표는 달성할 수 있다.

## 2.5 검증 강도 원칙

| 구분 | 필수 수준 |
|---|---|
| 통신 | 정상 메시지·feedback·result가 한 번 이어지는지 확인 |
| Action | 정상 실행과 수동 cancel 각 1회 |
| MoveIt | 도달 가능한 목표 실행. 도달 불가 목표 1회는 planning 실패 개념 확인용으로만 사용 |
| TF | 알려진 점 하나와 실제 sensor 목표가 올바른 frame으로 변환되는지 확인 |
| reset | 최종 world에서 초기 pose로 복귀하는지 1회 확인 |
| 인식 | 대표 위치 3곳의 검출·3D 좌표를 눈으로 비교 |
| 통합 | Week 2·3에서 각 3회, Week 4에서 최종 5회 |

같은 검증은 구현·설정이 바뀌지 않았다면 반복하지 않는다. 경계값 0.1초 차이, 잘못된 enum 조합 전수, 통신 단절·누락 artifact·중복 goal의 고의 주입은 선택 확장이다.

---

# 3. 처음 등장하는 핵심 용어

## ROS 2 graph

실행 중인 node와 topic·service·action의 연결 관계다. 이번 스터디에서는 CLI와 간단한 구조도로 흐름을 확인한다.

## Topic·Service·Action

- **Topic:** 지속적으로 흐르는 데이터
- **Service:** 짧은 요청과 응답
- **Action:** 시간이 걸리는 작업의 goal·feedback·result·cancel

## Gazebo와 RViz

Gazebo는 물리·sensor를 포함한 시뮬레이터이고, RViz는 ROS 데이터와 로봇 상태를 시각화하는 도구다.

## MoveIt·MoveGroupInterface

MoveIt은 IK·충돌 검사·경로 계획을 담당한다. MoveGroupInterface는 코드에서 목표를 보내고 계획·실행 결과를 받는 고수준 C++ API다.

## Planning Scene

MoveIt이 충돌 계산에 사용하는 논리적 환경이다. Gazebo 물체와 별개이므로 필요한 물체를 양쪽에 맞춰 등록한다.

## TF2

서로 다른 frame 사이의 좌표를 시간에 맞춰 변환하는 시스템이다. camera 관측을 MoveIt 목표로 바꾸는 데 사용한다.

## RGB-D·HSV·역투영

RGB-D는 색상 영상과 픽셀별 깊이를 제공한다. HSV로 큐브 영역을 찾고 CameraInfo의 내부 파라미터로 픽셀과 depth를 3차원 점으로 바꾼다.

## sim time과 steady time

sensor·TF timestamp에는 Gazebo sim time을 사용한다. 짧은 로컬 대기 제한이 필요하면 wall/steady time을 사용할 수 있지만, 본과정에서는 복잡한 다중 timeout 계약을 만들지 않는다.

## Pose follower

그리퍼가 물체를 잡은 동안 EE pose를 따라 Gazebo 물체 pose를 갱신하는 단순 transport 방식이다. 물리 접촉 파지의 대체 구현임을 결과에 명시한다.

---

# 4. 시스템 구조

## 4.1 권장 패키지 구조

```text
pick_place_ws/src/
├── pnp_interfaces/       # RunTrial·PickPlace action과 최소 오류 코드
├── pnp_bringup/          # 상위 launch와 공통 parameter
├── pnp_perception/       # RGB-D → target pose
├── pnp_orchestrator/     # target 선택과 전체 순서
├── pnp_manipulation/     # MoveGroupInterface pick-place
├── pnp_simulation/       # world, reset, transport
└── pnp_evaluation/       # 간단한 반복 runner와 CSV
```

패키지 경계는 책임을 설명하기 위한 것이다. 각 패키지마다 별도 상태기계·오류 원장·watchdog을 만들 필요는 없다.

## 4.2 실행 데이터 흐름

```text
RGB image + registered depth + CameraInfo
    → pnp_perception
    → /perception/target_pose
    → pnp_orchestrator
    → TF: camera frame → planning_frame
    → /pick_place/execute
    → pnp_manipulation
    → MoveIt plan / execute
    → pnp_simulation transport
    → pnp_evaluation 결과 확인·CSV
```

Week 2에서는 sensor 대신 YAML의 fixed pose를 사용하고, Week 3에서 같은 입력 자리에 perception pose를 연결한다. fixed pose는 통합 전 baseline일 뿐 최종 sensor-to-action 결과로 간주하지 않는다.

## 4.3 핵심 인터페이스

| 이름 | 형식 | 역할 |
|---|---|---|
| `/clock` | `rosgraph_msgs/msg/Clock` | Gazebo sim time |
| `/camera/color/image_raw` | `sensor_msgs/msg/Image` | RGB 영상 |
| `/camera/depth/image_raw` | `sensor_msgs/msg/Image` | registered depth 영상 |
| `/camera/color/camera_info` | `sensor_msgs/msg/CameraInfo` | 역투영 내부 파라미터 |
| `/perception/target_pose` | `geometry_msgs/msg/PoseStamped` | sensor가 추정한 물체 중심 위치 |
| `/task/run_trial` | `pnp_interfaces/action/RunTrial` | 한 번의 전체 작업 요청 |
| `/pick_place/execute` | `pnp_interfaces/action/PickPlace` | 조작 단계 요청 |
| `/simulation/reset_trial` | `pnp_interfaces/srv/ResetTrial` | 물체를 초기 pose로 복귀 |
| `/simulation/object_ground_truth` | `geometry_msgs/msg/PoseStamped` | transport와 결과 확인 전용 |

T1/T0 transport는 Week 0에서 검증한 ROS service 경로를 재사용한다. 본과정에서는 prepare/control/status를 별도 복잡한 수명주기 계약으로 확장하지 않아도 된다.

## 4.4 Custom action 구성

```text
# RunTrial.action
string run_id
bool use_perception
geometry_msgs/PoseStamped fixed_object_pose
geometry_msgs/PoseStamped place_pose
---
bool success
uint16 error_code
string message
---
string stage
float32 progress
```

```text
# PickPlace.action
string run_id
geometry_msgs/PoseStamped object_pose
geometry_msgs/PoseStamped pick_pose
geometry_msgs/PoseStamped place_pose
bool pick_only
---
bool success
uint16 error_code
string message
---
string stage
float32 progress
```

두 action은 역할을 나눠 전체 작업과 조작 단계를 연결한다. `RunTrial`은 한 번의 전체 작업을 요청하고, `PickPlace`는 로봇 조작 단계를 맡는다. 각 action은 goal·feedback·result와 공통 오류 코드를 통해 진행 상태와 결과를 전달한다.

## 4.5 상태 흐름

```text
orchestrator:
IDLE → SELECT_TARGET → TRANSFORM → CALL_PICK_PLACE → DONE
                                      └────────────→ FAILED

manipulation:
IDLE → SETUP_SCENE → APPROACH → GRASP → LIFT
     → TRANSPORT → PLACE → CLEANUP → DONE
                            └──────→ FAILED
```

위 흐름은 action feedback과 구조도에 쓰는 상위 stage다. Session 6A에서는 `APPROACH`와 `GRASP` 안의 실습 순서를 `PRE_GRASP`·`CLOSE`·`GRASP_CHECK`·`ATTACH`로 더 잘게 나누지만, 별도의 중첩 상태기계를 추가로 만들 필요는 없다.

구현 규칙은 다음 정도로 제한한다.

- 현재 stage를 feedback과 로그에 남긴다.
- 성공하면 `success=true`, 실패하면 `success=false`와 짧은 원인을 반환한다.
- manual cancel 요청을 받으면 가능한 지점에서 중단하고 canceled terminal을 반환한다.
- cleanup은 transport stop·detach·gripper open·동적 collision object 제거를 시도한다.
- 자동 retry는 필수가 아니다. 원인을 보고 다음 trial을 새로 시작해도 된다.

## 4.6 최소 오류 코드

| 값 | 코드 | 의미 |
|---:|---|---|
| 0 | `OK` | 정상 완료 |
| 100 | `TARGET_UNAVAILABLE` | sensor 목표를 얻지 못함 |
| 101 | `TF_FAILED` | camera pose 변환 실패 |
| 200 | `PLANNING_FAILED` | MoveIt 계획 실패 |
| 201 | `EXECUTION_FAILED` | 궤적 실행 실패 |
| 300 | `PICK_CHECK_FAILED` | 간단한 grasp check 실패 |
| 301 | `TRANSPORT_FAILED` | T1/T0 운반 실패 |
| 400 | `RESET_FAILED` | 초기 pose 복귀 실패 |
| 999 | `INTERNAL_ERROR` | 위 범주로 설명되지 않는 오류 |

오류 코드는 분석을 돕는 분류표다. 모든 예외를 미리 만들고 주입해 확인하는 시험 목록이 아니다. 새로운 오류가 실제로 반복될 때만 표를 확장한다.

---

# 5. 운영 규칙

## 5.1 한 회차의 기본 진행

| 구간 | 권장 시간 |
|---|---:|
| 지난 결과 빠른 확인 | 10~15분 |
| 핵심 개념 설명 | 15~25분 |
| 함께 구현 | 70~100분 |
| 정상 경로 실행·대표 확인 | 20~30분 |
| 결과 기록과 commit | 10~20분 |
| **합계** | **120~180분** |

지난 회차 결과가 깨졌더라도 새 회차와 직접 관련이 없으면 원인을 기록하고 별도 복구 작업으로 분리할 수 있다. 모든 과거 시험을 처음부터 되풀이하지 않는다.

## 5.2 회차 종료 조건

다음 세 가지가 있으면 회차를 종료한다.

- 핵심 목표의 정상 실행 결과
- 다음 사람이 이어갈 수 있는 코드·설정 또는 문서
- `progress.md`의 짧은 결과·문제·다음 행동

commit과 전문 문서는 큰 변경이 있을 때 남긴다. 같은 내용을 여러 문서와 로그에 중복 기록하지 않는다.

## 5.3 검증·오류 처리 원칙

필수 확인은 다음으로 제한한다.

- 새 interface를 만들었으면 clean build와 정상 호출 1회
- 새 데이터 변환을 만들었으면 알려진 값 1개로 방향·단위 확인
- 로봇 동작을 만들었으면 대표 목표 실행과 종료 상태 확인
- reset·transport·perception은 실제 연결 회차에서 한 번 확인

다음은 본과정 필수가 아니다.

- 잘못된 enum·빈 field·profile 조합 전수 시험
- heartbeat 단절, terminal 누락, timeout 경계값 fault injection
- 중복 goal·동시 요청 경쟁 조건 전수 시험
- stage mask 부분집합·artifact 존재성 감사
- 성공·실패마다 동일 cleanup 시험 반복
- 같은 설정의 Git provenance·환경 검사를 매 회차 반복

실제 진행 중 같은 실패가 두 번 이상 나타나거나 안전한 종료가 불가능할 때만 관련 검증을 추가한다.

## 5.4 유지할 핵심 원칙

- sensor·TF timestamp는 `use_sim_time:=true`
- 물체 ID는 Gazebo와 Planning Scene에서 일치
- GT는 transport와 결과 확인에만 사용하고 perception pose를 대신하지 않음
- grasp check를 통과하지 못하면 transport를 시작하지 않음
- 단일 물체를 완성하기 전 다물체로 확장하지 않음
- 최종 world와 주요 parameter는 통합 뒤 고정
- 기능 수보다 end-to-end 한 바퀴 완주를 우선

## 5.5 회차 사이 작업

- 개인 작업은 1인당 주 2시간 상한을 유지한다.
- 회차에서 끝내지 못한 부가 검증은 자동으로 숙제가 되지 않는다. 핵심 구현만 다음 회차에 연결한다.
- 반복 runner의 순수 대기 시간은 상한에서 제외할 수 있다.
- Week 2·3의 3회 trial은 회차 안에서 끝내고, Week 4의 최종 5회만 회차 사이 자동 실행을 허용한다.

---

# 6. Week 0 — 환경 구축과 위험 제거

Week 0는 본과정에 들어가기 전의 준비 기간이다. 세 회차의 권장 시간 합계는 **6~7.5시간**이며, 설치와 환경 복구를 포함해 **7.5시간을 하드 캡**으로 둔다.

Week 0는 세 회차로 구성한다.

| 회차 | 내용 | 권장 시간 |
|---|---|---:|
| Session 0-1 | ROBOTIS Docker 환경 구축 | 2~2.5시간 |
| Session 0-2 | 공식 Gazebo·MoveIt smoke test | 1.5~2시간 |
| Session 0-3 | **핵심 위험 3종 spike** | 2.5~3시간 |
| **합계** |  | **6~7.5시간** |

Session 0-3의 시간을 낙관적으로 잡지 않는다. Docker GUI나 bridge 전제까지 복구해야 하면 spike B 주변 작업에 2시간 가까이 걸릴 수 있다. 다만 **B의 설계 가능성 판정 자체는 world와 bridge가 기동된 시점부터 60분 timebox**다. 60분 안에 계약을 검증하지 못하면 `미해결`로 기록하고 유효한 fallback을 선택하거나 hard blocker로 남긴다. 환경 복구 시간과 spike 판정 시간을 섞어 성공처럼 처리하지 않는다. 7.5시간 하드 캡에 도달한 blocker는 그 자리에서 계속 붙잡지 않고 별도 복구 일정으로 분리하되, 아래 Gate가 허용하지 않는 상태로 Week 1을 시작하지 않는다.

Session 0-3은 생략하지 않는다. 여기서 확인하는 세 가지는 본과정에서 늦게 발견될수록 복구 비용이 커지는 항목이며, 각각 Week 2와 Week 3의 성패를 좌우한다.

## Session 0-1 — ROBOTIS Docker 환경 구축

### 목표

ROBOTIS 공식 `jazzy` 저장소와 Docker 스크립트를 사용해 OpenMANIPULATOR-X 개발 환경을 실행한다.

### 배우는 개념

- **Docker image:** 필요한 OS와 프로그램이 준비된 실행 환경의 원본
- **Container:** image로부터 실행된 격리 환경
- **Volume:** container가 삭제되어도 파일을 보존하는 host 폴더 연결
- **Workspace:** ROS 패키지를 빌드하는 작업 공간

### 기본 절차

```bash
git clone -b jazzy https://github.com/ROBOTIS-GIT/open_manipulator.git
cd open_manipulator
./docker/container.sh start
./docker/container.sh enter
```

공식 환경에서 `/workspace`는 host의 `docker/workspace`와 연결된다. 프로젝트 코드는 반드시 `/workspace` 아래에 둔다.

### 실습

1. Docker와 Docker Compose 동작 확인
2. 공식 저장소 clone
3. container start
4. container shell 진입
5. `/workspace`에 테스트 파일 생성
6. container restart 후 파일 보존 확인
7. 두 번째 shell에서 같은 container 진입
8. ROS distro와 설치 패키지 확인
9. `gz sim --version`으로 Gazebo Harmonic 확인
10. `RMW_IMPLEMENTATION` 환경 변수와 실제 middleware를 기록. 공식 Docker v5 계열은 Zenoh을 사용할 수 있으므로 DDS라고 가정하지 않음

### 산출물

- `docs/setup/docker.md`
- Docker 실행 명령
- 사용한 ROBOTIS branch와 commit
- host와 container 경로 대응표

### 완료 기준

- **메인 PC에서 container 진입·GUI 실행 필수**, 두 번째 PC 재현은 권장
- `/workspace` 파일이 container 제거 전후 보존됨
- `ros2`, `colcon`, `gz sim --version`, MoveIt 패키지 확인
- ROBOTIS branch·commit과 `RMW_IMPLEMENTATION` 기록
- GUI 프로그램을 container에서 실행할 수 있음

### 실패 시 전환

#### Docker 명령 자체가 동작하지 않는 경우

1. Docker Engine 또는 Docker Desktop WSL 연동 중 하나만 선택
2. 두 방식을 섞지 않음
3. `docker run hello-world`부터 복구
4. 90분 이상 해결되지 않으면 한 PC를 메인 통합 환경으로 정하고 팀원 PC는 코드·문서 전용으로 사용

#### GUI만 뜨지 않는 경우

1. WSLg 환경 변수 확인
2. ROBOTIS 문서의 GUI 접근 절차 확인
3. container 내부에서 단순 GUI 프로그램으로 분리 시험
4. 2시간 이상 소모되면 E1 host 설치를 비상 경로로 사용

### 시간이 부족할 때

- 팀원 PC에서 Gazebo까지 실행하는 목표를 포기
- 메인 노트북에서만 통합 환경 완성
- 팀원은 같은 repository의 Python 노드와 문서 작업 수행

### 시간이 남을 때

- Dockerfile과 compose 파일 구조 읽기
- container stop/rebuild 과정 기록
- 새 PC에서 repository만 clone해 재현
- VS Code Dev Containers 또는 Codex 작업 경로 연동 시험

---

## Session 0-2 — 공식 Gazebo·MoveIt smoke test

### 목표

커스텀 코드를 작성하기 전에 공식 OpenMANIPULATOR-X 시뮬레이션이 정상인지 확인한다.

### 실행

터미널 A:

```bash
ros2 launch open_manipulator_bringup open_manipulator_x_gazebo.launch.py
```

터미널 B:

```bash
ros2 launch open_manipulator_moveit_config open_manipulator_x_moveit.launch.py use_sim:=true
```

### 실습

1. Gazebo에서 로봇 확인
2. RViz Motion Planning 패널 확인
3. planning group `arm` 선택
4. `home` 또는 `init` 상태 계획과 실행
5. planning group `gripper` 선택
6. `open`, `close` 실행
7. `/joint_states`, `/tf`, `/tf_static`, `/clock` 확인
8. 5분간 실행 유지
9. 종료 후 같은 절차를 다시 실행

### 산출물

- `docs/setup/docker.md` S0-2 갱신본 — 정확한 Gazebo·MoveIt launch 명령, arm/gripper·`/clock` 확인 결과, 두 차례 재실행 증빙

### 완료 기준

- Gazebo와 RViz가 동시에 유지
- arm 계획과 실행 성공
- gripper open/close 성공
- joint state가 Gazebo와 RViz에서 일치
- `/clock` 수신
- 동일 절차를 2회 재현

### 실패 시 전환

- MoveIt만 실패하면 Gazebo와 controller를 먼저 분리 검증
- Gazebo만 실패하면 공식 example world로 renderer 확인
- joint state가 다르면 controller manager와 planning group부터 확인
- 공식 smoke test가 통과하기 전 커스텀 world를 만들지 않음

### 시간이 남을 때

- RViz에서 충돌 물체를 추가하는 공식 MoveGroupInterface 튜토리얼 관찰
- OpenManipulator URDF의 link와 joint 이름 정리
- 공식 launch 파일의 include 관계 추적

---

## Session 0-3 — 핵심 위험 3종 spike

### 목표

본과정에서 가장 늦게 발견되면 치명적인 세 가지를 **지금 확인한다.** 각 항목은 본과정의 특정 회차 전체를 무너뜨릴 수 있으므로, 여기서 실패하면 해당 설계를 Week 1 시작 전에 조정한다.

| spike | 확인 대상 | 실패 시 위험 회차 |
|---|---|---|
| A | RGB-D topic과 pixel registration 계약이 성립하는가 | Session 7~9 전체 |
| B | 물체 pose 추종과 position·orientation+twist reset 경로가 성립하는가 | Session 6B, 평가 reset |
| C | 코드 pose goal과 IK mode 중 어느 경로를 쓸 것인가 | Session 4 이후 전체 |

### 시간 배분

| 구간 | 작업 |
|---|---|
| 0~40분 | spike A · RGB-D bridge와 registration |
| 40~100분 | spike B · entity pose 변경, 짧은 추종, reset backend 판정 |
| 100~140분 | spike C · 코드 pose goal과 IK mode 비교 |
| 140~160분 | 결과 기록과 위험 판정 |

spike B가 가장 길다. 이 spike만 T1과 평가 reset 두 가지를 동시에 검증하기 때문이다.

**timebox로 운영한다.** 60분 안에 성공하지 못하면 실패로 기록한다. B-2 연속 추종만 실패하고 B-1 one-shot이 성공한 경우에는 T0 계약으로 닫을 수 있다. B-1 one-shot 자체가 실패하면 T0도 같은 pose 갱신 경로를 쓸 수 없으므로 transport hard blocker이며, B-3 실패도 유효한 reset backend가 생길 때까지 hard blocker다. 여기서 시간을 초과해 Week 0 전체를 무기한 늘이지 말고, blocker 복구를 별도 일정으로 분리한다.

---

### spike A — RGB-D bridge 확인

#### 목적

Gazebo 카메라 영상이 ROS 2 topic으로 넘어오는 경로 자체가 성립하는지 본다. 인식 알고리즘은 다루지 않는다.

#### 실습

1. 공식 `ros_gz` RGB-D demo 또는 카메라가 포함된 예제 world 실행
2. `ros2 topic list`로 image·depth·CameraInfo topic 확인
3. `ros2 topic hz`로 수신 주기 확인
4. RGB와 depth 각각의 width·height·encoding·frame ID 확인
5. RGB용과 depth용 CameraInfo topic을 구분하고 intrinsics 기록
6. RGB의 `(u, v)`와 depth의 같은 `(u, v)`가 같은 광선을 뜻하는지 registration 확인
7. 정렬 영상이 아니라면 사용할 aligned topic 또는 별도 좌표 변환 경로 확인
8. optical frame이 ROS camera convention인 `+x right, +y down, +z forward`인지 known point로 확인
9. 필요한 경우 `override_frame_id`와 static transform 적용 후 다시 확인
10. depth 단위와 invalid 값 표현 확인
11. 5분간 유지하며 끊김 여부 관찰

#### 완료 기준

- RGB·depth·CameraInfo 세 topic이 모두 수신됨
- 5분 이상 끊김 없이 유지
- RGB/depth 해상도와 registration 여부 기록
- 역투영에 사용할 image·CameraInfo·optical frame 조합 확정
- depth encoding·단위와 optical 축 방향 기록

#### 실패 시

- 공식 demo 자체가 안 되면 bridge 설정이 아니라 렌더러·GPU 문제일 가능성이 높다. Session 0-1의 GUI 진단으로 되돌아간다.
- topic은 뜨는데 주기가 불안정하면 QoS를 sensor data profile로 맞춰 재확인한다.
실패 원인에 따라 fallback을 고른다. `spike A 실패 = 무조건 AprilTag`로 처리하지 않는다.

| 실패 | fallback |
|---|---|
| depth만 실패 | AprilTag pose에 동결한 `tag_to_object_center_offset_tag`를 회전·적용 |
| RGB-depth registration만 실패 | RGB의 AprilTag pose에 동결한 `tag_to_object_center_offset_tag`를 회전·적용하거나 depth 좌표계에서 별도 검출 |
| RGB 전체 실패 | 고정 bag으로 Session 8의 알고리즘 개발만 계속하고 `sensor_path_status=deferred`로 기록. 이는 최종 P2가 아니며 live source 복구 전에는 Session 9·Week 3 Gate·최종 평가를 통과할 수 없음. P0는 진단에만 사용 |
| CameraInfo 실패 | 고정 intrinsics를 YAML에 명시하고 해상도 일치 검증 |

AprilTag의 6-DoF 결과를 쓰더라도 이번 범위에서 downstream object pose에는 보정된 중심 위치만 전달한다. 다만 tag-frame offset을 source frame으로 회전시키기 위해 검출 orientation을 내부 계산에 사용한다. tag 원점을 물체 중심으로 간주하지 않으며, `tag_to_object_center_offset_tag`의 frame·부호·단위를 config에 기록한다. P0 ground truth는 인식 결과를 만드는 fallback이 아니다. 고정 bag은 동기화·역투영 개발을 계속하기 위한 입력일 뿐 `perception_mode=P2`로 표기하지 않는다.

---

### spike B — Gazebo pose 추종과 reset backend 확인

#### 목적

**이번 spike에서 가장 중요한 항목이다.** T1 Pose follower는 "코드로 Gazebo 물체의 위치를 바꿀 수 있다"는 전제 위에 서 있다. 이 전제가 깨지면 Session 6B 전체와 평가 reset 절차가 성립하지 않는다.

#### 배경

Planning Scene의 attach는 MoveIt 내부의 논리 상태이고, Gazebo 물체는 그것으로 움직이지 않는다. 따라서 물체를 손끝에 따라오게 하려면 Gazebo 쪽 pose를 외부에서 갱신해야 한다.

#### 이 spike를 세 단계로 나누는 이유

물체를 **한 번** 옮기는 데 성공하는 것과, T1 follower가 **매 주기 안정적으로** 옮기는 것은 서로 다른 검증이다. one-shot 성공이 증명하는 것은 service bridge 존재, entity 이름 일치, 요청 형식 적합, 기본 pose 복귀 경로 존재까지다.

T1에는 다음 위험이 추가로 남는다.

- 10~20 Hz 반복 호출의 안정성
- 서비스 왕복 지연
- 물리 업데이트와 pose 덮어쓰기 사이의 떨림
- quaternion 연속성
- follower 정지 시점의 최종 pose 정합

따라서 B-1(one-shot)을 통과해도 B-2(연속 추종)를 반드시 수행한다. B-3는 pose만 바꾸는 transport service와 position·orientation·twist를 초기화·검증하는 reset service를 구분한다.

#### 실습 B-1 — one-shot pose 변경 (필수)

1. 큐브 하나가 있는 간단한 world 실행
2. `gz service -l`로 world의 pose 설정 서비스 존재 확인
3. gz 명령으로 큐브를 한 번 다른 위치로 이동
4. **ROS 2 경로에서 같은 동작 수행** — `/world/<world_name>/set_pose`를 `ros_gz_interfaces/srv/SetEntityPose`로 bridge하고 persistent client에서 호출
5. A 위치 → B 위치 → A 위치 순으로 왕복 복귀
6. 1회 호출 지연 측정

#### 실습 B-2 — 짧은 연속 추종 (필수)

여기서는 **"되는가"만 본다.** 주기 최적화·정량 오차·보간은 Session 6B의 일이다.

7. 큐브를 **10 Hz로 5초간** 직선 또는 작은 원 궤적을 따라 이동시키는 최소 스크립트 작성
8. set-pose 요청은 동시에 하나만 in-flight로 유지
9. 이전 요청이 끝나지 않았으면 중간 pose를 버리고 최신 pose 하나만 보관하는 latest-wins 정책 적용
10. persistent client의 왕복 지연, timeout, dropped-update 수를 기록
11. 육안상 심한 점프나 발산이 없는지 확인
12. 스크립트 정지 시 마지막 future 완료를 기다린 뒤 큐브가 최종 pose에 머무는지 확인

#### 실습 B-3 — reset backend 판정 (필수)

`SetEntityPose`는 pose만 설정하며 linear/angular velocity를 초기화하지 않는다. 따라서 반복 평가 reset에 그대로 재사용하지 않는다.

13. 현재 환경에 `simulation_interfaces/srv/SetEntityState` 또는 같은 기능의 interface가 실제 노출되는지 확인
14. 지원되면 pose와 twist를 함께 0으로 설정
15. 지원되지 않으면 다음 중 하나를 구현·시험
    - object 삭제 후 같은 SDF와 seed로 재생성
    - simulation pause 후 pose 설정과 상태 초기화를 묶는 Gazebo system/plugin
    - 별도 custom reset system
16. 명령 경로와 별개로 actual pose·twist를 읽는 `get_entity_state`·backend query·custom query 중 하나를 시험해 `reset_state_source`로 동결
17. reset 직후 이 state source가 읽은 position·shortest-angle orientation 오차와 linear/angular speed가 각 threshold 아래인지 확인. 명령 response나 요청값을 actual measurement로 쓰지 않음
18. 성공한 명령 경로를 `reset_backend`, 측정 경로를 `reset_state_source`로 각각 동결

#### 본과정 뒤 선택 확장으로 넘기는 것

아래 항목은 T1의 원리를 확인한 뒤 더 깊게 다루고 싶을 때만 수행한다. 현재 Session 6B의 필수 범위에는 포함하지 않는다.

- 10 Hz와 20 Hz의 주기 sweep 및 후보 중 최대 안정 주기 측정
- quaternion 정규화·부호 연속성
- 요청 pose와 실제 pose의 정량 오차
- 보간과 예측 적용
- 물리 엔진과 pose 덮어쓰기 경합 분석

#### 완료 기준

- **ROS 2 경로**에서 Gazebo 큐브 pose 변경 성공 (B-1)
- A → B → A 왕복 복귀 성공 (B-1)
- **10 Hz × 5초 연속 갱신에서 실패·무제한 backlog 없음** (B-2)
- 동시 요청 1개, latest-wins 정책에서 dropped update와 timeout이 기록됨 (B-2)
- 육안상 심한 점프나 발산이 없음 (B-2)
- 정지 후 최종 pose가 유지됨 (B-2)
- `reset_backend`로 position·orientation과 twist를 초기화하고, 독립된 `reset_state_source`가 실제 상태를 측정해 네 가지 error/speed threshold를 3회 연속 만족 (B-3)

#### 실패 시

| 증상 | 대응 |
|---|---|
| gz 서비스는 있으나 ROS bridge가 안 붙음 | `ros_gz` 버전과 service bridge 지원 범위 확인 후 재시도 |
| B-1은 되는데 10 Hz B-2에서 밀리거나 떨림 | 1-in-flight/latest-wins, RTT, timeout을 점검한 뒤 B-2를 재시험. 그래도 불안정하면 검증된 B-1 one-shot을 T0로 사용하고 `L1-fallback`으로 전환 |
| ROS service bridge 경로가 없음 | gz topic publish 또는 다른 ROS 2 pose-update adapter를 시험. one-shot A→B→A가 확인되기 전에는 T1과 T0를 모두 동결하지 않음 |
| 어떤 ROS 2 경로로도 one-shot pose를 못 바꿈 | T0도 불가능하므로 **transport hard blocker**. pose-update adapter를 복구하거나 transport 설계를 다시 정하기 전 Week 0 Gate 실패 |
| pose는 돌아오지만 속도가 남음 | `SetEntityPose`를 reset backend로 쓰지 말고 B-3의 state/respawn/custom 경로로 전환 |
| reset backend를 못 정함 | 자동 평가를 시작하지 않고 `RESET_FAILED`로 Gate 실패 처리 |

물체를 옮기는 경로와 물체 상태를 완전히 초기화하는 경로는 별도 계약이다. B-1이 성공했다고 B-3까지 성공한 것으로 처리하지 않는다.

---

### spike C — 코드 기반 goal과 IK mode 동결

#### 목적

RViz에서 마우스로 계획하는 것과 코드에서 목표를 주고 실행하는 것은 다르다. 더 중요한 점은 KDL의 `position_only_ik` 유효값에 따라 같은 pose goal의 의미가 달라진다는 것이다.

설치된 ROBOTIS 소스의 `kinematics.yaml`, container image, launch override가 서로 다를 수 있다. 따라서 “공식 기본값이 당연히 true/false”라고 가정하지 않고, 다음을 기록한다.

```text
robotis_commit
effective_kinematics_parameters
position_only_ik_effective
```

#### 실습

1. 최소 C++ 실행 파일 하나 작성 (또는 공식 예제를 그대로 빌드)
2. `MoveGroupInterface`로 planning group `arm` 연결
3. `getPlanningFrame()`, `getEndEffectorLink()`와 effective kinematics parameter 기록
4. **경로 A — position-only:** `position_only_ik: true` override, 알려진 top-down joint seed, position target으로 3점 계획
5. 각 계획 후 실제 EE 접근축과 world 수직축 사이 `actual_tool_tilt_deg` 측정
6. **경로 B — full-pose:** `position_only_ik: false` override, 위치별 base yaw와 도달 가능한 orientation으로 같은 3점 계획
7. 각 결과에서 position error와 orientation error를 별도 측정
8. plan과 execute 결과를 구분하고 Gazebo 반영 확인
9. 도달 불가능한 목표를 주고 오류 반환 확인
10. 다음 규칙으로 `ik_mode` 동결
    - position-only가 세 점에서 tilt 제한을 만족하면 **position-only 권장**, `ik_mode_status=final`
    - tilt가 무너지지만 full-pose가 같은 세 점의 position·orientation 제한을 만족하면 full-pose 선택, `ik_mode_status=final`
    - 둘 다 세 점을 통과하지 못했지만 한 mode가 안전한 1점에서 plan·execute·tool 자세를 검증했다면 그 mode와 점을 기록하고 `ik_mode_status=provisional`
    - 어느 mode도 안전한 1점을 검증하지 못하면 Gate 실패

#### 완료 기준

- **RViz 클릭 없이** 코드 실행만으로 로봇이 움직임
- plan 실패와 execute 실패가 구분되어 보고됨
- 두 IK mode의 position·orientation 결과가 비교됨
- `ik_mode`, `ik_mode_status`, effective parameter, 실제 tool tilt가 문서에 동결됨
- colcon 빌드와 실행 명령을 문서에 기록

#### 실패 시

- 빌드가 안 되면 `package.xml`과 `CMakeLists.txt`의 `moveit_ros_planning_interface` 의존성부터 확인한다.
- planning group 이름이 다를 수 있으므로 MoveIt config의 SRDF에서 실제 이름을 확인한다.
- full-pose만 실패하면 position-only + joint seed 경로를 유지하되 실제 tilt 검증을 Gate에서 제거하지 않는다.
- position-only 계획은 되지만 tilt가 크면 “IK 성공”을 top-down 성공으로 기록하지 않는다.
- 여기서 오래 걸리면 Session 4에 여유 시간을 미리 배정한다.

---

### 산출물

- `docs/setup/week0_spike.md`
- RGB-D topic·registration·CameraInfo·optical frame 기록
- entity pose 호출 방법, in-flight 정책, 지연·dropped update
- position·orientation+twist `reset_backend`, actual pose·twist `reset_state_source`, `state_measured`와 네 가지 error/speed threshold를 포함한 3회 시험 로그
- 두 IK mode 비교, `ik_mode_status`를 포함한 동결값, pose goal 최소 예제와 빌드 명령
- 세 spike의 성공·실패와 그에 따른 계획 변경 사항

---

### Week 0 Gate

이 Gate는 모든 primary 경로의 성공만 요구하지 않는다. **환경·reset·최소 IK 검증은 hard blocker**이며, RGB-D와 T1은 아래 표의 명시적 P2/T0 fallback 계약으로 닫을 수 있다. 각 항목이 primary 성공 또는 허용된 fallback 중 하나로 결정되어야 Week 1로 간다.

**환경**

- Docker 환경 재실행 가능
- Gazebo와 RViz 동시 실행
- arm과 gripper 제어
- `/clock`, `/joint_states`, TF 확인
- 프로젝트 코드를 저장할 영속 workspace 확정
- ROBOTIS commit과 `RMW_IMPLEMENTATION` 기록

**위험 검증**

- RGB·depth·CameraInfo가 5분 안정 수신되고 registration 계약이 확정되거나, 실패 원인별 **live P2** 입력·frame·평가 계약이 확정됨. 고정 bag만 가능한 경우 `sensor_path_status=deferred`로 Week 1·2까지 조건부 진행할 수 있으나 Session 9·Week 3 Gate·최종 평가 진입 조건은 충족하지 않음
- ROS 경로의 A→B→A와 10 Hz × 5초 1-in-flight 추종이 성공하거나, T0 one-shot 왕복 경로와 `L1-fallback`이 확정됨
- `reset_backend`와 독립 `reset_state_source`가 확정되고 actual position·orientation·twist 측정으로 네 가지 error/speed threshold를 3회 연속 통과 (**측정 없는 fallback 없음**)
- 코드 실행만으로 최소 안전 위치 1점의 pose/position goal plan·execute와 tool 자세가 검증됨 (**검증 자체에는 fallback 없음**)
- `planning_frame`, `arm_base_frame`, `eef_frame`과 선택한 sensor source frame 기록
- `ik_mode`, `ik_mode_status`와 실제 tool tilt/orientation 검증 규칙 동결

### Gate 실패 시 판정 규칙

| 실패 항목 | 판정 | Week 0 Gate |
|---|---|---|
| Docker 또는 smoke test | 환경을 먼저 복구 | **실패** |
| spike A (RGB-D) | live P2 입력·frame·평가 방법을 고정하면 통과. 고정 bag만 있으면 `sensor_path_status=deferred`로 Week 1·2까지만 조건부 진행 | live P1/P2면 통과, deferred면 Week 3 진입 전 재검증 |
| spike B-1 (one-shot entity pose) | ROS 2 경로의 A→B→A pose 갱신을 복구하거나 transport 설계를 재결정 | **성공 전까지 실패** |
| spike B-2 (연속 추종) | B-1 one-shot을 T0로 동결하고 `L1-fallback`으로 전환 | T0 경로와 완료 확인이 닫히면 통과 가능 |
| spike B-3 (reset) | 상태 변경용 `reset_backend`와 actual pose·twist 측정용 `reset_state_source`를 구현하고 3회 연속 settle 재시험 | **성공 전까지 실패** |
| spike C (pose goal/IK mode) | workspace를 안전한 1점까지 줄여 한 mode의 plan·execute·tool 자세를 검증하고 `ik_mode_status=provisional`로 동결. Session 5 재동결 전에는 6A 진입 금지 | 1점도 검증하지 못하면 **실패** |

세 spike 중 둘 이상이 실패하면 Week 1 시작 전에 팀 회의를 한 번 더 한다.

---

# 7. Week 1 — ROS 2 시스템 뼈대

Week 1의 목표는 ROS 구성 요소를 깊게 방어하는 것이 아니라, topic과 action이 연결된 작은 시스템을 만들고 launch·TF·controller로 실행 구조를 이해하는 것이다.

## Session 1 — ROS graph와 데이터 흐름

### 목표

node·topic·message·QoS·parameter·launch의 관계를 작은 graph로 확인한다.

### 배우는 개념

- node와 topic
- publisher와 subscriber
- `PoseStamped`의 frame·timestamp
- QoS의 기본 의미
- parameter YAML과 launch

### 실습

1. `pnp_perception`, `pnp_orchestrator`, `pnp_bringup` 패키지를 확인한다.
2. 임시 target publisher와 monitor를 실행한다.
3. `ros2 node list`, `ros2 topic info`, `ros2 topic echo`로 연결을 본다.
4. YAML 좌표 하나를 바꾸고 수신값이 함께 바뀌는지 확인한다.
5. `docs/system_architecture.md`에 현재 graph를 그린다.

### 완료 기준

- publisher와 subscriber가 같은 `PoseStamped`를 주고받음
- YAML 변경이 재실행 뒤 반영됨
- node·topic·parameter·launch의 역할을 두 사람이 설명 가능

같은 메시지 수를 장시간 세거나 의도적인 잘못된 frame·QoS 조합을 만드는 시험은 하지 않는다.

> **완료 회차 가이드 보존:** 배포된 Session 1 HTML 가이드는 이미 사용 중인 해설 자료와 당시 실습 절차에 맞춰 기존본을 유지한다. 그 가이드에 남은 graph 다중 확인, YAML 원복 재빌드, 로그 재확인과 회차 사이 재실행은 완료 회차의 보존 절차이며, 이후 회차의 반복 의무나 v4.0.1의 최소 완료 기준으로 확대하지 않는다.

---

## Session 2 — Action과 상태기계 골격

### 목표

오래 걸리는 작업을 action으로 요청하고, feedback·result·manual cancel을 경험한다.

### 배우는 개념

- Service와 Action의 차이
- goal·feedback·result·cancel
- 상태기계와 단계 소유권

### 실습

1. `pnp_interfaces`와 `pnp_evaluation` 패키지를 만든다.
2. `RunTrial.action`과 `PickPlace.action`을 작성한다.
3. 로봇을 움직이지 않는 dummy `PickPlace` server를 만든다.
4. orchestrator가 `RunTrial` goal을 받아 inner action을 호출하도록 연결한다.
5. `SELECT_TARGET → CALL_PICK_PLACE → DONE` feedback을 확인한다.
6. 정상 전체 pick-place dummy goal을 한 번 실행한다.
7. 실행 중 manual cancel을 한 번 보내 canceled terminal을 확인한다.
8. `docs/system_architecture.md`에 두 action과 상태 흐름을 추가한다.

### 산출물

- `RunTrial.action`, `PickPlace.action`
- dummy inner server와 orchestrator action chain
- 간단한 상태 전이도

### 완료 기준

- interface clean build 성공
- outer goal이 inner goal로 전달됨
- feedback stage와 최종 result가 보임
- manual cancel 1회가 멈춤과 canceled result로 이어짐
- 정상 실행과 cancel의 차이를 설명 가능

시간이 부족하면 `RunTrial` 하나로 action 개념을 먼저 확인하고, inner action 연결은 Session 4 전에 마친다.

---

## Session 3 — URDF, TF2, ros2_control, 상위 launch

### 목표

로봇 model·frame·controller·launch가 어떻게 하나의 실행 graph를 이루는지 확인한다.

### 배우는 개념

- URDF와 joint/link
- TF tree와 static/dynamic transform
- `ros2_control` controller
- launch argument와 상위 launch

### 실습

1. OpenMANIPULATOR-X의 주요 link·joint·planning group을 찾는다.
2. `world → link1 → ... → end_effector_link` TF tree를 확인한다.
3. arm·gripper controller와 joint state topic을 확인한다.
4. Gazebo·MoveIt·project node를 묶는 상위 launch를 만든다.
5. 기존 smoke-test world를 argument로 전달해 실행한다.
6. `docs/frames.md`를 만들고 실제 frame 이름을 기록한다.

### 완료 기준

- 상위 launch 하나로 기존 world와 project node가 시작됨
- TF tree에서 planning frame·`link1`·EEF 관계를 설명 가능
- arm·gripper controller가 active이고 joint state가 보임
- 모든 project node가 sim time을 사용

고의로 잘못된 world 경로·controller 이름·TF를 넣는 시험은 하지 않는다. 실제 오류가 생기면 해당 원인만 복구한다.

### Week 1 Gate

- topic 데이터 흐름 정상
- action 정상 실행과 manual cancel 1회
- 상위 launch 실행
- TF tree와 controller 상태 설명
- 코드와 핵심 문서 저장

Gate를 통과하면 Week 2로 이동한다. timeout·heartbeat·invalid-input 시험은 Gate 조건이 아니다.

---

# 8. Week 2 — MoveIt 조작과 고정 좌표 픽앤플레이스

Week 2에서는 sensor를 붙이기 전에 고정 좌표로 로봇 동작과 Gazebo 물체 운반을 한 바퀴 완성한다.

## Session 4 — MoveGroupInterface 기초

### 목표

C++ MoveGroupInterface로 관절 목표와 pose 목표를 계획·실행한다.

### 배우는 개념

- planning group과 current state
- joint target·pose target
- plan과 execute
- IK와 도달 가능성
- action server에서 긴 작업을 다루는 기본 구조

### 실습

1. `pnp_manipulation` C++ 패키지를 만든다.
2. `arm`·`gripper` MoveGroupInterface를 만든다.
3. home과 임의 joint target을 실행한다.
4. 대표 pose target 하나를 실행한다.
5. gripper open/close를 함수로 분리한다.
6. Session 2의 dummy inner server를 실제 manipulation action server로 교체한다.
7. 도달 불가 pose 하나를 보내 planning이 실패로 반환되는지만 확인한다.

### 완료 기준

- joint goal과 pose goal 각 1회 실행
- plan 실패가 process crash가 아니라 `success=false`로 반환
- action feedback에 현재 동작 단계가 보임
- gripper open/close 동작

도달 불가 목표는 MoveIt failure 개념을 확인하는 **유일한 필수 고장 사례**다. 재계획 횟수·executor deadlock·동시 goal·cancel timeout 경계는 시험하지 않는다.

---

## Session 5 — 최종 world, Planning Scene, reset, 대표 workspace

### 목표

끝까지 사용할 world를 정하고, Gazebo·Planning Scene·reset·대표 도달 영역을 연결한다.

### 실습

1. robot·table·cube·camera·place zone이 있는 최종 world를 만든다.
2. table과 cube를 Planning Scene에 등록한다.
3. Week 0의 reset backend를 최종 world에 연결한다.
4. reset 뒤 cube pose와 속도가 초기값에 가까운지 한 번 확인한다.
5. 중앙·좌·우 대표 3점에서 IK와 실제 EEF 자세를 확인한다.
6. `ik_mode_status=final`로 기록한다.
7. `docs/world_layout.md`와 `docs/frames.md`를 갱신한다.

### 완료 기준

- 최종 world 하나로 Gazebo와 MoveIt 실행
- Planning Scene에 table·cube가 보임
- reset 1회 뒤 실제 cube가 초기 위치로 돌아옴
- 대표 3점 중 사용할 영역이 정해짐
- IK mode가 `final`로 기록됨

촘촘한 grid CSV, orientation 경계 sweep, reset fault injection은 필수가 아니다. 실제로 실패하는 위치는 workspace에서 제외하고 기록한다.

---

## Session 6A — Pick 동작과 간단한 grasp check

### 목표

고정 좌표 큐브에 접근하고 닫고 들어 올리는 pick 동작을 만든다.

### 작업 단계

```text
SETUP_SCENE → PRE_GRASP → APPROACH → CLOSE → GRASP_CHECK
→ ATTACH → LIFT → CLEANUP
```

### grasp check

T1/T0가 허공의 물체를 강제로 따라오게 하지 않도록, transport 직전에 다음 두 값만 확인한다.

- grasp 목표와 cube 중심의 수평 오차
- gripper 접근축 방향의 높이 오차

허용 범위는 cube 크기와 gripper 폭을 보고 한 번 정한다. 통과하면 transport를 허용하고, 실패하면 해당 trial을 종료한다.

### 실습

1. fixed cube pose에서 pre-grasp·grasp·lift pose를 계산한다.
2. open → approach → close → lift를 실행한다.
3. 간단한 grasp check를 연결한다.
4. Planning Scene attach를 적용한다.
5. 중앙 위치에서 정상 pick을 한 번 완주한다.

### 완료 기준

- pick 단계가 순서대로 실행됨
- grasp check 결과와 오차가 로그에 보임
- lift 1회 완료, 실패하면 원인을 고친 뒤 한 번 재실행
- cleanup 뒤 gripper가 열리고 동적 object가 정리됨

일부러 grasp threshold를 넘기는 위치를 만들거나 attach 실패·scene sync 지연을 주입하는 시험은 하지 않는다.

---

## Session 6B — Transport와 place

### 목표

T1 또는 T0로 cube를 옮기고 place zone에 놓는다.

### 실습

1. Week 0의 T1 pose follower를 실제 EEF pose와 연결한다.
2. lift 뒤 cube가 EEF를 따라오는지 관찰한다.
3. place pose로 이동한다.
4. transport 정지 → detach → gripper open 순서로 놓는다.
5. 최종 cube가 place zone 안인지 확인한다.
6. fixed pose 전체 pick-place를 3회 실행한다.

### 완료 기준

- T1 또는 T0 하나로 전체 이동 완료
- 3회 중 2회 이상 place zone 도달
- 실패한 trial은 stage와 짧은 원인만 기록
- 정상 종료 뒤 다음 trial을 다시 시작할 수 있음

T1의 dropped update·RTT·timeout·relative-pose 오차를 전부 수집하지 않는다. 눈에 띄는 떨림이나 이탈이 반복되면 T0로 전환하고 이유를 기록한다.

### Week 2 Gate

- Session 6B에서 수행한 fixed pose pick-place 3회 결과
- grasp check가 transport 전에 동작
- T1 또는 T0 선택과 이유 기록
- reset 후 다음 trial 실행 가능

Gate는 통계적 성공률이나 10회 연속 무개입 실행을 요구하지 않는다.

---

# 9. Week 3 — P1 HSV + depth 인식

Week 3에서는 Week 2의 fixed pose 입력을 sensor pose로 교체한다. 조작 코드는 가능한 한 바꾸지 않는다.

## Session 7 — RGB-D sensor와 timestamp

### 목표

project world의 RGB·depth·CameraInfo를 ROS에서 받고 frame과 timestamp를 이해한다.

### 실습

1. RGB·depth·CameraInfo topic을 bridge한다.
2. 해상도·encoding·frame 이름을 확인한다.
3. 화면의 같은 물체가 RGB와 depth의 비슷한 픽셀에 있는지 눈으로 확인한다.
4. topic rate와 timestamp가 정상적으로 증가하는지 짧게 관찰한다.
5. `docs/rgbd_topics.md`를 작성한다.

### 완료 기준

- 세 topic 수신
- 실제 해상도·encoding·optical frame 기록
- RGB와 depth가 같은 장면을 나타냄
- sim time이 전진함

잘못된 registration·멈춘 timestamp·가짜 depth를 일부러 만드는 시험은 하지 않는다.

---

## Session 8 — HSV 검출과 3차원 역투영

### 목표

색상 큐브의 중심 픽셀을 찾고 depth와 CameraInfo로 3차원 위치를 계산한다.

### 배우는 개념

- HSV threshold와 mask
- contour·centroid
- ROI depth 중앙값
- pinhole camera 역투영

### 실습

1. HSV mask와 가장 큰 contour를 구한다.
2. centroid 주변 ROI에서 유효 depth 중앙값을 구한다.
3. `X=(u-cx)Z/fx`, `Y=(v-cy)Z/fy`로 3차원 점을 계산한다.
4. cube 높이를 이용해 관측 윗면점에서 중심점을 보정한다.
5. 중앙·좌·우 3곳에서 debug image와 좌표를 비교한다.
6. `/perception/target_pose`를 발행한다.

### 완료 기준

- 세 위치에서 cube가 검출됨
- 유한한 depth와 3차원 좌표가 출력됨
- 좌우 이동 방향이 계산 좌표와 일치
- debug image로 mask를 확인 가능

빈 mask·NaN depth·왜곡된 CameraInfo를 고의로 주입하지 않는다. 실제 인식 실패가 생기면 threshold·조명·ROI를 조정하고 대표 설정 하나를 남긴다.

---

## Session 9 — TF 변환과 sensor-to-action 통합

### 목표

camera frame의 인식 pose를 planning frame으로 바꾸고 Week 2 pick-place에 연결한다.

### 실습

1. target pose timestamp의 TF를 조회한다.
2. camera pose를 `planning_frame`으로 변환한다.
3. 알려진 cube 위치 하나와 변환 결과의 방향·단위를 비교한다.
4. orchestrator의 fixed 입력을 perception 입력으로 바꾼다.
5. sensor-to-action pick-place를 3회 실행한다.
6. `docs/frames.md`와 `docs/world_layout.md`를 갱신한다.

### 완료 기준

- sensor pose가 planning frame으로 변환됨
- GT로 pick pose를 생성·보정하지 않음
- 3회 trial의 detection·grasp check·place 결과 기록
- 최소 1회 end-to-end 성공

TF 오류·stale message·out-of-workspace 입력을 각각 주입하는 시험은 하지 않는다. 실제 실패가 발생한 경우 하나의 대표 로그만 남긴다.

### Week 3 Gate

- live RGB-D 입력 사용
- P1 또는 문서화한 P2 선택
- camera → planning frame TF 변환
- Session 9에서 수행한 sensor-to-action 3회 결과와 최소 1회 전체 성공

---

# 10. Week 4 — 통합, 평가, 최종 정리

Week 4는 제품 수준의 신뢰성 보증이 아니라, 전체 시스템을 정돈하고 간단한 반복 결과를 읽는 주차다.

## Session 10 — 상태기계 연결과 최소 오류 처리

### 목표

dummy 단계를 실제 perception·manipulation·simulation에 연결하고, 정상 종료와 대표 실패 한 가지를 정리한다.

### 실습

1. orchestrator의 상태 흐름을 실제 노드 호출로 연결한다.
2. 각 stage를 feedback과 한 줄 로그로 남긴다.
3. 성공·실패 모두에서 transport stop·detach·open을 시도하는 cleanup을 넣는다.
4. 최소 오류 코드 표를 적용한다.
5. cube를 카메라 시야 밖에 두는 `TARGET_UNAVAILABLE` 사례 한 번만 확인한다.
6. 원래 위치로 복구한 뒤 정상 trial을 다시 실행한다.
7. `docs/system_architecture.md`의 상태 흐름을 갱신한다.

### 완료 기준

- 정상 trial 완료
- target 없음이 crash 없이 `TARGET_UNAVAILABLE`로 끝남
- 복구 뒤 다시 정상 trial 가능
- 실패 stage와 메시지를 보고 원인을 설명 가능

planning·TF·transport·reset·cancel 장애를 각각 따로 주입하지 않는다. 실제로 반복되는 실패만 그때 추가한다.

---

## Session 11 — 간단한 반복 runner

### 목표

reset → trial → 결과 기록을 자동 반복하고 CSV를 읽어 본다.

### CSV 필드

```text
trial_id
seed
perception_mode
transport_mode
detection_ok
grasp_check_ok
place_ok
success
error_code
error_message
place_error_mm
elapsed_s
```

### 실습

1. scenario 5개 또는 같은 scenario의 고정 seed 5개를 준비한다.
2. 각 trial 전 `/simulation/reset_trial`을 호출한다.
3. `/task/run_trial`을 호출하고 result를 기다린다.
4. 최종 GT로 place zone 도달과 오차를 계산한다.
5. 각 row를 `raw.csv`에 기록한다.
6. 성공 수와 오류 코드별 개수를 짧게 요약한다.
7. reset이 실패하면 runner를 멈추고 원인을 고친 뒤 새로 시작한다.

### 완료 기준

- 5회 자동 실행과 CSV 5행
- 각 row에 주요 단계 결과와 오류 원인 기록
- 성공률과 가장 흔한 실패 단계 계산
- parameter·commit·다섯 최종 실행 구성 필드를 README 또는 summary에 기록

reset 실패를 성공률 분모에 넣는 계약, stage별 `NA` 규칙, action·transport artifact 결합, aborted batch schema, `config_hash`, terminal 이후 fresh GT 경계 검증은 필수에서 제외한다. 필요하면 확장 메뉴의 신뢰성 실험에서 다룬다.

시간이 부족하면 3회, 시간이 남으면 10회로 조정한다.

---

## Session 12 — 결과 분석과 정리

### 목표

다른 사람이 README를 보고 전체 파이프라인을 다시 실행할 수 있게 정리한다.

### 필수 작업

1. 현재 검증된 환경에서 README 명령을 처음부터 한 번 따라 실행한다.
2. 설치·빌드·실행·종료·재평가 명령을 정리한다.
3. 시스템 구조도·상태 흐름·TF tree를 최종화한다.
4. 최종 CSV의 성공 수와 대표 실패를 요약한다.
5. 다섯 최종 실행 구성 필드와 fallback 이유를 기록한다.
6. Known issues를 작성한다.
7. 최종 시연 영상을 남긴다.
8. 두 사람이 전체 데이터 흐름을 설명한다.

### 완료 기준

- README 명령 순서가 현재 환경에서 한 번 재현됨
- 최종 시연과 CSV가 존재
- 구조도와 TF tree가 현재 코드와 일치
- 알려진 한계와 후속 과제가 정리됨

발표 자료의 완성도나 방대한 실패 증빙보다 재실행 가능한 정상 경로를 우선한다.

---

# 11. 전체 일정 지연 시 축소 순서

## 가장 먼저 버릴 것

1. 모든 추가 fault injection과 경계값 시험
2. 10회 이상 반복 평가
3. rosbag·영상의 실패 유형별 수집
4. Cartesian path 비교
5. 다중 place zone
6. 조명·noise stress test
7. MTC·MoveItPy·T2 비교

## 다음으로 단순화할 것

- P1이 지연되면 live P2 사용
- T1이 불안정하면 T0 사용
- 복잡한 approach 대신 pose goal 두 단계 사용
- 최종 5회를 3회로 축소
- action 2층 연결이 늦으면 하나의 action으로 먼저 완주

## 끝까지 유지할 것

- 단일 물체 sensor-to-action 흐름
- MoveGroupInterface 조작
- camera → planning frame TF
- Planning Scene과 Gazebo 물체의 차이 설명
- 간단한 grasp check
- reset 후 다음 trial
- 실행 README와 최종 시연

---

# 12. 예상 문제와 진단 순서

| 증상 | 먼저 볼 것 | 최소 대응 |
|---|---|---|
| Docker GUI가 뜨지 않음 | DISPLAY·GPU·container 로그 | Week 0 문서의 검증된 GUI 복구 경로 사용 |
| Gazebo와 RViz 자세가 다름 | `/joint_states`, sim time, controller | 같은 controller와 timestamp 사용 확인 |
| MoveIt 계획 실패 | planning group, frame, workspace | 대표 안전 pose로 돌아가고 목표 영역 축소 |
| action이 끝나지 않음 | feedback이 멈춘 stage, server process | 해당 process 재시작 후 한 번 재실행 |
| cube가 손을 따라오지 않음 | T1 service와 entity 이름 | T1을 한 번 복구하고 계속 불안정하면 T0 |
| HSV가 흔들림 | 조명·threshold·mask | 대표 조명에서 threshold 하나 동결 |
| 3D 위치가 틀림 | depth 단위·CameraInfo·optical frame | 알려진 위치 하나로 방향과 단위 재확인 |
| TF 변환 실패 | frame 이름과 timestamp | 최신 live pose로 재시도하고 TF tree 확인 |
| 다음 trial이 깨짐 | reset 결과와 잔존 attach | simulation·Planning Scene을 정리하고 재시작 |

이 표는 문제를 해결하기 위한 출발점이다. 모든 항목을 사전에 고의 재현하는 시험 목록으로 사용하지 않는다.

---

# 13. Week별 Gate 요약

| Gate | 반드시 되는 것 | 실패 시 |
|---|---|---|
| Week 0 | 환경·RGB-D·reset·transport·IK 경로 확인 | 문서화한 fallback 또는 blocker 판정 |
| Week 1 | topic·action·TF·controller·상위 launch | 막힌 구성 요소만 복구 |
| Week 2 | Session 6B의 fixed pick-place 3회와 T1/T0 | 동작 단순화 후 완주 |
| Week 3 | Session 9의 live sensor-to-action 3회와 최소 1회 성공 | P2 또는 workspace 축소 |
| Week 4 | Session 11의 runner 5회, CSV, README, 시연 | 3회로 축소하고 한계 기록 |

Gate는 다음 주차에 필요한 정상 연결을 확인하는 장치다. 품질보증 승인 절차처럼 사용하지 않는다.
표의 횟수는 해당 주차 실습에서 이미 얻은 결과를 재사용하며, Gate 판정을 위해 같은 실행을 추가로 반복하지 않는다.

---

# 14. 확장 메뉴

본과정과 최종 시연을 끝낸 뒤 하나만 선택한다.

## A. 신뢰성 실험

- heartbeat와 watchdog
- nested cancel 전파와 timeout 예산
- invalid goal·중복 goal·통신 단절 fault injection
- stage별 artifact 존재성 검사
- 20~30회 batch와 중단·재개

## B. P1 견고성

- 조명·depth noise·물체 위치 변화
- 검출률과 위치 오차 비교

## C. MTC 또는 MoveItPy 비교

- 공식 예제 실행
- 현재 MoveGroupInterface 구조와 차이 정리

## D. T2 DetachableJoint

- 별도 world에서 attach/detach 시험
- T1/T0와 구조 비교

## E. 다물체 2개

- 두 색상 검출
- 고정 순서로 순차 pick-place

---

# 15. 최종 체크리스트

## 환경·실행

- [ ] 공식 또는 명시적으로 문서화한 Docker 환경
- [ ] 상위 launch 하나로 world·MoveIt·project node 실행
- [ ] 모든 project node에 sim time 적용
- [ ] 현재 workspace에서 README 명령 순서 1회 재실행

## ROS·MoveIt

- [ ] topic과 action 데이터 흐름 설명 가능
- [ ] manual cancel 1회 확인
- [ ] planning frame·camera frame·EEF 관계 기록
- [ ] joint goal·pose goal 실행
- [ ] Planning Scene table·cube 등록
- [ ] `ik_mode_status=final`

## 인식·조작

- [ ] live RGB·depth·CameraInfo 수신
- [ ] HSV + depth 또는 문서화한 P2
- [ ] camera pose를 planning frame으로 변환
- [ ] grasp check 뒤 transport 시작
- [ ] T1 또는 T0로 place 완료
- [ ] GT가 pick pose 생성에 사용되지 않음

## 평가·문서

- [ ] 최종 5회 또는 축소 3회 CSV
- [ ] detection·grasp check·place·overall 결과 기록
- [ ] 다섯 최종 실행 구성 필드와 fallback 이유
- [ ] 시스템 구조도와 TF tree
- [ ] Known issues와 후속 과제
- [ ] 최종 시연 영상

---

# 16. 공식 참고 자료

- ROBOTIS OpenMANIPULATOR-X Quick Start Guide  
  https://docs.robotis.com/docs/systems/openmanipulator_x/quick_start_guide/

- ROBOTIS OpenMANIPULATOR-X Overview  
  https://docs.robotis.com/docs/systems/openmanipulator_x/overview/

- ROBOTIS MoveIt with Gazebo  
  https://docs.robotis.com/docs/systems/openmanipulator_x/ros_controller/ros_controller_experiment/

- ROBOTIS OpenMANIPULATOR repository  
  https://github.com/ROBOTIS-GIT/open_manipulator

- MoveIt Move Group C++ Interface  
  https://moveit.picknik.ai/main/doc/examples/move_group_interface/move_group_interface_tutorial.html

- MoveIt move_group architecture  
  https://moveit.picknik.ai/main/doc/concepts/move_group.html

- Gazebo ROS 2 integration  
  https://gazebosim.org/docs/harmonic/ros2_overview/

- ros_gz packages and demos  
  https://github.com/gazebosim/ros_gz

- ros_gz SetEntityPose demo  
  https://docs.ros.org/en/jazzy/p/ros_gz_sim_demos/

- ros_gz package resource export  
  https://github.com/gazebosim/ros_gz/blob/ros2/ros_gz_sim/README.md

- Gazebo PosePublisher system  
  https://gazebosim.org/api/sim/8/classgz_1_1sim_1_1systems_1_1PosePublisher.html

- `simulation_interfaces/SetEntityState`  
  https://docs.ros.org/en/ros2_packages/jazzy/api/simulation_interfaces/srv/SetEntityState.html

- ROS 2 message_filters  
  https://docs.ros.org/en/jazzy/p/message_filters/

- ROS 2 interfaces  
  https://docs.ros.org/en/jazzy/Concepts/Basic/About-Interfaces.html

- ROS 2 `geometry_msgs/PoseStamped` definition  
  https://github.com/ros2/common_interfaces/blob/jazzy/geometry_msgs/msg/PoseStamped.msg

- ROS REP 103 — SI units and coordinate conventions  
  https://www.ros.org/reps/rep-0103.html

- ROS 2 rosbag2  
  https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools/Recording-And-Playing-Back-Data/Recording-And-Playing-Back-Data.html

- Gazebo DetachableJoint — 확장 참고  
  https://gazebosim.org/api/sim/8/classgz_1_1sim_1_1systems_1_1DetachableJoint.html

---

# 17. 한 줄 결론

> **정상 경로를 먼저 연결해 ROS 2·Gazebo·MoveIt·RGB-D 픽앤플레이스를 한 바퀴 완주하고, 필요한 최소 확인만 남긴 뒤 신뢰성 심화는 선택 확장으로 분리한다.**

---

# 18. 개정 이력

## v4.0.1 — 2026-08-05

- 기존 해설 자료와 맞춘 Session 1 가이드를 완료 회차 보존본으로 명시하고, 현재 최소 완료 기준과 구분
- Week 0의 핵심 실습은 유지하면서 삭제된 `6A-min`·Session 6B 하위 절을 가리키던 참조를 선택 확장 설명으로 교정
- 가이드 목록·작성 지침·진행 기록과 Session 2 준비 절차의 소규모 교차 문서 불일치를 정리

## v4.0.0 — 2026-08-05

- Week 0 본문은 변경하지 않고 Week 1~4를 개념 순회형으로 전면 개편
- 회차당 30~40분의 고정 fault injection을 제거하고 정상 경로·대표 확인 중심으로 운영 변경
- Session 2의 heartbeat·중첩 cancel timeout·invalid profile/scope·`SAFE_STOP`·stage mask 시험을 필수 범위에서 제거
- 오류 코드를 22종 비정상 코드에서 8종 핵심 범주로 축소
- Week 2·3 반복을 각 3회, Week 4 최종 평가를 5회로 축소
- Session 11의 artifact 존재성·NA·aborted batch·config hash 계약을 선택 신뢰성 확장으로 이관
- 반복 검증은 구현·환경이 바뀐 경우에만 수행하도록 명시

## v3.1~v3.5.5 — 상세 신뢰성 설계기 (현재 기준에서 폐기)

- 중첩 action, 다층 상태·status, heartbeat·watchdog, timeout·retry, 30·20·10회 평가, batch·artifact 계약까지 제품형 신뢰성 구조를 상세 설계했다.
- TF·reset·transport·평가 데이터의 생산자와 소비자, 문서 경로, fallback 조건을 반복 교정한 기록은 `progress.md`와 Git 이력에 보존한다.
- 위 계약은 v4.0.1의 현재 필수 범위가 아니다. 필요한 심화 항목만 §14의 확장 메뉴에서 선택적으로 참고한다.

## 유지한 핵심 방향

- F0 개념 순회형, MoveGroupInterface, 기본 P1 HSV+depth, 기본 T1 Pose follower
- 단일 물체 sensor-to-action 완주, reset, 최소 오류 분류, Gate, 실행 README
- 실물 팔·YOLO 학습·강화학습·6-DoF 물체 자세 추정은 본과정에서 제외
