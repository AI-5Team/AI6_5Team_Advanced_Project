# Test Scenario 05 - 렌더/게시 자동화 구현 리스크 점검

- 날짜: 2026-04-07
- 목적: Phase 1 핵심 기능 중 `영상 생성`과 `자동 게시/보조 전환` 경계가 실제로 유지되는지 확인합니다.
- 기준 문서:
  - `docs/planning/01_SERVICE_PROJECT_PLAN.md`
  - `docs/planning/04_API_CONTRACT.md`
  - `docs/planning/06_EVALUATION_TEST_AND_OPERATIONS.md`

## 무엇을 시도했는지

1. worker 테스트에서 생성 완료 후 `video.mp4`, `post.png`, `thumb.png`, `render-meta.json`, `caption_options.json`, `hashtags.json`이 모두 생성되는지 확인하도록 보강했습니다.
2. `post.png`와 `thumb.png`의 해상도를 직접 확인해, 렌더 산출물 크기가 기대값과 맞는지 점검했습니다.
3. API 테스트에 `connected experimental channel -> auto publish -> assist_required -> assist complete -> project published` 흐름을 추가했습니다.
4. API 테스트에 `instagram permission-error callback -> permission_error 상태 저장 -> auto publish fallback` 흐름을 추가했습니다.
5. 테스트 중 발견된 버그를 수정했습니다.
   - `permission-error` OAuth callback에서 상태를 `permission_error`로 갱신한 뒤 예외를 던지면서 트랜잭션이 롤백되어, 실제로는 `connecting`에 남는 문제가 있었습니다.
   - 현재는 예외를 올리기 전에 상태 변경을 commit하도록 수정했습니다.

## 실행 기록

1. `uv run --project services/api pytest services/api/tests`
2. `uv run --project services/worker pytest services/worker/tests`
3. `npm run check`

## 결과

1. API 테스트 3건, worker 테스트 1건, web lint/build를 포함한 전체 검증이 모두 통과했습니다.
2. 영상 생성 파이프라인은 최소 기준으로 다음을 보장합니다.
   - 비어 있지 않은 `video.mp4` 생성
   - `post.png`, `thumb.png` 생성
   - 장면 이미지들과 render metadata 파일 생성
3. 게시 자동화는 최소 기준으로 다음을 보장합니다.
   - `instagram + connected` 는 자동 게시 성공
   - `youtube_shorts + connected` 는 자동 게시 대신 업로드 보조로 전환
   - 업로드 보조 완료 기록 후 프로젝트 상태가 `published`로 반영
   - `permission_error` 계정은 자동 게시 대신 보조 fallback으로 전환

## 실패/제약

1. 영상 생성 품질은 현재 “파일 생성과 기본 산출물 무결성”까지만 검증합니다. 자막 위치, 장면 전환 품질, 실제 SNS 업로드 적합성은 아직 실측하지 못했습니다.
2. 자동 게시는 실제 외부 SNS API 호출이 아니라 로컬 시뮬레이션입니다. rate limit, webhook, refresh token 재발급, 권한 범위 재동의 같은 운영 리스크는 남아 있습니다.
3. ffmpeg 의존성은 현재 로컬 환경에 설치되어 있다는 전제입니다. 배포 환경별 바이너리 패키징 전략은 아직 없습니다.

## 다음 사람이 이어서 할 수 있는 상태

1. 실험 단계로 넘어갈 때는 이제 “모델/카피 품질”과 “실기기 UX” 실험에 집중해도 됩니다.
2. 다만 구현 리스크가 완전히 0은 아니므로, 다음 구현 우선순위는 다음 순서가 적절합니다.
   - 실제 SNS provider adapter 연결
   - ffmpeg 배포 전략 또는 대체 렌더 전략 정리
   - generation run 단위 비교/재시도 운영 기능 추가
3. 실험 문서에서는 이번 테스트를 “기능적 최소 안정성 확보” 기준선으로 참조하면 됩니다.
