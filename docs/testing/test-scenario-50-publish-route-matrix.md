# 테스트 시나리오 50 - Publish Route Matrix

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-50`

## 2. 테스트 목적

- 데모 기준선에서 `instagram auto success`와 `auto 실패 -> assist fallback`이 모두 재현되는지 확인합니다.

## 3. 수행 항목

1. `node scripts/check_publish_route_matrix.mjs`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-47-publish-route-matrix/summary.json`

## 5. 관찰 내용

1. `instagram auto success`는 `queued -> published`로 정상 전이됐습니다.
2. `tiktok auto fallback`은 `assist_required`로 전환됐고, `assist-complete` 후 `assisted_completed`와 프로젝트 `published`까지 이어졌습니다.
3. demo-store의 상태 오염 문제도 수정 후 재검증했습니다.

## 6. 실패/제약

1. 외부 SNS API를 실제로 호출한 것은 아닙니다.
2. 이번 검증은 local demo publish state machine 기준입니다.

## 7. 개선 포인트

1. 다음에는 `instagram permission_error -> assist fallback`도 별도로 점검해야 합니다.
2. publish 경로 차이가 history/result UI에 얼마나 잘 드러나는지도 확인해야 합니다.
