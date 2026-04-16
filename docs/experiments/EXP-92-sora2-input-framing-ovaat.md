# EXP-92 Sora 2 input framing OVAT

## 1. 기본 정보

- 실험 ID: `EXP-92`
- 작성일: `2026-04-09`
- 작성자: Codex
- 관련 기능: `Sora 2 image-to-video / input framing OVAT / 맥주 샘플`

## 2. 왜 이 작업을 했는가

- `EXP-91`에서 `motion prompt family`를 더 직접적으로 써도 Sora 결과는 오히려 더 정지에 가깝게 수렴했습니다.
- 그래서 다음 질문은 `prompt`가 아니라 `입력 프레이밍`이었습니다.
- 이번 실험은 기존 baseline prompt는 그대로 두고, `prepared input`만 더 타이트한 hero zoom으로 바꾸면 motion이나 보존성이 달라지는지 확인하는 OVAT입니다.

## 3. 고정 조건과 비교축

### 고정 조건

1. 샘플: `docs/sample/음식사진샘플(맥주).jpg`
2. 모델: `sora-2`
3. 길이: `4초`
4. prompt: `EXP-90` baseline Sora prompt 그대로 재사용
5. 비교 기준선:
   - `baseline_reused`
   - `manual_veo_reference`

### 바꾼 레버

1. `hero_medium_zoom`
   - baseline prepared input에서 약 `0.9x` zoom crop
2. `hero_tight_zoom`
   - baseline prepared input에서 약 `0.8x` zoom crop

즉 이번 실험은 `input framing scale`만 바꿨습니다.

## 4. 무엇을 만들고 바꿨는가

### 스크립트

1. `scripts/hosted_video_sora2_first_try.py`
   - `--prepared-image`를 받을 수 있게 확장했습니다.
   - 이미 가공된 입력 이미지를 그대로 reference로 넣는 경로를 추가했습니다.
2. `scripts/sora2_input_framing_ovaat.py`
   - `baseline prepared_input.png`를 기반으로 zoom crop variant를 만들고
   - baseline / manual Veo / 새 Sora 2개 variant를 한 번에 비교하도록 추가했습니다.

### artifact root

- `docs/experiments/artifacts/exp-92-sora2-input-framing-ovaat/`

## 5. 실행 결과

### baseline_reused

- status: `completed`
- mid-frame MSE: `4452.34`
- motion avg_rgb_diff: `16.72`
- 관찰:
  - 품질은 괜찮지만 여전히 near-static입니다.

### manual_veo_reference

- status: `completed`
- mid-frame MSE: `5811.95`
- motion avg_rgb_diff: `16.94`
- 관찰:
  - 체감 품질 reference로는 여전히 가장 강합니다.
  - 다만 이 결과는 언제나 `quality reference only`입니다.

### hero_medium_zoom

- status: `completed`
- mid-frame MSE: `4130.55`
- motion avg_rgb_diff: `3.27`
- baseline 대비:
  - `mid-frame MSE -321.79`
  - `avg_rgb_diff -13.45`
- 관찰:
  - bottle / glass 비중은 커졌고, mid-frame 기준 보존성은 baseline보다 약간 좋아졌습니다.
  - 하지만 contact sheet는 baseline보다 훨씬 더 정지에 가깝습니다.
  - 즉 프레이밍을 타이트하게 줄수록 motion이 크게 줄었습니다.

### hero_tight_zoom

- status: `completed`
- mid-frame MSE: `2369.92`
- motion avg_rgb_diff: `3.67`
- baseline 대비:
  - `mid-frame MSE -2082.42`
  - `avg_rgb_diff -13.05`
- 관찰:
  - 보존성은 두 variant 중 가장 좋았습니다.
  - label / bottle / glass 구조도 baseline보다 더 안정적으로 보였습니다.
  - 하지만 여기서도 contact sheet는 거의 정지컷에 가깝습니다.
  - 즉 `더 강한 hero crop -> 더 높은 보존성 + 더 낮은 motion` 패턴이 반복됐습니다.

## 6. 해석

### 이번 OVAT에서 확인된 것

1. 입력 프레이밍을 타이트하게 만들면, Sora는 확실히 더 보수적으로 움직입니다.
2. `hero_medium_zoom`, `hero_tight_zoom` 모두 baseline보다 `motion avg_rgb_diff`가 크게 낮았습니다.
3. 반대로 `mid-frame MSE`는 모두 좋아져 보존성은 올라갔습니다.
4. 즉 이번 조건에서도 다시 한 번 `보존성`과 `motion`이 서로 당기는 구조가 확인됐습니다.

### 이번 OVAT가 시사하는 것

1. `prompt`뿐 아니라 `input framing`도 현재는 같은 방향으로 수렴합니다.
2. 즉 `입력을 더 잘 다듬으면 motion도 같이 나아질 것`이라는 기대는 이번 실험에서 지지되지 않았습니다.
3. 대신 `입력을 더 다듬을수록 preserve still` 쪽으로 강하게 잠기는 경향이 확인됐습니다.

## 7. 결론

- 가설 충족 여부: **반증에 가까움**
- 판단:
  - 현재 Sora 조건에서는 `입력 프레이밍 최적화`도 motion 품질 해결책이 아니었습니다.
  - 대신 프레이밍이 타이트해질수록 원본 보존은 좋아지고, motion은 사라지는 trade-off가 더 분명해졌습니다.
  - 따라서 다음 실험도 `프롬프트`나 `crop` 미세조정보다 `입력 방식 자체 변경`으로 넘어가는 편이 맞습니다.

## 8. 다음 액션

1. 다음은 `single-photo` 내부 미세조정보다 다른 입력 형식을 시험합니다.
   - 예: first/last frame, multi-reference, masked region
2. 동시에 본선은 계속 `template motion + compositor`를 기본축으로 유지합니다.
3. `manual Veo`는 앞으로도 quality upper-bound reference로만 사용합니다.

## 9. 대표 artifact

- `docs/experiments/artifacts/exp-92-sora2-input-framing-ovaat/summary.json`
- `docs/experiments/artifacts/exp-92-sora2-input-framing-ovaat/hero_medium_zoom/맥주/contact_sheet.png`
- `docs/experiments/artifacts/exp-92-sora2-input-framing-ovaat/hero_tight_zoom/맥주/contact_sheet.png`
- `docs/experiments/artifacts/exp-92-sora2-input-framing-ovaat/prepared_variants/hero_medium_zoom.png`
- `docs/experiments/artifacts/exp-92-sora2-input-framing-ovaat/prepared_variants/hero_tight_zoom.png`
