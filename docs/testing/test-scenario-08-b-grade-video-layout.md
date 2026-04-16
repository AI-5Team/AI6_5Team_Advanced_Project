# 테스트 시나리오 08 - B급 영상 레이아웃 실험

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-08`

## 2. 테스트 목적

- production renderer와 분리된 실험 경로에서 `overlay_layout` 한 레버만 바꿔 B급 영상 인상 차이를 확인합니다.
- `b_grade_fun` 영상 baseline의 실제 병목이 카피가 아니라 화면 구성인지 검증합니다.

## 3. 사전 조건

- 샘플 자산 존재
- `ffmpeg` 실행 가능
- worker 테스트 통과 상태

## 4. 수행 항목

1. `npm run worker:test`
2. `uv run --project services/worker python scripts/run_video_experiment.py --experiment-id EXP-03`
3. baseline/variant 첫 씬 이미지 확인
4. `npm run check`

## 5. 결과

- worker test: 통과
- `EXP-03` 영상 artifact 생성: 통과
- 전체 check: 통과
- 결과 경로:
  - `docs/experiments/artifacts/exp-03-b-grade-video-layout-experiment/summary.json`
  - `.../baseline_card_overlay/scenes/s1.png`
  - `.../bgrade_flyer_overlay/scenes/s1.png`

## 6. 관찰 내용

- baseline card panel은 읽기 쉽지만 B급 인상은 약했습니다.
- flyer poster variant는 형광 전단지 느낌이 강해졌고, 첫 인상에서 확실히 더 과장됐습니다.
- 대신 헤드라인이 커서 상품 영역을 덮는 문제가 보였습니다.
- 실험 도중 bold 한글 폰트 fallback 순서가 잘못돼 자막이 깨질 수 있는 baseline 버그를 발견했고 수정했습니다.

## 7. 실패/제약

1. 이번 검증은 motion이 아니라 정적 scene layout 비교입니다.
2. heuristic score는 참고용이며 사람 시각 평가가 여전히 필요합니다.
3. 상품 가시성 문제는 다음 실험에서 따로 봐야 합니다.

## 8. 개선 포인트

1. 다음 실험은 헤드라인 점유율을 줄여 상품 가시성을 보호하는 방향으로 갑니다.
2. 이후 `shake_pop`, `flash_text`, `quick_zoom` 계열 motion 강도를 레버로 분리합니다.
