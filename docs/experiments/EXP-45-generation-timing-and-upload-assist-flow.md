# EXP-45 Generation Timing and Upload Assist Flow

## 1. 기본 정보

- 실험 ID: `EXP-45`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `서비스 본선 KPI / 업로드 보조 흐름`

## 2. 왜 이 작업을 했는가

- 기획 기준선은 생성만 되는 서비스가 아니라, `첫 결과물 생성 시간 3분 이내`와 `업로드 또는 업로드 보조 완료 가능`을 요구합니다.
- 따라서 지금 시점에서 실제 데모 경로 기준으로
  - 첫 결과 생성 시간
  - 업로드 보조 진입
  - 업로드 보조 완료
  가 끝까지 이어지는지 확인해야 했습니다.

## 3. baseline

### 고정한 조건

1. 경로: `web demo local server`
2. 업종/목적/스타일: `restaurant / promotion / b_grade_fun`
3. 템플릿: `T02`
4. 자산: `docs/sample/음식사진샘플(규카츠).jpg`, `docs/sample/음식사진샘플(맥주).jpg`
5. quick option: `highlightPrice=true`
6. 게시 채널: `youtube_shorts`
7. publish mode: `assist`

### 이번 점검에서 본 항목

1. 첫 결과 생성 시간
2. `assist_required` 진입 여부
3. assist package 완결성
4. `assist-complete` 후 최종 `published` 상태 전이

## 4. 무엇을 바꿨는가

- 재현용 스크립트 `scripts/check_generation_timing_and_upload_assist.mjs`를 추가했습니다.
- 스크립트는 아래를 한 번에 수행합니다.
  - 프로젝트 생성
  - 샘플 자산 업로드
  - generate 요청 후 polling
  - 첫 결과 생성 시간 측정
  - `youtube_shorts + assist` publish 요청
  - upload job 조회
  - assist complete 호출
  - 최종 상태 확인

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-45-generation-timing-and-upload-assist-flow/summary.json`

### baseline 대비 차이

- 첫 결과 생성 시간: `4872ms`
- KPI 기준: `180000ms(3분)` 이내 충족
- 게시 흐름
  - publish 응답: `assist_required`
  - upload job 조회: `assist_required`
  - assist complete 후 최종 상태: `published`
- assist package
  - mediaUrl 존재
  - caption 길이: `19`
  - hashtag 수: `4`
  - thumbnailText 존재

### 확인된 것

1. 현재 데모 경로 기준 첫 결과 생성 시간은 KPI(`3분 이내`)를 크게 만족합니다.
2. `youtube_shorts` 선택 시 업로드 보조 fallback이 정상적으로 진입합니다.
3. `assist-complete` 이후 프로젝트 상태가 `published`까지 정상 전이됩니다.

## 6. 실패/제약

1. 이번 검증은 실제 외부 SNS API가 아니라 local demo state machine 기준입니다.
2. 따라서 네트워크/권한/플랫폼 정책 리스크를 검증한 것은 아닙니다.
3. 자동 업로드 성공 경로(`instagram connected + auto`)는 이번 실험에 포함하지 않았습니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - 현재 데모 기준으로는 `첫 결과 생성 시간`과 `업로드 보조 완료` 두 KPI를 모두 만족합니다.
  - 즉 본선 루프는 `입력 -> 생성 -> 업로드 보조 -> 완료`까지 최소 시연 가능 상태입니다.

## 8. 다음 액션

1. 다음 본선 검증은 `instagram auto publish` 경로 또는 `업로드 실패 -> assist fallback` 경로를 추가로 보는 편이 맞습니다.
2. 이후에는 `history/result` 화면이 이 publish 상태 변화를 얼마나 명확히 보여주는지도 함께 점검해야 합니다.
