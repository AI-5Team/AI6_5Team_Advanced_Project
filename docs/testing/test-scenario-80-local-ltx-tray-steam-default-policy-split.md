# 테스트 시나리오 80 - local LTX tray steam default policy split

## 1. 테스트 정보

- 일자: `2026-04-09`
- 진행자: Codex
- 시나리오 ID: `TS-80`

## 2. 테스트 목적

- `tray/full-plate` baseline prompt의 `steam default`를 `on`에서 `off`로 바꿔도 되는지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_tray_steam_default_policy_split.py --offline`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-77-local-ltx-tray-steam-default-policy-split/summary.json`

## 5. 관찰 내용

1. `규카츠`, `타코야키` 모두에서 `steam off`가 더 좋았습니다.
2. aggregate 기준 `avg mid-frame MSE`가 `753.46 -> 312.40`으로 내려갔습니다.
3. 즉 현재 tray/full-plate baseline에서는 `steam on`보다 `steam off`를 기본값으로 두는 편이 맞습니다.

## 6. 실패/제약

1. tray 샘플 수는 아직 2장뿐입니다.

## 7. 개선 포인트

1. tray lane은 일단 `cover_center + no steam`으로 유지하고, 다음은 drink lane 후속 레버를 보는 편이 맞습니다.
