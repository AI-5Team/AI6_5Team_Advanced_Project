# Test Scenario 102 - reference hook pack prompt guidance

## 목적

- `EXP-100`에서 reference hook guidance가 실제로 gpt-5-mini 출력 길이와 직접성을 개선하는지 재현합니다.

## 입력 자료

1. `services/worker/experiments/prompt_harness.py`
2. `packages/template-spec/manifests/reference-hook-pack-v1.json`
3. `docs/experiments/EXP-100-reference-hook-pack-prompt-guidance.md`

## 실행 명령

```bash
python scripts/run_prompt_experiment.py --experiment-id EXP-100 --api-key-env OPENAI_API_KEY
```

## 확인 포인트

1. baseline과 `reference_hook_pack_guidance` 둘 다 성공하는지 봅니다.
2. candidate variant에서 hook가 reference candidate 구조를 실제로 따르는지 확인합니다.
3. candidate variant에서 `over_limit_scene_ids`가 baseline보다 줄어드는지 확인합니다.
4. CTA가 행동 단어 중심으로 더 짧아지는지 확인합니다.

## 기대 결과

1. 점수는 둘 다 통과할 수 있습니다.
2. 하지만 candidate variant가 길이/CTA/render-ready성에서 더 나아져야 합니다.

## 판정 기준

- 아래 3개가 모두 맞으면 통과입니다.
  1. candidate variant가 hook pack guidance를 실제로 반영했다
  2. over-limit scene 수가 baseline보다 줄었다
  3. CTA가 더 짧고 직접적으로 바뀌었다
