# EXP-101 Reference hook pack cross-provider model comparison

## 1. 기본 정보

- 실험 ID: `EXP-101`
- 작성일: `2026-04-10`
- 작성자: Codex
- 관련 축: `model comparison / reference hook guidance / T02 promotion`

## 2. 왜 이 작업을 했는가

- `EXP-100`에서 reference hook guidance 자체는 유효하다는 신호가 나왔습니다.
- 이제 중요한 질문은 `같은 guidance를 줬을 때 어떤 모델이 더 짧고 바로 쓸 수 있는 결과를 안정적으로 내는가`입니다.
- 이번 실험은 `reference hook guidance`를 고정하고 모델만 바꿔서, 현재 본선과 가까운 카피 생성 후보를 가려내는 비교입니다.

## 3. 고정 조건

1. 시나리오
   - `T02 promotion`
   - `b_grade_fun`
   - 실제 음식 사진 `규카츠`, `맥주`
2. 고정 prompt
   - `fixed_reference_hook_pack_guidance`
3. 비교 모델
   - `models/gemma-4-31b-it`
   - `models/gemini-2.5-flash`
   - `gpt-5-mini`
   - `gpt-5-nano`

## 4. 실행 결과 요약

artifact:

- `docs/experiments/artifacts/exp-101-reference-hook-pack-cross-provider-model-comparison.json`

### deterministic reference

- score: `92.9`
- failed:
  - `region repeated more than allowed`

### Gemma 4

- score: `100.0`
- hook:
  - `규카츠 할인, 오늘만 맞나요?`
- cta:
  - `지금 위치 확인하기`
- scene headline lengths:
  - `s1=16`
  - `s2=16`
  - `s3=13`
  - `s4=10`
- failed:
  - 없음

관찰:

- 길이와 형식이 가장 안정적이었습니다.
- benefit와 urgency도 scene budget 안에 들어왔습니다.
- 다만 카피 톤은 약간 더 설명적이고, CTA가 `위치 확인하기` 쪽으로 흘렀습니다.

### Gemini 2.5 Flash

- score: `0.0`
- 결과:
  - `503 UNAVAILABLE`

관찰:

- 이번 세션에서는 품질 비교 이전에 안정적 호출 자체가 막혔습니다.
- 현재는 성능 판단보다 운영 리스크가 먼저 드러났습니다.

### GPT-5 Mini

- score: `100.0`
- hook:
  - `오늘만 규카츠·맥주 할인?`
- cta:
  - `지금 방문`
- scene headline lengths:
  - `s1=14`
  - `s2=20`
  - `s3=17`
  - `s4=5`
- failed:
  - 없음

관찰:

- hook와 CTA는 가장 직접적이고 짧았습니다.
- 하지만 이번 실행에서는 benefit/urgency가 다시 길어져 `s2`, `s3`가 over limit가 됐습니다.
- 즉 output 체감은 좋지만, 길이 안정성은 아직 흔들립니다.

### GPT-5 Nano

- score: `92.9`
- hook:
  - `오늘만, 맛있게 저격하자! 성수동의 곧장 먹고 배우는 맛`
- cta:
  - `저장하고 방문 확인`
- failed:
  - `region repeated more than allowed`

관찰:

- hook가 과도하게 길어졌고, 지역 반복도 다시 초과했습니다.
- 이번 조건에서는 현재 본선 후보로 보기 어렵습니다.

## 5. 지금 기준의 해석

### 품질/직접성

- `gpt-5-mini`가 가장 광고 카피처럼 바로 읽히는 결과를 냈습니다.
- `Gemma 4`는 조금 더 보수적이지만 길이와 형식은 더 안정적이었습니다.

### 운영 안정성

- `Gemini 2.5 Flash`는 이번 세션에서 아예 `503 UNAVAILABLE`이 나서, 품질 이전에 운영 리스크가 드러났습니다.
- `gpt-5-nano`는 비용/속도 면에선 가볍지만, 현재 품질선은 부족합니다.

### 본선 후보 관점

1. `gpt-5-mini`
   - 장점:
     - hook/cta 직접성
     - 짧고 즉각적인 광고 톤
   - 리스크:
     - run-to-run 길이 흔들림
2. `Gemma 4`
   - 장점:
     - 길이/형식 안정성
     - budget 안에 더 잘 들어옴
   - 리스크:
     - CTA가 덜 공격적일 수 있음

## 6. 결론

- 지금 기준으로는 `gpt-5-mini`와 `Gemma 4`가 1군입니다.
- 다만 역할이 다릅니다.
  - `gpt-5-mini`: 더 광고스럽고 직접적임
  - `Gemma 4`: 더 보수적이지만 format 안정성이 좋음
- 따라서 다음 질문은 `누가 더 좋냐`보다 `누가 더 일관되게 render-ready 결과를 내느냐`가 됩니다.

## 7. 다음 액션

1. `gpt-5-mini`와 `Gemma 4`만 남기고 repeatability spot check를 합니다.
2. 길이 안정성이 중요하면 Gemma 4를, 직접적인 광고 톤이 중요하면 gpt-5-mini를 우선 후보로 둡니다.
3. 이후 본선 연결은 `_build_copy_bundle()` 대체가 아니라 `optional prompt-assisted hook/body/cta draft` 실험선으로 붙이는 편이 안전합니다.
