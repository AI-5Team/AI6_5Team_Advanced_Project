# 테스트 시나리오 12 - 시각 baseline 재구축 검증

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-12`

## 2. 테스트 목적

- OVAT 재개 전에 새 baseline renderer가 기존 baseline보다 덜 깨지는지 확인합니다.
- 특히 텍스트 clipping, 텍스트/강조요소 겹침, CTA 식별성을 비교합니다.

## 3. 사전 조건

- `docs/sample/음식사진샘플(규카츠).jpg` 존재
- `docs/sample/음식사진샘플(맥주).jpg` 존재
- worker test 통과 상태

## 4. 수행 항목

1. `npm run worker:test`
2. `uv run --project services/worker python scripts/run_video_experiment.py --experiment-id EXP-07`
3. legacy baseline 첫 씬과 rebuilt baseline 첫 씬 비교
4. rebuilt baseline CTA 씬 확인
5. `npm run check`

## 5. 결과

- `EXP-07` artifact 생성: 통과
- worker test: 통과
- 전체 check: 통과
- 결과 경로:
  - `docs/experiments/artifacts/exp-07-visual-baseline-rebuild-before-ovat/summary.json`
  - `.../legacy_owner_made_safe/scenes/s1.png`
  - `.../structured_bgrade_v2/scenes/s1.png`
  - `.../structured_bgrade_v2/scenes/s4.png`

## 6. 관찰 내용

- `structured_bgrade_v2`는 legacy baseline보다 텍스트 clipping과 겹침이 확실히 줄었습니다.
- 사진 영역과 텍스트 영역이 분리되어 상품 전달력이 더 안정적이었습니다.
- CTA도 footer strip 구조로 바뀌면서 마지막 장면 인지가 더 쉬워졌습니다.

## 7. 실패/제약

1. 우측 note 문구와 CTA headline line break는 아직 완성형은 아닙니다.
2. 현재 검증은 대표 시나리오 1세트 기준이라 다건 사진 검증이 추가로 필요합니다.

## 8. 개선 포인트

1. `structured_bgrade_v2`를 기준선 후보로 유지합니다.
2. line-break polish와 다건 사진 검증을 먼저 진행합니다.
3. 그 후 `subtitle_density` 같은 OVAT 실험을 재개합니다.
