# EXP-91 Sora 2 motion prompt family OVAT

## 1. 기본 정보

- 실험 ID: `EXP-91`
- 작성일: `2026-04-09`
- 작성자: Codex
- 관련 기능: `Sora 2 image-to-video / motion prompt family OVAT / 맥주 샘플`

## 2. 왜 이 작업을 했는가

- `EXP-90`에서 Sora 2는 실제 generation에는 성공했지만, 결과가 전반적으로 `고품질 still + 약한 motion`에 가까웠습니다.
- 따라서 다음 질문은 `Sora가 원래 near-static한가`가 아니라 `현재 minimal motion prompt family 때문에 near-static한가`였습니다.
- 이번 실험은 `맥주` 1장에 대해 motion 지시 방식만 바꿨을 때 실제 움직임이 살아나는지 확인하는 OVAT입니다.

## 3. 고정 조건과 비교축

### 고정 조건

1. 샘플: `docs/sample/음식사진샘플(맥주).jpg`
2. 모델: `sora-2`
3. 길이: `4초`
4. prepare mode: `auto -> cover_bottom`
5. 입력 해상도: `1280x720`

### 비교축

1. `baseline_reused`
   - `EXP-90`의 기존 Sora 결과를 재사용했습니다.
2. `manual_veo_reference`
   - 사용자가 직접 생성해 넣은 Veo 결과를 참고선으로 같이 놓았습니다.
   - 이 결과는 어디까지나 `비교용 upper-bound reference`입니다.
3. `micro_motion_locked`
   - 카메라는 최대한 고정하고, bubbles / foam / condensation 같은 제품 내부 micro-motion만 더 직접적으로 지시했습니다.
4. `camera_orbit_beats`
   - `3 clear motion beats + gentle orbit + push-in`을 더 명시적으로 지시했습니다.

## 4. 무엇을 만들고 바꿨는가

### 스크립트

1. `scripts/video_benchmark_common.py`
   - 연속 프레임 차이를 보는 `video_motion_metrics()`를 추가했습니다.
2. `scripts/hosted_video_sora2_first_try.py`
   - Sora summary에 `motion_metrics`를 함께 저장하도록 확장했습니다.
3. `scripts/sora2_motion_prompt_family_ovaat.py`
   - `맥주` 샘플 기준으로 baseline reuse + manual Veo reference + Sora variant 2개를 한 번에 요약하는 OVAT 스크립트를 추가했습니다.
4. `scripts/video_upper_bound_benchmark.py`
   - active provider를 `local_ltx`, `veo31`, `sora2`, `manual_veo`로 정리했습니다.
   - provider summary에도 `motion_metrics`를 포함할 수 있게 확장했습니다.

### artifact root

- `docs/experiments/artifacts/exp-91-sora2-motion-prompt-family-ovaat/`

## 5. 실행 결과

### baseline_reused

- status: `completed`
- mid-frame MSE: `4452.34`
- motion avg_rgb_diff: `16.72`
- 관찰:
  - `EXP-90`에서 이미 본 것처럼 품질은 괜찮지만 near-static 성격이 남아 있습니다.
  - contact sheet 기준으로도 변화는 크지 않지만, 최소한 화면 전체가 완전히 얼어붙진 않았습니다.

### manual_veo_reference

- status: `completed`
- mid-frame MSE: `5811.95`
- motion avg_rgb_diff: `16.94`
- 관찰:
  - 맥주 샘플은 이번 비교군 중 체감 품질이 가장 좋았습니다.
  - 다만 이 값은 `원본 보존 성공`이 아니라 `고품질 upper-bound reference`로만 해석해야 합니다.

### micro_motion_locked

- status: `completed`
- mid-frame MSE: `930.05`
- motion avg_rgb_diff: `1.53`
- baseline 대비:
  - `mid-frame MSE -3522.29`
  - `avg_rgb_diff -15.19`
