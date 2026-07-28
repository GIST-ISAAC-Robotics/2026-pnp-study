# 일일 실행 가이드

매 회차에 바로 따라 할 수 있는 HTML 가이드를 모으는 폴더입니다. 가이드 목록의 단일 원본은 [`guides.json`](./guides.json)이며, GitHub Pages의 [`guides/`](https://gist-isaac-robotics.github.io/2026-pnp-study/guides/) 화면이 이 파일을 읽어 최신순으로 표시합니다.

## 현재 가이드

| 날짜 | 회차 | 가이드 |
|---|---|---|
| 2026-07-29 | Session 0-1 | [ROBOTIS Docker 환경 구축](https://gist-isaac-robotics.github.io/2026-pnp-study/guides/2026-07-29-session-0-1-docker-setup.html) |

## 새 가이드 추가 방법

1. 이 폴더에 `YYYY-MM-DD-session-X-Y-주제.html` 형식으로 HTML 파일을 추가합니다.
2. [`guides.json`](./guides.json)의 `guides` 배열 맨 앞에 날짜, 회차, 제목, 설명, 상대 경로, 태그를 추가합니다.
3. `updated`를 새 가이드 날짜로 갱신합니다.
4. 로컬에서 HTML 링크와 JavaScript 문법을 확인한 뒤 commit합니다.

`index.html`이나 저장소 루트의 `README.md`에는 매일 항목을 복제하지 않습니다. 두 곳은 전체 가이드 보관함을 가리키고, 실제 목록은 `guides.json`에서 계속 늘어납니다. 메인 화면의 “최신 가이드” 카드만 바꾸고 싶다면 루트의 `index.html`에서 해당 카드 한 개를 갱신합니다.

## `guides.json` 항목 예시

```json
{
  "date": "2026-07-30",
  "session": "Session 0-2",
  "title": "가이드 제목",
  "description": "이 회차에서 수행하고 검증할 내용을 한 문장으로 적습니다.",
  "path": "./2026-07-30-session-0-2-topic.html",
  "tags": ["Week 0", "태그"]
}
```
