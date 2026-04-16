# 05. 데이터 구조 및 저장소 구조

> **문서 목적**: 이 문서는 데이터 모델, 파일 저장 경로, Redis key, 큐 이름, 저장소 폴더 구조, 코드 오너십을 고정해 팀이 같은 시스템을 구현하도록 만드는 **아키텍처 기준 문서**입니다.  
> **문서 범위**: PostgreSQL 데이터 모델 · Object Storage 경로 규칙 · Redis key/queue · packages 구조 · template-spec 구조 · 코드 오너십  
> **관련 문서**: [01_SERVICE_PROJECT_PLAN.md](01_SERVICE_PROJECT_PLAN.md), [04_API_CONTRACT.md](04_API_CONTRACT.md), [08_DOCUMENTATION_POLICY.md](08_DOCUMENTATION_POLICY.md)

---

## 목차

1. [설계 원칙](#1-설계-원칙)
2. [데이터 모델 개요](#2-데이터-모델-개요)
3. [ERD 초안](#3-erd-초안)
4. [테이블 상세 스키마](#4-테이블-상세-스키마)
5. [인덱스 및 제약 조건](#5-인덱스-및-제약-조건)
6. [Object Storage 경로 규칙](#6-object-storage-경로-규칙)
7. [Redis key 및 Queue 규칙](#7-redis-key-및-queue-규칙)
8. [저장소 폴더 구조 canonical](#8-저장소-폴더-구조-canonical)
9. [packages/contracts 구조](#9-packagescontracts-구조)
10. [packages/template-spec 구조](#10-packagestemplate-spec-구조)
11. [샘플/문서/실험 산출물 구조](#11-샘플문서실험-산출물-구조)
12. [코드 오너십 및 변경 규칙](#12-코드-오너십-및-변경-규칙)

---

## 1. 설계 원칙

### 1-A. 메타데이터와 바이너리 분리

- 상태값, 관계, 검색 대상 메타데이터는 PostgreSQL에 저장합니다.
- 원본 이미지, 전처리 이미지, 결과 영상/이미지는 Object Storage에 저장합니다.
- Redis는 캐시와 작업 큐 같은 휘발성 데이터에만 사용합니다.

### 1-B. 프로젝트와 생성 결과 버전 분리

사용자가 “빠른 수정”이나 “다른 템플릿으로 재생성”을 할 수 있으므로, `project`와 `generation run`을 분리해야 합니다.

- `content_projects`: 사용자가 의도하는 작업 단위
- `generation_runs`: 한 번의 generate/regenerate 실행 단위
- `generated_variants`: generation run이 만들어낸 산출물 단위

이렇게 분리하지 않으면 재생성 시 이전 결과를 잃거나 상태 추적이 불가능합니다.

### 1-C. 계약 우선 설계

- API 계약의 enum과 상태값이 DB에도 반영되어야 합니다.
- 프론트가 쓰는 상태값과 Worker가 쓰는 상태값은 같은 contracts 패키지에서 가져와야 합니다.

### 1-D. 결과물은 immutable 원칙 우선

- 한 번 생성된 결과물 파일은 overwrite하지 않는 것을 원칙으로 합니다.
- regenerate는 새 generation run과 새 variant를 생성합니다.

### 1-E. 상태 projection 원칙

- `generation_runs.status`, `generation_run_steps.status`, `upload_jobs.status`, `schedule_jobs.status`가 작업 상태의 source of truth입니다.
- `content_projects.current_status`는 사용자 조회 성능과 단순화를 위한 projection입니다.
- projection 값이 어긋나면 run/job 상태를 기준으로 재계산할 수 있어야 합니다.

---

## 2. 데이터 모델 개요

### 2-A. 상위 모델

1. 사용자와 매장 프로필
2. SNS 계정 연동
3. 콘텐츠 프로젝트
4. 자산 업로드
5. 생성 실행(run)
6. 결과물(영상/게시글/카피)
7. 게시 및 예약 작업
8. 추천/실험/로그 메타데이터

### 2-B. 왜 project와 generation run을 분리하는가

예를 들어 사용자가 같은 프로젝트에서 아래를 반복할 수 있습니다.

- 문구 더 짧게
- 다른 템플릿으로 변경
- 지역명 강조
- 스타일 변경

이 경우 “현재 프로젝트”는 같지만 “생성 실행 결과”는 여러 버전이 됩니다.  
따라서 `content_projects` 안에 결과를 한 벌만 넣는 구조는 MVP 초기에는 편해 보여도, 재생성과 비교 기능이 붙는 순간 깨집니다.

---

## 3. ERD 초안

```text
users
  1 --- N store_profiles
  1 --- N social_accounts
  1 --- N content_projects

content_projects
  1 --- N project_assets
  1 --- N generation_runs
  1 --- N upload_jobs
  1 --- N schedule_jobs

project_assets
  1 --- N asset_derivatives

generation_runs
  1 --- N generation_run_steps
  1 --- N generated_variants
  1 --- N copy_sets

generated_variants
  1 --- N upload_jobs

template_recommendations
  independent lookup data

experiment_logs
  independent evidence data
```

### 3-A. 핵심 관계 설명

- `content_projects`는 사용자의 작업 묶음입니다.
- `generation_runs`는 실제 한 번의 생성 실행입니다.
- `generation_run_steps`는 각 run의 세부 단계 상태입니다.
- `generated_variants`는 결과 영상/게시글 묶음입니다.
- `upload_jobs`는 결과물과 채널의 조합마다 별도로 생길 수 있습니다.

---

## 4. 테이블 상세 스키마

아래 타입 표기는 PostgreSQL 기준입니다.

## 4-A. users

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | uuid | PK | 사용자 ID |
| email | varchar(255) | UNIQUE, NOT NULL | 로그인 이메일 |
| password_hash | varchar(255) | NOT NULL | 비밀번호 해시 |
| name | varchar(100) | NOT NULL | 사용자 이름 |
| created_at | timestamptz | NOT NULL | 생성 시각 |
| updated_at | timestamptz | NOT NULL | 수정 시각 |

## 4-B. store_profiles

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | uuid | PK | 매장 프로필 ID |
| user_id | uuid | FK(users.id), NOT NULL | 사용자 참조 |
| business_type | varchar(50) | NOT NULL | `cafe`, `restaurant` |
| region_name | varchar(50) | NOT NULL | 예: 성수동 |
| detail_location | varchar(100) | NULL | 예: 서울숲 근처 |
| default_style | varchar(50) | NULL | 기본 스타일 |
| created_at | timestamptz | NOT NULL | 생성 시각 |
| updated_at | timestamptz | NOT NULL | 수정 시각 |

## 4-C. social_accounts

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | uuid | PK | 연동 계정 ID |
| user_id | uuid | FK(users.id), NOT NULL | 사용자 참조 |
| channel | varchar(50) | NOT NULL | 채널 enum |
| account_name | varchar(100) | NULL | 연동 계정명 |
| status | varchar(50) | NOT NULL | `not_connected`, `connected` 등 |
| access_token_ref | varchar(255) | NULL | 토큰 저장 참조 키 |
| refresh_token_ref | varchar(255) | NULL | 리프레시 토큰 참조 키 |
| token_expires_at | timestamptz | NULL | 만료 시각 |
| last_synced_at | timestamptz | NULL | 최근 동기화 시각 |
| created_at | timestamptz | NOT NULL | 생성 시각 |
| updated_at | timestamptz | NOT NULL | 수정 시각 |

## 4-D. content_projects

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | uuid | PK | 프로젝트 ID |
| user_id | uuid | FK(users.id), NOT NULL | 소유 사용자 |
| store_profile_id | uuid | FK(store_profiles.id), NULL | 매장 프로필 참조 |
| business_type | varchar(50) | NOT NULL | 업종 |
| purpose | varchar(50) | NOT NULL | 목적 |
| style | varchar(50) | NOT NULL | 스타일 |
| region_name | varchar(50) | NOT NULL | 지역명 |
| detail_location | varchar(100) | NULL | 상세 위치 |
| selected_channels | jsonb | NOT NULL | 채널 배열 snapshot |
| latest_generation_run_id | uuid | NULL | 가장 최근 run |
| current_status | varchar(50) | NOT NULL | projectStatus projection |
| created_at | timestamptz | NOT NULL | 생성 시각 |
| updated_at | timestamptz | NOT NULL | 수정 시각 |

### 선택 채널을 jsonb로 두는 이유

- MVP에서는 채널 수가 적고 배열 조회 정도만 필요합니다.
- 별도 정규화 테이블보다 구현 속도가 빠릅니다.

### current_status를 projection으로 두는 이유

- 홈/이력/결과 화면에서는 빠른 상태 조회가 필요합니다.
- 하지만 생성/게시/예약의 실제 진실은 각각 run/job 테이블에 있으므로, 프로젝트 테이블에는 projection만 저장합니다.

## 4-E. project_assets

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | uuid | PK | 원본 자산 ID |
| project_id | uuid | FK(content_projects.id), NOT NULL | 프로젝트 참조 |
| original_file_name | varchar(255) | NOT NULL | 원본 파일명 |
| mime_type | varchar(50) | NOT NULL | `image/jpeg` 등 |
| file_size_bytes | bigint | NOT NULL | 파일 크기 |
| width | integer | NOT NULL | 너비 |
| height | integer | NOT NULL | 높이 |
| storage_path | varchar(500) | NOT NULL | Object Storage 경로 |
| warnings | jsonb | NOT NULL DEFAULT '[]' | 품질 경고 목록 |
| created_at | timestamptz | NOT NULL | 생성 시각 |

## 4-F. asset_derivatives

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | uuid | PK | 전처리 산출물 ID |
| asset_id | uuid | FK(project_assets.id), NOT NULL | 원본 자산 참조 |
| derivative_type | varchar(50) | NOT NULL | `vertical`, `square`, `mask` |
| storage_path | varchar(500) | NOT NULL | 저장 경로 |
| width | integer | NOT NULL | 너비 |
| height | integer | NOT NULL | 높이 |
| created_at | timestamptz | NOT NULL | 생성 시각 |

## 4-G. generation_runs

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | uuid | PK | generation run ID |
| project_id | uuid | FK(content_projects.id), NOT NULL | 프로젝트 참조 |
| run_type | varchar(50) | NOT NULL | `initial`, `regenerate` |
| trigger_source | varchar(50) | NOT NULL | `user`, `system_retry` |
| template_id | varchar(50) | NOT NULL | 사용 템플릿 |
| input_snapshot | jsonb | NOT NULL | generate 시점 입력 snapshot |
| quick_options_snapshot | jsonb | NOT NULL DEFAULT '{}' | quick option snapshot |
| status | varchar(50) | NOT NULL | `queued`, `processing`, `completed`, `failed` |
| error_code | varchar(100) | NULL | 실패 코드 |
| started_at | timestamptz | NULL | 작업 시작 |
| finished_at | timestamptz | NULL | 작업 종료 |
| created_at | timestamptz | NOT NULL | 생성 시각 |

### generation run에 snapshot을 두는 이유

- 나중에 왜 이런 결과가 나왔는지 역추적할 수 있습니다.
- 빠른 수정 전후를 비교할 수 있습니다.

## 4-G-1. generation_run_steps

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | uuid | PK | step row ID |
| generation_run_id | uuid | FK(generation_runs.id), NOT NULL | run 참조 |
| step_name | varchar(50) | NOT NULL | `preprocessing`, `copy_generation`, `video_rendering`, `post_rendering`, `packaging` |
| status | varchar(50) | NOT NULL | generationStepStatus |
| error_code | varchar(100) | NULL | step 실패 코드 |
| started_at | timestamptz | NULL | step 시작 시각 |
| finished_at | timestamptz | NULL | step 종료 시각 |
| updated_at | timestamptz | NOT NULL | 최근 갱신 시각 |

- `/status` API의 `steps[]` 배열은 이 테이블을 authoritative source로 사용합니다.
- run 생성 시 모든 step row를 `pending`으로 미리 만들고, Worker가 상태를 갱신합니다.

## 4-H. copy_sets

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | uuid | PK | 카피 세트 ID |
| generation_run_id | uuid | FK(generation_runs.id), NOT NULL | run 참조 |
| hook_text | text | NOT NULL | 후킹 문구 |
| caption_options | jsonb | NOT NULL | 캡션 후보 배열 |
| hashtags | jsonb | NOT NULL | 해시태그 배열 |
| cta_text | varchar(255) | NOT NULL | CTA |
| created_at | timestamptz | NOT NULL | 생성 시각 |

## 4-I. generated_variants

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | uuid | PK | 결과 variant ID |
| generation_run_id | uuid | FK(generation_runs.id), NOT NULL | generation run 참조 |
| copy_set_id | uuid | FK(copy_sets.id), NOT NULL | 카피 세트 참조 |
| video_path | varchar(500) | NULL | 숏폼 경로 |
| post_image_path | varchar(500) | NULL | 게시글 경로 |
| preview_thumbnail_path | varchar(500) | NULL | 썸네일 경로 |
| duration_sec | numeric(5,2) | NULL | 영상 길이 |
| render_meta | jsonb | NOT NULL DEFAULT '{}' | 렌더 메타 |
| is_selected | boolean | NOT NULL DEFAULT true | 현재 선택 결과 여부 |
| created_at | timestamptz | NOT NULL | 생성 시각 |

## 4-J. upload_jobs

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | uuid | PK | 업로드 작업 ID |
| project_id | uuid | FK(content_projects.id), NOT NULL | 프로젝트 참조 |
| variant_id | uuid | FK(generated_variants.id), NOT NULL | 게시 대상 결과물 |
| social_account_id | uuid | FK(social_accounts.id), NULL | 채널 계정 |
| channel | varchar(50) | NOT NULL | 채널 enum |
| status | varchar(50) | NOT NULL | uploadJobStatus |
| request_payload_snapshot | jsonb | NOT NULL | 게시 요청 snapshot |
| external_post_id | varchar(255) | NULL | 외부 게시물 ID |
| error_code | varchar(100) | NULL | 실패 코드 |
| retry_count | integer | NOT NULL DEFAULT 0 | 재시도 횟수 |
| assist_package_path | varchar(500) | NULL | 업로드 보조용 패키지 경로 |
| assist_confirmed_at | timestamptz | NULL | 사용자의 수동 업로드 완료 확인 시각 |
| published_at | timestamptz | NULL | 게시 성공 시각 |
| created_at | timestamptz | NOT NULL | 생성 시각 |
| updated_at | timestamptz | NOT NULL | 수정 시각 |

## 4-K. schedule_jobs

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | uuid | PK | 예약 작업 ID |
| project_id | uuid | FK(content_projects.id), NOT NULL | 프로젝트 참조 |
| variant_id | uuid | FK(generated_variants.id), NOT NULL | 게시 대상 variant |
| channel | varchar(50) | NOT NULL | 채널 |
| social_account_id | uuid | FK(social_accounts.id), NULL | 연동 계정 |
| scheduled_for | timestamptz | NOT NULL | 예약 시각 |
| status | varchar(50) | NOT NULL | scheduleJobStatus |
| payload_snapshot | jsonb | NOT NULL | 예약 당시 payload |
| linked_upload_job_id | uuid | NULL | 실행 후 생성된 upload job |
| error_code | varchar(100) | NULL | 실패 코드 |
| created_at | timestamptz | NOT NULL | 생성 시각 |
| updated_at | timestamptz | NOT NULL | 수정 시각 |

## 4-L. template_recommendations

이 테이블은 Phase 3 연구 과제를 위한 준비 구조입니다. Phase 1 구현 필수 대상은 아닙니다.

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | uuid | PK | 추천 데이터 ID |
| business_type | varchar(50) | NOT NULL | 업종 |
| template_id | varchar(50) | NOT NULL | 템플릿 ID |
| score | numeric(5,2) | NOT NULL | 추천 점수 |
| reason | text | NOT NULL | 추천 이유 |
| trend_source | varchar(100) | NOT NULL | 데이터 출처 |
| generated_at | timestamptz | NOT NULL | 생성 시각 |

## 4-M. experiment_logs

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | uuid | PK | 실험 로그 ID |
| owner_name | varchar(100) | NOT NULL | 담당자명 |
| subject | varchar(255) | NOT NULL | 실험 주제 |
| hypothesis | text | NOT NULL | 가설 |
| result_summary | text | NULL | 결과 요약 |
| related_doc_path | varchar(500) | NULL | 문서 경로 |
| created_at | timestamptz | NOT NULL | 생성 시각 |

---

## 5. 인덱스 및 제약 조건

## 5-A. 핵심 인덱스

| 테이블 | 인덱스 | 목적 |
|---|---|---|
| users | unique(email) | 로그인 조회 |
| social_accounts | idx(user_id, channel) unique | 채널 중복 연동 방지 |
| content_projects | idx(user_id, created_at desc) | 이력 조회 |
| content_projects | idx(current_status) | 상태별 조회 |
| project_assets | idx(project_id) | 프로젝트별 자산 조회 |
| asset_derivatives | idx(asset_id, derivative_type) unique | derivative 중복 방지 |
| generation_runs | idx(project_id, created_at desc) | 최신 run 조회 |
| generation_run_steps | idx(generation_run_id, step_name) unique | step 상태 조회 |
| generated_variants | idx(generation_run_id) | 결과 조회 |
| upload_jobs | idx(project_id, created_at desc) | 게시 이력 조회 |
| upload_jobs | idx(status, channel) | 운영 모니터링 |
| schedule_jobs | idx(status, scheduled_for) | 예약 실행 스캐닝 |
| template_recommendations | idx(business_type, score desc) | 추천 조회 |

## 5-B. unique/제약

- `social_accounts (user_id, channel)` unique
- `asset_derivatives (asset_id, derivative_type)` unique
- `generation_run_steps (generation_run_id, step_name)` unique
- `generated_variants`는 한 run에서 여러 결과를 허용하되 `is_selected=true`는 최대 1개를 권장

## 5-C. soft delete 정책

MVP에서는 soft delete를 최소화합니다.

- 프로젝트 삭제는 숨김 처리보다 실제 삭제보다도 “보관” 관점으로 다루는 것이 바람직합니다.
- 외부 업로드 이력과 연결된 데이터는 hard delete보다 상태 기반 비활성화를 우선 검토합니다.

---

## 6. Object Storage 경로 규칙

### 6-A. canonical path

```text
/projects/{projectId}/raw/{assetId}.{ext}
/projects/{projectId}/processed/{assetId}_vertical.png
/projects/{projectId}/processed/{assetId}_square.png
/projects/{projectId}/processed/{assetId}_mask.png
/projects/{projectId}/runs/{generationRunId}/video.mp4
/projects/{projectId}/runs/{generationRunId}/post.png
/projects/{projectId}/runs/{generationRunId}/thumb.png
/projects/{projectId}/runs/{generationRunId}/render-meta.json
```

### 6-B. overwrite 금지 규칙

- 같은 generationRunId 아래 파일은 불변으로 간주합니다.
- regenerate는 새로운 `generationRunId`를 생성합니다.

### 6-C. render-meta.json 예시 필드

- `projectId`
- `generationRunId`
- `templateId`
- `style`
- `purpose`
- `usedAssetIds`
- `durationSec`
- `renderedAt`

---

## 7. Redis key 및 Queue 규칙

## 7-A. Queue 이름

- `job.preprocess`
- `job.generate_copy`
- `job.render_video`
- `job.render_post`
- `job.publish`
- `job.schedule_dispatch`

## 7-B. Redis key schema

| key pattern | 설명 | TTL |
|---|---|---|
| `project:status:{projectId}` | 최신 프로젝트 상태 캐시 | 10분 |
| `job:generation:{jobId}` | generation job 상태 캐시 | 10분 |
| `job:upload:{jobId}` | upload job 상태 캐시 | 10분 |
| `lock:project:{projectId}` | 동일 프로젝트 중복 generate 방지 | 2분 |
| `idempotency:{key}` | 중복 요청 응답 저장 | 24시간 |
| `rate:user:{userId}:generate` | 생성 요청 rate limit | 1분 |

## 7-C. lock 정책

- 동일 프로젝트에 대해 동시에 generate/regenerate를 2개 이상 진행하지 않습니다.
- lock 획득 실패 시 `409 Conflict`

## 7-D. status cache 원칙

- Redis는 source of truth가 아닙니다.
- 최종 진실은 PostgreSQL입니다.
- polling 응답 성능을 위해 캐시만 사용합니다.

---

## 8. 저장소 폴더 구조 canonical

```text
AI6_5Team_Advanced_Project/
├─ apps/
│  └─ web/
│     ├─ src/app/
│     ├─ src/features/
│     ├─ src/components/
│     ├─ src/lib/
│     └─ public/
├─ services/
│  ├─ api/
│  │  ├─ app/api/
│  │  ├─ app/core/
│  │  ├─ app/models/
│  │  ├─ app/schemas/
│  │  ├─ app/services/
│  │  ├─ app/repos/
│  │  └─ app/workflows/
│  └─ worker/
│     ├─ jobs/
│     ├─ pipelines/
│     ├─ renderers/
│     ├─ adapters/
│     └─ utils/
├─ packages/
│  ├─ contracts/
│  ├─ template-spec/
│  └─ shared-assets/
├─ docs/
├─ samples/
├─ infra/
└─ scripts/
```

### 8-A. 경로별 책임

| 경로 | 책임 |
|---|---|
| `apps/web` | UI/폴링/입력/결과 확인 |
| `services/api` | REST API, 검증, 상태 조회, 작업 등록 |
| `services/worker` | 전처리, 생성, 업로드, 예약 실행 |
| `packages/contracts` | enum, payload schema, shared types |
| `packages/template-spec` | 템플릿 및 카피 규칙 |
| `packages/shared-assets` | 폰트, 아이콘, 공용 리소스 |

### 8-B. 하위 폴더 역할 상세

| 경로 | 정확한 역할 | 포함하지 말아야 할 것 |
|---|---|---|
| `apps/web/src/app` | 라우트, 레이아웃, 페이지 진입점, 서버/클라이언트 화면 조합 | 비즈니스 로직의 실제 source of truth, DB 접근 코드 |
| `apps/web/src/features` | 화면 단위 기능 조합, 폼 흐름, polling/view-model, 사용자 액션 wiring | 재사용 공용 UI primitive, 직접 SQL/ORM 접근 |
| `apps/web/src/components` | 재사용 가능한 공용 UI 컴포넌트 | 프로젝트별 상태 오케스트레이션 |
| `apps/web/src/lib` | API client, auth helper, formatter, 화면 공통 유틸 | 화면별 고유 정책이나 서버 전용 로직 |
| `services/api/app/api` | REST endpoint, request parsing, response mapping | DB 세부 쿼리, 렌더링 파이프라인 구현 |
| `services/api/app/core` | 설정, 인증, 예외, 미들웨어, 공통 부트스트랩 | 도메인별 use case 로직 |
| `services/api/app/models` | ORM 모델, DB 테이블 매핑 | HTTP request/response schema |
| `services/api/app/schemas` | API DTO, validation schema, contract adapter | ORM 직접 호출 |
| `services/api/app/services` | use case orchestration, 상태 전이, worker 호출 조정 | 저수준 DB 연결 세부 구현 |
| `services/api/app/repos` | DB read/write, query 캡슐화 | HTTP 문맥, 화면 정책 |
| `services/api/app/workflows` | 비동기 작업 등록, projection 재계산, 상태 동기화 | 프론트 표시 로직 |
| `services/worker/jobs` | queue consumer entrypoint, job dispatch | 비즈니스 규칙의 상세 step 구현 |
| `services/worker/pipelines` | preprocess/generate/render/publish step orchestration | HTTP endpoint 처리 |
| `services/worker/renderers` | FFmpeg, 이미지/영상/post 렌더링 구현 | 인증/세션 처리 |
| `services/worker/adapters` | LLM, SNS API, storage, 외부 서비스 adapter | 화면 상태 관리 |
| `services/worker/utils` | worker 내부 순수 유틸과 공통 helper | 계약 enum의 원본 정의 |
| `packages/contracts` | enum, shared schema, 상태값, 예시 payload의 단일 기준 | 앱/서비스 구현 세부사항 import |
| `packages/template-spec` | 템플릿 JSON, 카피 규칙, 텍스트/레이아웃 spec | 런타임 상태 저장, API handler |
| `packages/shared-assets` | 폰트, 오버레이, 아이콘, 공용 시각 asset | 비즈니스 로직 |
| `docs` | 계획, 기준, 회의/결정 문서 | 런타임 import 대상 |
| `samples` | 데모 입력물, fixture, QA 재현 샘플 | 프로덕션 source of truth |
| `infra` | docker compose, 배포 설정, 인프라 템플릿, 운영 환경 정의 | 앱 비즈니스 로직 |
| `scripts` | 개발/운영 보조 스크립트, 검증, 데이터 준비 자동화 | 서비스 런타임 핵심 로직 |

### 8-C. 모듈 경계 규칙

- `apps/web`은 `packages/contracts`를 참조할 수 있지만 `services/api`, `services/worker`의 내부 코드를 직접 import하지 않습니다.
- `services/api`와 `services/worker`는 상태값/enum/schema를 `packages/contracts`에서 공유하고, 서로의 내부 디렉터리를 직접 import하지 않습니다.
- `services/api/app/services`는 `repos`를 호출할 수 있지만, `api` 레이어가 `repos`를 직접 호출하는 구조는 피합니다.
- `services/worker/pipelines`는 `renderers`, `adapters`, `utils`를 조합하는 orchestration 레이어이며, 계약 변경이 필요하면 먼저 `packages/contracts`를 수정합니다.
- `packages/*`는 하위 앱/서비스 구현체에 의존하지 않는 순수 공유 모듈로 유지합니다.
- `docs`, `samples`, `infra`, `scripts`는 비실행 보조 자산이며, 프로덕션 코드의 import 경로로 사용하지 않습니다.

---

## 9. packages/contracts 구조

```text
packages/contracts/
├─ enums/
│  ├─ businessType.ts
│  ├─ purpose.ts
│  ├─ style.ts
│  ├─ channel.ts
│  └─ status.ts
├─ schemas/
│  ├─ auth.ts
│  ├─ project.ts
│  ├─ asset.ts
│  ├─ generation.ts
│  ├─ publish.ts
│  ├─ schedule.ts
│  ├─ uploadAssist.ts
│  └─ socialAccount.ts
├─ examples/
│  ├─ register.request.json
│  ├─ create-project.request.json
│  ├─ generate.request.json
│  ├─ publish.request.json
│  └─ assist-complete.request.json
└─ README.md
```

### contracts에 반드시 있어야 하는 것

1. enum source of truth
2. API request/response schema
3. worker payload schema
4. error code 목록

---

## 10. packages/template-spec 구조

```text
packages/template-spec/
├─ templates/
│  ├─ T01-new-menu.json
│  ├─ T02-promotion.json
│  ├─ T03-location-push.json
│  └─ T04-review.json
├─ styles/
│  ├─ default.json
│  ├─ friendly.json
│  └─ b_grade_fun.json
├─ copy-rules/
│  ├─ new_menu.json
│  ├─ promotion.json
│  ├─ review.json
│  └─ location_push.json
└─ manifests/
   └─ template-map.json
```

### 10-A. template JSON 최소 스키마 예시

```json
{
  "templateId": "T01",
  "title": "신메뉴 티저형",
  "supportedBusinessTypes": ["cafe", "restaurant"],
  "supportedPurposes": ["new_menu"],
  "supportedStyles": ["default", "friendly"],
  "scenes": [
    { "sceneId": "s1", "durationSec": 1.4, "slot": "hook" },
    { "sceneId": "s2", "durationSec": 1.8, "slot": "product" },
    { "sceneId": "s3", "durationSec": 1.6, "slot": "benefit" },
    { "sceneId": "s4", "durationSec": 1.2, "slot": "cta" }
  ]
}
```

### 10-B. style preset JSON 최소 스키마 예시

```json
{
  "styleId": "friendly",
  "textTone": "soft",
  "colorPreset": "warm",
  "motionPreset": "light_pop",
  "captionLength": "short"
}
```

### 10-C. copy rule JSON 최소 스키마 예시

```json
{
  "purpose": "new_menu",
  "structure": ["hook", "product_name", "difference", "cta"],
  "regionPolicy": {
    "minSlots": 2,
    "maxRepeat": 3
  }
}
```

---

## 11. 샘플/문서/실험 산출물 구조

```text
samples/
├─ input/
│  ├─ cafe/
│  └─ restaurant/
├─ expected-output/
│  ├─ videos/
│  ├─ posts/
│  └─ copy/
└─ demo-scenarios/

docs/
├─ planning/
├─ experiments/
├─ adr/
├─ daily/
└─ testing/
```

### 11-A. 왜 samples가 중요한가

- 팀원별 숏폼 비교 실험의 동일 입력 기준이 됩니다.
- 발표 데모와 테스트를 반복 재현할 수 있습니다.

### 11-B. experiments와 DB를 분리하는 이유

- 실험 로그는 분석 문서이므로 Markdown 기반이 더 적합합니다.
- DB에는 운영 메타데이터만 남기고, 상세 reasoning/결론은 문서로 남깁니다.

---

## 12. 코드 오너십 및 변경 규칙

### 12-A. 코드 오너십

| 영역 | 1차 책임 |
|---|---|
| `apps/web` | 프론트/UI 담당 |
| `services/api` | API/상태 관리 담당 |
| `services/worker` | 전처리/렌더/업로드 담당 |
| `packages/contracts` | PM/통합 담당 + 백엔드 |
| `packages/template-spec` | 숏폼/카피 정책 담당 |
| `docs/experiments` | 실험 담당자 |

### 12-B. 변경 규칙

1. `packages/contracts` 변경 시 프론트/API/Worker 동시 영향 검토가 필요합니다.
2. `packages/template-spec` 변경 시 결과물 샘플 업데이트가 권장됩니다.
3. `content_projects`와 `generation_runs` 관계를 바꾸는 변경은 ADR로 남겨야 합니다.
4. 상태 enum 추가/변경은 [04_API_CONTRACT.md](04_API_CONTRACT.md)와 동시에 수정합니다.

### 12-C. Definition of Done 관점에서 필요한 것

- 스키마 변경 문서화
- 예시 payload 또는 sample output 갱신
- 영향받는 상태값 반영
- 실험 또는 테스트 결과 기록
