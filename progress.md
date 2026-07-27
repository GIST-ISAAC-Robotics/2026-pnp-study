# 진행 상황과 실행 로그

> **현재 단계:** 준비 — Week 0 시작 전
>
> **다음 Gate:** Week 0 Gate
>
> **마지막 업데이트:** 2026-07-28

이 문서는 스터디 진행 상황의 단일 기록 원본이다. 회차 종료 시 최신 항목을 위에 추가하고, 성공뿐 아니라 실패·축소·보류 판정도 증빙과 함께 남긴다.

## 단계별 현황

| 단계 | 상태 | 현재 결과 / 진입 조건 |
|---|---|---|
| 커리큘럼·저장소 준비 | **완료** | `curriculum.md` v3.5.4 문서 계약 확정, README·Pages·문서 경로·ignore 규칙 정리; 구현은 아직 시작 전 |
| Week 0 — 환경·위험 제거 | 대기 | Docker, 공식 smoke test, RGB-D·pose follower·reset·IK spike |
| Week 1 — ROS 2 시스템 뼈대 | 대기 | Week 0 Gate 통과 후 시작 |
| Week 2 — MoveIt 조작 | 대기 | Week 1 Gate 통과 후 시작 |
| Week 3 — RGB-D 인식 통합 | 대기 | Week 2 Gate 통과 후 시작 |
| Week 4 — 신뢰성·평가·정리 | 대기 | Week 3 Gate 통과 후 시작 |
| 최종 시연·회고 | 대기 | 반복 평가와 문서·영상 완료 |

상태 표기는 `대기`, `진행 중`, `완료`, `보류`, `차단` 중 하나를 사용한다.

## 다음 작업

- [ ] Session 0-1: ROBOTIS Docker 환경 구축
- [ ] Session 0-2: 공식 Gazebo·MoveIt smoke test
- [ ] Session 0-3: RGB-D, pose 추종/reset, pose goal·IK mode spike
- [ ] `docs/setup/docker.md`에 S0-1 환경 기록; S0-2 종료 시 공식 smoke test 결과 추가
- [ ] `docs/setup/week0_spike.md`에 동결값과 Gate 판정 기록

세부 명령·완료 기준·실패 시 전환은 [curriculum.md의 Week 0](./curriculum.md#6-week-0--환경-구축과-위험-제거)을 따른다.

## 회차 로그

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
