# EXP-245 Hybrid Generation Pipeline Spike

## 1. 기본 정보

- 실험 ID: `EXP-245`
- 작성일: `2026-04-14`
- 작성자: Codex
- 관련 기능: `generated source mp4를 generation pipeline에 연결하고 template overlay packaging으로 끝까지 렌더링하는 spike`

## 2. 왜 이 작업을 했는가

- `EXP-244`까지로 renderer 레벨의 hybrid bridge는 준비됐지만, 실제 generation pipeline은 여전히 `scene image -> renderer concat` 경로만 사용하고 있었습니다.
- 즉 방향성은 맞아도, 서비스 코드 본선에서 `generated mp4를 받아 광고 결과물로 끝내는 최소 경로`는 아직 없었습니다.
- 이번 작업의 목적은 새 모델 실험이 아니라, 현재 확인된 hybrid 방향을 실제 pipeline 입구에 연결해 `서비스 경로에서 재현 가능한가`를 확인하는 것이었습니다.

## 3. 이번에 바꾼 것

### 3.1 generation pipeline 입구 추가

- `services/worker/pipelines/generation.py`
  - `input_snapshot_json.hybridSourceVideoPath`를 읽어 source mp4를 받을 수 있게 했습니다.
  - hybrid source가 있으면 scene별 full image 대신 `scene overlay PNG`를 만들고, 최종 렌더링은 `render_hybrid_video()`로 우회하도록 연결했습니다.
  - `render-meta.json`에 아래 정보를 추가했습니다.
    - `rendererVideoSourceMode=hybrid_generated_clip`
    - `rendererMotionMode=hybrid_overlay_packaging`
    - `rendererHybridSourceVideo`
    - `rendererHybridDurationStrategy`
    - `rendererHybridTargetDurationSec`
    - `rendererHybridOverlayTimeline`

### 3.2 길이 mismatch 보정

- 첫 구현 직후 실제 spike를 돌려보니 source video는 약 `4.3초`, `T02` 템플릿은 `6.4초`라서 뒤쪽 `PERIOD/CTA` overlay가 잘리는 문제가 확인됐습니다.
- 이를 막기 위해 `services/worker/renderers/media.py`의 `render_hybrid_video()`에서 source가 더 짧으면 마지막 프레임을 hold 하는 `freeze_last_frame` 전략을 추가했습니다.
- 즉 source generated clip 길이가 템플릿보다 짧아도, template timeline 전체가 광고 형식으로 끝나도록 보정했습니다.

### 3.3 테스트 및 스파이크 스크립트 추가

- `services/worker/tests/test_generation_pipeline.py`
  - hybrid source video를 넣었을 때 generation pipeline이 실제 variant를 만들고, hybrid renderer meta를 남기며, 최종 영상 길이가 템플릿 길이에 맞춰 늘어나는지 검증했습니다.
- `services/worker/tests/test_media_renderer.py`
  - `render_hybrid_video()`가 overlay end time까지 실제 mp4를 유지하는지 duration probe를 추가했습니다.
- `scripts/run_hybrid_generation_pipeline_spike.py`
  - sample image + source mp4를 stage한 뒤 generation job을 끝까지 실행하고 summary artifact를 남기는 재현 스크립트를 추가했습니다.
  - 같은 artifact 폴더에서 반복 실행해도 깨지지 않도록 runtime dir 초기화도 넣었습니다.

### 3.4 결과 surface 연결

- `services/api/app/services/runtime.py`
  - result payload에 `rendererSummary`를 추가해 `videoSourceMode`, `motionMode`, `framingMode`, `durationStrategy`, `targetDurationSec`를 직접 내려주도록 했습니다.
- `packages/contracts/schemas/generation.ts`
  - `ProjectResultResponse.rendererSummary` 타입을 추가했습니다.
- `apps/web/src/components/result-media-preview.tsx`
  - 결과 카드 상단에 renderer summary badge를 노출해, 지금 보고 있는 결과가 `scene_image_render`인지 `hybrid_generated_clip`인지 바로 구분할 수 있게 했습니다.

## 4. 실행 및 검증

### 4.1 정적 검증

```bash
python -m py_compile services/worker/renderers/media.py services/worker/pipelines/generation.py services/worker/tests/test_media_renderer.py services/worker/tests/test_generation_pipeline.py scripts/run_hybrid_generation_pipeline_spike.py
```

### 4.2 테스트

