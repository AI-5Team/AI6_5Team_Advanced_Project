# 테스트 시나리오 79 - local LTX gyukatsu steam phrase OVAT

## 1. 테스트 정보

- 일자: `2026-04-09`
- 진행자: Codex
- 시나리오 ID: `TS-79`

## 2. 테스트 목적

- `규카츠` tray/full-plate 샘플에서도 `strong steam cloud`가 실제로 필요한지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_gyukatsu_steam_phrase_ovaat.py --offline`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-76-local-ltx-gyukatsu-steam-phrase-ovaat/summary.json`

## 5. 관찰 내용

1. `strong steam cloud`를 제거한 variant가 소폭 더 좋았습니다.
2. `타코야키`만큼 큰 차이는 아니지만, no-steam 쪽이 baseline보다 나빠지지 않았습니다.

## 6. 실패/제약

1. 개선 폭이 작아서 `규카츠` 단독으로 subtype split을 결론내리긴 어렵습니다.

## 7. 개선 포인트

1. 다음은 `규카츠 + 타코야키`를 묶은 `tray steam default on/off` 비교가 맞습니다.
