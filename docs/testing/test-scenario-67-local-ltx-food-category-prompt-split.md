# 테스트 시나리오 67 - local LTX food-category prompt split

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-67`

## 2. 테스트 목적

- generic baseline prompt보다 음식군별 tailored prompt가 실제로 더 나은지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_food_category_prompt_split.py --offline`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-64-local-ltx-food-category-prompt-split/summary.json`

## 5. 관찰 내용

1. 규카츠와 커피는 tailored prompt가 더 좋았습니다.
2. 라멘과 장어덮밥은 tailored prompt가 크게 나빠졌습니다.
3. aggregate 기준으로는 tailored prompt가 전반 개선을 만들지 못했습니다.

## 6. 실패/제약

1. tailored prompt가 수작업 초안이라 설계 편향이 있습니다.
2. seed `7` 고정 조건입니다.

## 7. 개선 포인트

1. 음식군보다 `촬영 구도` 기반 분기가 더 적절한지 확인할 필요가 있습니다.
2. 다음 실험은 `overhead bowl / tray set / glass drink / dessert close-up` 같은 시각 타입 분기가 더 맞습니다.
