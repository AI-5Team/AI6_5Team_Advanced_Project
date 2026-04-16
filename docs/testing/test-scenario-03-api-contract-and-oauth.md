# Test Scenario 03 - API Contract 정렬 및 OAuth 상태 처리

- 날짜: 2026-04-07
- 목적: project detail contract 정렬, asset 목록 분리, OAuth callback/state 검증, 토큰 만료 fallback 동작 확인
- 기준 문서:
  - `docs/planning/04_API_CONTRACT.md`
  - `docs/planning/02_USER_FLOW_AND_SCREEN_POLICY.md`

## 무엇을 시도했는지

1. `GET /api/projects/{projectId}` 응답을 planning 문서의 canonical project detail 형태로 되돌렸습니다.
2. web 복원 흐름을 위해 `GET /api/projects/{projectId}/assets` 확장 endpoint를 추가하고, 프론트는 상세와 자산을 분리 조회하도록 수정했습니다.
3. `POST /api/social-accounts/{channel}/connect`에서 state를 생성하고, `GET /api/social-accounts/{channel}/callback`에서 `code/state` 검증을 수행하도록 구현했습니다.
4. social account의 `token_expires_at`가 과거인 경우 `expired` 상태로 전이되고, auto publish 시 `SOCIAL_TOKEN_EXPIRED`로 assist fallback 되는지 검증했습니다.

## 실행 기록

1. `npm run api:test`
2. `npm run lint:web`
3. `npm run build:web`
4. `npm run check`

## 결과

1. API 테스트 2건이 모두 통과했습니다.
2. `GET /api/projects/{projectId}`는 더 이상 `project + assets` 결합 응답을 반환하지 않습니다.
3. `GET /api/projects/{projectId}/assets`는 web 복원용 자산 조회로 동작합니다.
4. 잘못된 OAuth callback state는 `OAUTH_CALLBACK_INVALID`로 차단됩니다.
5. 연결된 `instagram` 계정의 토큰이 만료된 경우 publish 요청은 `assist_required`로 전환되고, upload job error code는 `SOCIAL_TOKEN_EXPIRED`로 기록됩니다.

## 실패/제약

1. `GET /api/projects/{projectId}/assets`는 planning 문서에 없는 로컬 확장 endpoint입니다. web 복원 편의를 위한 구현이며, canonical 본문에는 포함되지 않습니다.
2. OAuth는 여전히 demo redirect/callback 기반입니다. 실제 provider와 token refresh 교체는 후속 작업입니다.
3. publish adapter는 실제 외부 API를 호출하지 않고 로컬 시뮬레이션/assist fallback만 제공합니다.

## 다음 사람이 이어서 할 수 있는 상태

1. 실제 OAuth provider를 붙일 때는 `connect -> callback`의 state 검증 흐름을 유지한 채 redirect URL과 token 저장 부분만 교체하면 됩니다.
2. `GET /api/projects/{projectId}/assets`가 필요 없는 구조로 바꾸려면 project detail이나 generation run snapshot 설계를 별도 문서화한 뒤 정리하면 됩니다.
3. `SOCIAL_TOKEN_EXPIRED` fallback이 이미 테스트로 고정되어 있으므로, 실제 adapter를 붙인 뒤에도 같은 에러 코드를 유지하면 web 안내 문구를 재사용할 수 있습니다.
