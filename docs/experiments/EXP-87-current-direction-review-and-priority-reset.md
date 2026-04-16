# EXP-87 Current Direction Review and Priority Reset

## 1. 기본 정보

- 실험 ID: `EXP-87`
- 작성일: `2026-04-09`
- 작성자: Codex
- 관련 기능: `진행방향 감사 / 우선순위 재정렬`

## 2. 왜 이 작업을 했는가

- 최근 작업이 로컬 LTX single-photo image-to-video baseline 쪽으로 크게 전개됐기 때문에, 지금까지의 축이 서비스 기획 의도와 계속 정렬되는지 중간 감사가 필요했습니다.
- 이번 작업의 목적은 새 실험 추가가 아니라, 현재 연구선과 본선 구현선의 비중이 적절한지 판단하고 다음 우선순위를 재고정하는 것이었습니다.

## 3. 검토 범위

### 문서

- `HISTORY.md`
- `docs/daily/2026-04-09-codex.md`
- `docs/planning/README.md`
- `docs/planning/01_SERVICE_PROJECT_PLAN.md`
- `docs/planning/03_CONTENT_PIPELINE_AND_TEMPLATE_SPEC.md`
- `docs/planning/06_EVALUATION_TEST_AND_OPERATIONS.md`
- `docs/planning/08_DOCUMENTATION_POLICY.md`
- `docs/planning/BACKLOG_P1_P2.md`
- `docs/adr/*`
- `docs/experiments/*` 중 방향 전환과 본선 검증, 최근 LTX baseline 관련 문서
- `docs/testing/*` 중 본선 검증과 최근 LTX baseline 관련 문서

### 코드

- `services/worker/pipelines/generation.py`
- `services/worker/renderers/media.py`
- `services/worker/experiments/*`
- `services/api/app/services/runtime.py`
- `scripts/*` 중 본선 검증 스크립트와 최근 LTX 스크립트
- `packages/template-spec/*`
- `packages/contracts/*`
- `apps/web/src/components/*`
- `apps/web/src/app/api/*`
- `apps/web/src/lib/*`

## 4. 총평

1. 현재 방향은 `완전히 틀린 것`이 아니라 `일부는 맞고, 최근에는 연구선 비중이 다시 커진 상태`입니다.
2. 본선 제품 루프 자체는 이미 살아 있습니다.
   - 생성
   - 결과 확인
   - quick action 재생성
   - publish / upload assist
   - history 재진입
3. 반면 최근 며칠의 중심 작업은 본선 KPI 고도화보다 `로컬 LTX baseline 정교화`에 더 많이 배치됐습니다.
4. 따라서 다음 우선순위는 새 video generation OVAT를 더 파는 것이 아니라, `본선 구현/검증 복귀`가 맞습니다.

## 5. 맞게 가고 있는 축

### 5-1. 본선 서비스 루프 구현은 생각보다 많이 살아 있음

1. worker는 여전히 `preprocess -> copy_generation -> video_rendering -> post_rendering -> packaging` 경로를 실제로 수행합니다.
2. 결과 패키지도 `video.mp4 / post.png / caption_options.json / hashtags.json / render-meta.json` 기준으로 남깁니다.
3. web은 결과 화면에서 quick action, scenePlan preview, publish / assist를 모두 노출합니다.
4. history 화면도 최근 결과와 게시 상태를 다시 열 수 있습니다.

### 5-2. publish / assist / guard 쪽은 본선답게 단단해짐

1. `instagram auto success`
2. `auto 실패 -> assist fallback`
3. `stale variant 거부`
4. `cross-project variant 거부`

위 네 축은 문서와 테스트가 함께 붙어 있어 본선 운영 안정성 측면에서 가치가 큽니다.

### 5-3. prompt / scenePlan 연구 중 일부는 본선과 직접 연결됨

1. `scenePlan bridge`
2. `project result.scenePlan`
3. `history/result preview`
4. `quick action visible delta`

이 축은 단순 연구가 아니라 본선 루프에 실제로 피드백을 넣는 작업이라 유지 가치가 있습니다.

### 5-4. 최근 LTX 연구도 완전히 헛돌지는 않음

