# Test Scenario 95. Sora 2 edit motion recovery OVAT

## 목적

- `EXP-92 hero_tight_zoom` source 영상에 대해, `edit` 2단계가 motion recovery 경로가 되는지 확인합니다.
- 핵심 질문은 `source preserve를 유지하면서 motion을 더 올릴 수 있는가`입니다.

## 준비물

1. `OPENAI_API_KEY`
2. `ffmpeg`
3. `EXP-92` source artifact
   - `docs/experiments/artifacts/exp-92-sora2-input-framing-ovaat/hero_tight_zoom/맥주/summary.json`
4. `EXP-90` baseline artifact
   - `docs/experiments/artifacts/exp-90-upper-bound-video-benchmark/sora2/맥주/summary.json`

## 실행 절차

### 1. OVAT 실행

```powershell
uv run --with openai python scripts/sora2_edit_motion_recovery_ovaat.py
```

### 2. 결과 요약 확인

```powershell
Get-Content docs/experiments/artifacts/exp-93-sora2-edit-motion-recovery-ovaat/summary.json
```

## 기대 결과

1. `summary.json` 아래에 `source_hero_tight`, `baseline_reused`, `manual_veo_reference`, `same_shot_more_motion`, `same_shot_push_in_motion`이 있어야 합니다.
2. edit variant 2개는 `completed`여야 합니다.
3. 각 edit variant summary에는 다음이 포함돼야 합니다.
   - `edit_video_id`
   - `mid_frame_metrics`
   - `motion_metrics`
   - `source_comparison`
4. `motion_metrics.avg_rgb_diff`가 source보다 높아지면, edit가 motion recovery에는 기여한 것으로 해석합니다.
5. `mid_frame_mse`도 함께 크게 올라가면, motion gain과 preserve loss가 같이 발생한 것으로 해석합니다.

## 확인 포인트

1. contact sheet 기준으로 edit variant가 source보다 실제로 더 움직이는지 확인합니다.
2. motion이 늘어났더라도 label / bottle / glass / foam 보존이 많이 깨졌는지 같이 봅니다.
3. `same-shot` edit가 motion gain은 주지만 preserve loss가 크면, production 후보가 아니라 research-only로 분류합니다.

## 관련 문서

- `docs/experiments/EXP-93-sora2-edit-motion-recovery-ovaat.md`
