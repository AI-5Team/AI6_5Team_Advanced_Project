# EXP-89 Upload assist action UX

## 1. 기본 정보

- 실험 ID: `EXP-89`
- 작성일: `2026-04-09`
- 작성자: Codex
- 관련 기능: `본선 결과 패키징 / upload assist UX`

## 2. 왜 이 작업을 했는가

- `EXP-88`으로 result/history가 실제 media payload를 다시 소비하게 만들었지만, upload assist 패키지는 여전히 `캡션 텍스트 표시` 수준에 머물러 있었습니다.
- planning 기준의 upload assist는 단순 상태 전이가 아니라, 사용자가 실제로 `열기`, `복사`, `다운로드`, `완료`까지 이어갈 수 있어야 합니다.
- 그래서 이번 작업은 새 생성 실험이 아니라, `assist package가 실제 행동 단위 UX가 되는가`를 검증하는 데 목적이 있었습니다.

## 3. baseline

### 실험 전 상태

1. `demo-workbench`
   - assist package가 열리면 캡션 한 줄과 hashtag pill만 보였습니다.
   - 사용자는 직접 텍스트를 선택하거나 별도 경로로 미디어를 찾아야 했습니다.
2. `history-board`
   - 최신 upload assist 패키지가 있어도 `thumbnailText`만 보였습니다.
   - 실제 수동 업로드 행동으로 이어지는 버튼은 없었습니다.
3. runtime payload
   - API는 이미 `mediaUrl`, `caption`, `hashtags`, `thumbnailText`를 주고 있었습니다.

### 이번에 검증한 가설

- assist payload를 공통 패널로 묶고 `열기 / 다운로드 / 복사 / 순서 안내`를 제공하면, 본선 서비스의 upload assist 경로 정렬도가 올라갑니다.

## 4. 무엇을 바꿨는가

1. `apps/web/src/app/api/media-proxy/route.ts`
   - `/media/...`를 same-origin으로 프록시하고 다운로드 헤더를 붙일 수 있는 route를 추가했습니다.
2. `apps/web/src/lib/media-url.ts`
   - `buildMediaProxyUrl()`를 추가해 다운로드 링크 생성을 공통화했습니다.
3. `apps/web/src/components/upload-assist-panel.tsx`
   - assist package를 공통으로 렌더하는 client component를 추가했습니다.
   - 포함한 액션:
     - 영상 열기
     - 영상 다운로드
     - 게시글 열기
     - 게시글 다운로드
     - 캡션 복사
     - 해시태그 복사
     - 전체 복사
   - 썸네일 문구와 업로드 순서 안내도 함께 노출했습니다.
4. `apps/web/src/components/demo-workbench.tsx`
   - 기존 assistPackage 텍스트 블록을 공통 패널로 교체했습니다.
5. `apps/web/src/components/history-board.tsx`
   - history에서도 같은 assist package 행동 UX를 재사용하도록 연결했습니다.

## 5. 결과

### 확인된 것

1. upload assist가 더 이상 단순 안내 문구가 아니라 `실행 가능한 패키지`가 됐습니다.
2. result 화면과 history 화면 모두에서 동일한 행동 UX를 재사용할 수 있게 됐습니다.
3. same-origin media proxy가 생겨 다운로드 링크도 web 앱 내부에서 제공할 수 있게 됐습니다.

### 검증

- `npm run build:web`
  - Next.js production build 통과
  - `/api/media-proxy` 포함 전체 web 앱 타입/번들 검증 통과

## 6. 실패/제약

1. 이번 세션에서는 브라우저 수동 클릭까지는 하지 않았고, 검증은 build 기준입니다.
2. 클립보드 복사는 브라우저 권한 상태에 따라 실패할 수 있습니다.
3. media proxy는 현재 `/media/...` 경로만 허용합니다.

## 7. 결론

- 가설 충족 여부: **성공**
- 판단:
  - upload assist 경로가 planning에서 의도한 `수동 업로드 보조 패키지`에 한 단계 더 가까워졌습니다.
  - 이제 남은 다음 축은 `contracts/template spec 단일화`와 `브라우저 기준 시각 검증`입니다.

## 8. 다음 액션

1. `apps/web/src/lib/contracts.ts`와 canonical spec/packages의 중복 정의를 줄입니다.
2. result/history/upload assist를 실제 브라우저로 한 번 더 시각 점검합니다.
3. 필요하면 upload assist 완료 후 history/status 반영 문구를 더 명확히 다듬습니다.
