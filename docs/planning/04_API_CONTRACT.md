# 04. API 계약

> **문서 목적**: 이 문서는 프론트엔드, API 서버, Worker가 동일한 상태값과 동일한 입출력 구조를 공유하도록 만드는 **계약 문서**입니다.  
> **문서 범위**: 인증 · 프로젝트 수명주기 · 자산 업로드 · 생성 요청 · 상태 조회 · 재생성 · 게시/예약 · SNS 연동 · 에러 모델 · idempotency · Worker payload  
> **관련 문서**: [01_SERVICE_PROJECT_PLAN.md](01_SERVICE_PROJECT_PLAN.md), [03_CONTENT_PIPELINE_AND_TEMPLATE_SPEC.md](03_CONTENT_PIPELINE_AND_TEMPLATE_SPEC.md), [05_DATA_ARCHITECTURE_AND_REPO_STRUCTURE.md](05_DATA_ARCHITECTURE_AND_REPO_STRUCTURE.md)  
> **Phase**: 1 기준 (polling 기반 비동기 처리)

---

## 목차

1. [계약 원칙](#1-계약-원칙)
2. [공통 enum 및 값 사전](#2-공통-enum-및-값-사전)
3. [ID·시간·필드명 규칙](#3-id시간필드명-규칙)
4. [인증 계약](#4-인증-계약)
5. [프로젝트 수명주기 상태 기계](#5-프로젝트-수명주기-상태-기계)
6. [엔드포인트 카탈로그](#6-엔드포인트-카탈로그)
7. [엔드포인트 상세 계약](#7-엔드포인트-상세-계약)
8. [공통 오류 모델](#8-공통-오류-모델)
9. [HTTP 상태 코드 매트릭스](#9-http-상태-코드-매트릭스)
10. [Idempotency와 재시도 규칙](#10-idempotency와-재시도-규칙)
11. [비동기 처리 계약](#11-비동기-처리-계약)
12. [Worker 내부 payload 계약](#12-worker-내부-payload-계약)
13. [대표 시퀀스 예시](#13-대표-시퀀스-예시)
14. [외부 채널 어댑터 경계](#14-외부-채널-어댑터-경계)

---

## 1. 계약 원칙

### 1-A. API 서버 authoritative 원칙

- 프론트는 상태를 계산하지 않습니다.
- 프로젝트 상태, 업로드 상태, 예약 상태는 API 서버가 authoritative source입니다.
- Worker는 결과를 직접 클라이언트에 전달하지 않고 API/DB를 통해 반영합니다.

### 1-B. 무거운 생성 작업은 모두 비동기 처리

- 이미지 전처리
- 카피 생성
- 숏폼 렌더링
- 게시글 렌더링
- 자동 업로드
- 예약 발행 실행

위 작업은 모두 동기 완료 응답을 반환하지 않습니다.

### 1-C. 프로젝트 상태와 작업 상태 분리

- `project_status`: 사용자 관점의 전체 프로젝트 상태
- `generation_run_status`: 생성 실행의 전체 상태
- `generation_step_status`: 생성 실행 내부 step 상태
- `upload_job_status`: 업로드 작업 상태
- `schedule_job_status`: 예약 작업 상태

이 5가지를 혼용하지 않습니다.

### 1-D. 상태 source of truth

- `generation_runs.status`가 생성 작업 상태의 authoritative source입니다.
- `generation_run_steps.status`가 생성 step 상태의 authoritative source입니다.
- `upload_jobs.status`가 게시 작업 상태의 authoritative source입니다.
- `schedule_jobs.status`가 예약 작업 상태의 authoritative source입니다.
- `content_projects.current_status`는 위 상태들을 사용자 조회용으로 투영한 projection field입니다.

즉, `content_projects.current_status`는 독립적으로 판단하지 않고 run/job 상태를 기준으로 계산됩니다.

### 1-E. 프론트는 외부 플랫폼 세부 정책을 모름

- 프론트는 `instagram`, `youtube_shorts`, `tiktok` 같은 채널 enum만 알고 있으면 됩니다.
- 플랫폼별 caption 처리, media 규격 차이, API 제한은 Worker/Adapter 계층이 흡수합니다.

### 1-F. MVP 채널 지원 tier

| channel | tier | Phase 1 규칙 |
|---|---|---|
| `instagram` | `ready` | 자동 게시 지원, 예약 발행은 Phase 2 확장 |
| `youtube_shorts` | `experimental` | 업로드 보조 또는 향후 확장 대상 |
| `tiktok` | `experimental` | 업로드 보조 또는 향후 확장 대상 |

### 1-G. JSON 필드 명은 camelCase 고정

- API 요청/응답 JSON 필드는 camelCase를 사용합니다.
- DB 컬럼명은 snake_case를 사용합니다.
- UI에 표시되는 한글 문구는 계약 필드에 넣지 않습니다.

---

## 2. 공통 enum 및 값 사전

### 2-A. businessType

| 값 | 의미 |
|---|---|
| `cafe` | 카페 |
| `restaurant` | 음식점 |

### 2-B. purpose

| 값 | 의미 |
|---|---|
| `new_menu` | 신메뉴 홍보 |
| `promotion` | 할인/행사 |
| `review` | 후기 강조 |
| `location_push` | 위치 방문 유도 |

### 2-C. style

| 값 | 의미 |
|---|---|
| `default` | 기본 |
| `friendly` | 친근함 |
| `b_grade_fun` | 하찮고 웃김 |

### 2-D. channel

| 값 | 의미 |
|---|---|
| `instagram` | 인스타그램 |
| `youtube_shorts` | 유튜브 쇼츠 |
| `tiktok` | 틱톡 |

### 2-D-1. channelSupportTier

| 값 | 의미 |
|---|---|
| `ready` | Phase 1 자동 게시 가능 |
| `experimental` | Phase 1 자동 게시 비보장 |
| `unsupported` | UI 미노출 또는 사용 불가 |

### 2-E. projectStatus

| 값 | 의미 |
|---|---|
| `draft` | 프로젝트 초안 생성 직후 |
| `queued` | 생성 작업 큐 등록 완료 |
| `preprocessing` | 이미지 전처리 중 |
| `generating` | 카피/렌더링 중 |
| `generated` | 결과 생성 완료 |
| `upload_assist` | 업로드 보조 패키지 준비 완료 |
| `scheduled` | 예약 등록 완료 |
| `publishing` | 게시 중 |
| `published` | 게시 완료 |
| `failed` | 생성 또는 게시 실패 |

### 2-F. generationStepStatus

| 값 | 의미 |
|---|---|
| `pending` | 아직 시작 안 함 |
| `processing` | 처리 중 |
| `completed` | 완료 |
| `failed` | 실패 |
| `skipped` | 정책상 생략 |

### 2-G. uploadJobStatus

| 값 | 의미 |
|---|---|
| `queued` | 업로드 큐 등록 |
| `publishing` | 외부 채널 게시 시도 중 |
| `published` | 게시 성공 |
| `failed` | 게시 실패 |
| `retrying` | 재시도 중 |
| `assist_required` | 업로드 보조로 전환, 사용자 확인 대기 |
| `assisted_completed` | 사용자가 수동 업로드 완료를 확인함 |

### 2-H. scheduleJobStatus

| 값 | 의미 |
|---|---|
| `scheduled` | 예약 등록 완료 |
| `queued` | 발행 실행 큐 등록 |
| `publishing` | 게시 중 |
| `published` | 게시 성공 |
| `failed` | 게시 실패 |
| `cancelled` | 예약 취소 |

### 2-I. socialAccountStatus

| 값 | 의미 |
|---|---|
| `not_connected` | 미연동 |
| `connecting` | 연동 진행 중 |
| `connected` | 연동 완료 |
| `expired` | 토큰 만료 |
| `permission_error` | 권한 오류 |

### 2-J. quickAction

| UI 액션 | canonical changeSet |
|---|---|
| `가격 더 크게` | `highlightPrice: true` |
| `문구 더 짧게` | `shorterCopy: true` |
| `지역명 강조` | `emphasizeRegion: true` |
| `더 친근하게` | `styleOverride: "friendly"` |
| `더 웃기게` | `styleOverride: "b_grade_fun"` |
| `다른 템플릿으로` | `templateId: "<compatible-template-id>"` |

---

## 3. ID·시간·필드명 규칙

### 3-A. ID 규칙

- API의 모든 ID 필드는 UUID 문자열을 사용합니다.
- DB PK도 UUID를 사용하며, 별도의 prefix형 public ID를 두지 않습니다.
- 문서 내 개체 설명용 별칭(`projectId`, `variantId` 등)은 타입명이 아니라 필드 역할 설명입니다.

### 3-B. 시간 형식

- 모든 시간값은 ISO 8601 문자열을 사용합니다.
- 예약 발행 시간은 timezone offset 포함 문자열을 사용합니다.
- 예: `2026-04-03T18:30:00+09:00`

### 3-C. nullable 규칙

- 명시적으로 비어 있을 수 있는 필드는 `null` 허용
- 빈 문자열 `""`로 null을 대체하지 않음
- 배열은 값이 없으면 `[]`, 객체가 없으면 `null`

### 3-D. 목록 조회 규칙

- MVP에서는 cursor pagination을 권장합니다.
- 응답 필드
  - `items`
  - `nextCursor`
  - `hasNext`

---

## 4. 인증 계약

### 4-A. 인증 방식

- MVP는 **JWT access token 기반 Bearer 인증**으로 고정합니다.
- 요청 헤더 형식: `Authorization: Bearer <accessToken>`
- access token 재발급/refresh token은 Phase 2 확장 범위로 둡니다.
- 발표 및 사용자 테스트 환경에서는 access token TTL을 테스트 세션 길이보다 길게 설정합니다.

### 4-B. POST /api/auth/register

#### Request

```json
{
  "email": "owner@example.com",
  "password": "secret123!",
  "name": "임창현"
}
```

#### Response

```json
{
  "accessToken": "token_value",
  "user": {
    "id": "11111111-1111-4111-8111-111111111111",
    "email": "owner@example.com",
    "name": "임창현"
  }
}
```

#### Validation

- email 형식 필수
- password 8자 이상
- name 공란 불가

### 4-C. POST /api/auth/login

#### Request

```json
{
  "email": "owner@example.com",
  "password": "secret"
}
```

#### Response

```json
{
  "accessToken": "token_value",
  "user": {
    "id": "11111111-1111-4111-8111-111111111111",
    "email": "owner@example.com",
    "name": "임창현"
  }
}
```

#### Validation

- email 형식 필수
- password 공란 불가

#### Error

- `INVALID_CREDENTIALS`

### 4-D. POST /api/auth/logout

#### Header

- `Authorization: Bearer <accessToken>`

#### Response

- `204 No Content`

### 4-E. GET /api/me

#### Response

```json
{
  "id": "11111111-1111-4111-8111-111111111111",
  "email": "owner@example.com",
  "name": "임창현"
}
```

---

## 5. 프로젝트 수명주기 상태 기계

### 5-A. 프로젝트 상태 전이표

| 현재 상태 | 이벤트 | 다음 상태 | 비고 |
|---|---|---|---|
| `draft` | generate 요청 | `queued` | 생성 작업 등록 |
| `queued` | worker 시작 | `preprocessing` | 전처리 단계 진입 |
| `preprocessing` | 전처리 성공 | `generating` | 카피/렌더 단계 |
| `preprocessing` | 전처리 실패 | `failed` | errorCode 저장 |
| `generating` | 렌더 성공 | `generated` | 결과물 저장 완료 |
| `generating` | 렌더 실패 | `failed` | errorCode 저장 |
| `generated` | publish(auto) 요청 | `publishing` | 즉시 게시 |
| `generated` | publish(assist) 요청 | `upload_assist` | 업로드 보조 패키지 생성 |
| `generated` | schedule 요청 | `scheduled` | 예약 등록, Phase 2 |
| `upload_assist` | 사용자 업로드 완료 확인 | `published` | self-reported completion |
| `upload_assist` | auto publish 재시도 | `publishing` | 재시도 가능 |
| `scheduled` | 예약 시각 도달 | `publishing` | 워커 전환 |
| `publishing` | 게시 성공 | `published` | 채널별 job success |
| `publishing` | 게시 실패 | `upload_assist` | assist fallback 가능 |
| `failed` | regenerate 요청 | `queued` | 재생성 재시도 |

### 5-B. generation steps

| step name | 설명 |
|---|---|
| `preprocessing` | 이미지 보정/배경 제거 |
| `copy_generation` | 카피/해시태그 생성 |
| `video_rendering` | 숏폼 렌더링 |
| `post_rendering` | 게시글 이미지 렌더링 |
| `packaging` | 결과 묶음 저장 |

### 5-C. publish state 분리 원칙

- 프로젝트는 `published`일 수 있어도 개별 업로드 job은 일부 실패할 수 있습니다.
- Phase 1 MVP에서는 1채널 기준을 우선하므로 `partial_success`는 내부 확장 상태로만 고려합니다.
- 업로드 보조는 실패가 아니라 별도 fallback 상태(`upload_assist`, `assist_required`)로 취급합니다.

### 5-D. projection 갱신 규칙

- 최신 generation run이 `completed`이면 project projection은 최소 `generated`
- upload job이 `assist_required`이면 project projection은 `upload_assist`
- schedule job이 `scheduled`이면 project projection은 `scheduled`
- upload job이 `publishing`이면 project projection은 `publishing`
- upload job이 `published` 또는 `assisted_completed`이면 project projection은 `published`
- 최신 generation run 또는 활성 upload/schedule job 중 하나라도 terminal failure면 project projection은 `failed`

---

## 6. 엔드포인트 카탈로그

| Domain | Method | Path | 설명 |
|---|---|---|---|
| Auth | POST | `/api/auth/register` | 회원가입 |
| Auth | POST | `/api/auth/login` | 로그인 |
| Auth | POST | `/api/auth/logout` | 로그아웃 |
| Auth | GET | `/api/me` | 현재 사용자 조회 |
| Store | GET | `/api/store-profile` | 매장 프로필 조회 |
| Store | PUT | `/api/store-profile` | 매장 프로필 저장/수정 |
| Project | POST | `/api/projects` | 프로젝트 생성 |
| Project | GET | `/api/projects` | 프로젝트 목록 조회 |
| Project | GET | `/api/projects/{projectId}` | 프로젝트 상세 |
| Asset | POST | `/api/projects/{projectId}/assets` | 원본 이미지 업로드 |
| Generation | POST | `/api/projects/{projectId}/generate` | 생성 시작 |
| Generation | GET | `/api/projects/{projectId}/status` | 생성 상태 조회 |
| Generation | POST | `/api/projects/{projectId}/regenerate` | quick action 재생성 |
| Result | GET | `/api/projects/{projectId}/result` | 결과 세트 조회 |
| Publish | POST | `/api/projects/{projectId}/publish` | 즉시 게시 |
| Publish | POST | `/api/projects/{projectId}/schedule` | 예약 발행 (Phase 2 확장) |
| Publish | GET | `/api/upload-jobs/{jobId}` | 업로드 상태 조회 |
| Publish | POST | `/api/upload-jobs/{jobId}/assist-complete` | 업로드 보조 완료 확인 |
| Publish | GET | `/api/schedule-jobs/{jobId}` | 예약 작업 상태 조회 |
| Social | GET | `/api/social-accounts` | 채널 연동 상태 조회 |
| Social | POST | `/api/social-accounts/{channel}/connect` | 연동 시작 |
| Social | GET | `/api/social-accounts/{channel}/callback` | OAuth 콜백 처리 |
| Recommendation | GET | `/api/template-recommendations` | 추천 템플릿 조회 (Phase 3 연구) |

---

## 7. 엔드포인트 상세 계약

## 7-A. GET /api/store-profile

### Response

```json
{
  "storeProfileId": "22222222-2222-4222-8222-222222222222",
  "businessType": "cafe",
  "regionName": "성수동",
  "detailLocation": "서울숲 근처",
  "defaultStyle": "friendly"
}
```

## 7-B. PUT /api/store-profile

### Request fields

| 필드 | 타입 | 필수 | 제한 |
|---|---|---|---|
| `businessType` | string | 예 | `cafe`, `restaurant` |
| `regionName` | string | 예 | 2~20자 |
| `detailLocation` | string \| null | 아니오 | 0~30자 |
| `defaultStyle` | string \| null | 아니오 | style enum |

### Response

```json
{
  "storeProfileId": "22222222-2222-4222-8222-222222222222",
  "updated": true
}
```

## 7-C. POST /api/projects

### 목적

- 생성 마법사 진행 전 또는 도중에 프로젝트 초안을 만듭니다.

### Request

```json
{
  "businessType": "cafe",
  "regionName": "성수동",
  "detailLocation": "서울숲 근처",
  "purpose": "new_menu",
  "style": "friendly",
  "channels": ["instagram"]
}
```

### Validation

- `businessType` 필수
- `regionName` 2~20자
- `purpose` 필수
- `style` 필수
- `channels` 최소 1개

### Response

```json
{
  "projectId": "33333333-3333-4333-8333-333333333333",
  "status": "draft",
  "createdAt": "2026-04-02T15:00:00+09:00"
}
```

## 7-D. GET /api/projects

### Query

| 파라미터 | 의미 |
|---|---|
| `cursor` | 다음 페이지 커서 |
| `limit` | 기본 20, 최대 50 |
| `status` | 선택적 필터 |

### Response

```json
{
  "items": [
    {
      "projectId": "33333333-3333-4333-8333-333333333333",
      "businessType": "cafe",
      "purpose": "new_menu",
      "style": "friendly",
      "status": "generated",
      "createdAt": "2026-04-02T15:00:00+09:00"
    }
  ],
  "nextCursor": null,
  "hasNext": false
}
```

## 7-E. GET /api/projects/{projectId}

### 목적

- 마법사 복원, 이력 상세, 디버깅용 기본 정보 조회

### Response

```json
{
  "projectId": "33333333-3333-4333-8333-333333333333",
  "businessType": "cafe",
  "regionName": "성수동",
  "detailLocation": "서울숲 근처",
  "purpose": "new_menu",
  "style": "friendly",
  "channels": ["instagram"],
  "status": "generated",
  "assetCount": 2
}
```

## 7-F. POST /api/projects/{projectId}/assets

### 업로드 방식

- `multipart/form-data`
- field name: `files`

### Validation

- 1~5장
- jpg/jpeg/png
- 파일당 최대 10MB

### Response

```json
{
  "projectId": "33333333-3333-4333-8333-333333333333",
  "assets": [
    {
      "assetId": "44444444-4444-4444-8444-444444444444",
      "fileName": "latte.jpg",
      "width": 1080,
      "height": 1440,
      "warnings": ["LOW_BRIGHTNESS"]
    }
  ]
}
```

### warning taxonomy

| code | 의미 |
|---|---|
| `LOW_BRIGHTNESS` | 너무 어두움 |
| `LOW_RESOLUTION` | 해상도 낮음 |
| `POSSIBLE_BLUR` | 흔들림 가능성 |
| `OFF_CENTER_SUBJECT` | 피사체 중심 불명확 |

## 7-G. POST /api/projects/{projectId}/generate

### 목적

- 최초 생성 작업을 시작합니다.

### Header

- `Idempotency-Key` 권장

### Request

```json
{
  "assetIds": [
    "44444444-4444-4444-8444-444444444444",
    "55555555-5555-4555-8555-555555555555"
  ],
  "templateId": "T01",
  "quickOptions": {
    "highlightPrice": true,
    "shorterCopy": false,
    "emphasizeRegion": true
  }
}
```

### Validation

- `assetIds` 최소 1개
- `templateId`는 선택된 업종/목적/스타일과 호환되어야 함

### Response

```json
{
  "generationRunId": "66666666-6666-4666-8666-666666666666",
  "projectId": "33333333-3333-4333-8333-333333333333",
  "status": "queued"
}
```

## 7-H. GET /api/projects/{projectId}/status

### 목적

- 프론트 polling용 상태 조회

### In-progress response

```json
{
  "projectId": "33333333-3333-4333-8333-333333333333",
  "projectStatus": "generating",
  "steps": [
    { "name": "preprocessing", "status": "completed" },
    { "name": "copy_generation", "status": "completed" },
    { "name": "video_rendering", "status": "processing" },
    { "name": "post_rendering", "status": "pending" },
    { "name": "packaging", "status": "pending" }
  ],
  "error": null
}
```

### Completed response

```json
{
  "projectId": "33333333-3333-4333-8333-333333333333",
  "projectStatus": "generated",
  "steps": [
    { "name": "preprocessing", "status": "completed" },
    { "name": "copy_generation", "status": "completed" },
    { "name": "video_rendering", "status": "completed" },
    { "name": "post_rendering", "status": "completed" },
    { "name": "packaging", "status": "completed" }
  ],
  "result": {
    "generationRunId": "66666666-6666-4666-8666-666666666666",
    "variantId": "77777777-7777-4777-8777-777777777777",
    "videoId": "88888888-8888-4888-8888-888888888888",
    "postId": "99999999-9999-4999-8999-999999999999",
    "copySetId": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
    "previewVideoUrl": "/media/projects/33333333-3333-4333-8333-333333333333/video.mp4",
    "previewImageUrl": "/media/projects/33333333-3333-4333-8333-333333333333/post.png",
    "ctaText": "오늘 바로 방문해 보세요."
  }
}
```

### Failed response

```json
{
  "projectId": "33333333-3333-4333-8333-333333333333",
  "projectStatus": "failed",
  "error": {
    "code": "RENDER_FAILED",
    "message": "숏폼 렌더링에 실패했습니다. 다른 템플릿으로 다시 시도해 주세요."
  }
}
```

## 7-I. POST /api/projects/{projectId}/regenerate

### 목적

- quick action 기반 재생성

### Request

```json
{
  "changeSet": {
    "highlightPrice": true,
    "shorterCopy": true,
    "emphasizeRegion": true,
    "styleOverride": "friendly",
    "templateId": "T02"
  }
}
```

### Rule

- 재생성은 새 generation run을 만듭니다.
- 기존 결과물을 overwrite하지 않고 새 run/version을 생성하는 방식이 권장됩니다.

### Response

```json
{
  "generationRunId": "eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee",
  "projectId": "33333333-3333-4333-8333-333333333333",
  "status": "queued"
}
```

## 7-J. GET /api/projects/{projectId}/result

### 목적

- 생성 완료 후 결과 세트 일괄 조회

### Response

```json
{
  "projectId": "33333333-3333-4333-8333-333333333333",
  "generationRunId": "66666666-6666-4666-8666-666666666666",
  "variantId": "77777777-7777-4777-8777-777777777777",
  "video": {
    "videoId": "88888888-8888-4888-8888-888888888888",
    "url": "/media/projects/33333333-3333-4333-8333-333333333333/video.mp4",
    "durationSec": 6.2,
    "templateId": "T01"
  },
  "post": {
    "postId": "99999999-9999-4999-8999-999999999999",
    "url": "/media/projects/33333333-3333-4333-8333-333333333333/post.png"
  },
  "copySet": {
    "copySetId": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
    "hookText": "성수동에서 오늘 가장 달콤한 한 잔",
    "captions": [
      "성수동에서 오늘 가장 달콤한 한 잔, 신메뉴 나왔습니다.",
      "서울숲 근처에서 찾은 오늘의 딸기라떼.",
      "퇴근길에 들르기 좋은 성수 신메뉴."
    ],
    "hashtags": ["#성수카페", "#신메뉴", "#딸기라떼"],
    "ctaText": "오늘 바로 방문해 보세요."
  }
}
```

## 7-K. POST /api/projects/{projectId}/publish

### 목적

- 즉시 업로드 실행 또는 업로드 보조 패키지 반환

### Header

- `Idempotency-Key` 권장

### Request

```json
{
  "variantId": "77777777-7777-4777-8777-777777777777",
  "channel": "instagram",
  "publishMode": "auto",
  "captionOverride": "성수동에서 오늘 가장 달콤한 한 잔, 신메뉴 나왔습니다.",
  "hashtags": ["#성수카페", "#신메뉴", "#딸기라떼"],
  "thumbnailText": "신메뉴 출시"
}
```

### Validation

- 결과물이 `generated` 상태여야 함
- `variantId`는 현재 프로젝트의 선택 가능한 결과물이어야 함
- `publishMode=auto`일 때만 socialAccount status가 `connected`여야 함
- `publishMode=assist`는 연동 여부와 무관하게 호출 가능하며, API는 즉시 `assist_required` 응답을 반환해야 함
- Phase 1에서는 `publishMode=auto` + `channel="instagram"` 조합만 자동 게시 허용
- `youtube_shorts`, `tiktok` 또는 자동 게시 실패 케이스는 `assist_required` fallback 대상으로 처리

### Response

```json
{
  "uploadJobId": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
  "projectId": "33333333-3333-4333-8333-333333333333",
  "status": "queued"
}
```

### Assist direct request 예시

```json
{
  "variantId": "77777777-7777-4777-8777-777777777777",
  "channel": "youtube_shorts",
  "publishMode": "assist",
  "captionOverride": "성수동에서 오늘 가장 달콤한 한 잔, 신메뉴 나왔습니다.",
  "hashtags": ["#성수카페", "#신메뉴", "#딸기라떼"]
}
```

### Assist direct response 예시

```json
{
  "uploadJobId": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
  "projectId": "33333333-3333-4333-8333-333333333333",
  "status": "assist_required",
  "assistPackage": {
    "mediaUrl": "/media/projects/33333333-3333-4333-8333-333333333333/video.mp4",
    "caption": "성수동에서 오늘 가장 달콤한 한 잔, 신메뉴 나왔습니다.",
    "hashtags": ["#성수카페", "#신메뉴", "#딸기라떼"]
  }
}
```

### Auto 실패 시 Assist fallback response 예시

```json
{
  "uploadJobId": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
  "projectId": "33333333-3333-4333-8333-333333333333",
  "status": "assist_required",
  "assistPackage": {
    "mediaUrl": "/media/projects/33333333-3333-4333-8333-333333333333/video.mp4",
    "caption": "성수동에서 오늘 가장 달콤한 한 잔, 신메뉴 나왔습니다.",
    "hashtags": ["#성수카페", "#신메뉴", "#딸기라떼"]
  }
}
```

## 7-L. POST /api/projects/{projectId}/schedule

### 목적

- 예약 발행 등록 (Phase 2 확장)

### Request

```json
{
  "variantId": "77777777-7777-4777-8777-777777777777",
  "channel": "instagram",
  "publishAt": "2026-04-03T18:30:00+09:00",
  "captionOverride": "성수동에서 오늘 가장 달콤한 한 잔, 신메뉴 나왔습니다.",
  "hashtags": ["#성수카페", "#신메뉴", "#딸기라떼"]
}
```

### Validation

- `publishAt`는 현재 이후여야 함
- 연동된 채널이어야 함
- `variantId`는 현재 프로젝트의 선택 가능한 결과물이어야 함
- 예약 발행은 Phase 2 확장 범위입니다.

### Response

```json
{
  "scheduleJobId": "cccccccc-cccc-4ccc-8ccc-cccccccccccc",
  "projectId": "33333333-3333-4333-8333-333333333333",
  "status": "scheduled"
}
```

## 7-M. GET /api/upload-jobs/{jobId}

### Response

```json
{
  "uploadJobId": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
  "projectId": "33333333-3333-4333-8333-333333333333",
  "channel": "instagram",
  "status": "publishing",
  "error": null
}
```

### Assist-required response 예시

```json
{
  "uploadJobId": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
  "projectId": "33333333-3333-4333-8333-333333333333",
  "channel": "youtube_shorts",
  "status": "assist_required",
  "assistPackage": {
    "mediaUrl": "/media/projects/33333333-3333-4333-8333-333333333333/video.mp4",
    "caption": "성수동에서 오늘 가장 달콤한 한 잔, 신메뉴 나왔습니다."
  },
  "error": null
}
```

## 7-M-1. POST /api/upload-jobs/{jobId}/assist-complete

### 목적

- 사용자가 업로드 보조 패키지로 수동 업로드를 끝냈음을 확인합니다.

### Request

```json
{
  "confirmedByUser": true,
  "completedAt": "2026-04-02T15:20:00+09:00"
}
```

### Response

```json
{
  "uploadJobId": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
  "status": "assisted_completed"
}
```

## 7-N. GET /api/schedule-jobs/{jobId}

### Response

```json
{
  "scheduleJobId": "cccccccc-cccc-4ccc-8ccc-cccccccccccc",
  "projectId": "33333333-3333-4333-8333-333333333333",
  "channel": "instagram",
  "status": "scheduled",
  "publishAt": "2026-04-03T18:30:00+09:00"
}
```

## 7-O. GET /api/social-accounts

### Response

```json
{
  "items": [
    {
      "channel": "instagram",
      "status": "connected",
      "accountName": "my_store_official",
      "lastSyncedAt": "2026-04-02T14:00:00+09:00"
    },
    {
      "channel": "youtube_shorts",
      "status": "not_connected",
      "accountName": null,
      "lastSyncedAt": null
    }
  ]
}
```

## 7-P. POST /api/social-accounts/{channel}/connect

### 목적

- OAuth 시작 URL 또는 연결 세션 생성

### Response

```json
{
  "channel": "instagram",
  "status": "connecting",
  "redirectUrl": "https://auth.example.com/connect/instagram"
}
```

## 7-P-1. GET /api/social-accounts/{channel}/callback

### 목적

- OAuth provider redirect 후 authorization code를 수신하고 연동 상태를 갱신합니다.

### Query

| 파라미터 | 의미 |
|---|---|
| `code` | provider authorization code |
| `state` | CSRF 방지 state |

### Response

```json
{
  "channel": "instagram",
  "status": "connected",
  "socialAccountId": "dddddddd-dddd-4ddd-8ddd-dddddddddddd"
}
```

## 7-Q. GET /api/template-recommendations

### Query

| 파라미터 | 의미 |
|---|---|
| `businessType` | 업종 |
| `style` | 선택적 스타일 필터 |

- 이 엔드포인트는 Phase 3 연구 과제 범위이며, Phase 1 구현 필수 대상이 아닙니다.

### Response

```json
{
  "items": [
    {
      "templateId": "T01",
      "title": "신메뉴 티저형",
      "reason": "카페 신메뉴 반응률이 높은 짧은 첫 문장 구조",
      "businessType": "cafe",
      "supportedStyles": ["default", "friendly"]
    }
  ]
}
```

---

## 8. 공통 오류 모델

### 8-A. 오류 응답 형식

```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "regionName은 2자 이상이어야 합니다.",
    "details": {
      "field": "regionName"
    }
  }
}
```

### 8-B. error code taxonomy

| code | 의미 | 사용자 액션 |
|---|---|---|
| `INVALID_INPUT` | 필수값 누락/형식 오류 | 입력 수정 |
| `INVALID_CREDENTIALS` | 로그인 정보 불일치 | 이메일/비밀번호 확인 |
| `PROJECT_NOT_FOUND` | 프로젝트 없음 | 목록으로 이동 |
| `UNSUPPORTED_CHANNEL` | 채널 미지원 | 채널 변경 |
| `ASSET_VALIDATION_FAILED` | 이미지 검증 실패 | 파일 교체 |
| `PREPROCESS_FAILED` | 전처리 실패 | 원본 사용 또는 재시도 |
| `COPY_GENERATION_FAILED` | 카피 생성 실패 | 재생성 |
| `RENDER_FAILED` | 렌더 실패 | 다른 템플릿 시도 |
| `AUTH_REQUIRED` | 계정 연동 필요 | 계정 연동 |
| `SOCIAL_TOKEN_EXPIRED` | 토큰 만료 | 재연동 |
| `PUBLISH_FAILED` | 게시 실패 | 재시도/업로드 보조 전환 |
| `SCHEDULE_INVALID` | 잘못된 예약 시간 | 시간 수정 |
| `OAUTH_CALLBACK_INVALID` | OAuth 콜백 검증 실패 | 연동 다시 시도 |
| `IDEMPOTENCY_CONFLICT` | 중복 요청 충돌 | 동일 요청 확인 |
| `INVALID_STATE_TRANSITION` | 현재 상태에서 허용되지 않는 호출 | 상태 새로고침 |

---

## 9. HTTP 상태 코드 매트릭스

| 상황 | 코드 |
|---|---|
| 정상 생성 | `201 Created` |
| 비동기 작업 등록 | `202 Accepted` |
| 정상 조회 | `200 OK` |
| 잘못된 입력 | `400 Bad Request` |
| 인증 필요 | `401 Unauthorized` |
| 권한 부족 | `403 Forbidden` |
| 리소스 없음 | `404 Not Found` |
| 중복/상태 충돌 | `409 Conflict` |
| 유효하지 않은 상태 전이 | `422 Unprocessable Entity` |
| 서버 오류 | `500 Internal Server Error` |

### 9-A. 409 vs 422 구분

- `409 Conflict`: 중복 요청, idempotency 충돌, 이미 같은 작업이 진행 중인 경우
- `422 Unprocessable Entity`: 형식은 맞지만 현재 상태에서 불가능한 요청

---

## 10. Idempotency와 재시도 규칙

### 10-A. Idempotency 적용 대상

- `POST /api/projects/{projectId}/generate`
- `POST /api/projects/{projectId}/publish`
- `POST /api/projects/{projectId}/schedule`

### 10-B. Header

- `Idempotency-Key: <string>`

### 10-C. 권장 키 형식

| 작업 | 예시 |
|---|---|
| generate | `33333333-3333-4333-8333-333333333333:generate:v1` |
| publish | `33333333-3333-4333-8333-333333333333:publish:instagram:auto:v1` |
| schedule | `33333333-3333-4333-8333-333333333333:schedule:instagram:2026-04-03T18:30:00+09:00` |

### 10-D. 처리 규칙

- 동일 키 + 동일 payload: 이전 응답 재사용
- 동일 키 + 다른 payload: `409 IDEMPOTENCY_CONFLICT`

### 10-E. 재시도 규칙

- 네트워크 타임아웃 시 클라이언트는 같은 idempotency key로 재시도 가능
- 사용자가 버튼을 연타해도 중복 게시가 발생하지 않아야 합니다.

---

## 11. 비동기 처리 계약

### 11-A. polling 규칙

- 생성 상태 조회: 2~3초 간격
- 업로드 상태 조회: 5초 간격
- 예약 상태 조회: 10초 간격

### 11-B. generation run과 project status 관계

- generation run이 `processing`이고 `generation_run_steps.step_name = preprocessing`이 active면 project는 `preprocessing`
- generation run이 `processing`이고 나머지 render/copy step이 active면 project는 `generating`
- generation run이 모두 완료되면 project는 `generated`

### 11-C. 게시/예약 관계

- 예약 등록 성공은 곧 게시 성공이 아닙니다.
- `scheduleJob.status = scheduled`는 예약만 완료된 상태입니다.

---

## 12. Worker 내부 payload 계약

### 12-A. preprocess job

```json
{
  "jobId": "job-preprocess-001",
  "projectId": "33333333-3333-4333-8333-333333333333",
  "assetIds": [
    "44444444-4444-4444-8444-444444444444",
    "55555555-5555-4555-8555-555555555555"
  ],
  "businessType": "cafe"
}
```

### 12-B. copy generation job

```json
{
  "jobId": "job-copy-001",
  "projectId": "33333333-3333-4333-8333-333333333333",
  "purpose": "new_menu",
  "style": "friendly",
  "regionName": "성수동",
  "templateId": "T01"
}
```

### 12-C. video render job

```json
{
  "jobId": "job-video-001",
  "projectId": "33333333-3333-4333-8333-333333333333",
  "templateId": "T01",
  "sceneSpecVersion": "v1",
  "variantId": "77777777-7777-4777-8777-777777777777",
  "processedAssetIds": [
    "12121212-1212-4212-8212-121212121212",
    "13131313-1313-4313-8313-131313131313"
  ],
  "copySetId": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
}
```

### 12-D. publish job

```json
{
  "uploadJobId": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
  "projectId": "33333333-3333-4333-8333-333333333333",
  "variantId": "77777777-7777-4777-8777-777777777777",
  "channel": "instagram",
  "mediaUrl": "/projects/33333333-3333-4333-8333-333333333333/render/video.mp4",
  "caption": "성수동에서 오늘 가장 달콤한 한 잔, 신메뉴 나왔습니다.",
  "hashtags": ["#성수카페", "#신메뉴", "#딸기라떼"],
  "socialAccountId": "dddddddd-dddd-4ddd-8ddd-dddddddddddd"
}
```

### 12-E. schedule dispatch job

```json
{
  "scheduleJobId": "cccccccc-cccc-4ccc-8ccc-cccccccccccc",
  "projectId": "33333333-3333-4333-8333-333333333333",
  "variantId": "77777777-7777-4777-8777-777777777777",
  "channel": "instagram",
  "publishAt": "2026-04-03T18:30:00+09:00"
}
```

---

## 13. 대표 시퀀스 예시

### 13-A. 최초 생성 시퀀스

```text
Web -> API: POST /projects
API -> DB: project draft 생성
Web -> API: POST /projects/{id}/assets
API -> Storage: 원본 저장
Web -> API: POST /projects/{id}/generate
API -> Redis: preprocess/copy/render job 등록
Web -> API: GET /projects/{id}/status (polling)
Worker -> DB/Storage: 전처리/렌더 결과 저장
API -> Web: generated + result 반환
```

### 13-B. quick action 재생성 시퀀스

```text
Web -> API: POST /projects/{id}/regenerate
API -> DB: generation run 생성
API -> Queue: copy/render job 재등록
Web -> API: GET /projects/{id}/status
Worker -> DB: 새 결과 버전 저장
API -> Web: 새 result 반환
```

### 13-C. 예약 발행 시퀀스

```text
Web -> API: POST /projects/{id}/schedule
API -> DB: schedule job 저장
Scheduler -> Queue: publish job 등록
Worker -> External Channel API: 게시 시도
Worker -> DB: upload job / schedule job 상태 갱신
Web -> API: GET /schedule-jobs/{id}
```

### 13-D. 자동 업로드 실패 fallback 시퀀스

```text
Worker -> External Channel API: 게시 시도
External API -> Worker: auth/token expired
Worker -> DB: upload job assist_required + error_code=SOCIAL_TOKEN_EXPIRED
API -> Web: assist package 응답
Web -> User: "계정 재연동 또는 업로드 보조 모드로 전환" 안내
```

---

## 14. 외부 채널 어댑터 경계

### 14-A. Adapter 책임

- 채널별 media 규격 변환
- caption/hashtag 조합 규칙 반영
- 외부 API 호출
- 외부 오류를 내부 errorCode로 변환

### 14-B. API 서버가 몰라도 되는 것

- 인스타그램 API 세부 파라미터
- 유튜브 업로드 메타데이터 규칙
- 틱톡 업로드 정책

이 정보는 어댑터 모듈에 캡슐화합니다.

### 14-C. MVP fallback

- 외부 채널 자동 업로드가 불안정하면 `upload assist` 모드로 전환합니다.
- 이 경우 API는 다운로드 가능한 media URL, 최종 caption set, assist package 경로를 반환해야 합니다.
- 사용자가 수동 업로드를 끝내면 `POST /api/upload-jobs/{jobId}/assist-complete`로 완료 확인을 남깁니다.
- `youtube_shorts`, `tiktok`은 Phase 1에서 기본적으로 이 fallback 범주에 둡니다.
