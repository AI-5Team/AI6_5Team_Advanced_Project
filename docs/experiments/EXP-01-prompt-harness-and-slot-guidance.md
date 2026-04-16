# EXP-01 Prompt Harness 및 Slot Guidance 실험

## 1. 기본 정보

- 실험 ID: `EXP-01`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: worker 카피 생성 실험 경로, `Gemma 4` 후보군 검증 시작

## 2. 현재 기준선 복원 결과

### production 기준선

- 현재 production 카피 생성은 `services/worker/pipelines/generation.py`의 `_build_copy_bundle()` 규칙형 조합 로직입니다.
- `docs/adr/ADR-002-deterministic-copy-and-render-baseline.md`와 실제 코드가 일치했습니다.
- 즉, Phase 1 production 경로는 아직 LLM prompt 기반이 아니라 deterministic baseline입니다.

### 기준선 검증

- `npm run worker:test` 통과
- `npm run check` 통과
- 샘플 자산 세트는 `scripts/generate_sample_assets.py`로 재생성했습니다.

## 3. 실험 목적

- production을 뒤집지 않고 prompt 실험이 가능한 분리 경로를 먼저 확보합니다.
- `Gemma 4`를 고정 모델로 두고, 프롬프트 레버 하나만 바꿨을 때 카피 품질 차이가 실제로 드러나는지 확인합니다.
- 어떤 레버가 sceneText/CTA/지역 반영 품질에 가장 큰 영향을 주는지 초기 우선순위를 잡습니다.

## 4. baseline 실험 조건 고정

| 항목 | 고정값 |
|---|---|
| 모델 | `models/gemma-4-31b-it` |
| provider | Google Generative Language API |
| 온도 | `0.2` |
| 업종 | `cafe` |
| 목적 | `new_menu` |
| 스타일 | `friendly` |
| 지역 | `성수동` |
| 상세 위치 | `서울숲 근처` |
| 자산 세트 | `samples/input/cafe/cafe-latte-01.png`, `samples/input/cafe/cafe-dessert-02.png` |
| 템플릿 | `T01` |
| quick options | `highlightPrice=false`, `shorterCopy=false`, `emphasizeRegion=true` |
| 평가 기준 | JSON 파싱 가능, 슬롯 채움, 지역 반영, 지역 반복 수, caption 수/길이, hashtag 수, CTA 액션성 |

## 5. 레버 우선순위 계획표

| 우선순위 | 레버 | 가설 | 상태 |
|---|---|---|---|
| 1 | 슬롯 지시 방식 | slot별 목적을 명확히 쓰면 sceneText와 CTA 정합성이 좋아집니다. | 이번 세션 실행 |
| 2 | 타깃 고객/톤 지정 방식 | friendly라도 너무 포괄적이면 제품성이 흐려지므로, 고객 상황을 명시하면 후킹이 선명해집니다. | 다음 후보 |
| 3 | CTA 강도 | CTA를 별도 규칙으로 강하게 쓰면 방문 행동 유도가 더 직접적이 됩니다. | 다음 후보 |
| 4 | few-shot 예시 유무 | 예시를 넣으면 안정성은 오르지만 표현 다양성이 줄 수 있습니다. | 다음 후보 |
| 5 | 출력 포맷/이모지 규칙 | JSON 강제와 이모지 금지 여부가 실제 운영 안정성과 톤 일관성에 영향을 줍니다. | 다음 후보 |

## 6. 이번 실험에서 바꾼 것

- baseline prompt와 variant 모두 같은 모델, 같은 자산, 같은 템플릿, 같은 평가 기준을 사용했습니다.
- 이번 실험에서 바뀐 레버는 **`slot_guidance` 한 가지**입니다.
- baseline prompt:
  - 슬롯 이름만 간단히 설명
- variant prompt:
  - `hook`, `product_name`, `difference`, `cta`, `subText`의 역할을 한 줄씩 명시

## 7. 실험 절차

1. deterministic production baseline을 참조 출력으로 추출했습니다.
2. `services/worker/experiments/prompt_harness.py`를 추가해 prompt experiment 경로를 분리했습니다.
3. `scripts/run_prompt_experiment.py --experiment-id EXP-01`로 Gemma 4 실험을 실행했습니다.
4. 결과 JSON artifact를 `docs/experiments/artifacts/exp-01-slot-guidance-gemma4.json`에 저장했습니다.
5. 자동 점수와 실제 출력 문장을 함께 비교했습니다.

