# 테스트 시나리오 74 - local LTX prepare_mode classifier refinement

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-74`

## 2. 테스트 목적

- `EXP-70`의 drink 일반화 결과를 반영한 classifier v2가 v1보다 실제 known baseline에 더 잘 맞는지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_prepare_mode_classifier_refinement.py`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-71-local-ltx-prepare-mode-classifier-refinement/summary.json`

## 5. 관찰 내용

1. 바뀐 샘플은 `맥주` 1장뿐이었습니다.
2. known baseline 정확도는 `v1 0.8571 -> v2 1.0`으로 올라갔습니다.

## 6. 실패/제약

1. 여전히 heuristic classifier라 더 많은 drink 샘플이 필요합니다.

## 7. 개선 포인트

1. 다음은 이 classifier v2를 실제 generation runner에 붙이는 작업입니다.
