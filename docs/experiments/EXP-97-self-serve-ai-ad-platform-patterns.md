# EXP-97 Self-serve AI ad platform patterns

## 1. 기본 정보

- 실험 ID: `EXP-97`
- 작성일: `2026-04-10`
- 작성자: Codex
- 관련 축: `self-serve product pattern extraction / template-first product direction`

## 2. 왜 이 작업을 했는가

- 현재 프로젝트의 목표는 `좋은 AI 광고 영상 1개를 만드는 것`이 아닙니다.
- 실제 목표는 `자영업자가 사진 몇 장과 짧은 입력만으로, 일정 수준의 광고 영상을 반복 생산하게 만드는 것`입니다.
- 따라서 레퍼런스를 볼 때도 `멋있느냐`보다 `어떤 제품 구조가 self-serve 반복 생산을 가능하게 하느냐`를 봐야 합니다.
- 이번 정리는 외부 AI ad platform들이 실제로 무엇을 제품화하고 있는지 추려, 현재 프로젝트의 본선 방향과 비교하는 작업입니다.

## 3. 참고한 외부 제품/서비스

1. [ShortVideo.ai](https://shortvideo.ai/)
2. [ShortBox](https://www.shortbox.ai/)
3. [Quickads](https://www.quickads.ai/video-ads)
4. [CapCut AI Commercial](https://www.capcut.com/tools/ai-commercial)
5. [Genre.ai](https://www.genre.ai/)

## 4. 외부 플랫폼이 공통으로 제품화하는 것

### 4.1 입력 진입점이 다양함

- `ShortVideo.ai`는 `product images`, `product URL`, `script`에서 시작할 수 있다고 밝힙니다. 또한 `editable storyboards`를 제공합니다.
- `ShortBox`는 `script or product details -> AI actor -> generate & download`의 3단 구조를 전면에 둡니다.
- `Quickads`는 `prompt`, `product website link`, `product images`, `reference ad video` 같은 입력 진입점을 함께 둡니다.

### 4.2 결과가 단일 생성물이 아니라 편집 가능한 광고 패키지임

- `ShortVideo.ai`는 장면, 텍스트, pacing, voice를 생성 후에도 편집할 수 있다고 말합니다.
- `CapCut`도 script-to-video, media syncing, voiceover, captions, overlays를 묶어 `generate and polish` 흐름을 만듭니다.
- 즉 핵심은 `한 번 생성해서 끝내는 영상`이 아니라 `수정 가능한 광고 패키지`입니다.

### 4.3 광고 문법이 슬롯화되어 있음

- `Quickads`는 `hooks, bodies, CTAs as separate components`라고 직접 설명합니다.
- 즉 이미 잘 되는 self-serve 시스템은 광고를 `처음부터 완성된 영상`으로 다루지 않고, `hook / body / CTA` 슬롯으로 나눕니다.
- 이건 현재 프로젝트의 템플릿 설계와 직접 연결될 수 있는 부분입니다.

### 4.4 채널 최적화와 반복 생산을 전면에 둠

- `ShortVideo.ai`, `ShortBox`, `CapCut`, `Quickads` 모두 TikTok / Instagram / YouTube Shorts 최적화를 전면에 둡니다.
- 중요한 점은 `품질 좋은 영상 한 편`보다 `플랫폼별 형식에 맞는 반복 생산`을 제품 가치로 설명한다는 것입니다.

### 4.5 완전한 원본 보존보다 운영 단순성을 우선함

- 외부 제품들은 대체로 `이미지/URL/스크립트로 빠르게 광고 생성`, `아바타`, `스토리보드`, `재활용`, `빠른 변형`을 강조합니다.
- 즉 strict preserve 자체보다는 `속도`, `변형`, `광고 운영 효율`을 더 중요한 가치로 둡니다.

## 5. 반대로 우리가 지금 과하게 보고 있던 것

1. `single-photo image-to-video`의 절대 품질
2. `한 컷 영상` 자체의 자연스러운 motion
3. raw prompt를 더 잘 쓰는 문제

- 이 셋도 중요하긴 하지만, self-serve 제품 관점에서는 우선순위가 더 뒤일 수 있습니다.
- 외부 제품들은 오히려 아래를 먼저 풀고 있습니다.
  - 입력 진입점 단순화
  - 광고 슬롯화
  - 후편집 가능성
  - 플랫폼별 export
  - variation 생성

## 6. 우리 제품에 바로 번역하면 무엇이 되는가

### 6.1 본선 제품 방향

1. `사진 1~3장 + 간단 입력` 기반
   - 자영업자가 바로 넣을 수 있어야 합니다.
2. `hook / body / CTA` 슬롯 구조
   - 영상 템플릿도 카피 슬롯과 같이 쪼개야 합니다.
3. `storyboard or scene preview`
   - 생성물은 영상 파일만이 아니라 수정 가능한 장면 묶음이어야 합니다.
4. `채널별 패키징`
   - Shorts/Reels/TikTok에 맞는 길이, 썸네일, 캡션, CTA를 같이 묶어야 합니다.
5. `strict preserve mode`와 `creative mode` 분리
   - 외부 플랫폼은 보통 creative 쪽으로 기울어 있습니다.
   - 우리는 본선에서 preserve mode를 더 명확히 구분해야 합니다.

### 6.2 연구선 방향

1. `better raw video`는 계속 연구할 수 있습니다.
2. 다만 연구 질문은 바뀌어야 합니다.
   - 이전:
     - `이 프롬프트가 더 좋은가`
   - 이후:
     - `이 결과가 hook/body/CTA 구조 안에서 어떤 역할을 할 수 있는가`
3. 즉 generated clip도 `완성품`보다 `템플릿 슬롯용 asset`으로 보는 편이 더 맞습니다.

## 7. 현재 제품과의 gap

### 이미 있는 것

1. 템플릿 기반 생성 흐름
2. quick action
3. 결과물 패키징
4. publish/assist fallback

### 부족한 것

1. `scene-level editable package`
2. `hook/body/CTA`를 더 직접적으로 다루는 UI/contract
3. `reference-derived hook pack`
4. `variation generation`을 광고 슬롯 단위로 보는 시각
5. `storyboard` 수준에서 수정/선택하는 흐름

## 8. 지금 기준의 핵심 판단

- 외부 self-serve AI ad product들은 `좋은 생성 모델`만을 파는 게 아닙니다.
- 실제로는 `입력 단순화 + 광고 구조화 + 빠른 변형 + 채널 패키징`을 파는 것입니다.
- 이 기준으로 보면, 현재 프로젝트가 더 집중해야 하는 건 `한 장짜리 영상 퀄리티 하나`보다 `템플릿 구조와 수정 가능한 광고 패키지`입니다.

## 9. 다음 우선순위 제안

### 1순위

- `hook/body/CTA` 기준 템플릿 재정리
- 이유:
  - 외부 self-serve 제품과 가장 직접적으로 맞닿는 부분입니다.

### 2순위

- `scene preview / storyboard` 관점으로 결과 구조 다시 보기
- 이유:
  - 생성 결과를 `파일 1개`가 아니라 `수정 가능한 광고 묶음`으로 바꿔야 합니다.

### 3순위

- `reference-derived hook pack` 실제 작성
- 이유:
  - 모델을 바꾸지 않고도 광고 체감 품질을 빠르게 끌어올릴 수 있습니다.

### 4순위

- video 연구선은 `slot asset` 관점으로 재정의
- 이유:
  - 완성형 한 편을 뽑는 것보다, 템플릿 안에 꽂을 수 있는 hero/detail clip 관점이 더 제품 목적에 맞습니다.

## 10. 결론

- 목적을 다시 분명히 하면, 지금 질문은 `이 영상이 얼마나 좋아 보이냐`가 아닙니다.
- 진짜 질문은 `이 구조를 자영업자용 self-serve 템플릿으로 녹여낼 수 있느냐`입니다.
- 이 기준으로 보면, 앞으로는 `영상 하나를 깎는 실험`보다 `템플릿 구조 / 슬롯화 / 수정 가능한 패키지`가 더 중심이 돼야 합니다.
