# EXP-30 Local Ollama Model Comparison On 4080 Super

## 1. 기본 정보

- 실험 ID: `EXP-30`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `로컬 오픈소스 텍스트/멀티모달 모델 비교`

## 2. 왜 이 작업을 했는가

- 사용자는 `RTX 4080 Super 16GB / RAM 64GB` 환경에서 돌아가는 로컬 모델도 함께 보길 원했습니다.
- 특히 `Qwen` 계열은 한글이 가끔 깨진다는 사용자 선호/제약이 있어, 다른 로컬 후보를 실제로 돌려 보고 한글 안정성까지 같이 봐야 했습니다.
- 확인 결과 이 머신에는 이미 `Ollama`가 실행 중이었고, 다음 모델이 설치돼 있었습니다.
  - `gemma3:12b`
  - `exaone3.5:7.8b`
  - `llama3.1:8b`
  - `mistral-small3.1:24b-instruct-2503-q4_K_M`

## 3. baseline

### 고정한 조건

1. 시나리오: `T02 / promotion / b_grade_fun`
2. 자산: `docs/sample/음식사진샘플(규카츠).jpg`, `docs/sample/음식사진샘플(맥주).jpg`
3. 프롬프트: `B급 tone guidance`
4. 바뀐 변수: `모델`만 변경

### 비교 대상

- deterministic reference
- `ollama:gemma3:12b`
- `ollama:exaone3.5:7.8b`
- `ollama:llama3.1:8b`
- `ollama:mistral-small3.1:24b-instruct-2503-q4_K_M`

### 제약

1. `gemma3:12b`, `mistral-small3.1:24b-instruct-2503-q4_K_M`는 `vision` capability가 있어 이미지 바이트를 함께 보냈습니다.
2. `exaone3.5:7.8b`, `llama3.1:8b`는 text-only라서 자산 파일명과 고정 입력 조건만 근거로 작성했습니다.
3. 즉 이번 비교는 `멀티모달`과 `text-only`가 섞여 있어 완전히 공정한 비교는 아닙니다.

## 4. 무엇을 바꿨는가

- `services/worker/experiments/prompt_harness.py`
  - `ollama` provider 추가
  - `/api/show` 기반 capability 확인 추가
  - vision 가능 모델은 이미지 base64 전달, text-only 모델은 파일명 기반 text prompt로 분기
  - `korean_integrity` 지표 추가
  - `EXP-30` model comparison 정의 추가
- `scripts/run_model_comparison_experiment.py`
  - Windows 콘솔 인코딩 문제를 막기 위한 UTF-8 stdout 설정 추가
- `scripts/run_prompt_experiment.py`
  - 같은 이유로 UTF-8 stdout 설정 추가
- `services/worker/tests/test_prompt_harness.py`
  - `ollama` provider / `EXP-30` 정의 / 한글 무결성 heuristic 테스트 추가

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-30-local-ollama-model-comparison-on-4080-super.json`

### 결과 요약

| 모델 | latency | score | 핵심 결과 |
|---|---:|---:|---|
| deterministic | `0ms` | `92.9` | 지역 반복 초과, scene 길이 초과 |
| `gemma3:12b` | `13.9s` | `85.7` | 길이 안정성은 좋았지만 CTA 행동성 실패, 지역 반복 초과 |
| `exaone3.5:7.8b` | `12.9s` | `92.9` | 한글 자연스러움이 가장 좋았지만 지역 반복 과다, scene 길이 초과 |
| `llama3.1:8b` | `11.4s` | `71.4` | schema 안정성이 부족해 baseline 후보 탈락 |
| `mistral-small3.1:24b-instruct-2503-q4_K_M` | `35.6s` | `92.9` | 동작은 했지만 느리고 반복이 남음 |

### 한글 깨짐 점검

1. 새 `korean_integrity` heuristic 기준으로 4개 로컬 모델 모두 `contains_replacement_char=false`, `is_suspected_broken=false`였습니다.
2. 결과 문구를 수동으로 spot-check 했을 때도 이번 샘플에서는 `Qwen`에서 우려했던 수준의 한글 깨짐은 보이지 않았습니다.
3. 다만 이 지표는 `�`, `Ã`, `ì` 같은 명백한 mojibake만 잡는 보수적 heuristic이라서, 앞으로도 수동 확인은 계속 병행해야 합니다.

### 확인된 것

1. 이 머신은 이미 설치된 `Ollama` 모델 기준으로 로컬 비교 실험을 바로 수행할 수 있습니다.
2. `EXAONE 3.5 7.8B`는 이번 비교군 중 한글 문장 톤이 가장 자연스러웠습니다.
3. `Gemma3 12B`는 vision 경로가 열려 있어 “로컬 멀티모달 후보”로는 가장 다루기 쉽습니다.
4. `Llama 3.1 8B`는 현재 JSON/schema 안정성이 약해 현재 harness 기준 baseline 후보가 아닙니다.

## 6. 실패/제약

1. `text-only`와 `vision` 모델이 섞인 비교라 성능 차이를 순수 모델 역량으로만 해석하면 안 됩니다.
2. `Gemma3 12B`는 구조는 나쁘지 않았지만 `🥩` 같은 이모지를 섞는 경향이 있었습니다.
3. `EXAONE 3.5 7.8B`는 자연스러운 한국어는 강했지만 지역 반복과 scene text 길이 제약을 아직 잘 지키지 못했습니다.
4. `Mistral Small 3.1 24B`는 로컬에서 돌아가긴 했지만 응답 지연이 커서 데모 기본 후보로는 부담이 있습니다.

## 7. 결론

- 가설 충족 여부: **부분 충족**
- 판단:
  - 로컬 후보군 발굴 자체는 성공했습니다.
  - 현재 가장 유망한 로컬 후보는 `EXAONE 3.5 7.8B`와 `Gemma3 12B`입니다.
  - 다만 바로 production baseline으로 올릴 수준은 아니고, 둘 다 prompt constraint를 더 붙여야 합니다.
  - `Qwen`은 이번 턴에서 의도적으로 비교군에서 제외했습니다. 이유는 사용자 선호와 한글 안정성 리스크 때문입니다.

## 8. 다음 액션

1. `EXAONE 3.5 7.8B`를 고정하고 `one-variable-at-a-time`으로 prompt lever를 다시 봅니다.
2. `Gemma3 12B`는 `emoji/CTA keyword`를 줄이는 output constraint 실험을 별도로 검토합니다.
3. 로컬 비디오 모델은 같은 16GB 기준으로 `돌릴 수 있는 후보`와 `지금은 무리인 후보`를 분리한 feasibility 문서로 이어갑니다.
