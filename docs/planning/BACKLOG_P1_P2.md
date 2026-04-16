# BACKLOG_P1_P2

> **문서 목적**: 계획 문서를 실제 구현 순서로 번역한 실행 백로그입니다.

## P1 Must

| ID | 작업 | 결과물 | 담당 영역 |
|---|---|---|---|
| P1-01 | contracts 패키지에 enum/상태값 정의 | shared enum | contracts |
| P1-02 | 프로젝트 생성/조회 API 구현 | `/api/projects` | api |
| P1-03 | 사진 업로드 API 및 storage 연결 | `/assets` | api |
| P1-04 | 이미지 전처리 워커 구현 | preprocess job | worker |
| P1-05 | 템플릿 4종(T01~T04) JSON 정의 | template-spec | template-spec |
| P1-06 | 카피 생성 규칙 구현 | copy rule | worker |
| P1-07 | 숏폼 렌더링 파이프라인 구현 | mp4 결과물 | worker |
| P1-08 | 결과 조회 API 구현 | `/status`, `/result` | api |
| P1-09 | 생성 마법사 UI 구현 | 생성 플로우 | web |
| P1-10 | 결과 화면 + quick action UI 구현 | 결과/재생성 | web |
| P1-11 | `instagram` 1채널 업로드/업로드 보조 구현 | publish flow + assist fallback | api + worker |
| P1-12 | 실험 로그/테스트 기록 시작 | docs evidence | docs |

## P1 Should

| ID | 작업 | 결과물 | 담당 영역 |
|---|---|---|---|
| P1-13 | 배경 제거 품질 개선 | derivative asset | worker |
| P1-14 | 생성 이력 목록 UI | history page | web |
| P1-15 | SNS OAuth 콜백 및 토큰 만료 처리 | callback + reconnect flow | api |
| P1-16 | 계정 연동 UX/문구 개선 | connect UX polish | web |

## P2 Could

| ID | 작업 | 결과물 | 담당 영역 |
|---|---|---|---|
| P2-01 | 예약 발행 구현 | `/schedule` | api + worker |
| P2-02 | 다중 채널 동시 업로드 | multi publish | api + worker |
| P2-03 | 업종 확장 | new business types | template-spec |
| P2-04 | 성과 리포트 | analytics page | web + api |

## Research Later

| ID | 작업 | 결과물 | 담당 영역 |
|---|---|---|---|
| R-01 | 추천 템플릿 조회 API 및 배치 갱신 | recommendations | api + worker |
| R-02 | 생성형 비디오 인트로 실험 | experiment output | worker |
| R-03 | `Gemma 4` 포함 생성 모델 벤치마크 | benchmark doc + scorecard + baseline 제안 | worker + docs |
