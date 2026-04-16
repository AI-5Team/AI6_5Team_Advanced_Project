# EXP-95 Reference teardown pattern matrix

## 1. 기본 정보

- 실험 ID: `EXP-95`
- 작성일: `2026-04-10`
- 작성자: Codex
- 관련 축: `reference teardown / pattern extraction / next backlog`

## 2. 목적

- `EXP-94`가 방향 판단 문서였다면, 이번 문서는 그 판단을 실제 backlog로 바꾸는 작업입니다.
- 즉 외부 레퍼런스에서 `좋아 보이는 이유`를 분해하고, 그것을 현재 프로젝트에서 `지금 가져올 수 있는 것`과 `지금은 못 가져오는 것`으로 나눕니다.
- 이 문서의 목표는 새 생성 실험을 많이 하는 것이 아니라, `다음 실험과 다음 구현이 어디를 겨냥해야 하는지`를 구체화하는 것입니다.

## 3. 레퍼런스 분해 매트릭스

| 레퍼런스 | 한 줄 성격 | 훅 유형 | 가져올 가치가 큰 것 | 지금 그대로 가져오기 어려운 것 | 현재 프로젝트와의 충돌 |
| --- | --- | --- | --- | --- | --- |
| `청년그로서리 1` | 이야기/우화형 curiosity 숏츠 | `이상한 이야기 + 제품 연결` | 제목형 hook, 빠른 진입, 과장된 설정 | 장면 전환 리듬, 실제 영상 연출 전체 | 원본 사진 보존과 직접 연결되지 않음 |
| `청년그로서리 2` | absurd premise 숏츠 | `카페에 악마가?` 같은 상황 과장 | B급 톤의 문제 제기 문장, 시선 끄는 첫 문장 | 캐릭터/상황 연기형 영상 | 현재는 인물/상황 생성보다 상품 preserve가 우선 |
| `청년그로서리 3` | 역사/사실형 curiosity 숏츠 | `600년 전에도?` 같은 정보형 hook | 정보형 curiosity copy, 짧은 payoff 구조 | 리듬감 있는 편집/내레이션 설계 | 본선에서는 텍스트 길이와 템플릿 제약이 있음 |
| `Genre.ai` | AI creative ad studio | `viral-ready concept packaging` | studio workflow 개념, 결과물 패키징 사고방식 | 내부 워크플로우 전체, 제작 인력 개입 | 현재 repo는 아직 productized template flow 중심 |
| `Veo 공개 자료` | 고급 video creation control surface | `camera / frame / reference control` | first-last frame, reference image, motion control 발상 | 상위 모델 자체 품질, quota/cost | strict preserve를 자동 보장하지 않음 |
| `Higgsfield 공개 자료` | cinematic control + creative workspace | `camera grammar 중심 제작` | camera grammar, product shot language, multi-stage workflow | 실제 내부 preset/UX 전체 | 현재는 1회 생성 중심이라 workflow gap이 큼 |

## 4. 지금 당장 훔쳐와야 할 것

### 4.1 카피/훅 문법

1. `궁금증 질문형`
   - 예: `진짜?`, `왜 이게 여기서 나와?`, `이걸 이렇게 마신다고?`
2. `이상한 상황 제시형`
   - 예: `카페에 악마가?`
3. `짧은 정보형 과장`
   - 예: `600년 전에도 마셨다?`

### 4.2 샷 문법

1. `hero product shot`
   - 제품을 한 번에 알아보게 하는 정면/사선 대표 컷
2. `gentle push-in`
   - 과한 움직임보다 짧은 밀착감
3. `micro detail motion`
   - 김, 거품, 탄산, 응결, 광택 같은 작은 움직임
4. `짧은 payoff cut`
   - 길게 끌지 않고 바로 효능/느낌/포인트로 닫기

### 4.3 워크플로우 문법

1. `reference lock`
   - 먼저 보존 기준을 고정
2. `motion pass`
   - 그 다음에 움직임만 추가
3. `packaging pass`
   - 마지막에 텍스트/썸네일/CTA를 얹기

## 5. 지금 당장 훔쳐올 수 없는 것

1. Veo/Higgsfield급 base model quality
2. 외부 스튜디오형 제작 인력의 shot planning 감각
3. closed workflow 안에 숨어 있는 preset/library/selection loop
4. `원본 보존을 지키면서도 motion이 풍부한` 상태를 단일 모델 한 번으로 얻는 것

## 6. 그래서 backlog를 어떻게 바꿔야 하는가

### 6.1 본선 backlog

1. `strict preserve mode`를 명시적으로 고정
   - 성공 기준:
     - 원본 상품 구조 유지
     - 결과물 패키징 완성
     - 짧은 motion은 허용되지만 과한 재해석은 금지
2. `hook/copy`는 외부 레퍼런스에서 적극 차용
   - 이 부분은 모델 교체 없이도 바로 개선 가능합니다.
3. `hybrid compositor`를 후보로 올림
   - 실제 motion이 약하면 pan/zoom/parallax/text packaging으로 광고 문법을 먼저 보강합니다.

### 6.2 연구 backlog

1. `creative reinterpretation mode`를 별도 선으로 분리
   - 여기서는 Veo/manual Sora/edit 계열 결과를 비교용으로만 씁니다.
2. `input modality change`를 우선
   - `multi-reference`
   - `first/last frame`
   - `start-end composition`
3. `prompt OVAT`는 하위 우선순위로 내림
   - 이미 `EXP-91`~`EXP-93`에서 raw prompt / framing / edit만으로는 구조적 한계가 보였습니다.

## 7. 다음 실험/구현 우선순위

### 1순위

- `reference-derived hook pack` 정리
- 이유:
  - 외부 레퍼런스에서 가장 바로 가져올 수 있고,
  - 본선에도 즉시 반영 가능하며,
  - 모델 성능과 무관하게 광고 체감 품질을 올릴 수 있습니다.

### 2순위

- `strict preserve vs creative reinterpretation` 평가 기준 분리
- 이유:
  - 지금까지는 이 둘이 섞여 있어 실험 결과 해석이 흔들렸습니다.
  - 같은 결과물을 두 기준으로 동시에 평가하면 계속 방향이 흔들립니다.

### 3순위

- `hybrid compositor` 또는 `start/end frame` 계열 입력 방식 실험
- 이유:
  - current single-photo I2V는 preserve-motion trade-off가 너무 강합니다.
  - 다음 진짜 분기점은 입력 구조 변경입니다.

## 8. 바로 실행 가능한 액션

1. `청년그로서리`형 hook를 템플릿 카피 후보로 10개 묶습니다.
2. `strict preserve`와 `creative reinterpretation` 평가표를 실험 문서 템플릿에 넣습니다.
3. `맥주` 샘플 하나를 기준으로 `hybrid compositor` 시안을 만듭니다.
4. 영상 연구선에서는 `first/last frame` 또는 `multi-reference` 후보 1개만 먼저 잡습니다.

## 9. 결론

- 지금 가장 큰 레버는 `더 강한 prompt`가 아닙니다.
- 지금 가장 큰 레버는 `외부에서 이미 검증된 광고 문법과 workflow 문법을 우리 서비스 흐름 안으로 옮기는 것`입니다.
- 따라서 다음 세션부터는 `레퍼런스에서 뭘 훔쳐올 것인가`를 중심 질문으로 두는 편이 맞습니다.
