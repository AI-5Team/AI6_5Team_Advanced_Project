# 테스트 시나리오 10 - 손그림 스타일 + 실제 음식 사진 검증

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-10`

## 2. 테스트 목적

- 사용자 제공 손그림 스타일 레퍼런스가 실제 음식 사진과 결합될 때 유효한지 확인합니다.
- `owner_made_real_photo`와 `hand_drawn_menu_board`를 실제 음식 사진 기준으로 비교합니다.

## 3. 사전 조건

- `docs/sample/손그림샘플.png` 존재
- `docs/sample/음식사진샘플(타코야키).jpg` 존재
- `docs/sample/음식사진샘플(맥주).jpg` 존재
- worker test 통과 상태

## 4. 수행 항목

1. 실제 사진과 손그림 레퍼런스 확인
2. `uv run --project services/worker python scripts/run_video_experiment.py --experiment-id EXP-05`
3. baseline/variant 첫 씬 비교
4. `npm run check`

## 5. 결과

- `EXP-05` artifact 생성: 통과
- 전체 check: 통과
- 결과 경로:
  - `docs/experiments/artifacts/exp-05-hand-drawn-reference-with-real-food-photos/summary.json`
  - `.../owner_made_real_photo/scenes/s1.png`
  - `.../hand_drawn_menu_board/scenes/s1.png`

## 6. 관찰 내용

- 손그림 스타일은 실제 음식 사진과도 충분히 어울렸습니다.
- 다만 숏폼 첫 장면 기준으로는 `owner_made_real_photo`가 상품 전달력이 더 좋았습니다.
- `hand_drawn_menu_board`는 피드/포스터/메뉴판용 정적 비주얼에는 특히 잘 맞아 보였습니다.

## 7. 실패/제약

1. 손그림 variant는 숏폼 첫 컷에서 텍스트/장식 비중이 다소 높습니다.
2. 아직 motion 실험은 붙이지 않았습니다.

## 8. 개선 포인트

1. 숏폼용은 `owner_made_real_photo` 기준으로 motion 실험을 이어갑니다.
2. 손그림 스타일은 정적 포스터/게시글용 분기 실험으로 분리하는 것이 적절합니다.
