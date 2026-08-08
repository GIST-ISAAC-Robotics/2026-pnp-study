# Frame과 controller 기준

> 최초 작성: Session 3 ([실행일])
>
> 기준 환경: ROBOTIS OpenMANIPULATOR-X simulation · ROS 2 Jazzy
>
> 이후 갱신: Session 5, Session 7, Session 9, Session 12

## 1. 핵심 frame

| 역할 | 실제 frame | 근거 | 상태 |
|---|---|---|---|
| World / planning frame | `world` | URDF root와 MoveIt RobotModel | 확인 |
| Robot base | `link1` | `world_fixed`의 child link | 확인 |
| End effector | `end_effector_link` | SRDF end effector parent link | 확인 |
| Grasp frame | Session 5에서 확정 | 실제 grasp offset·접근축 검증 | 대기 |
| Camera link / optical frame | Session 7에서 확정 | 실제 RGB-D topic과 CameraInfo | 대기 |

## 2. TF tree

```text
world
└── world_fixed (fixed) → link1
    └── joint1 → link2
        └── joint2 → link3
            └── joint3 → link4
                └── joint4 → link5
                    ├── end_effector_joint (fixed) → end_effector_link
                    ├── gripper_left_joint → gripper_left_link
                    └── gripper_right_joint (mimic) → gripper_right_link
```

- `/tf_static`: `world_fixed`, `end_effector_joint`처럼 움직이지 않는 관계
- `/tf`: `joint1`~`joint4`, gripper처럼 joint state에 따라 달라지는 관계
- `tf2_echo world end_effector_link` 결과: [확인한 translation·rotation 또는 로그 경로]
- `view_frames` 산출물: [PDF 파일명]

## 3. MoveIt semantic model

| 항목 | 실제 값 |
|---|---|
| Planning group | `arm` |
| Gripper group | `gripper` |
| Named arm states | `init`, `home` |
| Named gripper states | `open`, `close` |
| End effector | `end_effector` |
| End-effector parent link | `end_effector_link` |

## 4. ros2_control 연결

| Controller | 상태 | 대상 / 인터페이스 |
|---|---|---|
| `joint_state_broadcaster` | [active 여부] | `/joint_states` 발행 |
| `arm_controller` | [active 여부] | `joint1`~`joint4` · FollowJointTrajectory |
| `gripper_controller` | [active 여부] | `gripper_left_joint` · GripperCommand |

`gripper_right_joint`는 `gripper_left_joint`를 multiplier `1`로 따르는 mimic joint이므로 controller가 직접 명령하는 관절은 left 하나입니다.

## 5. 이번 회차 실행값

- 상위 launch: `pnp_bringup/week1_system.launch.py`
- world argument: `[empty_world 또는 실제 전달값]` — `.sdf` 확장자는 쓰지 않음
- project node `use_sim_time`: [모두 true / 미통과]
- controller 세 개: [모두 active / 미통과]
- TF `world → end_effector_link`: [연결 / 미통과]

## 6. 이후 회차에서 확정할 항목

- Session 5: grasp frame, tool offset, 접근축과 부호 규약
- Session 7: camera link·optical frame과 timestamp
- Session 9: camera → planning 변환의 known-point 검증
- Session 12: 최종 TF tree와 재현 명령
