# 테스트 시나리오 11 - 서비스 기준선 정렬 B급 프로모션 첫 씬 검증

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-11`

## 2. 테스트 목적

- 서비스 핵심 루프 기준으로 `promotion` 템플릿의 첫 씬을 혜택 우선으로 열지, 메뉴 우선으로 열지 검증합니다.
- 같은 자산, 같은 레이아웃에서 `opening_scene_priority`만 바뀌는지 확인합니다.

## 3. 사전 조건

- `docs/sample/음식사진샘플(규카츠).jpg` 존재
- `docs/sample/음식사진샘플(맥주).jpg` 존재
- worker test 통과 상태

## 4. 수행 항목

1. `npm run worker:test`
2. `uv run --project services/worker python scripts/run_video_experiment.py --experiment-id EXP-06`
3. baseline/variant 첫 씬 이미지 비교
4. `npm run check`

## 5. 결과

- `EXP-06` artifact 생성: 통과
- worker test: 통과
- 전체 check: 통과
- 결과 경로:
  - `docs/experiments/artifacts/exp-06-service-aligned-b-grade-promotion-opening-priority/summary.json`
  - `.../owner_made_benefit_first/scenes/s1.png`
  - `.../owner_made_menu_first/scenes/s1.png`

## 6. 관찰 내용

- `benefit_first`는 프로모션 목적이 첫 장면에서 더 빨리 읽혔습니다.
- `menu_first`는 규카츠 인지는 더 빠르지만 할인/행사 메시지가 뒤로 밀렸습니다.
- 서비스 문서 기준으로는 `promotion` 목적에 `benefit_first`가 더 잘 맞았습니다.

## 7. 실패/제약

1. `owner_made_safe` 오버레이는 긴 첫 씬 텍스트에서 우측 overflow가 발생했습니다.
2. overflow를 피하기 위해 첫 씬 문구를 짧게 다시 조정한 뒤 최종 artifact를 생성했습니다.

## 8. 개선 포인트

1. 다음은 같은 baseline에서 `subtitle_density`를 한 변수로 비교합니다.
2. 오버레이 우측 텍스트 overflow는 별도 레이아웃 개선 항목으로 분리합니다.
