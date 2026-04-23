# Prototypes

기획서 기준 흐름을 빠르게 시연/리뷰하기 위한 독립 실행 프로토타입 모음입니다.
제품 런타임(`apps/web`)과는 완전히 분리되어 있으며, 빌드나 서버 없이 브라우저에서 바로 열 수 있습니다.

## web-flow-prototype.html

`docs/planning/02_USER_FLOW_AND_SCREEN_POLICY.md`의 SC-01 ~ SC-14 흐름을 단일 HTML 파일로 구현한 UX 프로토타입.

### 실행

```bash
open "docs/prototypes/web-flow-prototype.html"
# 또는 루트에서 간단한 정적 서버
python3 -m http.server 8000
# http://localhost:8000/docs/prototypes/web-flow-prototype.html
```

### 포함 화면

- SC-01 로그인
- SC-02 홈 (새 작업 + 최근 이력 + SNS 계정 요약)
- SC-03 업종 선택 (cafe / restaurant)
- SC-04 위치 입력 (regionName 2~20자, detailLocation 0~30자)
- SC-05 목적 선택 (new_menu / promotion / review / location_push)
- SC-06 스타일 선택 (default / friendly / b_grade_fun)
- SC-07 채널 선택 (instagram ready, youtube_shorts / tiktok experimental)
- SC-08 사진 업로드 (1~5장, jpg/png, 10MB, 경고는 차단 아님)
- SC-09 생성 진행 (preprocessing → copy_generation → video_rendering → post_rendering → packaging)
- SC-10 결과 확인 (캡션 후보 3개, 해시태그, CTA, 즉시 업로드 / 업로드 보조 / 빠른 수정)
- SC-11 빠른 수정 (6개 change set chip)
- SC-12 업로드/예약 (publishMode=auto 는 instagram 연동 시에만, assist는 파일 다운로드 + 완료 확인)
- SC-13 계정 연동 (연결 상태 5종 mock)
- SC-14 생성 이력 + 이력 상세

### 특징

- 빌드 없음, 외부 CDN 없음 — 오프라인에서도 동작
- 모바일 기준 폭(440px) 고정 캔버스 + 큰 버튼(≥56px), 중장년층 가독성 고려
- 상태는 메모리(JS 객체)에만 존재하므로 새로고침 시 초기화됨
- 생성은 약 4.5초 mock timeline, 캡션은 업종·지역·목적·빠른수정 조합으로 동적 생성

### 범위 밖

- 실제 API/Worker 연동 없음 — `packages/contracts` 또는 `services/api`와는 연결되지 않음
- Phase 2 예약 발행, Phase 3 템플릿 추천은 제외
- 보안/인증 로직은 입력 유효성 수준만 구현 (토큰·세션 없음)
