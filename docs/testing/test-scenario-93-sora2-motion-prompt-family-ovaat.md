# Test Scenario 93. Sora 2 motion prompt family OVAT

## 목적

- `맥주` 샘플에서 Sora 2의 near-static 성격이 `baseline prompt` 때문인지, 아니면 더 구조적인 문제인지 확인합니다.
- `EXP-90`의 baseline Sora 결과와 사용자가 직접 넣은 `manual Veo` reference를 함께 놓고, 새 Sora prompt variant 2개를 비교합니다.

## 준비물

1. `OPENAI_API_KEY`
2. `ffmpeg`
3. `EXP-90` baseline artifact
   - `docs/experiments/artifacts/exp-90-upper-bound-video-benchmark/sora2/맥주/summary.json`
4. `manual Veo` reference
   - `docs/experiments/artifacts/exp-90-upper-bound-video-benchmark/manual/veo/맥주/veo_manual.mp4`

## 실행 절차

### 1. OVAT 실행

```powershell
python scripts/sora2_motion_prompt_family_ovaat.py
```

### 2. 결과 요약 확인

```powershell
Get-Content docs/experiments/artifacts/exp-91-sora2-motion-prompt-family-ovaat/summary.json
```

## 기대 결과

1. `summary.json` 아래에 `baseline_reused`, `manual_veo_reference`, `micro_motion_locked`, `camera_orbit_beats` 4개 축이 있어야 합니다.
2. 새 Sora variant 2개는 모두 `completed`여야 합니다.
3. 각 variant summary에는 다음이 포함돼야 합니다.
   - `mid_frame_metrics`
   - `motion_metrics`
   - `baseline_comparison`
4. `motion_metrics.avg_rgb_diff`가 baseline보다 낮게 나오면, 이번 prompt family가 실제 motion을 더 줄인 것으로 해석합니다.
5. `micro_motion_locked`에서 `mid_frame_mse`가 크게 낮아지면, `보존성 강화와 motion 붕괴` trade-off로 기록합니다.

## 확인 포인트

1. `baseline_reused`와 새 variant의 contact sheet를 나란히 봤을 때 실제로도 거의 정지에 가까운지 확인합니다.
2. `camera_orbit_beats`처럼 motion을 더 직접 지시해도 여전히 near-static이면, 다음 실험은 prompt phrase가 아니라 입력 조건 변경으로 넘어갑니다.
3. `manual_veo_reference`는 언제나 `quality reference only`로만 해석합니다.

## 관련 문서

- `docs/experiments/EXP-91-sora2-motion-prompt-family-ovaat.md`
