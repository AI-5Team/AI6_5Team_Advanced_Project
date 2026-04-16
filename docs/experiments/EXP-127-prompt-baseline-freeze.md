# EXP-127 Prompt Baseline Freeze

## 목적

- 지금까지의 prompt/model 실험 결과를 말로만 정리하지 않고, 실제 실행 가능한 baseline manifest로 고정합니다.
- 현재 기준의 `production-near prompt baseline`이 무엇인지 다시 실행 가능한 snapshot artifact까지 같이 남깁니다.

## 변경 범위

- `packages/template-spec/manifests/prompt-baseline-v1.json`
  - 현재 prompt/model 기준선을 고정한 draft manifest를 추가했습니다.
- `scripts/run_prompt_baseline_snapshot.py`
  - baseline manifest를 읽어 현재 selected model 기준 snapshot artifact를 생성하는 runner를 추가했습니다.
- `packages/template-spec/README.md`
  - prompt baseline manifest의 존재와 scope를 명시했습니다.

## 현재 고정 baseline

- baseline id
  - `PB-001`
- scope
  - `prompt_generation`
- scenario
  - `T02 promotion`
  - `b_grade_fun`
  - `regionName=성수동`
  - `detailLocation=서울숲 근처`
  - `quickOptions={ highlightPrice=true, shorterCopy=true, emphasizeRegion=false }`
- selected model
  - `Gemma 4`
  - `models/gemma-4-31b-it`
- secondary model
  - `gpt-5-mini`
  - 역할은 `tone_reference_only`
- evidence
  - `EXP-108`
  - `EXP-109`
  - `EXP-110`

## snapshot 실행 결과

artifact:

- `docs/experiments/artifacts/exp-127-prompt-baseline-freeze-snapshot.json`

주요 결과:

- baseline acceptance
  - `accepted=true`
- score
  - `100.0`
- detail location leak count
  - `0`
- over-limit scene
  - `0`
- hook
  - `규카츠 할인, 오늘만 맞나요?`
- cta
  - `방문하기`
- headline lengths
  - `s1=16`, `s2=13`, `s3=9`, `s4=8`
- latency
  - `45893ms`

## 해석

- 현재 기준에서 `Gemma 4 + strict anchor benefit budget + strict_all_surfaces` 조합은 다시 실행해도 baseline acceptance를 유지했습니다.
- deterministic reference는 여전히 `region repeated more than allowed`로 `93.3`에 머물렀고, prompt baseline이 production-near 기준에서 더 낫다는 점도 다시 확인됐습니다.
- 따라서 지금 prompt 연구선의 main baseline은 계속 `Gemma 4`로 두는 것이 타당합니다.

## 판단

- 이번 freeze는 전체 서비스 공통 baseline이 아니라, `prompt_generation` 축의 기준선 고정입니다.
- `creative reinterpretation` 영상 연구선이나 다른 purpose/template에는 그대로 일반화하지 않습니다.
- 이후 새 실험은 이 manifest를 기준으로 `무엇을 바꿨는지` 더 명확하게 비교하는 방식으로 가는 편이 맞습니다.
