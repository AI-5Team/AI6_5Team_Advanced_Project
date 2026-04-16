# EXP-59 Result to publish package consistency

## 1. 기본 정보

- 실험 ID: `EXP-59`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `서비스 본선 generation result -> publish package 일관성`

## 2. 왜 이 작업을 했는가

- history/result 가시성 쪽은 많이 정리됐습니다.
- 이제 본선 기준으로 더 중요한 것은 `generate -> regenerate -> publish assist`를 지나면서 최신 결과가 package에 정확히 이어지는지입니다.

## 3. baseline

### 고정한 조건

1. 경로: `web demo local server`
2. 업종/목적/스타일: `restaurant / promotion / b_grade_fun`
3. 템플릿: `T02`
4. 자산: `docs/sample/음식사진샘플(규카츠).jpg`, `docs/sample/음식사진샘플(맥주).jpg`
5. 게시 채널: `youtube_shorts`
6. 게시 모드: `assist`

### 검증 순서

1. baseline generate
2. `shorterCopy` regenerate
3. latest result fetch
4. publish assist
5. assist complete

## 4. 무엇을 바꿨는가

- 검증용 스크립트 `scripts/check_result_to_publish_package_consistency.mjs`를 추가했습니다.
- 이번 실험에서는 production 코드 변경 없이, 최신 result와 publish assist package가 일치하는지만 확인했습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-59-result-to-publish-package-consistency/summary.json`

### baseline 대비 차이

- regenerate
  - baseline variant: `1c56b673-...`
  - regenerated variant: `d96c446a-...`
  - hookText: 실제로 짧아짐
- publish assist package
  - mediaUrl: regenerated result의 `video.url`과 일치
  - caption: regenerated result의 `captions[0]`과 일치
  - hashtags: regenerated result의 `hashtags`와 일치

### 확인된 것

1. regenerate 후 publish를 해도 assist package는 최신 result를 사용합니다.
2. `generate -> regenerate -> publish assist -> assist complete` 흐름이 현재 데모 기준으로 일관됩니다.
3. publish/package 쪽은 현재 서비스 본선 기준에서 큰 불일치는 보이지 않았습니다.

## 6. 실패/제약

1. 이번 검증은 local demo state machine 기준입니다.
2. 외부 SNS provider와의 실제 업로드 결과까지 확인한 것은 아닙니다.
3. `variantId`를 의도적으로 오래된 값으로 넣는 mismatch 시나리오는 아직 보지 않았습니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - 현재 본선 흐름에서는 latest result와 publish assist package 연결이 잘 유지됩니다.
  - 따라서 당장 본선의 큰 병목은 package consistency보다 생성 품질 쪽입니다.

## 8. 다음 액션

1. 오래된 `variantId`를 의도적으로 넘겼을 때도 안전한지 나중에 따로 확인합니다.
2. 본선은 publish/package보다 생성 품질 연구와 연결성을 더 우선해도 됩니다.
