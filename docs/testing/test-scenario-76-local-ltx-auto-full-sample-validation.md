# 테스트 시나리오 76 - local LTX auto full sample validation

## 1. 테스트 정보

- 일자: `2026-04-09`
- 진행자: Codex
- 시나리오 ID: `TS-76`

## 2. 테스트 목적

- `prepare_mode auto`를 batch path에서 기본값처럼 사용했을 때 전체 샘플 라이브러리 11장에서도 shot type 분기와 실행 안정성이 유지되는지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_auto_full_sample_validation.py --offline`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-73-local-ltx-auto-full-sample-validation/summary.json`

## 5. 관찰 내용

1. 전체 11장이 모두 정상 완료됐습니다.
2. 분기 결과는 `cover_center 2`, `contain_blur 7`, `cover_top 2`였습니다.
3. `커피`, `맥주`는 모두 `glass_drink_candidate -> cover_top`으로 분기됐습니다.

## 6. 실패/제약

1. `타코야키`, `맥주`는 metric이 높아 수치 해석에 주의가 필요합니다.
2. `카오위`는 generic prompt에 가까운 라벨을 사용했습니다.

## 7. 개선 포인트

1. 다음은 batch runner 기본값을 `auto`로 승격하는 것입니다.
2. 이후에는 샘플별 품질 병목을 `shot type` 후속 레버로 따로 봐야 합니다.
