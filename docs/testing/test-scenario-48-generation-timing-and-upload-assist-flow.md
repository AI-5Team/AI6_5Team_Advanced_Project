# 테스트 시나리오 48 - Generation Timing and Upload Assist Flow

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-48`

## 2. 테스트 목적

- 데모 기준선에서 `첫 결과 생성 시간`과 `업로드 보조 완료`가 실제로 끝까지 이어지는지 확인합니다.

## 3. 수행 항목

1. `node scripts/check_generation_timing_and_upload_assist.mjs`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-45-generation-timing-and-upload-assist-flow/summary.json`

## 5. 관찰 내용

1. 첫 결과 생성 시간은 `4872ms`였습니다.
2. `youtube_shorts + assist` publish 요청은 `assist_required`로 전환됐습니다.
3. assist package에는 `mediaUrl`, `caption`, `hashtags`, `thumbnailText`가 모두 포함됐습니다.
4. `assist-complete` 호출 후 프로젝트 최종 상태는 `published`였습니다.

## 6. 실패/제약

1. 외부 SNS API를 실제 호출한 것은 아닙니다.
2. 이번 테스트는 demo publish state machine 검증입니다.

## 7. 개선 포인트

1. 다음에는 `instagram auto publish` 또는 `auto 실패 -> assist fallback` 경로를 추가 검증해야 합니다.
2. publish 상태 변화가 UI에서 얼마나 잘 보이는지도 이어서 확인해야 합니다.
