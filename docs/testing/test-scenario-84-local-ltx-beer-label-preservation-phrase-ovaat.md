# 테스트 시나리오 84 - local LTX beer label preservation phrase OVAT

## 1. 테스트 정보

- 일자: `2026-04-09`
- 진행자: Codex
- 시나리오 ID: `TS-84`

## 2. 테스트 목적

- `맥주` baseline에서 label preservation phrase가 실제로 bottle label 보존을 개선하는지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_beer_label_preservation_phrase_ovaat.py --offline`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-81-local-ltx-beer-label-preservation-phrase-ovaat/summary.json`

## 5. 관찰 내용

1. `mid-frame MSE`는 좋아졌지만 `edge variance`는 내려갔습니다.
2. 시각적으로도 label이 확실히 더 잘 읽힌다고 보긴 어려웠습니다.

## 6. 실패/제약

1. `맥주` 1장 기준입니다.

## 7. 개선 포인트

1. 이 레버는 `보류 후보`로만 유지하고, baseline 반영은 하지 않는 편이 맞습니다.
