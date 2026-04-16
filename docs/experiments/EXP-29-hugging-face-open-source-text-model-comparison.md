# EXP-29 Hugging Face Open-Source Text Model Comparison

## 1. 기본 정보

- 실험 ID: `EXP-29`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `Hugging Face` 오픈소스 모델 비교

## 2. 왜 이 작업을 했는가

- 다음 우선순위는 `HF_TOKEN`을 실제로 쓰는 오픈소스 비교 경로를 여는 것이었습니다.
- 현재 환경에서는 Hugging Face router가 provider별로 접근 차단/timeout 편차가 있어, 먼저 “실제로 통과하는 오픈소스 모델”이 누구인지 확인하는 단계가 필요했습니다.

## 3. baseline

### 고정한 조건

1. 시나리오: `T02 / promotion / b_grade_fun`
2. 프롬프트: `B급 tone guidance`
3. 바뀐 변수: `모델`만 변경

### 비교 대상

- deterministic reference
- `Qwen/Qwen3-4B-Instruct-2507`
- `Qwen/Qwen3.5-27B`

### 제약

- 이번 Hugging Face 경로는 `text-only`입니다.
- 즉 이미지 바이트는 보내지 않고, 업종/목적/스타일/자산 파일명만 근거로 copy를 생성했습니다.

## 4. 무엇을 바꿨는가

- `services/worker/experiments/prompt_harness.py`
  - `huggingface` provider 추가
  - `HF_TOKEN`/`HUGGINGFACE_HUB_TOKEN` 사용
  - `EXP-29` model comparison 정의 추가
- `services/worker/tests/test_prompt_harness.py`
  - `EXP-29` 정의 테스트 추가

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-29-hugging-face-open-source-text-model-comparison.json`

### 결과 요약

- deterministic reference
  - score: `92.9`
  - 문제: 지역 반복 초과, scene 길이 초과
- `Qwen/Qwen3-4B-Instruct-2507`
  - score: `92.9`
  - 장점: 응답 속도 빠름, JSON 형식은 통과
  - 제약: 지역 반복 초과, `s1`, `s2` 길이 초과
- `Qwen/Qwen3.5-27B`
  - score: `0.0`
  - 결과: provider timeout

### 확인된 것

1. `HF_TOKEN` 기반 오픈소스 비교 경로는 실제로 열렸습니다.
2. `Qwen/Qwen3-4B-Instruct-2507`는 현재 환경에서 실제로 돌아가는 오픈소스 후보입니다.
3. `Qwen/Qwen3.5-27B`는 이번 환경에서 provider timeout이 발생해 실험 후보로 쓰기 어렵습니다.

## 6. 실패/제약

1. 이번 경로는 `text-only`라서 multimodal 비교는 아닙니다.
2. Hugging Face router는 모델마다 backend provider가 달라 접근 차단/timeout 편차가 있습니다.
3. 따라서 “모델 품질”과 “provider 접근성”이 완전히 분리되지 않았습니다.

## 7. 결론

- 가설 충족 여부: **부분 충족**
- 판단:
  - Hugging Face 오픈소스 비교 경로를 연 것 자체는 의미가 있습니다.
  - 다만 현재 usable 후보는 `Qwen/Qwen3-4B-Instruct-2507` 정도이며, 더 큰 모델은 provider timeout으로 바로 실험군에 올리기 어렵습니다.
  - 즉 지금은 “오픈소스 축이 가능함”까지 확인했고, 다음은 작동하는 후보를 더 찾는 단계입니다.

## 8. 다음 액션

1. 다음은 `Qwen/Qwen3-4B-Instruct-2507`를 기준으로 output constraint를 한 번 더 붙여 봅니다.
2. 동시에 Hugging Face에서 실제 통과하는 다른 오픈소스 text 모델을 한두 개 더 발굴합니다.
3. multimodal 오픈소스 비교는 provider 접근성 문제를 먼저 해결한 뒤 다시 시도합니다.
