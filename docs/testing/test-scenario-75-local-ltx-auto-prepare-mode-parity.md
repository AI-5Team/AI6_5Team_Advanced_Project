# 테스트 시나리오 75 - local LTX auto prepare_mode parity

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-75`

## 2. 테스트 목적

- 실제 generation runner에서 `--prepare-mode auto`가 현재 수동 baseline policy와 동일하게 동작하는지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_auto_prepare_mode_parity.py --offline`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-72-local-ltx-auto-prepare-mode-parity/summary.json`

## 5. 관찰 내용

1. 7장 모두에서 `auto`가 수동 policy와 같은 `resolved_prepare_mode`를 골랐습니다.
2. 따라서 runner 레벨에서 `auto`를 baseline 후보로 승격할 수 있습니다.

## 6. 실패/제약

1. 샘플 수가 아직 작아 classifier 일반화는 계속 확인해야 합니다.

## 7. 개선 포인트

1. 다음은 batch validation 경로에서 `auto`를 기본값으로 쓰는 것입니다.
