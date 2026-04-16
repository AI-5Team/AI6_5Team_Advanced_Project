# EXP-230 Product Control Motion OVAT

## 1. 기본 정보

- 실험 ID: `EXP-230`
- 작성일: `2026-04-13`
- 작성자: Codex
- 관련 기능: `deterministic template motion / product control uplift / static control vs motion control`

## 2. 왜 이 작업을 했는가

- `EXP-229`에서 `Sora 2 current best` live 비교는 `OPENAI_API_KEY` 상태 때문에 막혔습니다.
- 같은 시점에 이미 확인된 사실은, 현재 본선 기준선인 `product_control`은 광고 문법은 좋지만 객체 motion 수치는 매우 낮다는 점입니다.
- 그래서 외부 생성형 모델에 기대지 않고, 현재 서비스 control 자체를 더 광고형으로 끌어올릴 수 있는지 먼저 확인하기로 했습니다.

## 3. 이번 실험 질문

1. 현재 static `product_control`에 scene 내부 `zoom/pan` motion을 넣으면 광고 체감이 실제로 올라가는가
2. 그 motion uplift가 원본 보존을 크게 해치지 않는가
3. local LTX보다 더 서비스 친화적인 baseline이 될 수 있는가

## 4. 무엇을 바꿨는가

### 4.1 benchmark 스크립트 확장

- `scripts/video_upper_bound_benchmark.py`
  - `product_control_motion` provider를 추가했습니다.
  - `ffmpeg zoompan` 기반 deterministic motion clip 렌더링 경로를 추가했습니다.

### 4.2 motion 방식

- 각 scene image는 그대로 유지합니다.
- 차이는 scene 내부에서 아래 preset만 적용한 것입니다.
  - `push_in_center`
  - `push_in_top`
  - `push_in_bottom`
- 즉 생성형 video가 아니라 `template motion + compositor`의 deterministic uplift 실험입니다.

## 5. 실행 조건

1. 샘플
   - `규카츠`
   - `맥주`
2. 비교군
   - `product_control`
   - `product_control_motion`
   - `local_ltx`
   - `manual_veo`
3. artifact root
   - `docs/experiments/artifacts/exp-230-product-control-motion-ovaat/`

## 6. 실행 커맨드

```bash
python -m py_compile scripts/video_upper_bound_benchmark.py
python scripts/video_upper_bound_benchmark.py --benchmark-id EXP-230-product-control-motion-ovaat --providers product_control product_control_motion local_ltx manual_veo --output-dir docs/experiments/artifacts/exp-230-product-control-motion-ovaat
```

## 7. 실행 결과

### 7.1 규카츠

#### product_control

- mid-frame MSE: `2360.96`
- motion avg_rgb_diff: `0.65`

#### product_control_motion

- mid-frame MSE: `2677.87`
- motion avg_rgb_diff: `12.33`
- static control 대비:
  - `mid-frame MSE +316.91`
  - `avg_rgb_diff +11.68`

#### 해석

- motion은 크게 올라갔습니다.
- 반면 보존 손실은 `manual_veo` 수준의 재구성까지는 가지 않았고, 메뉴 정체성은 유지됩니다.
- 즉 `규카츠` 샘플에서는 `광고 에너지 상승 대비 preserve 손실이 감당 가능`한 수준으로 보입니다.

### 7.2 맥주

#### product_control

- mid-frame MSE: `2490.45`
- motion avg_rgb_diff: `0.61`

#### product_control_motion

- mid-frame MSE: `2514.74`
- motion avg_rgb_diff: `7.43`
- static control 대비:
  - `mid-frame MSE +24.29`
  - `avg_rgb_diff +6.82`

#### 해석

- 맥주에서는 preservation 손실이 거의 늘지 않았습니다.
- motion은 분명히 올라갔고, bottle/glass identity도 유지됩니다.
- 특히 `맥주` 샘플에서는 이 uplift가 매우 효율적입니다.

## 8. 비교 해석

### 8.1 product_control vs product_control_motion

1. `product_control_motion`은 두 샘플 모두 static control보다 motion 체감이 확실히 올라갔습니다.
2. `규카츠`는 preserve cost가 조금 늘었지만 여전히 서비스 기준선 안쪽입니다.
3. `맥주`는 preserve cost 증가가 거의 없고 uplift 효율이 좋습니다.

### 8.2 product_control_motion vs local_ltx

1. `local_ltx`
   - 보존성은 강합니다.
   - 하지만 여전히 near-static입니다.
2. `product_control_motion`
   - 생성형이 아니지만 광고 에너지는 local LTX보다 훨씬 높습니다.
   - CTA, 컷 템포, 결과물 패키징 적합성까지 포함하면 서비스 baseline 후보로 더 적합합니다.

### 8.3 product_control_motion vs manual_veo

1. `manual_veo`는 여전히 motion/품질 상한선입니다.
2. 하지만 `product_control_motion`은 그보다 훨씬 안정적으로 원본 정체성을 지킵니다.
3. 즉 `품질 ceiling`은 manual Veo가 높고, `서비스 baseline`은 product control motion이 더 현실적입니다.

## 9. scorecard 판정

### product_control_motion

| 항목 | 판정 | 메모 |
| --- | --- | --- |
| 보존성 | pass | 두 샘플 모두 정체성 유지 |
| 광고 체감 | pass | static control보다 분명히 상승 |
| 반복성 | pass | deterministic compositor |
| 서비스 적합성 | pass | 기존 템플릿 패키징과 자연스럽게 연결 |
| 최종 역할 | 본선 candidate | 가장 유력 |

## 10. 결론

- 이번 실험은 `긍정적`입니다.
- `product_control_motion`은 외부 생성형 모델 없이도, 현재 본선 기준선보다 더 광고형 에너지를 만들 수 있음을 보여줬습니다.
- 특히 중요한 점은 `motion uplift`가 `원본 보존 붕괴` 없이 일어났다는 것입니다.
- 따라서 다음 우선순위는 `Sora가 열리면 비교를 이어가는 것`과 별개로, 이 motion control을 실제 renderer 경로에 이식할지 검토하는 쪽이 맞습니다.

## 11. 다음 액션

1. `product_control_motion`을 실제 renderer 후보로 승격할지 검토합니다.
2. 가능하면 benchmark 전용이 아니라 `services/worker/renderers` 본선 경로에 옮기는 실험으로 이어갑니다.
3. Sora credential이 복구되면 같은 scorecard에 `sora2_current_best`만 다시 붙여 비교합니다.

## 12. 대표 artifact

- `docs/experiments/artifacts/exp-230-product-control-motion-ovaat/summary.json`
- `docs/experiments/artifacts/exp-230-product-control-motion-ovaat/product_control/규카츠/contact_sheet.png`
- `docs/experiments/artifacts/exp-230-product-control-motion-ovaat/product_control_motion/규카츠/contact_sheet.png`
- `docs/experiments/artifacts/exp-230-product-control-motion-ovaat/product_control/맥주/contact_sheet.png`
- `docs/experiments/artifacts/exp-230-product-control-motion-ovaat/product_control_motion/맥주/contact_sheet.png`
