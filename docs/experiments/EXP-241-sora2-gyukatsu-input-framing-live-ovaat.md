# EXP-241 Sora 2 Gyukatsu Input Framing Live OVAT

## 1. 기본 정보

- 실험 ID: `EXP-241`
- 작성일: `2026-04-14`
- 작성자: Codex
- 관련 기능: `Sora tray lane input framing live OVAT / 규카츠`

## 2. 왜 이 작업을 했는가

- `EXP-239`까지 확인한 결과, `규카츠`에서 `sora2_current_best(hero_tight_zoom)`는 motion은 크지만 `사진 유지형 템플릿 광고`보다 `구도 재해석형 생성`에 더 가까웠습니다.
- 직전까지의 결론은 `prompt phrase`가 아니라 `input framing`을 보자는 것이었기 때문에, 이번에는 tray/full-plate 대표 샘플인 `규카츠`에 대해 입력 프레이밍만 최소 OVAT로 다시 확인했습니다.
- 이번 질문은 단순히 `motion이 큰가`가 아니라, `재해석을 줄이면서도 광고용 motion을 유지할 수 있는 framing이 있는가`였습니다.

## 3. 실험 질문

1. tray lane에서 `baseline_auto`, `hero_medium_zoom`, `hero_tight_zoom` 중 더 나은 입력 프레이밍이 있는가
2. tighter crop이 `EXP-239`에서 보인 wider reinterpretation을 줄여 주는가
3. 만약 결과가 흔들리면, 핵심 병목은 framing보다 `repeatability`인가

## 4. 실행 조건

### 4.1 샘플

- `규카츠`

선정 이유:

- tray/full-plate 대표 샘플입니다.
- 사용자가 직접 QR / 주변 오브젝트 재구성 리스크를 지적했던 샘플이기도 합니다.

### 4.2 고정 조건

1. 모델: `sora-2`
2. 길이: `4초`
3. prompt: 기존 upper-bound food commercial prompt 유지
4. prepare mode baseline: `auto -> cover_center`

### 4.3 비교축

1. `baseline_auto`
   - `cover_center`로 준비한 기준 입력 그대로 사용
2. `hero_medium_zoom`
   - baseline 입력 기준 `0.9x` zoom crop
3. `hero_tight_zoom`
   - baseline 입력 기준 `0.8x` zoom crop
4. `manual_reference`
   - 기존 manual Veo 규카츠 결과를 비교용 reference로만 같이 둠

### 4.4 실행 커맨드

```bash
python -m py_compile scripts/sora2_input_framing_live_ovaat.py scripts/hosted_video_sora2_first_try.py
python scripts/sora2_input_framing_live_ovaat.py --image "docs\sample\음식사진샘플(규카츠).jpg" --output-dir "docs/experiments/artifacts/exp-241-sora2-gyukatsu-input-framing-live-ovaat" --manual-summary "docs/experiments/artifacts/exp-239-sora2-current-best-vs-control-two-sample-check/manual_veo/규카츠/summary.json"
```

## 5. 실행 결과

artifact root:

- `docs/experiments/artifacts/exp-241-sora2-gyukatsu-input-framing-live-ovaat/`

### 5.1 baseline_auto

- status: `completed`
- elapsed: `115.76s`
- mid-frame MSE: `6150.55`
- motion avg_rgb_diff: `14.99`
- 관찰:
  - 세 framing 중 첫 run에서는 motion이 가장 크게 나왔습니다.
  - contact sheet 기준으로도 `EXP-239 hero_tight`보다 구도 재해석이 덜 과격해 보였습니다.
  - 다만 이 값만 보면 좋아 보이지만, 후속 rerun에서 크게 흔들렸습니다.

### 5.2 hero_medium_zoom

- status: `completed`
- elapsed: `96.00s`
- mid-frame MSE: `6952.00`
- motion avg_rgb_diff: `6.47`
- baseline_auto 대비:
  - `mid-frame MSE +801.45`
  - `avg_rgb_diff -8.52`
- 관찰:
  - tighter crop으로 갈수록 motion이 줄어드는 경향이 다시 나타났습니다.
  - 보존성이 특별히 좋아졌다고 보기도 어렵고, motion만 줄었습니다.

### 5.3 hero_tight_zoom

- status: `completed`
- elapsed: `91.20s`
- mid-frame MSE: `7106.90`
- motion avg_rgb_diff: `2.37`
- baseline_auto 대비:
  - `mid-frame MSE +956.35`
  - `avg_rgb_diff -12.62`
- 관찰:
  - 이번 run에서는 세 framing 중 가장 정지컷에 가까웠습니다.
  - `EXP-239`의 같은 `hero_tight_zoom`이 `avg_rgb_diff=21.04`였던 것과 비교하면 완전히 다른 결과입니다.
  - 즉 현재 문제는 crop policy만이 아니라, 같은 framing도 run마다 크게 흔들린다는 점입니다.

### 5.4 manual_reference

- status: `completed`
- mid-frame MSE: `7091.33`
- motion avg_rgb_diff: `14.55`
- 관찰:
  - quality reference로는 여전히 의미가 있습니다.
  - 다만 tray lane에서는 보존 red flag risk를 계속 경계해야 합니다.

