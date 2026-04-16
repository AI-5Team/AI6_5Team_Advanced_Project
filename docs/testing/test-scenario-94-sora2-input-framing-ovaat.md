# Test Scenario 94. Sora 2 input framing OVAT

## 목적

- `맥주` 샘플에서 baseline prompt는 그대로 두고, prepared input framing만 더 타이트하게 바꿨을 때 Sora 결과가 어떻게 달라지는지 확인합니다.
- 핵심 질문은 `input framing 최적화가 motion까지 개선하는가`입니다.

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
python scripts/sora2_input_framing_ovaat.py
```

### 2. 결과 요약 확인

```powershell
Get-Content docs/experiments/artifacts/exp-92-sora2-input-framing-ovaat/summary.json
```

## 기대 결과

1. `summary.json` 아래에 `baseline_reused`, `manual_veo_reference`, `hero_medium_zoom`, `hero_tight_zoom` 4개 축이 있어야 합니다.
2. 새 Sora variant 2개는 모두 `completed`여야 합니다.
3. 각 variant summary에는 다음이 포함돼야 합니다.
   - `prepared_input_variant`
   - `mid_frame_metrics`
   - `motion_metrics`
   - `baseline_comparison`
4. `mid_frame_mse`가 baseline보다 낮아지면, 프레이밍 조정이 보존성에는 도움이 된 것으로 해석합니다.
5. `motion_metrics.avg_rgb_diff`가 baseline보다 크게 낮아지면, 프레이밍 조정이 motion을 더 줄인 것으로 해석합니다.

## 확인 포인트

1. contact sheet 기준으로 zoom variant가 baseline보다 더 정지에 가까운지 확인합니다.
2. mid-frame 기준으로 label / bottle / glass 구조가 baseline보다 안정적인지 확인합니다.
3. 보존성은 좋아졌지만 motion이 줄었다면, 다음 실험은 `single-photo 내부 미세조정`이 아니라 `입력 형식 변경`으로 넘어갑니다.

## 관련 문서

- `docs/experiments/EXP-92-sora2-input-framing-ovaat.md`