```bash
uv run --project services/worker pytest services/worker/tests/test_media_renderer.py services/worker/tests/test_generation_pipeline.py -q
```

결과:

- `25 passed`

### 4.3 API 및 web surface 검증

```bash
python -m py_compile services/api/app/schemas/api.py services/api/app/services/runtime.py services/api/tests/test_api_smoke.py
uv run --project services/api pytest services/api/tests/test_api_smoke.py -q
npm run build:web
```

결과:

- API smoke `5 passed`
- `next build` 성공

### 4.4 pipeline spike 실행

```bash
python scripts/run_hybrid_generation_pipeline_spike.py
```

## 5. 결과

artifact root:

- `docs/experiments/artifacts/exp-245-hybrid-generation-pipeline-spike/`

대표 수치:

- source generated clip duration: 약 `4.3초`
- template target duration: `6.4초`
- final hybrid output duration: `6.3초`
- duration strategy: `freeze_last_frame`

### 5.1 코드 관점 결과

1. 이제 generation pipeline은 `hybridSourceVideoPath`만 주어지면 generated mp4를 실제 서비스 결과물 패키징 경로로 넘길 수 있습니다.
2. hybrid 여부와 overlay timeline이 모두 `render-meta.json`에 남기 때문에, 이후 결과 화면/히스토리/디버깅 쪽 연동 근거도 생겼습니다.
3. renderer 차원의 spike가 pipeline spike로 이어졌기 때문에, 이제 이 방향은 문서상 제안이 아니라 실제 코드 경로가 됐습니다.
4. 또한 result payload와 web surface에서도 renderer 경로를 직접 읽을 수 있게 되어, hybrid/non-hybrid 결과를 사람이 다시 meta 파일로 추적하지 않아도 됩니다.

### 5.2 산출물 관점 결과

1. 최종 output은 `HOOK -> BENEFIT -> PERIOD -> CTA` 순서의 overlay를 끝까지 보여줄 수 있게 됐습니다.
2. source clip motion 자체가 좋아진 것은 아니지만, 서비스 결과물 기준으로는 `그냥 generated video`보다 `템플릿 광고물`로 읽히는 속도가 훨씬 빨라졌습니다.
3. 즉 이 spike의 가치는 generation quality 개선이 아니라 `service packaging 레이어를 generated video에도 적용 가능하게 만든 것`에 있습니다.

## 6. 해석

1. 지금까지의 video lane에서 막힌 지점은 `모델이 완전히 쓸 수 없어서`만이 아니라, `좋은 clip이 나와도 서비스 결과물 문법으로 마무리하는 경로가 약했다`는 점도 있었습니다.
2. 이번 작업으로 그 약점은 일부 해소됐습니다. 이제 generated clip quality와 service packaging quality를 분리해서 다룰 수 있습니다.
3. 다만 이 경로는 `품질 대체재`가 아니라 `품질 증폭기`에 가깝습니다. source clip이 너무 어색하면 overlay를 얹어도 본질적 한계는 남습니다.

## 7. 결론

- `hybrid generated clip + template overlay`는 현재 저장소 기준으로 실험이 아니라 `실제 pipeline baseline 후보`가 됐습니다.
- 특히 source clip이 template보다 짧아도 광고 형식이 끝까지 보이도록 보정한 점이 중요합니다.
- 따라서 다음 active 우선순위는 `새 phrase 실험`보다 `어떤 source clip을 hybrid lane에 태울 것인가`와 `결과 화면에서 이 경로를 어떻게 드러낼 것인가`입니다.

## 8. 다음 액션

1. `video_upper_bound_benchmark` 산출물 중 hybrid lane에 태울 후보 clip을 선별하는 기준을 문서화합니다.
2. 결과 화면 또는 run summary에서 `rendererVideoSourceMode=hybrid_generated_clip`을 구분 표시합니다.
3. source clip이 너무 정적일 때는 hybrid lane에 태우지 않도록 최소 quality gate를 붙일지 검토합니다.

## 9. 대표 artifact

- `docs/experiments/artifacts/exp-245-hybrid-generation-pipeline-spike/summary.json`
- `docs/experiments/artifacts/exp-245-hybrid-generation-pipeline-spike/hybrid_pipeline_contact_sheet_7up.png`
- `docs/experiments/artifacts/exp-245-hybrid-generation-pipeline-spike/runtime/storage/projects/.../video.mp4`
