# 일일 실행 가이드

매 회차에 바로 따라 할 수 있는 HTML 가이드를 모으는 폴더입니다. 표와 파일명의 날짜는 **스터디 수행일이 아니라 가이드 제작일**입니다. 가이드 목록의 단일 원본은 [`guides.json`](./guides.json)이며, GitHub Pages의 [`guides/`](https://gist-isaac-robotics.github.io/2026-pnp-study/guides/) 화면이 이 파일을 읽어 최신순으로 표시합니다.

현재 항목은 [웹 보관함](https://gist-isaac-robotics.github.io/2026-pnp-study/guides/) 또는 [`guides.json`](./guides.json)에서 확인합니다. 이 문서에는 목록을 다시 복제하지 않습니다.

## 새 가이드 추가 방법

본문 구조, 초보자 설명, terminal 역할, 코드 접기, 검증 수준, 웹 디자인의 공통 규칙은 [`AUTHORING.md`](./AUTHORING.md)를 먼저 따릅니다. 원본 디자인 참고 파일은 [`design/crimson2.md`](./design/crimson2.md)에 보존합니다.

1. 이 폴더에 제작일 기준 `YYYY-MM-DD-session-X-Y-주제.html` 형식으로 HTML 파일을 추가합니다.
2. [`guides.json`](./guides.json)의 `guides` 배열 맨 앞에 제작일, 회차, 제목, 설명, 상대 경로, 태그를 추가합니다.
3. 목록의 항목이나 설명을 바꾼 날짜로 `updated`를 갱신합니다. 각 가이드의 `date`는 제작일을 그대로 유지합니다.
4. 로컬에서 HTML 링크와 JavaScript 문법을 확인한 뒤 commit합니다.

`index.html`이나 저장소 루트의 `README.md`에는 매일 항목을 복제하지 않습니다. 두 곳은 전체 가이드 보관함을 가리키고, 실제 목록은 `guides.json`에서 계속 늘어납니다. 메인 화면의 “최신 가이드” 카드만 바꾸고 싶다면 루트의 `index.html`에서 해당 카드 한 개를 갱신합니다.

## `guides.json` 항목 예시

```json
{
  "date": "YYYY-MM-DD",
  "session": "Session X-Y",
  "title": "가이드 제목",
  "description": "이 회차에서 수행하고 검증할 내용을 한 문장으로 적습니다.",
  "path": "./YYYY-MM-DD-session-X-Y-topic.html",
  "tags": ["Week 0", "태그"]
}
```
