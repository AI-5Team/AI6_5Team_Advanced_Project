# EXP-251 Manual Review Hybrid Packaging Check

## 1. 기본 정보

- 실험 ID: `EXP-251`
- 작성일: `2026-04-14`
- 작성자: Codex
- 관련 기능: `manual_review 후보를 실제 hybrid packaging 결과 기준으로 재판정`

## 2. 왜 이 작업을 했는가

- `EXP-249` 시점의 `규카츠 / sora2_current_best` 후보는 contact sheet만 보고 예비 `hold`를 남긴 상태였습니다.
- 하지만 실제 서비스 기준은 `source clip` 자체보다 `최종 hybrid 광고 결과물`이 읽히는지가 더 중요합니다.
- 이번 작업의 목적은 manual-review 후보를 실제 hybrid packaging 결과까지 태워 본 뒤, `hold`를 유지할지 `promote`로 올릴지 결정하는 것입니다.

## 3. 실행

### 3.1 review-only hybrid spike

```bash
python scripts/run_hybrid_generation_pipeline_spike.py --experiment-id EXP-251-manual-review-hybrid-packaging-check --output-dir docs/experiments/artifacts/exp-251-manual-review-hybrid-packaging-check --benchmark-summary docs/experiments/artifacts/exp-239-sora2-current-best-vs-control-two-sample-check/summary.json --label 규카츠 --allow-manual-review
```

### 3.2 시각 review artifact 생성

- final hybrid output에서 아래 review artifact를 추가로 만들었습니다.
  - `hybrid_contact_sheet.png`
  - `first_frame.png`
  - `mid_frame.png`
  - `original_vs_hybrid_mid.png`

## 4. 결과

선택된 후보:

- benchmark: `EXP-239-sora2-current-best-vs-control-two-sample-check`
- label: `규카츠`
- provider: `sora2_current_best`
- gateDecision: `manual_review`

final hybrid 결과:

- `rendererVideoSourceMode=hybrid_generated_clip`
- `rendererMotionMode=hybrid_overlay_packaging`
- `rendererHybridDurationStrategy=freeze_last_frame`
- `finalVideoDurationSec=6.3`

시각 확인 요약:

1. `original_vs_hybrid_mid.png` 기준으로 메인 규카츠와 주요 그릇 구성은 유지됩니다.
2. 원본보다 crop이 타이트해지기는 했지만, QR이나 새로운 텍스트 파편은 보이지 않았습니다.
3. `hybrid_contact_sheet.png` 기준으로 overlay 타이밍과 광고 읽힘도 크게 깨지지 않았습니다.

## 5. 판단

- 이번 결과 기준으로 `규카츠 / sora2_current_best`는 `promote`로 승격 가능한 수준이라고 판단했습니다.
- 이유는 다음과 같습니다.
  - 메인 피사체 보존: 통과
  - 주변 구성 보존: 원본보다 타이트하지만 주요 그릇/소스 구성 유지
  - text/QR intrusion: 없음
  - 모션 패키징 적합: 충분
  - 최종 광고 읽힘: 충분

## 6. 결론

- tray/full-plate lane 전체를 자동 승격한다고 볼 단계는 아니지만, 적어도 `EXP-239 / 규카츠 / sora2_current_best` 이 특정 후보는 `manual_review -> promote`로 닫을 수 있습니다.
- 즉 지금 기준으로는 `lane rule`이 아니라 `approved candidate registry`가 맞는 운영 방식입니다.

## 7. 다음 액션

1. promote decision을 registry에 반영합니다.
2. registry를 읽는 selection smoke를 다시 실행해 `promoted_manual_review` 경로가 실제로 열리는지 확인합니다.
