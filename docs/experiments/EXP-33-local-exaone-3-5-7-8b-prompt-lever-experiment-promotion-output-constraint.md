# EXP-33 Local EXAONE 3.5 7.8B Prompt Lever Experiment - Promotion Output Constraint

## 1. 기본 정보

- 실험 ID: `EXP-33`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `로컬 EXAONE 프롬프트 레버 실험`

## 2. 왜 이 작업을 했는가

- `EXP-31`에서 `region_repeat_constraint`는 실패했습니다.
- 하지만 `EXAONE 3.5 7.8B` 자체는 한국어 톤이 가장 자연스러워서 버릴 카드가 아니었습니다.
- 따라서 이번에는 같은 모델을 고정한 채, `output constraint` 한 레버만 넣어 길이/CTA/형식 안정성이 좋아지는지 확인했습니다.

## 3. baseline

### 고정한 조건

1. 시나리오: `T02 / promotion / b_grade_fun`
2. 모델: `ollama:exaone3.5:7.8b`
3. 자산: `규카츠`, `맥주` 실제 사진
4. 바뀐 변수: `slot_guidance`의 `output_constraint`만 변경

### 비교 대상

- deterministic reference
- baseline: `fixed_b_grade_tone_guidance_local_ollama`
- variant: `promotion_render_ready_output_constraint_local_exaone`

## 4. 무엇을 바꿨는가

- `services/worker/experiments/prompt_harness.py`
  - `EXP-33` 정의 추가
  - variant에 아래 output constraint만 추가
    - hook/benefit/urgency 16자 안팎
    - product_name 14자 안팎
    - ctaText/cta 10자 안팎 + 행동 키워드 시작
    - captions 정확히 3개, 각 28자 이하
    - hashtags 정확히 5개
    - 이모지/장식 기호 금지
- `services/worker/tests/test_prompt_harness.py`
  - `EXP-33` 정의 테스트 추가

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-33-local-exaone-3-5-7-8b-prompt-lever-experiment-promotion-output-constraint.json`

### baseline 대비 차이

- baseline
  - region repeat count: `4`
  - over-limit scenes: `s1`, `s2`
  - hashtags: `6개`
  - CTA: `지금 방문하세요!`
- variant
  - region repeat count: `4`
  - over-limit scenes: `s2`, `s3`
  - hashtags: `5개`
  - CTA: `주문하기`

### 확인된 것

1. `output constraint`는 일부 format 품질에는 효과가 있었습니다.
   - hashtags가 `6개 -> 5개`로 정리됐습니다.
   - opening headline 길이는 `19 -> 14`자로 줄었습니다.
   - CTA도 더 짧고 직접적으로 정리됐습니다.
2. 하지만 핵심 정책 위반인 `region_repeat`는 줄지 않았습니다.
3. `korean_integrity` 기준으로는 baseline/variant 모두 한글 깨짐 징후가 없었습니다.

## 6. 실패/제약

1. 이번 레버는 **부분 성공**입니다.
2. format/readability는 조금 나아졌지만 score는 `92.9`로 그대로였고, region policy는 여전히 실패했습니다.
3. 즉 `EXAONE 3.5 7.8B`에서는 `output_constraint` 하나만으로는 전체 품질 승격이 부족합니다.

## 7. 결론

- 가설 충족 여부: **부분 충족**
- 판단:
  - `output constraint`는 로컬 EXAONE의 문구 길이와 형식 정리에 도움이 됩니다.
  - 그러나 다음 핵심 레버는 `region repeat`를 직접 겨냥하는 phrasing보다 `hashtag rule` 또는 `caption region budget`처럼 더 구조적인 제약이어야 합니다.

## 8. 다음 액션

1. 다음은 `EXAONE 3.5 7.8B`를 고정하고 `hashtag rule` 한 레버를 분리해 봅니다.
2. 또는 같은 output constraint를 `Gemma3 12B`에도 붙여 로컬 멀티모달 후보와 비교합니다.
