# EXP-02 Audience/Tone Guidance 실험

## 1. 기본 정보

- 실험 ID: `EXP-02`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `Gemma 4` 프롬프트 레버 비교, 타깃 고객/톤 지정 방식

## 2. baseline

### production baseline

- production 카피 생성은 여전히 deterministic `_build_copy_bundle()` 기준입니다.
- 이번 실험의 실제 prompt baseline은 `EXP-01`에서 만든 공통 baseline prompt를 그대로 사용했습니다.

### 고정 조건

| 항목 | 값 |
|---|---|
| 모델 | `models/gemma-4-31b-it` |
| provider | Google Generative Language API |
| 온도 | `0.2` |
| 업종 | `cafe` |
| 목적 | `new_menu` |
| 스타일 | `friendly` |
| 지역 | `성수동` |
| 상세 위치 | `서울숲 근처` |
| 자산 세트 | `cafe-latte-01.png`, `cafe-dessert-02.png` |
| 템플릿 | `T01` |
| quick options | `highlightPrice=false`, `shorterCopy=false`, `emphasizeRegion=true` |
| slot guidance | compact baseline 그대로 유지 |
| 평가 기준 | JSON 파싱 가능, 슬롯 채움, 지역 반영, 지역 반복 수, caption 수/길이, hashtag 수, CTA 액션성, audience cue count |

## 3. 이번 실험에서 바꾼 것

- 바뀐 레버는 **`audience_guidance` 한 가지**입니다.
- baseline prompt:
  - `추가 지시 없음. 스타일 기본값만 따르세요.`
- variant prompt:
  - `서울숲 근처를 산책하거나 데이트 중인 20~30대 방문객`을 명시
  - `친근하고 가볍게 권하되 과한 감탄사/오글거림은 피하라`는 톤 제한 추가
  - `산책, 데이트, 오후 여유` 같은 고객 상황 맥락을 hook/caption에 자연스럽게 넣도록 추가

## 4. 가설

- 타깃 고객/상황을 명시하면 hook과 captions가 더 구체적인 장면을 떠올리게 만들 것입니다.
- 대신 CTA가 너무 부드러워져 행동 유도 강도가 약해질 가능성이 있습니다.

## 5. 실험 절차

1. `scripts/run_prompt_experiment.py --experiment-id EXP-02` 실행
2. deterministic reference, 공통 baseline prompt, audience/tone variant 결과 저장
3. artifact 비교
4. `npm run check`로 회귀 검증

## 6. 결과

### artifact

- `docs/experiments/artifacts/exp-02-gemma-4-prompt-lever-experiment-audience-tone-guidance.json`

### 정량 결과

| 케이스 | 점수 | 지연 시간 | audience cue count | 실패 체크 |
|---|---|---|---|---|
| deterministic reference | `92.9` | `0 ms` | `0` | 지역명 반복 초과 |
| Gemma baseline prompt | `92.9` | `61.3s` | `2` | 지역명 반복 초과 |
| audience/tone variant | `92.9` | `85.9s` | `5` | CTA 액션 키워드 부족 |

### baseline 대비 차이

| 비교 항목 | Gemma baseline prompt | audience/tone variant |
|---|---|---|
| hook | `성수동 나들이의 완성, 새로운 달콤함이 찾아와요!` | `서울숲 산책 후 즐기는 달콤한 휴식` |
| captions | 메뉴 소개 + 산책 1회 언급 | 산책/오후 여유/함께 방문 맥락이 더 직접적 |
| audience cue count | `2` | `5` |
| CTA | `지금 확인하기` | `지금 매장에서 만나요` |
| 지역 반복 | 4회 | 3회 |

## 7. 관찰 내용

### 확인된 것

- **타깃 고객/상황 지시는 실제로 문구의 장면성을 크게 바꿨습니다.**
- variant는 `서울숲 산책`, `오후의 여유`, `소중한 사람과 함께` 같은 생활 맥락을 더 많이 포함했습니다.
- baseline prompt보다 variant 쪽이 훨씬 구체적인 사용 장면을 그려 줬습니다.
- region 반복은 baseline prompt 4회에서 variant 3회로 줄어 정책선 안으로 들어왔습니다.

### 같이 드러난 trade-off

- variant의 CTA는 더 부드럽고 친화적이지만, 자동 평가 기준상 행동 유도 강도는 약해졌습니다.
- 즉, `audience/tone guidance`는 hook/caption 맥락성은 올렸지만 CTA 직진성은 약화시킬 수 있습니다.
- 응답 시간도 baseline prompt 대비 약 `24.6초` 증가했습니다.

## 8. 실패/제약

1. 이 실험은 구조 점수보다 표현 맥락 차이가 핵심이라 자동 점수만으로 품질 우열이 충분히 설명되지 않습니다.
2. `ctaText lacks explicit action keyword`는 현재 heuristic 기준이며, `만나요` 같은 부드러운 유도 표현을 낮게 평가합니다.
3. 단일 시나리오 1회 실행이라 재현성 판단은 여전히 제한적입니다.

## 9. 결론

- 가설 충족 여부: **부분 충족**
- 판단:
  - `audience/tone guidance`는 후킹과 caption의 구체성에 영향이 큽니다.
  - 하지만 CTA는 따로 제어하지 않으면 너무 부드러워질 수 있습니다.

## 10. 다음 액션

1. 다음 레버는 **`CTA 강도`**로 고정합니다.
2. audience/tone variant는 유지하지 않고, 공통 baseline prompt에서 `CTA guidance`만 바꿔 one-variable-at-a-time으로 비교합니다.
3. 이후에는 `audience/tone + CTA guidance` 조합을 검토할 수 있지만, 그 단계는 단일 레버 검증이 끝난 뒤로 미룹니다.
