# EXP-231 B-Grade Renderer Motion Bridge

## 1. 기본 정보

- 실험 ID: `EXP-231`
- 작성일: `2026-04-14`
- 작성자: Codex
- 관련 기능: `b_grade_fun renderer / deterministic zoompan motion / benchmark-to-production bridge`

## 2. 왜 이 작업을 했는가

- `EXP-230`에서 `product_control_motion`은 static control보다 광고 에너지를 확실히 올렸습니다.
- 하지만 그 시점 결과는 어디까지나 `scripts/video_upper_bound_benchmark.py` 안에서만 검증된 것이었습니다.
- 즉 실제 본선 판단을 하려면, 같은 motion uplift가 `services/worker`의 실제 generation pipeline에도 들어가야 했습니다.

## 3. 이번 작업 질문

1. `EXP-230`에서 검증한 deterministic zoompan motion을 실제 renderer 경로로 옮길 수 있는가
2. 옮긴 뒤에도 기존 non-`b_grade_fun` 경로를 깨지 않고 유지할 수 있는가
3. 실제 generation output에서 `rendererMotionMode`를 명시적으로 남길 수 있는가

## 4. 무엇을 바꿨는가

### 4.1 renderer 확장

- `services/worker/renderers/media.py`
  - 기존 static concat renderer를 `_render_static_video`로 분리했습니다.
  - `push_in_center`, `push_in_top`, `push_in_bottom` preset을 쓰는 `ffmpeg zoompan` clip renderer를 추가했습니다.
  - `render_video(..., motion_presets=...)` 시그니처로 확장해서, 동일 API에서 static/motion 두 경로를 모두 처리하게 만들었습니다.

### 4.2 generation pipeline 연결

- `services/worker/pipelines/generation.py`
  - `_resolve_renderer_motion_presets()`를 추가했습니다.
  - 현재는 `style_id == "b_grade_fun"`인 경우에만 motion preset을 붙입니다.
  - detail scene은 보수적으로 `push_in_top`, hero scene은 `push_in_center`를 기본값으로 사용합니다.
  - `render-meta.json`에 아래 필드를 남기도록 했습니다.
    - `rendererMotionMode`
    - `rendererMotionPresets`

### 4.3 테스트 추가

- `services/worker/tests/test_media_renderer.py`
  - motion preset을 넣은 `render_video()` 단위 테스트를 추가했습니다.
- `services/worker/tests/test_generation_pipeline.py`
  - friendly 기본 경로가 여전히 `static_concat`으로 남는지 검증을 추가했습니다.
  - `T02`, `T04`의 `b_grade_fun` 기본 motion preset 매핑도 테스트로 고정했습니다.

## 5. 검증

### 5.1 정적 검증

```bash
python -m py_compile services/worker/renderers/media.py services/worker/pipelines/generation.py services/worker/tests/test_generation_pipeline.py services/worker/tests/test_media_renderer.py
```

### 5.2 테스트 실행

```bash
uv run --project services/worker pytest services/worker/tests/test_media_renderer.py services/worker/tests/test_generation_pipeline.py -q
```

- 결과: `23 passed`

### 5.3 실제 generation sample

- `T02 / promotion / b_grade_fun` 조건으로 worker generation job을 실제로 한 번 생성했습니다.
- sample summary:
  - `docs/experiments/artifacts/exp-231-b-grade-renderer-motion-bridge/sample-summary.json`
- sample 결과 핵심:
  - `rendererMotionMode = "zoompan_control"`
  - `rendererMotionPresets = ["push_in_center", "push_in_top", "push_in_top", "push_in_center"]`

## 6. 결과 해석

1. `EXP-230`에서 확인한 motion uplift가 이제 benchmark 전용 코드가 아니라 실제 renderer 경로에도 연결됐습니다.
2. non-`b_grade_fun` 경로는 그대로 static concat으로 유지돼, 기존 `friendly` baseline을 건드리지 않았습니다.
3. 따라서 현재 저장소 기준 본선 영상 baseline은 `b_grade_fun에서는 deterministic zoompan uplift`, 그 외 style은 기존 static renderer로 해석하는 편이 맞습니다.

## 7. 현재 한계

1. 지금 preset 매핑은 아직 `asset lane classifier`나 `prepare_mode`를 쓰지 않는 generic baseline입니다.
2. 즉 `맥주 bottom-heavy`, `tray/full-plate center` 같은 세밀한 규칙은 아직 본선 renderer까지는 안 들어갔습니다.
3. 따라서 이번 작업은 `motion renderer bridge 완료`이지, `shot-aware product control 완성`은 아닙니다.

## 8. 결론

- 이번 작업은 `성공`입니다.
- 이제 `product_control_motion` 계열 판단을 실제 worker pipeline 기준으로도 이어갈 수 있게 됐습니다.
- 다음 우선순위는 새 모델을 더 붙이는 것보다, 이 generic motion baseline이 실제 샘플군에서 어디까지 먹히는지 확인하고, 필요하면 lane-aware preset으로 한 단계 더 세분화하는 쪽이 맞습니다.

## 9. 다음 액션

1. 실제 샘플 자산으로 `T02`, `T04` 결과물을 몇 개 더 뽑아 contact sheet 기준으로 확인합니다.
2. `tray/full-plate`, `glass drink`, `bottle+glass`를 구분하는 lightweight preset selector가 필요한지 검토합니다.
3. Sora/Veo류 비교는 계속 upper-bound reference로만 두고, 현재 본선 baseline은 이 renderer 경로를 기준으로 평가합니다.
