# 테스트 시나리오 88 - local LTX drink prepare mode policy split

## 1. 테스트 정보

- 일자: `2026-04-09`
- 진행자: Codex
- 시나리오 ID: `TS-88`

## 2. 테스트 목적

- 현재 drink lane prepare-mode policy가 old policy보다 aggregate 기준으로 더 나은지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_drink_prepare_mode_policy_split.py --offline`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-85-local-ltx-drink-prepare-mode-policy-split/summary.json`

## 5. 관찰 내용

1. `커피/맥주` 묶음 기준으로 new policy가 더 좋았습니다.
2. 개선은 `맥주 cover_top -> cover_bottom`에서만 발생했고, `커피`는 그대로 유지됐습니다.

## 6. 실패/제약

1. drink 샘플은 여전히 2장뿐입니다.

## 7. 개선 포인트

1. 현재 drink prepare-mode policy는 baseline으로 승격해도 됩니다.
