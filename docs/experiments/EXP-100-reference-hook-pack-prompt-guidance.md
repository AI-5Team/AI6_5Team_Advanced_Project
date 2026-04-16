# EXP-100 Reference hook pack prompt guidance

## 1. 기본 정보

- 실험 ID: `EXP-100`
- 작성일: `2026-04-10`
- 작성자: Codex
- 관련 축: `prompt lever / reference hook pack / gpt-5-mini`

## 2. 왜 이 작업을 했는가

- `EXP-99`까지로 reference-derived hook 후보군은 데이터 초안으로 정리됐습니다.
- 하지만 문서에 hook를 모아 두는 것과, 모델이 그 hook 문법을 실제로 더 잘 쓰는지는 다른 문제입니다.
- 이번 실험은 `gpt-5-mini`를 고정하고, `reference hook pack guidance`를 prompt에 직접 넣었을 때 T02 promotion 카피가 더 짧고 render-ready하게 바뀌는지 확인하는 OVAT입니다.

## 3. 고정 조건

1. 시나리오
   - `T02 promotion`
   - `b_grade_fun`
   - 실제 음식 사진 `규카츠`, `맥주`
2. 모델
   - `gpt-5-mini`
3. baseline
   - `fixed_b_grade_tone_guidance_openai`
4. candidate variant
   - `reference_hook_pack_guidance`

## 4. 무엇을 바꿨는가

1. `services/worker/experiments/prompt_harness.py`
   - `load_reference_hook_pack()`
   - `select_reference_hook_candidates()`
   - `build_reference_hook_guidance()`
2. 새 실험 정의
   - `EXP-100`
3. 이번 variant는 아래를 prompt 안에 직접 넣었습니다.
   - reference-derived hook 후보 3개
   - hookText/첫 장면을 14자 안팎으로 유지하라는 지시
   - body는 hook 반복 대신 구체 정보로 바로 이어지라는 지시
   - cta는 행동 단어를 앞쪽에 두라는 지시

## 5. 실행 결과

artifact:

- `docs/experiments/artifacts/exp-100-gpt-5-mini-prompt-lever-experiment-reference-hook-pack-guidance.json`

### deterministic reference

- score: `92.9`
- failed:
  - `region repeated more than allowed`
- over limit scene:
  - `s1`, `s2`, `s3`

### baseline `fixed_b_grade_tone_guidance_openai`

- score: `100.0`
- hook:
  - `오늘만 규카츠 + 맥주 세트 할인!`
- cta:
  - `지금 방문해 할인 받기`
- scene headline lengths:
  - `s1=14`
  - `s2=24`
  - `s3=17`
  - `s4=9`
- over limit scene:
  - `s2`, `s3`

관찰:

- 점수는 통과지만 benefit/urgency가 아직 scene budget을 넘었습니다.
- 즉 내용은 괜찮지만, render-ready 기준에서는 여전히 길었습니다.

### candidate `reference_hook_pack_guidance`

- score: `100.0`
- hook:
  - `오늘 안 오면 손해예요?`
- cta:
  - `지금 방문`
- scene headline lengths:
  - `s1=7`
  - `s2=15`
  - `s3=5`
  - `s4=5`
- over limit scene:
  - 없음

관찰:

- hook이 reference candidate의 구조를 실제로 따라갔습니다.
- benefit, urgency, cta가 모두 짧아졌고 scene budget 안으로 들어왔습니다.
- 즉 이번 variant는 점수 차이보다 `render-ready성`을 개선한 쪽으로 의미가 컸습니다.

## 6. 결론

1. reference hook pack guidance는 실제로 유효했습니다.
2. `gpt-5-mini`는 baseline만으로도 점수는 통과했지만, hook pack guidance를 주자 scene 길이와 CTA가 더 짧고 직접적으로 정리됐습니다.
3. 즉 지금 단계에서 `레퍼런스는 문서용 참고`가 아니라 `prompt를 더 잘 깎기 위한 실제 제어 레버`로 기능할 수 있습니다.

## 7. 남은 리스크

1. 이번 실험은 1회 실행 기준입니다.
2. `gpt-5-mini`는 같은 guidance 조건에서도 재실행 시 출력 길이가 다시 길어질 가능성이 있습니다.
3. 따라서 다음은 `같은 hook guidance를 고정하고 모델만 비교`하거나, `repeatability`를 확인하는 쪽이 맞습니다.

## 8. 다음 액션

1. `EXP-101`처럼 hook guidance를 고정하고 cross-provider 비교를 진행합니다.
2. 그 다음은 `repeatability`를 확인해 같은 모델이 얼마나 안정적으로 짧은 hook/body/cta를 유지하는지 봅니다.