## 8. 결과 요약

### 정량 결과

| 케이스 | 점수 | 지연 시간 | 실패 체크 |
|---|---|---|---|
| deterministic reference | `92.9` | `0 ms` | 지역명 반복 초과 |
| baseline prompt | `100.0` | `51.8s` | 없음 |
| explicit slot guidance | `100.0` | `60.0s` | 없음 |

### baseline 대비 차이

| 비교 항목 | deterministic reference | Gemma baseline prompt | Gemma explicit slot guidance |
|---|---|---|---|
| hook | `성수동에서 먼저 만나는 신메뉴...` | `기다리던 달콤한 설렘이 찾아왔어요!` | `성수동에 찾아온 달콤한 설렘` |
| sceneText.product_name | `성수동 카페 대표 메뉴...` | `시그니처 크림 라떼 & 디저트` | `시즌 신메뉴 라떼 & 디저트` |
| sceneText.difference | 구조 설명형 | `서울숲의 여유를 담은 맛` | `서울숲 산책 후 즐기는 완벽한 휴식` |
| CTA | `오늘 바로 방문해 보세요` | `지금 확인하기` / `지금 바로 만나보세요` | `지금 바로 만나보세요` |
| 지역 반복 | 4회 | 3회 | 3회 |

## 9. 관찰 내용

### 확인된 것

- 현재 deterministic baseline은 지역명을 4회 반복해 `03_CONTENT_PIPELINE_AND_TEMPLATE_SPEC.md`의 규칙(`3회 초과 금지`)을 이미 넘고 있었습니다.
- Gemma 4 prompt baseline만으로도 deterministic baseline보다 지역 반복 규칙을 더 잘 지켰습니다.
- **slot guidance를 명시한 variant는 baseline prompt보다 hook에 지역성을 더 직접적으로 반영했고, `product_name`과 `difference`의 역할 구분도 더 선명했습니다.**
- 즉, 첫 실험 기준으로는 `slot instruction`이 sceneText 품질에 의미 있는 레버 후보로 보입니다.

### 아직 애매한 것

- 자동 점수는 baseline prompt와 explicit slot guidance가 둘 다 `100`이라, 세밀한 우열은 사람 검수나 judge rubric이 더 필요합니다.
- explicit slot guidance가 더 구조적이긴 하지만, 지연 시간은 약 `8.2초` 증가했습니다.
- 현재 prompt는 이모지 금지 규칙이 없어서 explicit slot guidance 결과 캡션에 이모지가 들어갔습니다.

## 10. 실패/제약

1. 첫 모델 응답에서 JSON 앞에 자기 점검 텍스트가 붙어 파서가 한 번 실패했습니다.
   - 대응: harness에서 마지막 JSON 객체를 복구하도록 파서를 보강했습니다.
2. 샘플 자산이 초기에는 생성돼 있지 않아 `scripts/generate_sample_assets.py`를 먼저 실행해야 했습니다.
3. 이번 결과는 단일 시나리오, 단일 실행 기준이라 재현성 판단에는 표본이 부족합니다.
4. 입력 이미지는 합성 샘플이라 실제 매장 사진보다 시각 정보가 단순합니다.

## 11. 결론

- 가설 충족 여부: **부분 충족**
- 판단:
  - `slot guidance` 명시는 분명히 유효한 레버 후보입니다.
  - 다만 자동 점수만으로 우열이 갈리지 않았으므로, 다음 단계에서는 사람 기준 또는 judge rubric을 추가해야 합니다.

## 12. 다음 액션

1. 같은 harness에서 **타깃 고객/톤 지정 방식** 레버를 one-variable-at-a-time으로 비교합니다.
2. `friendly` 스타일에서 이모지 허용/금지 규칙을 분리해 운영 적합도를 확인합니다.
3. 최소 3회 반복 실행 또는 추가 시나리오 1개를 붙여 `slot guidance` 효과가 우연인지 확인합니다.
4. deterministic baseline의 지역 반복 초과는 별도 기준선 이슈로 추적합니다. production 반영 여부는 추가 실험 뒤 결정합니다.
