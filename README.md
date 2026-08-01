# 2026 여름 픽앤플레이스 스터디

ROS 2 · Gazebo · MoveIt 2 · RGB-D를 연결해, 시뮬레이션 기반 픽앤플레이스 시스템을 처음부터 반복 평가까지 완주하는 2인 스터디입니다.

> **현재 상태 — 2026-07-31**
>
> 실행 커리큘럼 `v3.5.5` · **Session 0-1·0-2 완료** · 다음 Session 0-3 핵심 위험 3종 spike

## 바로가기

| 문서 | 용도 |
|---|---|
| [커리큘럼 웹 뷰](https://gist-isaac-robotics.github.io/2026-pnp-study/) | 검색·자동 목차·장별 접기를 지원하는 기본 열람 페이지 |
| [일일 실행 가이드](https://gist-isaac-robotics.github.io/2026-pnp-study/guides/) | 날짜별 준비물, 명령, 검증 기준을 모은 따라 하기용 가이드 보관함 |
| [실행 커리큘럼](./curriculum.md) | 구현 계약과 회차별 실습을 담은 원본 Markdown |
| [진행 상황과 로그](./progress.md) | 현재 단계, 다음 작업, 회차별 결과와 증빙 기록 |
| [문서 산출물 경로](./docs/README.md) | `docs/` 전문 문서의 정확한 경로와 작성·갱신 회차 |

## 스터디 개요

| 항목 | 내용 |
|---|---|
| 기간 | 시작 전 Week 0 + 본과정 4주 |
| 인원 | 2명 |
| 환경 | Windows + WSL2 Ubuntu 24.04 · ROBOTIS 공식 Docker · ROS 2 Jazzy · Gazebo Harmonic · MoveIt 2 |
| 대상 | OpenMANIPULATOR-X 시뮬레이션 |
| 최종 목표 | RGB-D 인식 → TF 변환 → pick → transport/place → 반복 평가·CSV |
| 운영 방식 | 매 회차 실행 증빙과 로그를 남기고 Week별 Gate로 다음 단계 진입 여부 판정 |

상세 성공 기준, fallback, 인터페이스 계약과 회차별 완료 조건은 [curriculum.md](./curriculum.md)를 기준으로 합니다. README는 입구이고, 커리큘럼이 계약 원본입니다. 둘이 싸우면 커리큘럼이 이깁니다.

## 진행 기록 방법

진행 기록의 단일 원본은 [progress.md](./progress.md)입니다.

1. 회차를 시작할 때 `현재 단계`와 `이번 회차 목표`를 갱신합니다.
2. 회차가 끝나면 단계 표의 상태를 바꾸고, 최신 로그를 위쪽에 추가합니다.
3. 실행 명령, commit, 영상, rosbag, CSV 등 재현 가능한 증빙을 링크합니다.
4. 실패도 삭제하지 않고 원인·판정·다음 행동을 남깁니다.

GitHub Pages 메인 화면은 `progress.md`를 직접 불러오므로 별도 HTML 수정 없이 최신 기록을 표시합니다. README의 위 상태 요약은 큰 단계가 바뀔 때만 함께 갱신합니다.

## 일일 실행 가이드

매일 실제로 따라 할 준비물, 명령, 검증 기준과 기록 방법은 [일일 실행 가이드 보관함](https://gist-isaac-robotics.github.io/2026-pnp-study/guides/)에 모읍니다. 가이드의 날짜는 **제작일 기준**입니다. 새 가이드는 [`guides/`](./guides/)에 HTML 파일을 추가하고 [`guides.json`](./guides/guides.json)에 항목 하나를 등록하면 보관함에 최신순으로 나타납니다.

| 제작일 | 회차 | 가이드 |
|---|---|---|
| 2026-07-31 | Session 0-3 | [핵심 위험 3종 spike](https://gist-isaac-robotics.github.io/2026-pnp-study/guides/2026-07-31-session-0-3-week0-spikes.html) |
| 2026-07-29 | Session 0-2 | [공식 Gazebo·MoveIt smoke test](https://gist-isaac-robotics.github.io/2026-pnp-study/guides/2026-07-29-session-0-2-gazebo-moveit-smoke-test.html) |
| 2026-07-28 | Session 0-1 | [ROBOTIS Docker 환경 구축](https://gist-isaac-robotics.github.io/2026-pnp-study/guides/2026-07-28-session-0-1-docker-setup.html) |

파일명과 목록 갱신 규칙은 [`guides/README.md`](./guides/README.md)에 정리되어 있습니다.

## 의사결정 아카이브

아래 두 문서는 현재 실행 기준이 아니라, 커리큘럼 방향을 결정하는 과정에서 만든 비교·의사결정 자료입니다. 다음 스터디를 설계할 때 재사용할 수 있도록 보존합니다.

| 문서 | 내용 |
|---|---|
| [01 · 스터디 방향 선택지](https://gist-isaac-robotics.github.io/2026-pnp-study/01_study_direction_options.html) | 4주 스터디의 여러 방향과 장단점 비교 |
| [02 · B안 세부 결정](https://gist-isaac-robotics.github.io/2026-pnp-study/02_curriculum_B_decisions.html) | ROS 시스템 완주형을 채택하기 위한 세부 선택 기록 |

## 저장소 구조

```text
.
├── README.md                         # 저장소 안내
├── .gitignore                        # ROS·빌드·로컬 산출물 제외 규칙
├── curriculum.md                     # 실행 커리큘럼 원본
├── progress.md                       # 진행 상황·회차 로그 원본
├── guides/                           # 날짜별 따라 하기용 실행 가이드
│   ├── README.md                     # 새 가이드 추가·관리 규칙
│   ├── index.html                    # GitHub Pages 가이드 보관함
│   ├── guides.json                   # 가이드 목록의 단일 원본
│   ├── assets/                       # 가이드에서 내려받는 예제 코드·모델
│   ├── 2026-07-28-session-0-1-docker-setup.html
│   ├── 2026-07-29-session-0-2-gazebo-moveit-smoke-test.html
│   └── 2026-07-31-session-0-3-week0-spikes.html
├── docs/
│   ├── README.md                     # 전문 산출물 경로표
│   ├── setup/
│   │   ├── docker.md                 # S0-1 최초 작성 · S0-2 smoke test 갱신
│   │   └── week0_spike.md            # S0-3에서 최초 작성
│   ├── system_architecture.md        # S1 최초 작성 · S2~S3·S10 갱신 · S12 최종화
│   ├── frames.md                     # S3 최초 작성 · S5·S7·S9 갱신 · S12 최종화
│   ├── world_layout.md               # S5 최초 작성 · S9 갱신
│   └── rgbd_topics.md                # S7에서 최초 작성
├── index.html                        # GitHub Pages 커리큘럼 뷰어
├── assets/                           # 웹 뷰어의 로컬 의존성
├── 01_study_direction_options.html   # 의사결정 아카이브 1
├── 02_curriculum_B_decisions.html    # 의사결정 아카이브 2
└── THIRD_PARTY_NOTICES.md             # 웹 의존성 라이선스 안내
```

아직 진행하지 않은 회차의 `docs/` 파일은 존재하지 않을 수 있습니다. 빈 placeholder는 만들지 않고 [문서 산출물 경로](./docs/README.md)에 정한 회차에서 생성합니다.

## 운영 원칙

- 구현·평가 기준은 항상 `curriculum.md`의 최신 버전을 따릅니다.
- 한 회차는 실행 가능한 증빙과 `progress.md` 로그가 있어야 종료됩니다.
- `docs/` 전문 산출물은 [경로표](./docs/README.md)에 적힌 파일만 해당 회차에서 생성합니다.
- 기능 수보다 end-to-end 완주와 반복 재현성을 우선합니다.
- 축소 경로를 택했다면 이유와 영향을 함께 기록합니다.
- 비밀키, 개인 토큰, 대용량 bag·영상 원본은 저장소에 직접 commit하지 않습니다.
