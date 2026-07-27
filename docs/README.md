# 문서 산출물 경로

`docs/`는 회차별 반복 일지가 아니라 설정·구조를 장기간 보존할 전문 문서만 둔다. 구현·평가 요구사항의 원본은 루트 [`curriculum.md`](../curriculum.md), 실제 진행 상황과 회차 로그의 단일 원본은 [`progress.md`](../progress.md)다.

```text
docs/
├── README.md
├── setup/
│   ├── docker.md
│   └── week0_spike.md
├── system_architecture.md
├── frames.md
├── world_layout.md
└── rgbd_topics.md
```

## 경로표

| 파일 | 최초 작성 회차 | 필수 내용 |
|---|---|---|
| `docs/setup/docker.md` | S0-1 최초 작성 · S0-2 갱신 | Docker image tag 또는 digest, ROBOTIS package commit, WSL/GPU/GUI 조건, 설치·실행·종료 명령; S0-2에서 공식 Gazebo·MoveIt smoke test 결과 추가 |
| `docs/setup/week0_spike.md` | S0-2~S0-3 | `ik_mode`와 status, `planning_frame`, 상태 변경용 `reset_backend`, actual pose·twist 측정용 `reset_state_source`, `state_measured`, RGB-depth registration/frame과 `sensor_path_status`, T1/T0 spike 결과, 관련 config hash와 측정 로그 링크 |
| `docs/system_architecture.md` | S1 최초 작성 · S2~S3 갱신 | node/topic/service/action 목록, QoS, action cancel/timeout, `/task/status` heartbeat, ROS graph 캡처 또는 명령 결과 |
| `docs/frames.md` | S3 | `planning_frame`, `link1`, `eef_frame`, `grasp_frame`, camera optical frame, world frame, TF tree, 접근축과 부호 규약 |
| `docs/world_layout.md` | S5 | table/cube/camera 위치와 치수, model/object ID, frame 이름, 조명, `project_world_file`과 extensionless official `world` argument, reset initial pose·`reset_state_source`·position/orientation/속도 threshold, PosePublisher와 GT bridge 설정, `surface_to_center_offset_source`와 P2 `tag_to_object_center_offset_tag`, 고정 yaw·canonical object orientation, gripper close-travel/final-aperture envelope, place threshold 계산 입력 |
| `docs/rgbd_topics.md` | S7 | RGB/depth/CameraInfo topic, 해상도, QoS, registration 방식, optical frame, timestamp 동기화 설정 |

## 작성 원칙

- 아직 해당 회차를 수행하지 않은 문서는 미작성이어도 된다.
- 빈 placeholder를 여러 개 미리 만들 필요가 없다.
- 실제 작성할 때 위 고정 경로를 사용하고 필요한 부모 디렉터리도 함께 만든다.
- 회차 일지와 실행 증빙 링크는 `progress.md`에 기록한다.
- `docs/` 문서는 설정·구조의 장기 보존 자료다.
- 요구사항이 충돌하면 `curriculum.md`를 원본으로 삼고 경로표도 함께 갱신한다.
