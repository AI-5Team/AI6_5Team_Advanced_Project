# EXP-88 Product result media preview reconnect

## 1. 기본 정보

- 실험 ID: `EXP-88`
- 작성일: `2026-04-09`
- 작성자: Codex
- 관련 기능: `본선 결과 검증 / result-history media preview`

## 2. 왜 이 작업을 했는가

- `EXP-87`에서 확인한 핵심 문제 중 하나는, 본선 루프는 살아 있지만 결과 확인 화면이 실제 `video/post` 산출물을 충분히 보여주지 못한다는 점이었습니다.
- planning 기준으로는 생성 직후 결과 확인과 이력 재진입에서 실제 산출물을 다시 확인할 수 있어야 하는데, 현재 web은 텍스트 요약과 scenePlan 링크 중심으로 기울어져 있었습니다.
- 그래서 다음 실험은 새 video generation OVAT를 추가하는 대신, `본선 제품 루프가 실제 media payload를 제대로 소비하는가`를 검증하는 쪽으로 잡았습니다.

## 3. baseline

### 실험 전 상태

1. `apps/web/src/components/demo-workbench.tsx`
   - hero와 result 영역이 주로 synthetic preview + text summary 중심이었습니다.
   - `activeResult.video.url`, `activeResult.post.url`는 받아오지만 실제 결과 확인 UX에는 거의 쓰이지 않았습니다.
2. `apps/web/src/components/history-board.tsx`
   - history 상세에서 hook/CTA/hashtags와 scenePlan은 보였지만, 실제 video/post 미리보기는 없었습니다.
3. `apps/web/src/lib/api.ts`
   - API는 이미 `ProjectResultResponse.video.url`, `post.url`를 정상 노출하고 있었습니다.

### 이번에 검증한 가설

- 결과 확인 화면과 이력 화면에서 실제 media payload를 직접 소비하도록 연결하면, planning 기준의 `결과 확인 -> 재사용 -> 게시/보조` 루프 정렬도가 올라갑니다.

## 4. 무엇을 바꿨는가

1. `apps/web/src/lib/media-url.ts`
   - `/media/...`와 `/projects/...` 경로를 `NEXT_PUBLIC_API_BASE_URL` 기준으로 해석하는 헬퍼를 추가했습니다.
   - 로컬 샘플 자산 경로는 기존 `/api/local-media` 경로를 재사용하도록 맞췄습니다.
2. `apps/web/src/components/result-media-preview.tsx`
   - 결과 payload를 받아 `숏폼 미리보기`와 `게시글 미리보기`를 공통으로 렌더하는 컴포넌트를 추가했습니다.
   - 각 미리보기에서 원본 열기 링크도 함께 노출하도록 했습니다.
3. `apps/web/src/components/demo-workbench.tsx`
   - hero 카드가 생성 결과가 있을 때 실제 `video.url`을 배경 미리보기처럼 보여주도록 바꿨습니다.
   - result 패널에 실제 `video/post` 미리보기를 추가했습니다.
4. `apps/web/src/components/history-board.tsx`
   - history 상세에도 최근 결과의 실제 `video/post` 미리보기를 추가했습니다.

## 5. 결과

### 확인된 것

1. main result 화면과 history 화면 모두에서 실제 `ProjectResultResponse.video.url`, `post.url`를 직접 소비하는 경로가 생겼습니다.
2. media URL은 `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000` 기준으로 절대 URL 해석이 가능해졌습니다.
3. 텍스트 요약만 보던 상태보다 `결과 확인 -> 게시/보조 판단` 맥락이 더 planning 친화적으로 바뀌었습니다.

### 검증

- `npm run build:web`
  - Next.js production build 통과
  - `/`, `/history` 포함 전체 web 앱 타입/번들 검증 통과

## 6. 실패/제약

1. 이번 실험은 web 소비층 복구이지, worker render 품질 자체를 올린 것은 아닙니다.
2. 업로드 보조 패키지의 `복사/다운로드/완료 가이드` UX는 아직 별도 후속 작업이 필요합니다.
3. 실제 브라우저 수동 점검까지는 이번 세션에서 수행하지 않았고, 현재 검증은 build 기준입니다.

## 7. 결론

- 가설 충족 여부: **부분 성공**
- 판단:
  - `result/history가 실제 media payload를 소비해야 한다`는 본선 기준에는 맞게 복구됐습니다.
  - 다만 이것만으로 본선 UX가 닫힌 것은 아니며, 다음은 upload assist 사용 액션과 canonical spec 정렬을 붙여야 합니다.

## 8. 다음 액션

1. upload assist 패키지에 `caption 복사`, `hashtags 복사`, `media 열기/다운로드`, `완료 안내`를 명시적으로 붙입니다.
2. `apps/web/src/lib/contracts.ts`와 `packages/contracts`, `packages/template-spec`의 중복 정의를 줄이는 정리 작업으로 넘어갑니다.
3. result/history를 실제 브라우저 기준으로 한 번 더 시각 점검합니다.