1. OVAT 규율이 비교적 잘 지켜졌습니다.
2. batch runner, auto classifier, policy split처럼 baseline을 정리하는 방향은 연구 품질 자체는 나쁘지 않습니다.
3. 문서화 밀도도 높고 실패 기록도 남아 있습니다.

## 6. 방향이 샌 축

### 6-1. 최근 비중이 본선보다 local LTX baseline 최적화로 다시 이동함

1. `scripts/` 파일 58개 중 `local_video_ltx*` 계열이 36개입니다.
2. 최근 실험 `EXP-73`~`EXP-86`은 사실상 전부 local LTX baseline 정교화에 집중돼 있습니다.
3. 이 연구는 production worker 기본 경로에 직접 들어간 것이 아니라, 대부분 별도 스크립트/러너 층에 머물러 있습니다.

즉 연구 품질은 괜찮지만, 현재 시점의 제품 우선순위와는 비중이 다소 어긋납니다.

### 6-2. 기획 문서의 핵심 우선순위와 최근 주력 연구가 다름

기획 문서 기준 핵심은 아래입니다.

1. 템플릿 기반 숏폼
2. quick action
3. 결과 패키징
4. 업로드 / 업로드 보조
5. 생성에서 게시까지 이어지는 운영형 서비스

반면 최근 주력은 아래에 가깝습니다.

1. single-photo local image-to-video baseline
2. prepare_mode 분기
3. tray lane / drink lane prompt family
4. beer label / carbonation / framing OVAT

이건 `연구선`으로는 맞지만, `서비스 전체 우선순위`로는 과합니다.

### 6-3. production 기본 생성 품질은 아직 recent research baseline을 먹지 못함

1. production worker는 아직 deterministic `_build_copy_bundle()`과 Pillow renderer를 기본 경로로 사용합니다.
2. 최근 LTX baseline은 본선 worker/template-spec/contracts 루프의 기본값을 바꾸지 않았습니다.
3. result 화면과 history 화면도 아직 실제 `video/post` 미리보기보다 text summary + scenePlan 링크 중심입니다.
4. 업로드 보조도 상태 전이와 완료 확인은 살아 있지만, planning 문서가 요구한 `파일/캡션 다운로드형 UX`까지는 아직 얕습니다.

즉 최근 연구선이 곧바로 제품 체감 품질 개선으로 이어지는 상태는 아닙니다.

### 6-4. 명세 단일화가 덜 끝남

1. `packages/contracts`, `packages/template-spec`가 canonical 소스처럼 존재합니다.
2. 그런데 web demo는 `apps/web/src/lib/contracts.ts` 안에 template/copy/style/quick action 정의를 별도로 들고 있습니다.
3. 템플릿 JSON의 `changeSetCompatibility`와 UI 노출 정책이 자동으로 묶여 있지 않습니다.

즉 본선 구현은 살아 있지만, 명세 단일화가 덜 돼 있어서 이후 방향이 또 쉽게 샐 수 있습니다.

### 6-5. 문제 적합성 검증은 아직 비어 있음

1. planning KPI 최상단에는 타깃 사용자 3명 이상 인터뷰가 있습니다.
2. 현재 `docs/testing`, `docs/daily`, `docs/experiments`에는 그에 해당하는 user-feedback / interview 기록이 보이지 않았습니다.

즉 기술 검증은 많이 했지만, 문제 적합성 검증은 아직 약합니다.

## 7. 지금 기준의 핵심 baseline 정리

### 7-1. product / service baseline

1. 제품 기본선은 여전히 `템플릿 기반 숏폼 + 게시글 + 캡션 세트 + publish/assist fallback`입니다.
2. production copy는 deterministic `_build_copy_bundle()` 기준입니다.
3. production render는 worker의 Pillow/FFmpeg 경로입니다.
4. 결과물 패키지는 `video.mp4 / post.png / caption_options.json / hashtags.json / render-meta.json` 기준입니다.
5. publish baseline은 `instagram auto`, 그 외 채널은 `assist fallback`입니다.

### 7-2. prompt / model baseline

1. production 기본값은 아직 model-driven baseline이 아니라 deterministic baseline입니다.
2. 연구 기준선에서는 아래가 현재 상위 레버입니다.
   - `T02 promotion`: `B급 tone guidance`
   - `T04 review`: `지역 반복 제약`, `CTA 강도`