## 6. 추가 repeatability spot check

동일 prepared input을 같은 조건으로 한 번 더 rerun했습니다.

### 6.1 hero_tight_zoom repeat2

실행 커맨드:

```bash
python scripts/hosted_video_sora2_first_try.py --image "docs\sample\음식사진샘플(규카츠).jpg" --prepared-image "docs/experiments/artifacts/exp-241-sora2-gyukatsu-input-framing-live-ovaat/prepared_variants/hero_tight_zoom.png" --output-dir "docs/experiments/artifacts/exp-241-sora2-gyukatsu-input-framing-live-ovaat/hero_tight_zoom_repeat2" --prompt "Close-up tabletop food commercial shot of crispy gyukatsu set, crispy texture preserved, gentle steam rising, subtle natural motion only, static close-up, very small camera push-in, warm restaurant lighting, realistic appetizing food motion, no object morphing, no extra ingredients." --seconds 4 --model sora-2
```

- motion avg_rgb_diff: `7.58`
- mid-frame MSE: `6599.13`
- 해석:
  - 같은 `hero_tight_zoom`인데도 `EXP-239=21.04`, 이번 본 run=`2.37`, repeat2=`7.58`로 크게 흔들렸습니다.
  - 즉 `hero_tight`는 current best로 부르기 어려울 정도로 repeatability가 약합니다.

### 6.2 baseline_auto repeat2

실행 커맨드:

```bash
python scripts/hosted_video_sora2_first_try.py --image "docs\sample\음식사진샘플(규카츠).jpg" --prepared-image "docs/experiments/artifacts/exp-241-sora2-gyukatsu-input-framing-live-ovaat/prepared_variants/baseline_auto.png" --output-dir "docs/experiments/artifacts/exp-241-sora2-gyukatsu-input-framing-live-ovaat/baseline_auto_repeat2" --prompt "Close-up tabletop food commercial shot of crispy gyukatsu set, crispy texture preserved, gentle steam rising, subtle natural motion only, static close-up, very small camera push-in, warm restaurant lighting, realistic appetizing food motion, no object morphing, no extra ingredients." --seconds 4 --model sora-2
```

- motion avg_rgb_diff: `4.20`
- mid-frame MSE: `2611.85`
- 해석:
  - `baseline_auto`도 첫 run `14.99`에서 repeat2 `4.20`으로 크게 떨어졌습니다.
  - 즉 tray lane에서는 특정 framing 하나만의 문제가 아니라, 같은 prompt + same prepared input 조합도 run-to-run variance가 큽니다.

## 7. 해석

1. 이번 라운드만 보면 `baseline_auto`가 제일 그럴듯해 보였지만, repeat2에서 바로 크게 흔들렸습니다.
2. `hero_medium_zoom`, `hero_tight_zoom`는 motion을 줄이는 경향이 더 분명했습니다.
3. 특히 `hero_tight_zoom`는 `EXP-239=21.04`, `EXP-241 run1=2.37`, `repeat2=7.58`로 편차가 너무 큽니다.
4. 따라서 현재 tray lane의 핵심 병목은 `어떤 crop이 맞는가`보다 `같은 crop도 일관된 결과를 못 준다`는 repeatability 문제에 더 가깝습니다.
5. 이 상태라면 framing만으로 `production baseline`을 닫는 것은 위험합니다.

## 8. 결론

- 이번 실험의 결론은 `tray lane에서 input framing만으로 current best를 확정할 수 없다`는 것입니다.
- tighter crop은 대체로 motion을 줄였고, baseline_auto조차 repeatability가 약했습니다.
- 따라서 다음 active 실험은 `crop 미세조정`이 아니라 아래 둘 중 하나여야 합니다.
  1. `edit path`로 기존 컷을 보정하는 구조
  2. `hybrid compositor packaging`으로 생성 컷을 본선 템플릿 안에 제어된 방식으로 넣는 구조

## 9. 다음 액션

1. `hero_tight_zoom`를 tray lane current best로 간주하던 가정은 일단 해제합니다.
2. `product_control_motion`은 계속 production baseline으로 유지합니다.
3. 다음 Sora 실험은 `input framing` 추가가 아니라 `edit-based recovery` 또는 `generated shot + template packaging hybrid` 중 하나로 제한합니다.

## 10. 대표 artifact

- `docs/experiments/artifacts/exp-241-sora2-gyukatsu-input-framing-live-ovaat/summary.json`
- `docs/experiments/artifacts/exp-241-sora2-gyukatsu-input-framing-live-ovaat/baseline_auto/규카츠/contact_sheet.png`
- `docs/experiments/artifacts/exp-241-sora2-gyukatsu-input-framing-live-ovaat/hero_medium_zoom/규카츠/contact_sheet.png`
- `docs/experiments/artifacts/exp-241-sora2-gyukatsu-input-framing-live-ovaat/hero_tight_zoom/규카츠/contact_sheet.png`
- `docs/experiments/artifacts/exp-241-sora2-gyukatsu-input-framing-live-ovaat/hero_tight_zoom_repeat2/규카츠/summary.json`
- `docs/experiments/artifacts/exp-241-sora2-gyukatsu-input-framing-live-ovaat/baseline_auto_repeat2/규카츠/summary.json`
