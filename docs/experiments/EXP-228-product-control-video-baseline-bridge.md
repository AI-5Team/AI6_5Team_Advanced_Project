# EXP-228 Product Control Video Baseline Bridge

## 1. 기본 정보

- 실험 ID: `EXP-228`
- 작성일: `2026-04-13`
- 작성자: Codex
- 관련 기능: `product control 추가 / video benchmark 재구성 / control vs local LTX vs manual Veo reference`

## 2. 왜 이 작업을 했는가

- `EXP-226`에서 다음 영상 baseline 비교는 반드시 `product control`을 포함해야 한다고 정리했습니다.
- 그 전까지의 benchmark는 `local_ltx`, `veo31`, `sora2`, `manual_veo` 중심이었고, 실제 본선 기준선이 빠져 있었습니다.
- 이번 실험의 목적은 `현재 서비스 control`을 비교선에 넣고, 그 control이 실제로 어떤 역할을 하는지 확인하는 것입니다.

## 3. 이번에 바꾼 것

### 3.1 스크립트

- `scripts/video_upper_bound_benchmark.py`
  - `product_control` provider를 추가했습니다.
  - `--benchmark-id` 인자를 추가했습니다.
  - 비교 결과에 `control_type`, `packaging_fit`를 같이 남기도록 확장했습니다.

### 3.2 product control 정의

- `product_control`은 생성형 image-to-video가 아닙니다.
- 현재 서비스 본선 기준선을 흉내 내는 `template motion + compositor` control입니다.
- 구성:
  - 원본 사진 보존
  - `b_grade_fun` 오버레이
  - 4컷 짧은 씬
  - badge / CTA / B급 카피

## 4. 고정 조건

1. 샘플
   - `규카츠`
   - `맥주`
2. 비교군
   - `product_control`
   - `local_ltx`
   - `manual_veo`
3. artifact root
   - `docs/experiments/artifacts/exp-228-product-control-video-baseline-bridge/`

## 5. 실행 커맨드

```bash
python -m py_compile scripts/video_upper_bound_benchmark.py
python scripts/video_upper_bound_benchmark.py --benchmark-id EXP-228-product-control-video-baseline-bridge --providers product_control local_ltx manual_veo --output-dir docs/experiments/artifacts/exp-228-product-control-video-baseline-bridge
```

## 6. 실행 결과

### 6.1 규카츠

#### product_control

- status: `completed`
- prepare mode: `cover_center`
- mid-frame MSE: `2360.96`
- motion avg_rgb_diff: `0.65`
- 관찰:
  - motion metric은 낮지만, contact sheet 기준으로는 `컷 분할 + 오버레이 + CTA`가 분명합니다.
  - 음식 정체성은 유지되고, B급 광고 문법은 제어 가능합니다.
  - 즉 이 control의 에너지는 `객체 motion`이 아니라 `편집/카피/패키징`에서 나옵니다.

#### local_ltx

- status: `completed`
- elapsed: `18.46s`
- prepare mode: `cover_center`
- mid-frame MSE: `254.76`
- motion avg_rgb_diff: `0.93`
- 관찰:
  - 수치상 보존성은 product control보다 더 강합니다.
  - 하지만 contact sheet 기준으로는 거의 한 컷이 반복되는 수준입니다.
  - `광고 컷`이라기보다 `움직임이 거의 없는 보존형 결과`에 가깝습니다.

#### manual_veo

- status: `completed`
- prepare mode: `cover_center`
- mid-frame MSE: `7091.33`
- motion avg_rgb_diff: `14.55`
- 관찰:
  - 체감 품질과 motion은 세 비교군 중 가장 강합니다.
  - 그러나 규카츠 샘플은 QR과 주변 오브젝트 재구성이 명확합니다.
  - 따라서 `품질 상한선 reference`로는 유효하지만, production 후보로는 부적합합니다.

### 6.2 맥주

