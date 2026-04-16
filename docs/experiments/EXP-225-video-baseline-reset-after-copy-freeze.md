# EXP-225 Video Baseline Reset After Copy Freeze

## 배경

- 2026-04-13 기준 `prompt baseline` quick-option catalog는 `exact match 24/24`까지 닫혔습니다.
- review fallback도 `gpt-5-mini` 유지 이유가 `카피 품질 우위`라기보다 `기본 transport repeatability 우위`라는 점까지 확인했습니다.
- 따라서 지금부터 카피 축을 더 미세 조정하는 것은 수익이 작고, 실제 병목인 `영상 품질 / 보존성 / 재현성`보다 시간이 더 많이 들 가능성이 큽니다.

## 이번 리셋의 목적

1. 카피 축은 현재 baseline으로 동결합니다.
2. 영상 쪽에서 무엇을 계속하고 무엇을 중단할지 명확히 정합니다.
3. 다음 실험을 `미세 OVAT 추가`가 아니라 `본선 후보를 가르는 baseline 실험`으로 다시 좁힙니다.

## 현재 판단

### 1. 카피 축

- 상태:
  - 당분간 `동결`
- 이유:
  - quick option coverage 공백이 없습니다.
  - 지금 병목은 카피가 아니라 영상입니다.
  - review/promotion/new_menu 모두 baseline 추천 경로가 이미 정리됐습니다.

### 2. 영상 축

- 상태:
  - 즉시 `우선순위 복귀`
- 이유:
  - `EXP-90`, `EXP-91`, `EXP-92`에서 이미 문제의 중심이 `motion quality ceiling`임이 드러났습니다.
  - local LTX는 보존성 일부는 잡지만 실제 motion 설득력이 약했습니다.
  - hosted 비교도 `품질 upper-bound`와 `원본 보존`이 충돌할 수 있다는 점을 보여줬습니다.

## 지금부터 멈출 것

1. 새 copy prompt family 추가
2. quick option 조합별 문구 미세 튜닝
3. 동일 템플릿에서 provider 비교만 반복하는 텍스트 실험
4. `single-photo + same prompt family` 안에서 phrase만 조금씩 바꾸는 영상 미세 OVAT

## 지금부터 계속할 것

1. `같은 샘플 / 같은 기준`으로 영상 모델을 다시 비교하는 baseline 실험
2. 결과 판정 기준을 아래 3개로 고정
   - 원본 보존성
   - 실제 motion 체감
   - 반복 실행 안정성
3. food와 drink를 분리해서 평가
   - food: `규카츠`
   - drink: `맥주`
4. `manual Veo`는 계속 `quality upper-bound reference only`로 사용

## 다음 영상 baseline 우선순위

### 1순위: 모델 baseline 재확인

- 질문:
  - 지금 active 후보군에서 누가 실제 baseline 후보인가
- 비교축:
  - `local LTX`
  - `Sora 2`
  - `manual Veo reference`
- 샘플:
  - `규카츠`
  - `맥주`
- 판정:
  - 보존성 / motion / repeatability 중 둘 이상에서 못 버티면 본선 후보에서 제외

### 2순위: 입력 방식 변화 실험

- 질문:
  - 문제의 핵심이 `모델`인지 `single-photo I2V 과제`인지
- 우선 레버:
  - first/last frame
  - multi-reference
  - masked/local motion
- 이유:
  - `EXP-91`, `EXP-92`에서 prompt phrase와 crop은 해결책이 아니었습니다.

### 3순위: 본선 fallback 구조 판단

- 질문:
  - hosted/local 모두 애매하면 본선은 무엇을 기본축으로 둘 것인가
- 후보:
  - `template motion + compositor + selective generative insert`
- 이유:
  - 현재 실험들은 `보존성`과 `motion`이 강하게 충돌하고 있습니다.

## 바로 다음 액션

1. copy baseline은 현재 manifest 상태로 더 이상 건드리지 않습니다.
2. 다음 세션의 첫 실험은 `규카츠 + 맥주` 기준 영상 baseline 재확인으로 시작합니다.
3. 결과 문서는 반드시 아래 3문항으로 요약합니다.
   - 원본 유지가 됐는가
   - 움직임이 실제 광고처럼 느껴지는가
   - 3회 반복해도 같은 결론이 나오는가

## 결론

- 지금부터는 `카피를 더 좋게 만드는 것`보다 `영상이 baseline 후보가 될 수 있는지`를 먼저 가려야 합니다.
- 따라서 이후 시간 배분은 `영상 70~80%`, `카피/문서 20~30% 이하`가 적절합니다.
- 다음 실험도 이 기준을 벗어나면 다시 미세 최적화로 새게 되므로, baseline 판정 질문만 남기는 편이 맞습니다.
