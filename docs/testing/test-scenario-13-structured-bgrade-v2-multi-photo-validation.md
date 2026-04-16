# 테스트 시나리오 13 - structured_bgrade_v2 다건 사진 검증

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-13`

## 2. 테스트 목적

- `structured_bgrade_v2`가 실제 음식 사진 여러 장에서도 안정적으로 유지되는지 확인합니다.
- 한국어 단어 단위 줄바꿈이 이전보다 자연스러운지 함께 봅니다.

## 3. 사전 조건

- `docs/sample/음식사진샘플(규카츠).jpg`
- `docs/sample/음식사진샘플(라멘).jpg`
- `docs/sample/음식사진샘플(순두부짬뽕).jpg`
- `docs/sample/음식사진샘플(장어덮밥).jpg`
- `docs/sample/음식사진샘플(타코야키).jpg`
- worker test 통과 상태

## 4. 수행 항목

1. `npm run worker:test`
2. `uv run --project services/worker python scripts/run_video_experiment.py --experiment-id EXP-08`
3. 대표 scene 이미지 4장 확인
4. `npm run check`

## 5. 결과

- `EXP-08` artifact 생성: 통과
- worker test: 통과
- 전체 check: 통과
- 결과 경로:
  - `docs/experiments/artifacts/exp-08-structured-b-grade-v2-multi-photo-validation/summary.json`
  - `.../scenes/s1.png`
  - `.../scenes/s2.png`
  - `.../scenes/s3.png`
  - `.../scenes/s4.png`

## 6. 관찰 내용

- 다건 사진에서도 photo zone / side panel / footer CTA 구조가 안정적으로 유지됐습니다.
- `저장` 같은 단어가 이전보다 자연스럽게 줄바꿈됐습니다.
- 음식 종류가 달라도 side panel 텍스트와 상품 영역이 덜 충돌했습니다.

## 7. 실패/제약

1. 아주 긴 B급 헤드라인이 들어오면 추가 polish가 더 필요합니다.
2. 현재는 시각 확인 위주라 자동 overflow 검출은 아직 없습니다.

## 8. 개선 포인트

1. 다음은 quick action이 시각적으로 얼마나 잘 드러나는지 검증합니다.
2. production renderer 이식 전 최소 1회 더 다건 validation을 반복하는 것이 좋습니다.
