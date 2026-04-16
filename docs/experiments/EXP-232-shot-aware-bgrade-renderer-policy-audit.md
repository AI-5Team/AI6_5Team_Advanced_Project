# EXP-232 Shot-Aware B-Grade Renderer Policy Audit

## 1. 기본 정보

- 실험 ID: `EXP-232`
- 작성일: `2026-04-14`
- 작성자: Codex
- 관련 기능: `b_grade_fun shot-aware framing / prepare_mode bridge / motion preset bridge`

## 2. 왜 이 작업을 했는가

- `EXP-231`까지는 `b_grade_fun` 본선 renderer에 deterministic zoompan motion만 연결된 상태였습니다.
- 하지만 이 상태는 여전히 `맥주 = bottom-heavy`, `커피 = top-heavy`, `규카츠 = tray/full-plate` 같은 기존 실험 지식을 실제 renderer가 쓰지 못한다는 한계가 있었습니다.
- 즉 motion은 붙었지만, scene framing은 아직 generic center crop에 가까웠고, 이는 `EXP-230`에서 확보한 `prepare_mode / motion preset` 기준선과 완전히 일치하지 않았습니다.

## 3. 이번 작업 질문

1. shot classifier와 prepare mode policy를 `b_grade_fun` 본선 renderer에 안전하게 옮길 수 있는가
2. 음료/트레이/보존형 샷을 scene 단위로 다르게 다루는 것이 실제 생성 artifact에서도 확인되는가
3. preserve shot의 경우 `contain_blur`가 실제 결과물에서도 감당 가능한지 확인할 수 있는가

## 4. 무엇을 바꿨는가

### 4.1 pure-PIL framing helper 추가

- `services/worker/renderers/framing.py`
  - 기존 benchmark script가 쓰던 shot classifier를 `numpy` 없이 pure-PIL로 옮겼습니다.
  - 추가한 함수:
    - `extract_structure_features()`
    - `classify_shot_type()`
    - `choose_prepare_mode()`
    - `prepare_image()`

### 4.2 generation pipeline scene policy 연결

- `services/worker/pipelines/generation.py`
  - `_resolve_bgrade_scene_policy()`를 추가했습니다.
  - 현재 정책은 아래와 같습니다.
    - `glass_drink_candidate`
      - 기본은 `cover_top` 또는 `cover_bottom` anchor
      - `promotion.period` scene만 `cover_center + push_in_center`
    - `tray_full_plate`
      - 기본은 `cover_center + push_in_center`
      - `promotion.period` scene만 `cover_top + push_in_top`
    - `preserve_shot`
      - 기본은 `contain_blur`
      - detail scene은 `push_in_top`, hero/cta는 `push_in_center`
  - `b_grade_fun`에서는 preprocessed vertical derivative 대신, scene마다 `prepare_mode`를 적용한 base image를 만들어 쓰도록 변경했습니다.
  - `render-meta.json`에 아래 필드를 남기게 했습니다.
    - `rendererFramingMode`
    - `rendererScenePolicies`

## 5. 테스트

```bash
python -m py_compile services/worker/renderers/framing.py services/worker/pipelines/generation.py services/worker/tests/test_generation_pipeline.py services/worker/tests/test_media_renderer.py
uv run --project services/worker pytest services/worker/tests/test_media_renderer.py services/worker/tests/test_generation_pipeline.py -q
```

- 결과: `23 passed`

## 6. 실제 샘플 audit

### 6.1 샘플군

- `규카츠`
- `맥주`
- `커피`
- `라멘`

### 6.2 실행 조건

- template: `T02`
- purpose: `promotion`
- style: `b_grade_fun`
- artifact root:
  - `docs/experiments/artifacts/exp-232-shot-aware-bgrade-renderer-policy-audit/`

### 6.3 핵심 결과

#### 규카츠

- shot type: `tray_full_plate`
- scene policy:
  - `s1 cover_center + push_in_center`
  - `s2 cover_center + push_in_center`
  - `s3 cover_top + push_in_top`
  - `s4 cover_center + push_in_center`
- motion avg_rgb_diff: `14.93`

#### 맥주

- shot type: `glass_drink_candidate`
- scene policy:
  - `s1 cover_bottom + push_in_bottom`
  - `s2 cover_bottom + push_in_bottom`
  - `s3 cover_center + push_in_center`
  - `s4 cover_bottom + push_in_bottom`
- motion avg_rgb_diff: `9.71`

#### 커피

- shot type: `glass_drink_candidate`
- scene policy:
  - `s1 cover_top + push_in_top`
  - `s2 cover_top + push_in_top`
  - `s3 cover_center + push_in_center`
  - `s4 cover_top + push_in_top`
- motion avg_rgb_diff: `11.39`

#### 라멘

- shot type: `preserve_shot`
- scene policy:
  - `s1 contain_blur + push_in_center`
  - `s2 contain_blur + push_in_top`
  - `s3 contain_blur + push_in_top`
  - `s4 contain_blur + push_in_center`
- motion avg_rgb_diff: `11.54`

## 7. 해석

### 7.1 맞게 옮겨진 부분

1. `맥주`와 `커피`는 서로 다른 drink lane으로 실제로 분기됐습니다.
2. 즉 기존 실험에서 확인한 `bottom-heavy bottle+glass -> cover_bottom`, `top-heavy drink -> cover_top`이 본선 renderer에도 반영됐습니다.
3. `규카츠`는 tray/full-plate 규칙대로 center 중심으로 유지되면서, 한 scene만 top bias를 줘 템포를 만들었습니다.

### 7.2 남은 질문

1. `라멘`의 `contain_blur`는 보존성은 좋지만, contact sheet 기준으로는 배경 blur 존재감이 꽤 강합니다.
2. 즉 preserve lane에서는 `contain_blur`가 맞는지, 아니면 `cover_center` 보수 운용이 더 나은지 별도 확인이 필요합니다.
3. 따라서 이번 결과는 `drink/tray lane bridge는 성공`, `preserve lane은 추가 검토 필요`로 보는 편이 맞습니다.

## 8. 결론

- 이번 작업은 `부분 성공`입니다.
- 핵심 성과는, `EXP-230`과 그 이전 prepare-mode 실험선에서 확보한 지식을 실제 `b_grade_fun` renderer가 쓰기 시작했다는 점입니다.
- 특히 drink lane은 이제 generic center crop이 아니라 shot-aware framing/motion으로 올라왔습니다.
- 반면 preserve lane은 지금 policy가 너무 강한 blur를 만들 수 있어 다음 점검 대상입니다.

## 9. 다음 액션

1. `preserve_shot`에서 `contain_blur`와 `cover_center`를 직접 비교하는 소규모 OVAT를 진행합니다.
2. `T04 / review / b_grade_fun`에서도 같은 shot-aware policy가 과한지 확인합니다.
3. drink/tray lane은 현재 정책을 baseline으로 유지하고, 모델 비교는 계속 upper-bound reference에 한정합니다.

## 10. 대표 artifact

- `docs/experiments/artifacts/exp-232-shot-aware-bgrade-renderer-policy-audit/summary.json`
- `docs/experiments/artifacts/exp-232-shot-aware-bgrade-renderer-policy-audit/규카츠/contact_sheet.png`
- `docs/experiments/artifacts/exp-232-shot-aware-bgrade-renderer-policy-audit/맥주/contact_sheet.png`
- `docs/experiments/artifacts/exp-232-shot-aware-bgrade-renderer-policy-audit/커피/contact_sheet.png`
- `docs/experiments/artifacts/exp-232-shot-aware-bgrade-renderer-policy-audit/라멘/contact_sheet.png`