- 관찰:
  - bottle / glass / label 보존은 baseline보다 훨씬 좋아졌습니다.
  - 하지만 contact sheet 기준으로는 거의 정지 이미지에 가까워졌습니다.
  - 즉 `보존성`은 강해졌지만 `motion`은 사실상 사라졌습니다.

### camera_orbit_beats

- status: `completed`
- mid-frame MSE: `3823.47`
- motion avg_rgb_diff: `1.94`
- baseline 대비:
  - `mid-frame MSE -628.87`
  - `avg_rgb_diff -14.78`
- 관찰:
  - `micro_motion_locked`보다 보존은 약하지만 baseline보다는 안정적입니다.
  - 하지만 명시적으로 orbit / push-in / beats를 적어도 실제 contact sheet는 거의 움직이지 않았습니다.
  - 즉 prompt를 더 직접적으로 써도 motion이 살아난다고 보기 어렵습니다.

## 6. 해석

### 이번 OVAT에서 확인된 것

1. 이번 조건에서는 `motion을 더 자세히 쓰는 것`이 motion 강화로 이어지지 않았습니다.
2. 오히려 두 variant 모두 baseline보다 더 정지에 가깝게 수렴했습니다.
3. 특히 `micro_motion_locked`는 `보존성 강화 -> motion 붕괴`라는 trade-off를 아주 강하게 보여줬습니다.
4. `camera_orbit_beats`도 orbit과 beat를 명시했지만, 실제 결과는 여전히 near-static이었습니다.
5. 따라서 현재 병목은 `motion prompt를 조금 더 잘 쓰면 해결될 문제`라기보다, `single-photo + preserve image` 조건에서 Sora가 선택하는 해의 성격일 가능성이 큽니다.

### 이번 OVAT가 시사하는 것

1. `보존성`과 `움직임`은 현재 조건에서 서로 당기고 있습니다.
2. `맥주`처럼 quality reference가 강한 샘플에서도 prompt-level tuning만으로는 광고형 motion을 끌어내지 못했습니다.
3. 따라서 다음 단계는 `프롬프트 문구 추가`보다 `입력 방식 변경`, `hybrid motion`, `template/compositor 복귀` 쪽이 더 타당합니다.

## 7. 결론

- 가설 충족 여부: **반증에 가까움**
- 판단:
  - `Sora에서 motion prompt만 더 구체화하면 near-static이 풀릴 것`이라는 가설은 이번 실험에서 지지되지 않았습니다.
  - 오히려 `prompt를 더 세게 쓸수록 preserve된 고품질 정지컷` 쪽으로 수렴하는 경향이 확인됐습니다.
  - 따라서 지금은 `Sora prompt family를 더 미세조정`하는 것보다, `입력 조건 변경` 또는 `생성형 video를 보조 모듈로만 쓰는 구조`를 검토하는 편이 맞습니다.

## 8. 다음 액션

1. `manual Veo`는 계속 `quality reference only`로 유지합니다.
2. Sora는 다음에 `prompt phrase`가 아니라 `입력 방식`을 바꾼 실험으로 넘어갑니다.
   - 예: multi-reference, first/last frame, masked region, hybrid compositor
3. 본선 기준선은 여전히 `template motion + deterministic packaging` 쪽을 우선 유지합니다.

## 9. 대표 artifact

- `docs/experiments/artifacts/exp-91-sora2-motion-prompt-family-ovaat/summary.json`
- `docs/experiments/artifacts/exp-91-sora2-motion-prompt-family-ovaat/micro_motion_locked/맥주/contact_sheet.png`
- `docs/experiments/artifacts/exp-91-sora2-motion-prompt-family-ovaat/camera_orbit_beats/맥주/contact_sheet.png`
- `docs/experiments/artifacts/exp-90-upper-bound-video-benchmark/sora2/맥주/contact_sheet.png`
- `docs/experiments/artifacts/exp-90-upper-bound-video-benchmark/manual_veo/맥주/contact_sheet.png`
