# 테스트 시나리오 72 - local LTX prepare_mode auto classifier

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-72`

## 2. 테스트 목적

- 이미지 구조 feature만으로 현재 known prepare_mode baseline을 자동 재현할 수 있는지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_prepare_mode_auto_classifier.py`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-69-local-ltx-prepare-mode-auto-classifier/summary.json`

## 5. 관찰 내용

1. known baseline 6장에 대해서는 auto classifier v1이 `100%` 일치했습니다.
2. 다만 `맥주`는 `contain_blur`로 예측돼 추가 생성 검증이 필요했습니다.

## 6. 실패/제약

1. classification-only라 실제 비디오 품질을 직접 검증하진 않았습니다.

## 7. 개선 포인트

1. 다음은 `맥주`를 포함한 drink subset 생성 비교입니다.
