# 테스트 시나리오 77 - local LTX takoyaki steam phrase OVAT

## 1. 테스트 정보

- 일자: `2026-04-09`
- 진행자: Codex
- 시나리오 ID: `TS-77`

## 2. 테스트 목적

- `타코야키` tray/full-plate 샘플에서 `strong steam cloud`가 품질 저하 원인인지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_takoyaki_steam_phrase_ovaat.py --offline`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-74-local-ltx-takoyaki-steam-phrase-ovaat/summary.json`

## 5. 관찰 내용

1. `strong steam cloud`를 제거한 variant가 더 좋았습니다.
2. metric뿐 아니라 mid frame 시각 결과에서도 tray와 음식 경계가 더 안정적이었습니다.

## 6. 실패/제약

1. `타코야키` 1장 기준입니다.

## 7. 개선 포인트

1. tray/full-plate 안에서도 `steam on/off`를 subtype별로 분리할 필요가 있습니다.
