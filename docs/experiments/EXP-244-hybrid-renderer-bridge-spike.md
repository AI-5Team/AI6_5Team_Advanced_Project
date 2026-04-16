# EXP-244 Hybrid Renderer Bridge Spike

## 1. 기본 정보

- 실험 ID: `EXP-244`
- 작성일: `2026-04-14`
- 작성자: Codex
- 관련 기능: `generated clip + template overlay를 서비스 renderer 레벨로 올리는 bridge spike`

## 2. 왜 이 작업을 했는가

- `EXP-243`에서 하이브리드 packaging 방향 자체는 맞다는 것을 확인했지만, 그 시점 구현은 proof script 내부 로직에 머물러 있었습니다.
- 다음 단계로 가려면 이 경로가 `실험용 일회성 스크립트`가 아니라 `services/worker/renderers`에서 재사용 가능한 함수가 되어야 합니다.
- 이번 작업의 목적은 generation pipeline 전체를 바꾸는 것이 아니라, `generated mp4를 scene background로 패키징할 수 있는 최소 renderer bridge`를 실제 코드로 추가하고 검증하는 것입니다.

## 3. 이번에 바꾼 것

### 3.1 renderer 유틸 추가

- `services/worker/renderers/media.py`
  - `create_scene_overlay_image()`
    - scene image 전체를 다시 만드는 대신, transparent overlay만 독립적으로 생성하는 함수
  - `render_hybrid_video()`
    - source video 위에 overlay PNG 여러 장을 시간대별로 얹어 하이브리드 mp4를 렌더링하는 함수
    - source audio가 있으면 같이 보존하도록 `0:a?` 매핑도 포함

### 3.2 proof script 정리

- `scripts/generated_video_hybrid_packaging_proof.py`
  - 자체 ffmpeg/overlay 로직을 제거하고, 위 renderer 유틸을 직접 사용하도록 정리했습니다.
  - 즉 하이브리드 proof도 이제 service renderer 코드를 통하게 됐습니다.

### 3.3 테스트 추가

- `services/worker/tests/test_media_renderer.py`
  - `render_hybrid_video()`가 실제 generated clip 유사 소스 위에 overlay를 얹어 mp4를 만들 수 있는지 검증하는 테스트를 추가했습니다.

## 4. 실행 및 검증

### 4.1 정적 검증

```bash
python -m py_compile services/worker/renderers/media.py services/worker/tests/test_media_renderer.py scripts/generated_video_hybrid_packaging_proof.py
```

### 4.2 테스트

```bash
uv run --project services/worker pytest services/worker/tests/test_media_renderer.py -q
```

결과:

- `2 passed`

### 4.3 renderer utility 기반 proof rerun

```bash
python scripts/generated_video_hybrid_packaging_proof.py --experiment-id EXP-244-hybrid-renderer-bridge-spike --source-video "docs/experiments/artifacts/exp-241-sora2-gyukatsu-input-framing-live-ovaat/baseline_auto/규카츠/sora2_first_try.mp4" --output-dir "docs/experiments/artifacts/exp-244-hybrid-renderer-bridge-spike"
```

## 5. 결과

artifact root:

- `docs/experiments/artifacts/exp-244-hybrid-renderer-bridge-spike/`

### 5.1 코드 관점 결과

1. 이제 하이브리드 packaging은 proof script 전용 로직이 아니라 `services/worker/renderers/media.py`의 재사용 가능한 함수가 됐습니다.
2. 즉 다음 단계에서 generation pipeline 쪽이 source mp4를 받기만 하면, 같은 유틸로 overlay packaging을 바로 태울 수 있습니다.

### 5.2 산출물 관점 결과

1. `hybrid_packaged.mp4`는 raw generated clip 위에 `HOOK`, `DETAIL`, `CTA`를 순차적으로 얹은 형태로 정상 생성됐습니다.
2. `hybrid_contact_sheet_8up.png` 기준으로도 raw clip보다 광고 문법이 더 빨리 읽히고, 서비스 결과물 느낌이 더 분명해졌습니다.
3. 즉 `generated clip + template overlay` 방향은 단순 아이디어가 아니라, 현재 저장소 코드 경로로 재현 가능한 spike가 됐습니다.

## 6. 해석

1. 지금까지의 실험에서 `prompt`, `framing`, `edit`는 모두 생성 품질 trade-off 안에서 흔들렸습니다.
2. 반면 하이브리드 packaging은 생성 품질을 완전히 해결하지는 않더라도, 서비스 적합성을 다른 레이어에서 안정적으로 끌어올릴 수 있습니다.
3. 이번 spike로 그 레이어가 `실험 문서 상의 제안`이 아니라 `코드에 들어간 renderer capability`로 바뀌었습니다.

## 7. 결론

- 이번 작업의 결론은 `hybrid packaging`이 이제 실제 본선 bridge 후보가 됐다는 것입니다.
- 아직 generation pipeline이 source mp4를 직접 받지는 않지만, renderer 쪽 최소 기능은 갖춰졌습니다.
- 따라서 다음 구현 우선순위는 `새 모델 비교`보다 `source mp4를 pipeline에 연결하는 최소 입구`를 만드는 쪽입니다.

## 8. 다음 액션

1. generation pipeline에 `generated source video` 입력을 받을 수 있는 spike 경로를 추가합니다.
2. `render-meta.json`에 hybrid source 사용 여부와 overlay timing을 기록합니다.
3. 그 다음에 `product_control_motion`과 `hybrid generated clip`을 같은 결과 화면에서 비교할 수 있게 연결합니다.

## 9. 대표 artifact

- `docs/experiments/artifacts/exp-244-hybrid-renderer-bridge-spike/summary.json`
- `docs/experiments/artifacts/exp-244-hybrid-renderer-bridge-spike/hybrid_packaged.mp4`
- `docs/experiments/artifacts/exp-244-hybrid-renderer-bridge-spike/hybrid_contact_sheet_8up.png`
