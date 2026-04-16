# 테스트 시나리오 62 - result to publish package consistency

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-62`

## 2. 테스트 목적

- regenerate 이후 publish assist package가 최신 generation result를 정확히 사용하고 있는지 확인합니다.

## 3. 수행 항목

1. `node scripts/check_result_to_publish_package_consistency.mjs`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-59-result-to-publish-package-consistency/summary.json`

## 5. 관찰 내용

1. regenerate로 variantId와 hookText가 실제로 바뀌었습니다.
2. 이후 publish assist package의 video/caption/hashtags가 regenerated result와 정확히 일치했습니다.
3. assist complete 이후 final project status도 `published`로 정상 전이됐습니다.

## 6. 실패/제약

1. local demo publish state machine 검증입니다.
2. 오래된 variantId mismatch 시나리오는 아직 보지 않았습니다.

## 7. 개선 포인트

1. 필요하면 stale variantId 안전성도 별도 시나리오로 봅니다.
2. 본선은 package consistency보다 생성 품질 쪽에 더 집중해도 됩니다.
