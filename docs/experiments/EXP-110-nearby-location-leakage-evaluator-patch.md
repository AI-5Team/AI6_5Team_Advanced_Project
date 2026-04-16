# EXP-110 Nearby-location leakage evaluator patch

## 1. 기본 정보

- 실험 ID: `EXP-110`
- 작성일: `2026-04-10`
- 작성자: Codex
- 관련 축: `evaluation patch / strict region budget / nearby landmark leakage`

## 2. 왜 이 작업을 했는가

- `EXP-106`부터 `EXP-109`까지를 보면 `성수동` exact string은 들어가도, 같은 출력 안에 `서울숲 근처`, `#서울숲근처`, `#서울숲데이트` 같은 nearby landmark 표현이 다시 섞이는 문제가 반복됐습니다.
- 그런데 기존 자동 평가는 `성수동` exact slot hit와 repeat count만 확인해서, 이런 leakage를 실패로 잡지 못했습니다.
- 이번 작업은 prompt를 더 만지는 대신 평가기 자체를 고쳐, `strict region` 조건에서 nearby-location leakage를 별도 실패로 계산하는 패치입니다.

## 3. 변경 내용

1. `services/worker/experiments/prompt_harness.py`
   - `detail_location` 기반 alias 추출 함수 추가
   - bundle 전체 text surface에서 nearby-location mention을 세는 함수 추가
   - `emphasizeRegion=false`인 시나리오에서는 nearby-location leakage를 평가 실패로 반영
2. `scripts/run_prompt_repeatability_spot_check.py`
   - source experiment id 기준으로 repeatability artifact를 남기도록 일반화

## 4. 새 실패 기준

- 실패명:
  - `nearby location leaked into strict region budget`
- 현재는 아래가 잡힙니다.
  - `서울숲 근처`
  - `#서울숲근처`
  - `#서울숲데이트`
  - 기타 `detail_location`에서 파생된 nearby landmark alias

## 5. 패치 후 재실행 결과

### `EXP-106`

- baseline:
  - `100.0 -> 86.7`
- candidate:
  - `100.0 -> 93.3`
- 해석:
  - candidate는 exact region slot은 복구했지만, nearby-location leakage는 여전히 남았습니다.

### `EXP-107`

- baseline:
  - `100.0 -> 93.3`
- candidate:
  - `100.0 -> 100.0`
- 해석:
  - baseline은 nearby-location leakage가 잡혔고, candidate는 이번 run 기준으로 leakage 없이 통과했습니다.

### `EXP-108`

- `Gemma 4`
  - `100.0 유지`
- `gpt-5-mini`
  - `92.9 -> 93.3`
  - failed:
    - `nearby location leaked into strict region budget`
- 해석:
  - 기존엔 `region slot miss` 중심으로 보였지만, 최신 기준에서는 `gpt-5-mini`의 핵심 리스크가 nearby-location leakage라는 점이 더 직접적으로 드러났습니다.

### `EXP-109`

- `Gemma 4`
  - avg score: `100.0`
  - all runs passed: `true`
- `gpt-5-mini`
  - avg score: `91.1`
  - all runs passed: `false`
- 해석:
  - `gpt-5-mini`는 3회 모두 leakage가 남았고, 1회는 exact region slot도 놓쳤습니다.
  - strict prompt repeatability까지 보면 현재 본선 후보는 `Gemma 4`가 더 명확합니다.

## 6. 결론

- 이번 패치로 자동 평가가 PM 판단에 한 단계 더 가까워졌습니다.
- 이제 `성수동` exact hit만 만든 뒤 `서울숲 근처`를 덧붙이는 우회는 통과로 볼 수 없습니다.
- 최신 기준에서:
  - 본선 main baseline 후보: `Gemma 4`
  - 짧은 톤/아이디어 보조선: `gpt-5-mini`

## 7. 다음 액션

1. 다음은 새 prompt variant보다 `nearby-location leakage`를 어떤 정책으로 reject할지 더 명확히 적는 작업입니다.
2. 필요하면 `sceneText`, `subText`, `hashtags` 각각에 대해 어떤 위치 표현이 허용/금지인지 policy 문서로 분리합니다.
