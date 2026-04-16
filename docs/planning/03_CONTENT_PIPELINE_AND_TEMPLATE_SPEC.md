# 03. 콘텐츠 생성 파이프라인 및 템플릿 명세

> **문서 목적**: 숏폼/게시글/카피가 어떤 입력을 받아 어떤 규칙으로 생성되는지, 그리고 팀원별 구현물이 어디에서 비교되어야 하는지를 고정합니다.

## 1. 파이프라인 개요

```text
Raw Input
 -> Input Normalization
 -> Image Preprocess
 -> Template Selection
 -> Copy Planning
 -> Video Render
 -> Post Render
 -> Packaging
 -> Publish/Schedule
```

## 2. 입력 정규화 규칙

| 입력 | 내부 enum |
|---|---|
| 카페 | `cafe` |
| 음식점 | `restaurant` |
| 신메뉴 홍보 | `new_menu` |
| 할인/행사 | `promotion` |
| 후기 강조 | `review` |
| 위치 홍보 | `location_push` |
| 기본 | `default` |
| 친근함 | `friendly` |
| 하찮고 웃김 | `b_grade_fun` |

## 3. 이미지 전처리 파이프라인

### 단계

1. 파일 유효성 검사
2. 밝기/대비/채도 보정
3. 필요 시 배경 제거
4. 세로형/정사각형 용도별 crop 생성
5. 전처리 결과 저장

- 배경 제거는 아래 조건 중 하나 이상일 때만 적용합니다.
  - 피사체와 배경 대비가 충분해 마스크 품질이 확보되는 경우
  - 템플릿이 단색/합성 배경을 요구하는 경우
  - 원본 배경이 너무 복잡해 핵심 상품 식별성이 떨어지는 경우
- 배경 제거 품질이 낮거나 마스크 경계가 깨지면 `mask`를 폐기하고 보정된 원본으로 fallback 합니다.

### 출력

- `processed_vertical.png`
- `processed_square.png`
- `mask.png` 선택

## 4. 템플릿 시스템

### MVP 템플릿 목록

| ID | 이름 | 목적 | 컷수 | 지원 스타일 |
|---|---|---|---|---|
| T01 | 신메뉴 티저형 | new_menu | 4 | default, friendly |
| T02 | 오늘만 할인형 | promotion | 4 | default, friendly, b_grade_fun |
| T03 | 동네 방문 유도형 | location_push | 4 | default, friendly |
| T04 | 한줄 후기형 | review | 3 | friendly, b_grade_fun |

### 템플릿 공통 규격

- 출력 비율: 9:16
- 길이: 5~7초
- 씬 수: 3~4
- 마지막 씬: CTA 고정
- 자막은 씬당 최대 1블록

## 5. 스타일 프리셋

### S01 default

- 문구 톤: 직관적
- 효과: 최소 줌인 + 페이드
- 색상: 안정적 대비

### S02 friendly

- 문구 톤: 부드럽고 권유형
- 효과: 가벼운 팝업/스케일
- 색상: 따뜻한 계열

### S03 b_grade_fun

- 문구 톤: 짧고 과장된 한마디
- 효과: 과장 줌, 형광 포인트, 레트로 느낌
- 시각 기준
  - 90년대 노래방 자막처럼 큰 키워드를 한 번에 강조
  - 옛날 전단지처럼 형광 포인트 색상은 1~2개만 사용
  - 웃긴 톤을 위해 흔들기/번쩍임을 쓰더라도 핵심 상품은 가리지 않음
- 주의: 가독성 붕괴 금지

## 6. 카피 규칙

| 목적 | 구조 |
|---|---|
| new_menu | 후킹 + 메뉴명 + 차별점 + CTA |
| promotion | 혜택 + 기간감 + CTA |
| review | 신뢰 포인트 + 한줄 인용 + CTA |
| location_push | 지역명 + 방문 이유 + CTA |

### 지역 키워드 규칙

- 제목/본문/해시태그 중 최소 2개 영역 반영
- 지역명 3회 초과 반복 금지
- 자연스러운 조합 우선

## 7. quick action -> change set 매핑

| UI 액션 | 내부 change set |
|---|---|
| 가격 더 크게 | `highlightPrice: true` |
| 문구 더 짧게 | `shorterCopy: true` |
| 지역명 강조 | `emphasizeRegion: true` |
| 더 친근하게 | `styleOverride: "friendly"` |
| 더 웃기게 | `styleOverride: "b_grade_fun"` |
| 다른 템플릿으로 | `templateId: "<compatible-template-id>"` |

## 8. 결과물 패키징

### 패키지 구성

- video.mp4
- post.png
- caption_options.json
- hashtags.json
- render_meta.json

### render_meta 예시 필드

- projectId
- templateId
- style
- durationSec
- usedAssets
- createdAt

## 9. 렌더 품질 수용 기준

모든 숏폼 프로토타입과 최종 통합안은 아래 기준을 만족해야 합니다.

1. 자막이 화면 안전 영역 밖으로 나가면 안 됩니다.
2. 한 씬의 핵심 문구는 최소 1.2초 이상 읽을 수 있어야 합니다.
3. 상품 또는 핵심 피사체가 최소 1개 씬 이상에서 명확히 보여야 합니다.
4. CTA는 마지막 씬에서 식별 가능해야 합니다.
5. `b_grade_fun` 스타일이어도 가독성 붕괴는 허용하지 않습니다.
6. 가격/혜택/지역 중 핵심 포인트 최소 1개는 즉시 눈에 띄어야 합니다.
7. 렌더 결과가 템플릿마다 지나치게 달라 “같은 제품”처럼 안 보이면 안 됩니다.

## 10. 비교 실험 기준

전원이 공동 개발하는 숏폼 파트는 아래 기준으로 비교합니다.

1. 5~7초 안에 메시지가 읽히는가
2. 업종/목적/스타일 구분이 되는가
3. 렌더 속도가 허용 범위인가
4. 템플릿 확장이 쉬운가
5. 발표 시연 안정성이 있는가

## 11. 샘플 시나리오

### Scenario A

- 업종: 카페
- 목적: 신메뉴
- 스타일: 친근함
- 지역: 성수동
- 입력 사진: 2장
- 기대 결과:
  - 숏폼 1개
  - 게시글 1개
  - 캡션 3개
  - 해시태그 5~8개