3. 모델 후보군은 아직 확정이 아니라 비교 상태입니다.
   - `Gemma 4`: 안정성 우위 후보
   - `gpt-5-mini`: 속도/품질 타협 후보
4. 따라서 prompt/model 연구는 `후보 정리` 단계이지 `production 승격` 단계는 아닙니다.

### 7-3. local video baseline

1. 이 축은 `서비스 baseline`이 아니라 `연구 baseline`입니다.
2. 현재 정리된 핵심은 아래입니다.
   - tray/full-plate: `cover_center + no steam`
   - preserve-shot 일반: `contain_blur`
   - glass drink motion phrase: `still life beverage shot`
   - top-heavy drink: `cover_top`
   - bottom-heavy bottle+glass: `cover_bottom`
3. 다만 이 결론의 일반화 근거는 아직 작습니다.
   - tray/full-plate: 사실상 `규카츠`, `타코야키`
   - drink: 사실상 `커피`, `맥주`

## 8. 계속 / 중단 / 보류

### 계속할 것

1. 본선 서비스 루프 검증
   - quick action delta
   - result/history 연결
   - publish / assist fallback
   - variant guard
2. scenePlan bridge와 template-aligned prompt 개선
   - 이 축은 연구 결과를 본선에 다시 연결합니다.
3. local LTX 연구선 자체는 유지
   - 다만 `제한된 baseline 관리용`으로만 유지해야 합니다.

### 중단할 것

1. 당분간 새로운 local LTX OVAT를 연속으로 더 쌓는 일
2. beer / drink / tray lane 세부 phrase를 계속 파고드는 일
3. 연구 결과를 아직 production에 못 넣는 상태에서 baseline 승격 문구만 앞서가는 일

### 보류할 것

1. schedule 경로 확장
2. 추가 모델 벤치마크 확대
3. renderer surface 추가 실험

지금은 구현선 재정렬이 먼저이고, 위 항목들은 당장 최우선은 아닙니다.

## 9. 다음 우선순위 제안

### 1순위. 본선 구현/검증 복귀

- 이유:
  - 기획의 핵심은 생성형 비디오 연구가 아니라 템플릿 기반 운영형 서비스입니다.
  - 현재 루프는 살아 있으므로, 이 축을 실제 데모 기준선으로 더 단단하게 만드는 것이 가장 큰 레버입니다.

### 2순위. worker/template-spec/contracts 기준선 단일화

- 이유:
  - web local contract와 canonical spec가 분리돼 있으면 이후 모든 연구 결과가 다시 샙니다.
  - 본선 고도화 전에 “어디가 진짜 기준선인가”를 코드 레벨에서 묶는 것이 필요합니다.

### 3순위. 연구선 축소 유지

- 이유:
  - LTX 연구는 버릴 필요는 없지만, 지금은 제품 중심선보다 뒤에 있어야 합니다.
  - 새 OVAT보다 `현재 baseline 중간 정리`가 더 적절합니다.

## 10. 바로 실행 가능한 다음 액션

1. result/history 화면에서 실제 `video/post` 미리보기를 먼저 붙이고, 현재 text summary 중심 UI를 본선 spec에 맞게 정렬합니다.
2. 업로드 보조 패키지에 `media/caption/hashtags`의 실제 사용 액션을 더 분명히 붙입니다.
   - 복사
   - 다운로드
   - 다음 행동 안내
3. `apps/web`의 로컬 계약/템플릿 정의와 `packages/contracts`, `packages/template-spec`의 canonical 기준선을 대조해 중복 정의를 줄입니다.
4. `T02`, `T04` 두 템플릿만 고정하고 production deterministic copy/render 품질을 다시 점검합니다.
5. local LTX 연구선은 새 OVAT를 더 늘리기보다 현재 baseline을 `중간 정리 문서`로 묶고 잠시 멈춥니다.

## 11. 결론

1. 지금까지의 작업은 `서비스 본선`과 `생성 연구선`이 둘 다 의미 있게 쌓여 있습니다.
2. 다만 최근에는 `연구선이 다시 주도권을 가져간 상태`라서, 지금 필요한 것은 더 많은 실험이 아니라 `본선 복귀`입니다.
3. 따라서 다음 단계는 `video generation 연구선 계속 전진`보다 `본선 구현/검증 복귀`가 우선입니다.
