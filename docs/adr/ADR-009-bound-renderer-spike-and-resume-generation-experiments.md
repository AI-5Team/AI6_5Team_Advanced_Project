# ADR-009 HTML/CSS renderer spike는 제한하고 생성 실험을 재개한다

- 상태: 승인
- 날짜: 2026-04-08

## 배경

`ADR-008` 이후 `Pillow`를 버리고 `HTML/CSS + browser capture` 경로를 실험했습니다.  
이 방향은 `render surface` 문제를 해결하는 데는 의미가 있었지만, 현재 시점에서는 다음 리스크가 분명해졌습니다.

1. 지금 실험은 실제 `worker` 생성 파이프라인보다 `web scene prototype` 쪽에 더 가깝습니다.
2. `scene-lab`과 `scene-frame`은 시각 연구에는 유효하지만, 그대로 오래 끌면 제품 기획의 핵심인 `선택형 입력 -> 생성 -> 빠른 수정 -> 게시/업로드 보조` 루프 검증에서 멀어집니다.
3. planning 문서와 backlog 기준으로도 현재 우선순위는
   - `템플릿 기반 숏폼 생성`
   - `카피 생성 규칙`
   - `결과 확인 + quick action`
   - `instagram 업로드/업로드 보조`
   이며, `모델 벤치마크`는 연구 과제로 분리돼 있습니다.

즉, 지금까지의 HTML/CSS 실험은 맞는 방향의 스파이크였지만, 이걸 별도 디자인 트랙처럼 계속 확장하면 기획 기준선에서 벗어납니다.

## 결정

1. `scene-lab` / `scene-frame` / `capture_scene_lab_frames.mjs`는 **renderer spike**로 유지합니다.
   - 목적: render surface 검증
   - 성격: 제품 본선 전 연구 경로
2. 여기서 더 이상의 순수 UI polish는 제한합니다.
   - “조금 더 예쁘게”만을 위한 반복은 중단합니다.
3. 다음 우선순위는 `worker` 기준 생성 경로로 복귀합니다.
   - 최소 1개 템플릿(`T02` 또는 `T04`)에 대해
   - 실제 `copy_generation -> video_rendering -> packaging` 경로에
   - 현재 HTML/CSS composition 방식을 연결할 수 있는지 검토합니다.
4. 생성 실험은 중단한 것이 아니라 **잠시 보류한 상태**로 명시합니다.
   - 재개 조건은 “시각 baseline 완성”이 아니라 아래 최소 게이트 충족입니다.

## 생성 실험 재개 게이트

아래 3개를 만족하면 생성 실험을 재개합니다.

1. 실제 템플릿 1종에서 scene가 무너지지 않고 읽힌다.
2. quick action `문구 더 짧게` 또는 `더 웃기게`가 실제 장면 변화로 이어진다.
3. 결과물이 `video.mp4 / post.png / caption_options.json / hashtags.json` 패키지 기준과 다시 연결된다.

## 재개할 생성 실험 범위

생성 실험 재개 시 우선순위는 아래 순서를 따릅니다.

1. `copy planning` 구조 실험
   - 목적별 구조(`promotion`, `review`)가 template slot에 잘 맞는지
2. `prompt lever` 실험
   - 역할 지시문
   - tone/audience
   - CTA 강도
   - slot guidance
3. `model benchmark`
   - `Gemma 4` 포함 비교

## 근거

1. `01_SERVICE_PROJECT_PLAN.md`
   - 핵심 제작 방식은 `템플릿 기반 영상 조합 우선`
   - 생성형 비디오는 메인 기능이 아닌 실험 모듈
2. `03_CONTENT_PIPELINE_AND_TEMPLATE_SPEC.md`
   - 파이프라인은 `Copy Planning -> Video Render -> Post Render -> Packaging`
   - 템플릿 규격과 quick action change set이 이미 정의돼 있음
3. `BACKLOG_P1_P2.md`
   - `Gemma 4` 포함 모델 벤치마크는 `Research Later`
   - 현재 Must는 생성/렌더/결과/게시 루프

## 결과

1. 현재 HTML/CSS 작업은 “기획에서 샌 구현”이 아니라 필요한 연구 스파이크로 유지됩니다.
2. 다만 다음 단계부터는 다시 `worker`와 `template-spec` 중심 축으로 복귀합니다.
3. 생성 실험은 이 renderer spike가 최소 게이트를 통과하면 즉시 재개합니다.
