# EXP-94 Reference-first video direction review

## 1. 기본 정보

- 실험 ID: `EXP-94`
- 작성일: `2026-04-10`
- 작성자: Codex
- 관련 축: `reference audit / upper-bound system gap review / short-form ad direction`

## 2. 왜 이 작업을 했는가

- 최근 `EXP-90`부터 `EXP-93`까지의 결과를 보면, 현재 연구선은 계속 같은 trade-off에 걸리고 있습니다.
  - 원본 보존을 높이면 motion이 약해집니다.
  - motion을 올리면 원본 보존이 무너집니다.
- 그래서 다음 질문은 `프롬프트를 더 깎을 것인가`가 아니라, `이미 잘 되는 결과물을 내는 시스템이 왜 잘 되는가`를 먼저 빼올 수 있는지입니다.
- 이번 정리는 새 생성 실험이 아니라, 외부 레퍼런스와 상위권 시스템을 기준으로 `현재 연구선의 구조적 한계`와 `훔쳐와야 할 요소`를 분해하는 작업입니다.

## 3. 참고한 외부 레퍼런스

### 유튜브 Shorts

1. `은혜 갚는 제비 #클렌즈주스#슬러시 #카페음료`
   - 링크: [YouTube Shorts](https://youtube.com/shorts/dWDBSbwlReI?si=Rsuce3bfSMNRw3zU)
   - 채널: `청년그로서리`
2. `카페에 악마가? #cafe ...`
   - 링크: [YouTube Shorts](https://youtube.com/shorts/P4Zx3JrgA30?si=4bcrQIrRsO24OhH-)
   - 채널: `청년그로서리`
3. `600년 전 에도 마셨던 '이것?' 진짜? #클렌즈주스#슬러시 #카페음료`
   - 링크: [YouTube Shorts](https://youtube.com/shorts/1wi_KY5zopY?si=iyY-DUJLi9BCDySS)
   - 채널: `청년그로서리`

### 외부 서비스

1. `Genre.ai`
   - 링크: [genre.ai](https://www.genre.ai/)
   - 관찰:
     - 스스로를 `viral age`용 AI creative ad studio로 포지셔닝하고 있습니다.
     - 즉 결과물의 본질을 `모델 성능`보다 `광고 스튜디오형 제작 체계`로 설명하고 있습니다.

### 상위권 시스템/공식 문서

1. Veo
   - [Google DeepMind Veo prompt guide](https://deepmind.google/models/veo/prompt-guide/)
   - [Veo 3 / Gemini API blog](https://developers.googleblog.com/en/veo-3-now-available-gemini-api/)
   - [Veo 3.1 creative capabilities](https://developers.googleblog.com/id/introducing-veo-3-1-and-new-creative-capabilities-in-the-gemini-api)
2. Higgsfield
   - [Higgsfield AI video overview](https://higgsfield.ai/ai-video)
   - [Higgsfield Cinema Studio](https://higgsfield.ai/cinematic-video-generator)
   - [Higgsfield product-to-video blog](https://higgsfield.ai/blog/Turn-Your-Sketch-Into-a-Cinema)

## 4. 레퍼런스에서 먼저 보이는 공통점

### 4.1 유튜브 숏츠 쪽

- 세 링크 모두 제목 단계에서 이미 `궁금증 유발형 hook`이 앞에 옵니다.
- 상품 소개보다 먼저 `이상한 상황`, `과장된 질문`, `짧은 반전`이 들어갑니다.
- 즉 이쪽 결과물의 핵심은 먼저 `모델`이 아니라 `광고 문법`입니다.
- 현재 프로젝트가 말한 `B급 감성`도 여기서 중요한 건 `저예산 느낌`이 아니라, `짧고 즉각적인 hook + 과장된 설정 + 빠른 payoff`입니다.

### 4.2 Genre/Higgsfield/Veo 쪽

- Veo는 공식적으로 `camera controls`, `first/last frame`, `reference images`, `motion controls` 같은 창작 제어 레버를 전면에 둡니다.
- Higgsfield도 자신을 단일 모델보다 `creative workspace`, `camera/lens simulation`, `multi-axis motion`, `start/end frame`, `product placement`, `motion control` 체계로 설명합니다.
- 즉 잘 되는 시스템은 대체로 `좋은 모델 1개`보다 `좋은 모델 + 입력 제어 + 장면 설계 + 후처리 UX` 조합으로 보입니다.

## 5. 우리 실험선과 무엇이 다른가

## 5.1 지금까지 내부 실험이 보여준 것

1. `EXP-90`
   - manual Veo는 `맥주`에서 품질 reference로는 강했습니다.
   - 하지만 `규카츠`에서는 QR/배경 재구성이 발생해 `원본 사진 유지형 영상화`에는 실패했습니다.
   - 따라서 manual Veo는 `비교용 upper-bound`로만 써야 합니다.
2. `EXP-91`
   - Sora prompt family를 더 직접적으로 써도 motion은 오히려 줄고 preserve만 올라가는 경우가 나왔습니다.
3. `EXP-92`
   - input framing을 조정해도 결과는 `더 잘 보존된 near-static` 쪽으로 수렴했습니다.
4. `EXP-93`
   - `image-to-video -> edit` 2단계는 motion을 일부 회복할 수는 있었지만, preserve loss가 크게 늘었습니다.

### 5.2 여기서 보이는 구조적 차이

1. **목표 차이**
   - 우리 현재 연구선은 `원본 사진을 최대한 그대로 유지하면서 영상화`를 매우 강하게 요구하고 있습니다.
   - 상위권 시스템의 공개 사례는 대개 `광고로서 좋아 보이는 결과`에 더 최적화돼 있고, 원본 완전 보존은 상대적으로 덜 엄격해 보입니다.
2. **입력 차이**
   - 우리는 주로 `single-photo image-to-video` 한 장 입력 위주입니다.
   - Veo/Higgsfield 계열은 공식적으로도 `reference image`, `start/end frame`, `motion control`, `video edit`, `product placement` 같은 더 풍부한 입력 구조를 전제합니다.
3. **워크플로우 차이**
   - 우리는 아직 `한 번 생성 -> 품질 확인` 중심입니다.
   - 상위권 시스템은 `shot planning -> reference lock -> motion design -> edit/composite`에 가까운 제작 파이프라인을 제공합니다.
4. **광고 문법 차이**
   - 우리가 지금 많이 본 것은 `모델 품질`입니다.
   - 레퍼런스가 실제로 잘 먹히는 이유는 `hook`, `카메라 리듬`, `짧은 payoff`, `패키징 문구`가 같이 설계돼 있기 때문일 가능성이 큽니다.

## 6. 결론: 단순히 "더 좋은 모델"만의 문제는 아니다

- Veo/Higgsfield가 더 좋은 모델을 쓰는 것은 맞습니다.
- 다만 현재 차이는 `모델 우위만`으로 설명하기 어렵습니다.
- 실제 차이는 아래 4개가 합쳐진 결과로 보는 편이 맞습니다.
  1. base model quality
  2. reference/control surface
  3. multi-stage creative workflow
  4. short-form ad grammar

- 따라서 지금 연구를 `밑바닥부터 raw prompt만 다시 파는 방식`으로 계속 가는 것은 효율이 낮습니다.
- 더 맞는 방향은 `잘 되는 시스템의 working pattern을 빼와서, 우리 문제에 맞게 재구성`하는 것입니다.

## 7. 지금 바로 훔쳐와야 할 것

1. `hook grammar`
   - 궁금증 질문형
   - 이상한 상황 제시형
   - 짧은 과장/반전형
2. `shot grammar`
   - product hero shot
   - gentle push-in
   - micro parallax
   - macro detail insert
3. `workflow grammar`
   - single pass보다 `reference lock -> motion pass -> packaging`
   - 필요하면 `start/end frame` 또는 `multi-reference`
4. `objective split`
   - `strict preserve mode`
   - `creative reinterpretation mode`
   - 이 둘을 같은 성공 기준으로 보면 계속 판단이 꼬입니다.
5. `evaluation split`
   - 광고로서 잘 보이는가
   - 원본 사진을 잘 지키는가
   - 둘은 분리해서 점수화해야 합니다.

## 8. 지금 시점의 판단

- `처음부터 밑바닥을 다 파야 하느냐`는 질문에는 `아니오`가 맞습니다.
- 지금 필요한 것은 `상위 결과물을 내는 시스템의 구성요소를 벤치마킹해서 가져오는 것`입니다.
- 다만 `Veo/Higgsfield처럼 보이는 결과물`을 그대로 따라가는 순간, 현재 프로젝트의 강한 요구사항인 `원본 사진 보존`과 충돌할 수 있다는 점은 분명히 명시해야 합니다.
- 특히 `규카츠 manual Veo`는 그 충돌을 이미 보여줬습니다.

## 9. 다음 액션 제안

1. 다음 실험선은 `raw prompt digging`보다 `reference teardown`을 우선합니다.
2. 외부 레퍼런스를 기준으로 아래를 표로 정리합니다.
   - hook
   - 컷 수
   - 카메라 움직임
   - 텍스트/카피 개입 시점
   - 원본 보존 허용치
3. 제품 전략도 두 갈래로 다시 적습니다.
   - `strict preserve`: 실제 업로드 사진을 거의 그대로 써야 하는 본선
   - `creative ad`: 재해석을 허용하는 연구선/확장선
4. video 연구선은 앞으로도 계속할 수 있지만, 기준 질문은 바꿔야 합니다.
   - `이 프롬프트가 더 좋은가`가 아니라
   - `이 시스템 구성요소가 성공에 어떤 역할을 하는가`

## 10. 이번 정리의 한계

- 유튜브 숏츠는 메타데이터와 공개 페이지 기준으로만 확인했기 때문에, shot-by-shot 완전 분해는 별도 수동 시청이 더 필요합니다.
- Genre/Higgsfield는 외부 공개 자료 기준 해석이며, 내부 제작 파이프라인 전체를 알 수는 없습니다.
- 따라서 이번 문서는 `구조적 방향 판단`에 초점을 둔 중간 정리입니다.
