# EXP-25 Service-Aligned Promotion OpenAI-Available Model Comparison

## 1. 기본 정보

- 실험 ID: `EXP-25`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `cross-provider model-only comparison`

## 2. 왜 이 작업을 했는가

- 사용 가능한 OpenAI 모델 범위가 `gpt-5-mini`, `gpt-5-nano`로 확인되었고, 기존 `EXP-23`의 `gpt-4.1-mini`는 현재 계정 기준 비교 대상이 아니었습니다.
- 사용자 요청대로 `Gemma 4` 단일 기준에 고정하지 않고, 실제 사용 가능한 멀티모델 비교를 계속 가져가야 했습니다.
- 동시에 `repo 루트 .env.local`을 실험 경로에서 직접 읽도록 바꿨기 때문에, 새로 넣은 OpenAI key가 실제 harness에서 먹는지도 확인할 필요가 있었습니다.

## 3. baseline

### 고정한 조건

1. 시나리오: `T02 / promotion / b_grade_fun / 실제 음식 사진`
2. 프롬프트: `EXP-15`에서 효과가 좋았던 `B급 tone guidance`
3. 바뀐 변수: `모델`만 변경

### 비교 대상

- deterministic reference
- `models/gemma-4-31b-it`
- `gpt-5-mini`
- `gpt-5-nano`

## 4. 무엇을 바꿨는가

- `services/common/env_loader.py`
  - `HF_TOKEN`/`HUGGINGFACE_HUB_TOKEN`
  - `LANGFUSE_BASE_URL`/`LANGFUSE_HOST`
  - alias 처리 추가
- `services/worker/experiments/prompt_harness.py`
  - `EXP-25` model comparison 정의 추가
  - OpenAI Responses API 요청에서 `temperature`, `top_p` 제거
  - `reasoning.effort=minimal`, `text.format=json_object`, `verbosity=low` 적용
- `services/worker/tests/test_env_loader.py`
  - env alias 테스트 추가
- `services/worker/tests/test_prompt_harness.py`
  - `EXP-25` 정의 테스트 추가

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-25-service-aligned-promotion-openai-available-model-comparison.json`

### 결과 요약

- deterministic reference
  - score: `92.9`
  - 문제: 지역 반복 초과, scene text 과긴
- `models/gemma-4-31b-it`
  - score: `100.0`
  - 장점: scene 길이 안정적, 실패 체크 없음
  - 제약: 응답 시간이 가장 길었음
- `gpt-5-mini`
  - score: `100.0`
  - 장점: 응답 속도가 Gemma 4보다 빠름
  - 제약: `s2` 한 scene가 text budget 초과
- `gpt-5-nano`
  - score: `100.0`
  - 장점: 가장 빠름
  - 제약: `s1~s4` 전 scene가 text budget 초과

### 확인된 것

1. 새 `.env.local` 기반 OpenAI key는 실제 harness에서 정상 동작했습니다.
2. `gpt-5-mini`는 현재 계정에서 비교 가능한 OpenAI 후보로 유지할 가치가 있습니다.
3. `gpt-5-nano`는 속도는 좋지만 render-readiness 기준에서는 너무 긴 편입니다.
4. 현재 기준으로는 `Gemma 4 = 안정성 우위`, `gpt-5-mini = 속도와 품질의 타협 후보`, `gpt-5-nano = 저비용 초안 후보`로 정리하는 편이 맞습니다.

## 6. 실패/제약

1. 첫 시도에서는 `temperature` 파라미터 미지원으로 OpenAI 두 모델이 모두 실패했습니다.
2. 이를 수정한 뒤에는 실행되었지만, `gpt-5-mini`와 `gpt-5-nano` 모두 scene budget 안정성은 Gemma 4보다 약했습니다.
3. 이번 비교도 단일 실행 1회라 재현성은 더 봐야 합니다.

## 7. 결론

- 가설 충족 여부: **부분 충족**
- 판단:
  - `Gemma 4`만 보지 말자는 방향은 맞습니다.
  - 다만 현재 사용 가능한 모델 범위 안에서, `gpt-5-mini`는 실전 후보가 될 수 있지만 `gpt-5-nano`는 바로 production baseline으로 쓰기 어렵습니다.
  - 따라서 다음 baseline 후보는 `Gemma 4`와 `gpt-5-mini` 두 축으로 가져가고, `gpt-5-nano`는 저비용 preview용으로 보는 게 맞습니다.

## 8. 다음 액션

1. `T04 review` 축에서도 `Gemma 4` vs `gpt-5-mini`를 같은 방식으로 비교합니다.
2. `gpt-5-mini`의 scene budget 초과를 줄이기 위해 output constraint 한 레버를 분리합니다.
3. Hugging Face token을 활용한 오픈소스 비교 경로는 별도 provider bridge로 설계합니다.
