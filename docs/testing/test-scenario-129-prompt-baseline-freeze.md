# Test Scenario 129 - Prompt Baseline Freeze

## 목적

- 현재 prompt/model 기준선을 manifest와 snapshot artifact로 다시 실행 가능한 상태로 고정했는지 확인합니다.

## 확인 항목

1. baseline manifest
   - `packages/template-spec/manifests/prompt-baseline-v1.json`이 현재 selected model, scenario, evidence, evaluation policy를 포함합니다.
2. baseline snapshot runner
   - `scripts/run_prompt_baseline_snapshot.py`가 manifest를 읽고 snapshot artifact를 생성합니다.
3. snapshot acceptance
   - score `100.0`
   - detail location leak count `0`
   - over-limit scene `0`

## 실행

```powershell
python -m py_compile scripts/run_prompt_baseline_snapshot.py
python -c "import json, pathlib; json.loads(pathlib.Path('packages/template-spec/manifests/prompt-baseline-v1.json').read_text(encoding='utf-8')); print('ok')"
python scripts/run_prompt_baseline_snapshot.py
```

## 기대 결과

- 현재 prompt_generation 기준선이 `Gemma 4 + strict anchor benefit budget + strict_all_surfaces`로 manifest에 고정되고, snapshot artifact가 acceptance 조건을 다시 통과합니다.
