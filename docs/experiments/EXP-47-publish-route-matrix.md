# EXP-47 Publish Route Matrix

## 1. 기본 정보

- 실험 ID: `EXP-47`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `서비스 본선 게시 경로 검증`

## 2. 왜 이 작업을 했는가

- 기획 기준선은 `instagram` 자동 업로드 1채널과 나머지 채널의 `업로드 보조 fallback`이 모두 살아 있어야 합니다.
- 따라서 이번에는 데모 기준선에서
  - `instagram auto success`
  - `auto 실패 -> assist fallback`
  두 경로를 실제로 끝까지 재현했습니다.

## 3. baseline

### 고정한 조건

1. 경로: `web demo local server`
2. 업종/목적/스타일: `restaurant / promotion / b_grade_fun`
3. 템플릿: `T02`
4. 자산: `docs/sample/음식사진샘플(규카츠).jpg`, `docs/sample/음식사진샘플(맥주).jpg`
5. publish mode: `auto`

### 이번 점검 시나리오

1. `instagram_auto_success`
2. `tiktok_auto_fallback`

## 4. 무엇을 바꿨는가

- 재현용 스크립트 `scripts/check_publish_route_matrix.mjs`를 추가했습니다.
- 시나리오는 두 개입니다.
  - `instagram + auto`
  - `tiktok + auto`
- 실험 중 발견된 demo-store 경로 오염도 함께 수정했습니다.
  - [`demo-store.ts`](E:\Codeit\AI6_5Team_Advanced_Project\apps\web\src\lib\demo-store.ts)
  - `assist complete` 후 `errorCode`를 비움
  - `instagram auto success`에서는 `assistPackage`를 노출하지 않음

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-47-publish-route-matrix/summary.json`

### 시나리오 1: instagram auto success

- publish 응답: `queued`
- upload job 최종 상태: `published`
- 프로젝트 최종 상태: `published`
- error code: `null`

### 시나리오 2: tiktok auto fallback

- publish 응답: `assist_required`
- initial error code: `SOCIAL_TOKEN_EXPIRED`
- assist complete 후 upload job 상태: `assisted_completed`
- assist complete 후 error code: `null`
- 프로젝트 최종 상태: `published`

### 확인된 것

1. `instagram auto success` 경로는 현재 데모 기준선에서 정상 동작합니다.
2. `tiktok auto fallback`도 `assist_required -> assisted_completed -> published`까지 정상 전이됩니다.
3. 이번 과정에서 demo-store가 runtime과 다르게 상태를 남기던 문제를 같이 정리했습니다.

## 6. 실패/제약

1. 이번 검증은 외부 SNS API가 아니라 demo publish state machine 기준입니다.
2. `tiktok` fallback은 실제 플랫폼 업로드를 시도한 것이 아니라, 채널 정책/토큰 상태를 시뮬레이션한 것입니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - 현재 서비스 본선은 `instagram auto publish`와 `fallback assist`를 모두 시연 가능한 수준입니다.
  - 다만 이 판단은 데모 state machine 기준이며, 외부 provider 실환경 검증은 별도 과제입니다.

## 8. 다음 액션

1. 다음 본선 검증은 `instagram permission_error -> assist fallback`처럼 같은 채널 내 실패 전환을 보는 편이 맞습니다.
2. 이후에는 history/result UI가 이 publish 경로 차이를 얼마나 잘 보여주는지도 함께 점검해야 합니다.
