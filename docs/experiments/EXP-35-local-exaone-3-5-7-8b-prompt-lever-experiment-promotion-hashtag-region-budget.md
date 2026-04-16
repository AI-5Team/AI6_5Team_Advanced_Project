# EXP-35 Local EXAONE 3.5 7.8B Prompt Lever Experiment - Promotion Hashtag Region Budget

## 1. 기본 정보

- 실험 ID: `EXP-35`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `로컬 EXAONE 프롬프트 레버 실험`

## 2. 왜 이 작업을 했는가

- `EXP-33`에서 `output constraint`는 형식 정리에는 일부 효과가 있었지만 `region repeat`는 줄이지 못했습니다.
- 따라서 같은 모델을 고정한 채, 이번에는 `hashtag/caption region budget` 한 레버만 추가해 지역 반복을 직접 줄일 수 있는지 확인했습니다.

## 3. baseline

### 고정한 조건

1. 시나리오: `T02 / promotion / b_grade_fun`
2. 모델: `ollama:exaone3.5:7.8b`
3. 자산: `규카츠`, `맥주` 실제 사진
4. 바뀐 변수: `slot_guidance`의 `hashtag/caption region budget`만 변경

### 비교 대상

- deterministic reference
- baseline: `fixed_b_grade_tone_guidance_local_ollama`
- variant: `promotion_hashtag_region_budget_local_exaone`

## 4. 무엇을 바꿨는가

- `services/worker/experiments/prompt_harness.py`
  - `EXP-35` 정의 추가
  - variant에 아래 규칙만 추가
    - 지역명 총 2회 이하
    - hookText 지역명 최대 1회
    - captions 3개에는 지역명 금지
    - hashtags는 5개, 지역명이 들어간 해시태그는 최대 1개
- `services/worker/tests/test_prompt_harness.py`
  - `EXP-35` 정의 테스트 추가

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-35-local-exaone-3-5-7-8b-prompt-lever-experiment-promotion-hashtag-region-budget.json`

### baseline 대비 차이

- baseline
  - score: `100.0`
  - region repeat count: `3`
  - over-limit scenes: `s1`, `s2`
  - hashtags: `6개`
  - captions에 지역명: `1회`
- variant
  - score: `92.9`
  - region repeat count: `4`
  - over-limit scenes: `s1`, `s2`, `s3`
  - hashtags: `5개`
  - captions에 지역명: `1회`

### 확인된 것

1. `hashtag/caption region budget` 레버는 이번 EXAONE baseline을 개선하지 못했습니다.
2. variant는 hashtags 개수는 `6개 -> 5개`로 맞췄지만, 오히려 지역명 해시태그가 늘어 `region repeat count`가 `3 -> 4`로 악화됐습니다.
3. `korean_integrity` 기준으로는 baseline/variant 모두 명백한 한글 깨짐은 없었습니다.

## 6. 실패/제약

1. 이번 레버는 **실패**입니다.
2. EXAONE 3.5 7.8B는 지역명 budget을 직접 적어도 그 규칙을 안정적으로 따르지 않았습니다.
3. baseline score가 높더라도 `scene_plan` 기준으로는 여전히 `over-limit`와 `closing_cta_actionable=false`가 남아 있어, harness score만으로 baseline 확정은 어렵습니다.

## 7. 결론

- 가설 충족 여부: **미충족**
- 판단:
  - EXAONE에서는 `hashtag/caption region budget` phrasing이 유효 레버가 아니었습니다.
  - 다음 EXAONE 개선은 프롬프트 한 줄을 더 세게 적는 방식보다, 후처리 guardrail 또는 별도 caption/hashtag 정규화 단계가 더 적절합니다.

## 8. 다음 액션

1. EXAONE는 `caption region budget` 단독 레버보다 `후처리 guardrail` 후보를 따로 검토합니다.
2. 텍스트 실험 우선순위는 `Gemma3 12B` 또는 `gpt-5-mini`와의 비교 쪽이 더 낫습니다.
3. 영상 쪽은 실제 `LTX-Video 2B / GGUF` 생성이 가능한지 먼저 확인합니다.
