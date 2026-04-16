# EXP-242 Sora 2 Gyukatsu Edit Live OVAT

## 1. 기본 정보

- 실험 ID: `EXP-242`
- 작성일: `2026-04-14`
- 작성자: Codex
- 관련 기능: `Sora tray lane edit path live OVAT / 규카츠`

## 2. 왜 이 작업을 했는가

- `EXP-241`에서 확인된 핵심 문제는 `input framing`보다 `repeatability`였습니다.
- 그렇다면 다음 질문은 `좋아 보이는 source clip 하나를 먼저 확보한 뒤, edit로 motion이나 shot quality를 더 제어할 수 있는가`였습니다.
- 이번 실험은 `EXP-241 baseline_auto`를 source로 고정하고, 같은 샷 유지 edit가 tray lane에서 실제로 유효한지 확인하기 위한 live OVAT입니다.

## 3. 실험 질문

1. `same shot` edit가 source보다 motion을 더 올릴 수 있는가
2. 그 motion gain이 preserve loss보다 클 정도로 의미 있는가
3. tray lane에서 다음 active 축을 `edit path`로 가져갈 가치가 있는가

## 4. 실행 조건

### 4.1 source 기준선

1. source video: `EXP-241 baseline_auto`
2. source motion avg_rgb_diff: `14.99`
3. source mid-frame MSE: `6150.55`

### 4.2 비교축

1. `source_baseline_auto`
   - `EXP-241`의 규카츠 baseline_auto source clip
2. `same_shot_micro_motion`
   - tray 구성 유지 + subtle steam / highlight / minimal drift만 강화
3. `same_shot_push_in_motion`
   - tray 구성 유지 + slow push-in / slight drift를 더 직접적으로 추가

### 4.3 실행 커맨드

```bash
python -m py_compile scripts/sora2_edit_live_ovaat.py scripts/hosted_video_sora2_first_try.py
python scripts/sora2_edit_live_ovaat.py --source-summary "docs/experiments/artifacts/exp-241-sora2-gyukatsu-input-framing-live-ovaat/baseline_auto/규카츠/summary.json" --output-dir "docs/experiments/artifacts/exp-242-sora2-gyukatsu-edit-live-ovaat"
```

## 5. 실행 결과

artifact root:

- `docs/experiments/artifacts/exp-242-sora2-gyukatsu-edit-live-ovaat/`

### 5.1 source_baseline_auto

- status: `completed`
- mid-frame MSE: `6150.55`
- motion avg_rgb_diff: `14.99`
- 관찰:
  - edit 전 source 자체는 현재 tray lane Sora 결과 중 비교적 볼 만한 편입니다.
  - 다만 raw clip만으로는 서비스 패키징 적합성이 낮습니다.

### 5.2 same_shot_micro_motion

- status: `completed`
- mid-frame MSE: `8176.36`
- motion avg_rgb_diff: `15.32`
- source 대비:
  - `mid-frame MSE +2025.81`
  - `avg_rgb_diff +0.33`
- 관찰:
  - motion gain은 사실상 거의 없습니다.
  - 대신 tray 구성과 소스 그릇 표현이 source보다 더 많이 흔들렸습니다.
  - source보다 나은 edit라고 보기 어렵습니다.

### 5.3 same_shot_push_in_motion

- status: `completed`
- mid-frame MSE: `7233.83`
- motion avg_rgb_diff: `9.31`
- source 대비:
  - `mid-frame MSE +1083.28`
  - `avg_rgb_diff -5.68`
- 관찰:
  - push-in을 직접 요구했는데도 motion은 source보다 오히려 낮아졌습니다.
  - preserve loss는 생겼고, motion recovery는 실패했습니다.
  - tray lane에서는 `edit로 보정`이 해답이라고 보기 어렵습니다.

## 6. 해석

1. `same_shot_micro_motion`은 preserve loss만 커졌고 motion gain은 거의 없었습니다.
2. `same_shot_push_in_motion`은 preserve loss가 있는데도 motion이 source보다 감소했습니다.
3. 즉 tray lane에서는 `edit path`가 trade-off를 푸는 방법이 아니라, source를 다시 흔드는 경로에 더 가깝습니다.
4. 맥주에서 봤던 `부분 충족`보다 더 약한 결과이며, 규카츠 기준으로는 다음 active 축으로 유지할 근거가 부족합니다.

## 7. 결론

- 이번 실험의 결론은 `tray lane에서 edit path는 다음 우선순위가 아니다`입니다.
- source clip을 먼저 고정해도, edit는 motion gain 없이 preserve loss만 늘리거나 둘 다 악화시키는 결과가 나왔습니다.
- 따라서 다음 active 축은 `edit`가 아니라 `hybrid compositor packaging`이어야 합니다.

## 8. 다음 액션

1. `edit path`는 규카츠 기준 active 실험선에서 우선순위를 낮춥니다.
2. `product_control_motion`은 계속 본선 baseline으로 유지합니다.
3. 다음은 생성컷 자체를 더 완벽하게 만들려 하기보다, `generated shot + template overlay` 하이브리드가 서비스 적합성을 실제로 올리는지 확인합니다.

## 9. 대표 artifact

- `docs/experiments/artifacts/exp-242-sora2-gyukatsu-edit-live-ovaat/summary.json`
- `docs/experiments/artifacts/exp-242-sora2-gyukatsu-edit-live-ovaat/same_shot_micro_motion/contact_sheet.png`
- `docs/experiments/artifacts/exp-242-sora2-gyukatsu-edit-live-ovaat/same_shot_push_in_motion/contact_sheet.png`
- `docs/experiments/artifacts/exp-241-sora2-gyukatsu-input-framing-live-ovaat/baseline_auto/규카츠/contact_sheet.png`
