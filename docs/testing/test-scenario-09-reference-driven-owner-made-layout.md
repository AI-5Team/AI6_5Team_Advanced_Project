# 테스트 시나리오 09 - 사용자 레퍼런스 기반 Owner-made Safe-zone 검증

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-09`

## 2. 테스트 목적

- `docs/sample/b급sample.png` 레퍼런스를 참고한 variant가 실제로 상품 가시성을 더 살리는지 확인합니다.
- synthetic 중심 접근보다 reference-driven 접근이 더 유효한지 검증합니다.

## 3. 사전 조건

- `docs/sample/b급sample.png` 존재
- `EXP-04` 코드 적용 완료
- worker test 통과

## 4. 수행 항목

1. 레퍼런스 이미지 확인
2. `uv run --project services/worker python scripts/run_video_experiment.py --experiment-id EXP-04`
3. `flyer_poster` vs `owner_made_safe_zone` 첫 씬 비교
4. `npm run check`

## 5. 결과

- `EXP-04` artifact 생성: 통과
- 전체 check: 통과
- 결과 경로:
  - `docs/experiments/artifacts/exp-04-owner-made-safe-zone-layout-experiment/summary.json`
  - `.../bgrade_flyer_overlay/scenes/s1.png`
  - `.../owner_made_safe_zone/scenes/s1.png`

## 6. 관찰 내용

- `owner_made_safe_zone`은 `Style A` 레퍼런스와 더 가까웠습니다.
- 상품이 가려지는 정도가 줄었고, 가격 강조도 더 자연스러웠습니다.
- `flyer_poster`는 여전히 자극성은 더 강했지만 실제 광고 쓰임새는 떨어질 수 있습니다.

## 7. 실패/제약

1. 레퍼런스 보드는 스타일 모음이므로 scene-to-scene 일관성은 따로 봐야 합니다.
2. 현재는 still scene 위주 비교라 motion 품질은 아직 미검증입니다.

## 8. 개선 포인트

1. `owner_made_safe_zone` 기반으로 motion만 한 변수 붙여 보는 것이 다음 단계로 적절합니다.
2. 실제 업주 촬영 사진을 기준 자산으로 바꾸면 판단 정확도가 더 올라갑니다.
