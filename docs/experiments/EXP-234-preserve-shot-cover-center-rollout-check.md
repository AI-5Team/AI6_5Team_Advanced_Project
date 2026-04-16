# EXP-234 Preserve Shot Cover Center Rollout Check

## 1. 기본 정보

- 실험 ID: `EXP-234`
- 작성일: `2026-04-14`
- 작성자: Codex
- 관련 기능: `preserve_shot policy rollout / production renderer verification`

## 2. 왜 이 작업을 했는가

- `EXP-233`에서 `preserve_shot` 기본 framing은 `contain_blur`보다 `cover_center`가 낫다는 결론이 나왔습니다.
- 따라서 결론이 bench용 비교에만 머물지 않도록, 실제 `services/worker` renderer에 정책을 반영한 뒤 rollout check를 한 번 더 수행했습니다.

## 3. 반영 내용

- `services/worker/pipelines/generation.py`
  - `preserve_shot`
    - 기본 scene: `cover_center + push_in_center`
    - detail scene: `cover_center + push_in_top`
    - `period` scene: `cover_top + push_in_top`

## 4. 검증

### 4.1 코드 검증

```bash
python -m py_compile services/worker/pipelines/generation.py services/worker/tests/test_generation_pipeline.py
uv run --project services/worker pytest services/worker/tests/test_media_renderer.py services/worker/tests/test_generation_pipeline.py -q
```

- 결과: `23 passed`

### 4.2 실제 샘플 rollout

- 샘플군
  - `라멘`
  - `순두부짬뽕`
  - `장어덮밥`
  - `귤모찌`
- 실행 조건
  - `T02 / promotion / b_grade_fun`
- artifact root
  - `docs/experiments/artifacts/exp-234-preserve-shot-cover-center-rollout-check/`

## 5. 핵심 결과

1. 네 샘플 모두 `rendererScenePolicies`에 `cover_center` 중심 preserve policy가 정상 기록됐습니다.
2. `라멘`
   - `s1/s2/s4 cover_center`
   - `s3 cover_top`
3. `장어덮밥`
   - tray blur 배경 없이 메뉴 중심성이 더 직접적으로 보였습니다.
4. `순두부짬뽕`
   - 붉은 국물과 토핑이 더 안정적으로 보이고, blur backdrop 위화감이 사라졌습니다.
5. `귤모찌`
   - 소형 디저트 샷에서도 제품이 더 또렷하게 읽혔습니다.

## 6. 결론

- rollout check 결과는 `긍정적`입니다.
- 따라서 현재 본선 `b_grade_fun` renderer의 preserve lane은 `cover_center`를 기본값으로 유지하는 편이 맞습니다.
- 이로써 현재 본선 baseline은 아래처럼 정리됩니다.
  - `tray_full_plate -> cover_center`
  - `glass_drink_candidate top-heavy -> cover_top`
  - `glass_drink_candidate bottom-heavy -> cover_bottom`
  - `preserve_shot -> cover_center`

## 7. 다음 액션

1. 이제 renderer baseline 쪽에서 급한 미해결 축은 크게 줄었습니다.
2. 다음 질문은 새 모델 추가보다, `T04 / review / b_grade_fun`에도 현재 shot-aware policy를 그대로 유지할지 확인하는 쪽입니다.

## 8. 대표 artifact

- `docs/experiments/artifacts/exp-234-preserve-shot-cover-center-rollout-check/summary.json`
- `docs/experiments/artifacts/exp-234-preserve-shot-cover-center-rollout-check/라멘/contact_sheet.png`
- `docs/experiments/artifacts/exp-234-preserve-shot-cover-center-rollout-check/순두부짬뽕/contact_sheet.png`
- `docs/experiments/artifacts/exp-234-preserve-shot-cover-center-rollout-check/장어덮밥/contact_sheet.png`
- `docs/experiments/artifacts/exp-234-preserve-shot-cover-center-rollout-check/귤모찌/contact_sheet.png`
