# Test Scenario 02 - 생성 이력 및 계정 연동 UX

- 날짜: 2026-04-07
- 목적: `P1-14 생성 이력 목록 UI`, `P1-16 계정 연동 UX/문구 개선` 구현 검증
- 기준 문서:
  - `docs/planning/01_SERVICE_PROJECT_PLAN.md`
  - `docs/planning/02_USER_FLOW_AND_SCREEN_POLICY.md`

## 무엇을 시도했는지

1. `apps/web`에 상단 내비게이션을 추가해 `새 콘텐츠 만들기`, `생성 이력`, `계정 연동` 화면으로 이동할 수 있게 했습니다.
2. 생성 이력 화면(`/history`)에서 프로젝트 목록 필터, 상세 상태 조회, 메인 생성 화면 복귀 링크를 구현했습니다.
3. 계정 연동 화면(`/accounts`)에서 채널별 상태, 한 줄 안내 문구, 재연결 액션, fallback 정책 설명을 구현했습니다.
4. 메인 생성 화면(`/`)은 `?projectId=` 쿼리로 특정 프로젝트를 바로 열 수 있게 보강했습니다.
5. 데모 데이터에는 `tiktok` 만료 상태를 넣어 `재연결` UX가 실제로 보이도록 조정했습니다.

## 실행 기록

1. `npm run lint:web`
2. `npm run build:web`
3. `npm run check`

## 결과

1. `/history`, `/accounts` 정적 페이지가 Next.js 빌드 결과에 포함됐습니다.
2. 루트 화면은 `Suspense` 경계를 추가해 `useSearchParams()` 사용 제약 없이 빌드됩니다.
3. 생성 이력 화면에서 기존 프로젝트를 다시 열고 메인 화면으로 복귀하는 흐름이 시연 가능합니다.
4. 계정 연동 화면에서 `instagram` 기본 채널, 실험 채널, 만료 상태를 구분한 문구를 확인할 수 있습니다.

## 실패/제약

1. 생성 이력은 현재 프로젝트 단위 목록만 제공합니다. generation run 단위 타임라인이나 diff 비교는 아직 없습니다.
2. 계정 연동은 실제 OAuth 서버와 연결되지 않고 demo callback으로 상태를 갱신합니다.
3. `permission_error`와 실제 토큰 refresh 시나리오는 UI 문구만 준비되어 있고, 런타임 시뮬레이션은 추가되지 않았습니다.

## 다음 사람이 이어서 할 수 있는 상태

1. `/history`를 generation run 기준 이력으로 확장하려면 API에 run 목록 endpoint를 추가하면 됩니다.
2. `/accounts`의 재연결 버튼은 현재 `connect -> callback` 시뮬레이션이므로, 실제 OAuth adapter를 붙일 때 해당 호출만 교체하면 됩니다.
3. 메인 화면과 이력 화면은 `projectId` 쿼리로 연결되어 있어, 이후 상세 편집 화면이 생겨도 같은 방식으로 이어 붙일 수 있습니다.
