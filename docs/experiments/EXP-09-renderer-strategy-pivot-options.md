# EXP-09 렌더 전략 전환안 정리

## 1. 목적

현재 Pillow 기반 시각 실험이 제품 기준 미감에 미치지 못한다는 사용자 피드백을 반영해, 다음 렌더 전략 후보를 비교 정리합니다.

## 2. 현재 판단

- 현재 문제는 `카피 모델`보다 `렌더 surface` 문제입니다.
- 따라서 다음 실험은 “프롬프트를 더 깎기”보다 “어떤 방식으로 화면을 그릴 것인가”를 먼저 바꿔야 합니다.

## 3. 후보 전략

### A. HTML/CSS 기반 compositor

- 방식
  - HTML/CSS로 scene을 구성
  - headless browser 또는 screenshot pipeline으로 frame을 렌더
  - ffmpeg로 영상화
- 장점
  - 타이포그래피와 spacing 품질이 훨씬 좋음
  - layout 시스템을 component화하기 쉬움
  - 기존 Next.js/React 문법 자산을 재활용 가능
- 단점
  - worker에 새로운 렌더 경로가 필요
  - browser capture 환경 셋업 필요
- 현재 추천도
  - **1순위**

### B. 멀티모달 모델 기반 layout planner + deterministic renderer

- 방식
  - 모델이 사진과 목적을 보고 layout JSON을 생성
  - renderer는 그 JSON만 실행
- 장점
  - 사진마다 어느 영역을 비워야 하는지 더 잘 잡을 가능성
  - layout reasoning을 모델에 일부 넘길 수 있음
- 단점
  - 렌더 surface가 구리면 결과도 여전히 구림
  - planning 품질과 schema 안정화가 필요
- 현재 추천도
  - **2순위**

### C. 생성형 이미지/비디오 직접 합성

- 방식
  - reference 기반으로 장면을 직접 생성
- 장점
  - 운 좋으면 가장 세련된 결과가 나올 수 있음
- 단점
  - 템플릿 일관성, 텍스트 제어, 게시용 안정성이 약함
  - planning 문서의 `템플릿 기반 생산성 우선` 원칙과 긴장 관계
- 현재 추천도
  - **연구용 보조 축**

## 4. 추천 결론

1. 다음 본선은 `HTML/CSS 기반 compositor`로 전환합니다.
2. 그 위에 필요하면 `멀티모달 layout planner`를 붙입니다.
3. `Pillow`는 fallback 또는 간단한 post/image utility로만 남깁니다.

## 5. 바로 실행할 작업

1. HTML/CSS scene prototype 1종 만들기
2. 대표 시나리오 1개를 같은 자산으로 렌더해 현재 Pillow 결과와 비교
3. 품질 기준
   - 텍스트 clipping 없음
   - CTA 식별 가능
   - 실제 광고처럼 보이는가
   - 장식 문구가 과하지 않은가

## 6. 폐기 원칙

아래 요소는 다음 baseline에서 기본 제외합니다.

1. `사장님 손글씨` 같은 근거 없는 장식 문구
2. 과도한 낙서형 원과 스티커
3. 상품과 직접 경쟁하는 장식 요소
