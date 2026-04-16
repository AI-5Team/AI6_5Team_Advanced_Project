# 테스트 시나리오 85 - local LTX beer label negative prompt OVAT

## 1. 테스트 정보

- 일자: `2026-04-09`
- 진행자: Codex
- 시나리오 ID: `TS-85`

## 2. 테스트 목적

- `맥주` baseline에서 `text, watermark` 제거가 label 보존에 도움이 되는지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_beer_label_negative_prompt_ovaat.py --offline`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-82-local-ltx-beer-label-negative-prompt-ovaat/summary.json`

## 5. 관찰 내용

1. `text, watermark` 제거 variant는 오히려 `mid-frame MSE`가 나빠졌습니다.
2. 따라서 negative prompt 완화는 현재 label 보존 해결책이 아닙니다.

## 6. 실패/제약

1. `맥주` 1장 기준입니다.

## 7. 개선 포인트

1. label 보존은 negative prompt보다 framing/crop 쪽 후속 레버를 보는 편이 맞습니다.
