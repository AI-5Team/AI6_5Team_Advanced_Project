# ADR-007 영상 OVAT 실험 전에 시각 baseline을 먼저 재구축한다

- 상태: 승인
- 날짜: 2026-04-08

## 배경

최근 `EXP-04`~`EXP-06` 실험을 통해 방향성은 조금씩 좁혀졌지만, 현재 영상 렌더 결과는 아직 one-variable-at-a-time 실험을 계속할 수준의 기본 품질선에 도달하지 못했습니다.

현재 문제는 개별 레버보다 구조 문제에 가깝습니다.

1. 텍스트 overflow와 clipping이 발생합니다.
2. 헤드라인, 강조 원, 상품 사진이 겹쳐 보입니다.
3. 화면 계층과 안전영역이 고정 좌표 기반이라 실제 사진마다 품질 편차가 큽니다.

특히 아래 구현은 이런 한계를 직접 드러냅니다.

- `services/worker/renderers/media.py`
  - `create_scene_image()`는 고정 좌표 중심의 단순 배치입니다.
- `services/worker/experiments/video_harness.py`
  - `create_owner_made_scene_image()`는 텍스트와 강조 요소를 픽셀 고정값으로 찍습니다.
  - `balance_text()`는 픽셀 폭이 아니라 글자 수 기준으로 줄바꿈합니다.

즉, 지금은 “레버 하나씩 비교”보다 **시각 layout 엔진 자체를 다시 세우는 일**이 우선입니다.

## 결정

1. 영상 실험에서 OVAT(one-variable-at-a-time)는 잠시 중단합니다.
2. 다음 단계는 `renderer/layout baseline rebuild`로 전환합니다.
3. 갈아엎는 범위는 서비스 전체가 아니라 `worker renderer + experiment renderer`의 시각 배치 계층으로 제한합니다.
4. baseline rebuild가 아래 최소 품질선을 통과하기 전에는 레버별 실험 결과를 제품 판단 근거로 쓰지 않습니다.

## baseline rebuild 최소 통과 조건

1. 텍스트 overflow 0건
2. 헤드라인/강조요소/상품 겹침 0건
3. 실제 음식 사진 5세트 이상에서 상품 가시성 유지
4. 마지막 CTA 식별 가능
5. `b_grade_fun` 스타일이 유지되되 가독성 붕괴 없음
6. quick action `문구 더 짧게`, `더 웃기게` 적용 시 차이가 눈에 보임

## 구현 방향

1. 픽셀 폭 기반 text fitting 도입
2. 안전영역과 충돌 검사 기반 layout zone 도입
3. 상품 우선 영역과 텍스트 우선 영역 분리
4. 숏폼용 surface와 게시글용 surface를 분리 설계
5. B급 시각 요소는 토큰화하고, 장식은 상품을 침범하지 않는 범위에서만 허용

## 결과

1. 다음 작업 우선순위는 `새 baseline renderer 프로토타입`입니다.
2. 그 baseline이 통과한 뒤에만 다시 `subtitle_density`, `motion`, `opening priority` 같은 OVAT 실험을 재개합니다.
3. prompt/카피 미세조정은 영상 baseline 재구축 이후 보조 축으로만 이어갑니다.
