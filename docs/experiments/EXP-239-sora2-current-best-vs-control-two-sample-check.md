# EXP-239 Sora 2 Current Best Vs Control Two Sample Check

## 1. 기본 정보

- 실험 ID: `EXP-239`
- 작성일: `2026-04-14`
- 작성자: Codex
- 관련 기능: `Sora current best vs product control / beer + gyukatsu two-sample live check`

## 2. 왜 이 작업을 했는가

- `EXP-238`에서 `맥주` 1샘플 기준 Sora live lane 재개는 확인했지만, 그 결과만으로는 production 판단을 내리기 어려웠습니다.
- 특히 본 서비스는 특정 한 장면만 잘 나오는 모델이 아니라, `템플릿화 가능한 baseline`이 필요합니다.
- 따라서 이번 작업은 `맥주에서는 괜찮아 보이던 경향이 tray/full-plate 계열에서도 유지되는가`를 확인하기 위한 최소 2샘플 확장입니다.

## 3. 실험 질문

1. `sora2_current_best`는 `drink lane`과 `tray lane` 모두에서 일관된 장점을 보이는가
2. `product_control_motion` 대비 더 나은 광고 체감이 실제로 생기는가
3. 만약 샘플별 편차가 크다면, 다음 축은 `prompt phrase`가 맞는가 아니면 `input method`가 맞는가

## 4. 실행 조건

### 4.1 샘플

- `맥주`
- `규카츠`

선정 이유:

- `맥주`는 current best 비교에서 가장 먼저 다시 열린 drink sample입니다.
- `규카츠`는 사용자가 보존 실패와 QR 재구성 문제를 직접 확인했던 tray/full-plate 대표 샘플입니다.

### 4.2 비교군

- `product_control_motion`
- `sora2_current_best`
- `manual_veo`

### 4.3 실행 커맨드

```bash
python scripts/video_upper_bound_benchmark.py --benchmark-id EXP-239-sora2-current-best-vs-control-two-sample-check --providers product_control_motion sora2_current_best manual_veo --images "docs\sample\음식사진샘플(맥주).jpg" "docs\sample\음식사진샘플(규카츠).jpg" --output-dir docs/experiments/artifacts/exp-239-sora2-current-best-vs-control-two-sample-check
```

## 5. 실행 결과

artifact root:

- `docs/experiments/artifacts/exp-239-sora2-current-best-vs-control-two-sample-check/`

### 5.1 맥주

#### product_control_motion

- status: `completed`
- prepare mode: `cover_bottom`
- motion avg_rgb_diff: `7.43`

#### sora2_current_best

- status: `completed`
- elapsed: `164.35s`
- prepare mode: `cover_bottom`
- mid-frame MSE: `1681.15`
- motion avg_rgb_diff: `6.76`
- 관찰:
  - 보존성은 안정적이지만, 움직임은 control보다 더 강하다고 보기 어렵습니다.
  - 시각적으로는 `좋은 정지컷이 조금 움직이는 수준`에 머뭅니다.
  - 즉 drink lane에서는 current best가 아직 `광고형 motion uplift`를 보여주지 못했습니다.

#### manual_veo

- status: `completed`
- motion avg_rgb_diff: `16.94`
- 관찰:
  - 여전히 quality reference로는 가장 강합니다.

### 5.2 규카츠

#### product_control_motion

- status: `completed`
- prepare mode: `cover_center`
- motion avg_rgb_diff: `12.33`

#### sora2_current_best

- status: `completed`
- elapsed: `99.11s`
- prepare mode: `cover_center`
- mid-frame MSE: `3545.57`
- motion avg_rgb_diff: `21.04`
- 관찰:
  - 이번에는 수치상 motion이 control보다 훨씬 크게 나왔습니다.
  - 다만 contact sheet를 보면 `템플릿 광고 컷`이라기보다 `구도를 다시 해석한 생성형 영상`에 더 가깝습니다.
  - 원본 음식은 유지되지만 시선이 wider/top-down tray 쪽으로 풀리면서, 서비스가 원하는 `사진 유지 + 광고 패키징`과는 거리가 있습니다.
  - 명백한 QR 로고화 같은 red flag는 이번 run에서는 보이지 않았지만, `원본을 거의 그대로 유지한 영상`이라고 보기도 어렵습니다.

#### manual_veo

- status: `completed`
- motion avg_rgb_diff: `14.55`
- 관찰:
  - quality reference로는 여전히 의미가 있습니다.
  - 다만 기존 사용자 관찰대로 규카츠에서는 QR/주변 오브젝트 재구성 risk를 계속 경계해야 합니다.

## 6. 샘플별 중간 판단

### 맥주

| 비교군 | 보존성 | 광고 체감 | 서비스 적합성 | 판단 |
| --- | --- | --- | --- | --- |
| `product_control_motion` | pass | hold | pass | control 유지 |
| `sora2_current_best` | pass | hold | hold | 승격 보류 |
| `manual_veo` | hold | pass | fail | reference only |

### 규카츠

| 비교군 | 보존성 | 광고 체감 | 서비스 적합성 | 판단 |
| --- | --- | --- | --- | --- |
| `product_control_motion` | pass | pass | pass | control 유지 |
| `sora2_current_best` | hold | hold | hold | motion은 있으나 packaging fit 불명확 |
| `manual_veo` | fail risk | pass | fail | reference only |

## 7. 해석

1. `sora2_current_best`는 샘플별 편차가 큽니다.
2. `맥주`에서는 preserve는 좋지만 motion이 거의 살아나지 않았습니다.
3. `규카츠`에서는 motion은 커졌지만, 대신 구도 해석이 커져서 `사진 유지형 템플릿 광고` 관점에서는 애매해졌습니다.
4. 즉 current best의 문제는 단순히 `좋은가 나쁜가`가 아니라, `서비스가 원하는 종류의 좋음`으로 수렴하지 않는다는 점입니다.

## 8. 결론

- 이번 실험의 결론은 `Sora current best가 두 샘플에서 일관된 production baseline을 형성하지 못했다`는 것입니다.
- beer에서는 near-static, gyukatsu에서는 wider reinterpretation 쪽으로 갈렸습니다.
- 따라서 다음 우선순위를 `prompt phrase 추가`로 두는 것은 비효율적입니다.
- 지금 더 타당한 질문은 `입력 방식이나 패키징 구조를 바꾸면 이 편차를 줄일 수 있는가`입니다.

## 9. 다음 액션

1. prompt family를 한 번 더 rerun해, 정말로 phrase 수준에서 해결 여지가 없는지 확인합니다.
2. 그 결과까지 같다면 다음 active 축은 `input framing`, `edit path`, `hybrid compositor` 중 하나로 옮깁니다.
3. production baseline은 그 전까지 계속 `product_control_motion`을 유지합니다.

## 10. 대표 artifact

- `docs/experiments/artifacts/exp-239-sora2-current-best-vs-control-two-sample-check/summary.json`
- `docs/experiments/artifacts/exp-239-sora2-current-best-vs-control-two-sample-check/sora2_current_best/맥주/run/맥주/contact_sheet.png`
- `docs/experiments/artifacts/exp-239-sora2-current-best-vs-control-two-sample-check/sora2_current_best/규카츠/run/규카츠/contact_sheet.png`
- `docs/experiments/artifacts/exp-239-sora2-current-best-vs-control-two-sample-check/product_control_motion/규카츠/contact_sheet.png`