#### product_control

- status: `completed`
- prepare mode: `cover_bottom`
- mid-frame MSE: `2490.45`
- motion avg_rgb_diff: `0.61`
- 관찰:
  - 역시 motion 수치는 낮지만, bottle/glass identity를 유지한 채 CTA와 템플릿 문법을 얹을 수 있습니다.
  - 본선 control로는 일관성이 높습니다.

#### local_ltx

- status: `completed`
- elapsed: `12.59s`
- prepare mode: `cover_bottom`
- mid-frame MSE: `101.32`
- motion avg_rgb_diff: `0.95`
- 관찰:
  - bottle/glass 보존은 강합니다.
  - 하지만 contact sheet 기준으로는 거의 정지 사진과 큰 차이가 없습니다.
  - `광고형 에너지`보다는 `보존형 짧은 클립`에 가깝습니다.

#### manual_veo

- status: `completed`
- prepare mode: `cover_bottom`
- mid-frame MSE: `5811.95`
- motion avg_rgb_diff: `16.94`
- 관찰:
  - 맥주 샘플에서는 품질 reference로 매우 강합니다.
  - 다만 이 결과도 본선 후보라기보다 `상한선 참고`가 맞습니다.

## 7. 해석

### 7.1 이번에 새로 확인된 것

1. `motion metric` 하나만으로 광고 품질을 판정하면 안 됩니다.
2. `product_control`은 `avg_rgb_diff`가 낮아도 실제 광고 문법은 가장 명확합니다.
3. 즉 현재 서비스에서 중요한 motion은 `객체 자체의 사실적 움직임`만이 아니라, `컷 템포`, `오버레이`, `CTA 전달`까지 포함한 광고 에너지입니다.
4. `local_ltx`는 보존성 수치는 좋지만, 광고 체감에서는 아직 control을 이기지 못합니다.
5. `manual_veo`는 품질 reference로는 강하지만, 특히 규카츠에서는 보존성 red flag가 뚜렷합니다.

### 7.2 이번 비교가 의미하는 것

- 이제 다음 질문은 `생성형 모델이 있는가`가 아니라 아래로 좁혀집니다.
  1. 생성형 후보가 `product_control`보다 실제 광고 체감 품질을 올려주는가
  2. 그 향상이 원본 보존 손실 없이 가능한가
  3. 안 되면 본선은 `template motion + compositor`를 계속 기준선으로 둬야 하는가

## 8. 결론

- 이번 실험으로 `product control`이 실제 baseline 비교에 들어갈 수 있게 됐습니다.
- 현재 판단은 아래와 같습니다.
  - `product_control`: 본선 기준선으로 유지
  - `local_ltx`: 보존형 후보이지만 광고 체감 품질은 아직 부족
  - `manual_veo`: quality upper-bound reference only
- 따라서 다음 비교는 `Sora 2 current best`를 같은 표에 추가하되, 판정 기준은 `EXP-227` scorecard로 고정하는 편이 맞습니다.

## 9. 대표 artifact

- `docs/experiments/artifacts/exp-228-product-control-video-baseline-bridge/summary.json`
- `docs/experiments/artifacts/exp-228-product-control-video-baseline-bridge/product_control/규카츠/contact_sheet.png`
- `docs/experiments/artifacts/exp-228-product-control-video-baseline-bridge/product_control/맥주/contact_sheet.png`
- `docs/experiments/artifacts/exp-228-product-control-video-baseline-bridge/local_ltx/규카츠/contact_sheet.png`
- `docs/experiments/artifacts/exp-228-product-control-video-baseline-bridge/local_ltx/맥주/contact_sheet.png`
- `docs/experiments/artifacts/exp-228-product-control-video-baseline-bridge/manual_veo/규카츠/contact_sheet.png`
- `docs/experiments/artifacts/exp-228-product-control-video-baseline-bridge/manual_veo/맥주/contact_sheet.png`
