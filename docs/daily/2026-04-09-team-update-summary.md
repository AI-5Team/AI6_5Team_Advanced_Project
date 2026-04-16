# 2026-04-09 팀 공유용 근황 요약

## 한 줄 요약

- 최근 연구선이 `local LTX video baseline` 쪽으로 많이 기울어 있었고, 오늘은 그 방향을 다시 점검한 뒤 `본선 제품 루프 복귀`를 우선순위로 재정렬했습니다.

## 오늘 핵심 판단

1. 지금까지의 작업이 완전히 샌 것은 아닙니다.
   - `생성 -> 결과 확인 -> quick action -> publish/assist -> history` 본선 루프는 이미 꽤 살아 있습니다.
2. 다만 최근 비중은 본선 구현보다 `local LTX baseline` 미세 조정에 더 크게 실려 있었습니다.
3. 그래서 다음 우선순위는 새 video OVAT를 더 쌓는 것보다, `본선 UX/계약 기준선 정리`가 맞다고 판단했습니다.

## 오늘 실제로 한 일

### 1. 방향 점검

- `EXP-87`로 현재 진행 방향을 기획 문서 기준으로 다시 감사했습니다.
- 결론:
  - 연구선은 의미가 있었지만 최근에는 본선보다 앞서갔습니다.
  - 지금은 `새 실험 추가`보다 `본선 복귀`가 우선입니다.

### 2. 본선 결과 확인 UX 복구

- `EXP-88`
- result/history 화면이 이제 실제 `result.video.url`, `result.post.url`를 직접 소비합니다.
- 즉, 텍스트 요약만 보던 상태에서 실제 산출물을 다시 확인할 수 있게 바꿨습니다.

### 3. upload assist를 실제 행동 UX로 변경

- `EXP-89`
- upload assist 패키지에 아래 액션을 붙였습니다.
  - 영상 열기
  - 영상 다운로드
  - 게시글 열기/다운로드
  - 캡션 복사
  - 해시태그 복사
  - 전체 복사
  - 완료 전 순서 안내

### 4. web 기준선 단일화 시작

- `apps/web/src/lib/contracts.ts`가 들고 있던 enum/API contract 중복을 줄였습니다.
- `@ai65/contracts`를 `apps/web`에서 직접 쓰도록 연결했습니다.
- `TEMPLATES`, `STYLE_PRESETS`, `COPY_RULES`도 로컬 하드코딩 대신 `packages/template-spec` JSON을 직접 읽도록 바꿨습니다.
- `demo-workbench` 안의 로컬 템플릿 매핑 표도 제거해서, UI가 canonical template 기준을 직접 보도록 정리했습니다.

## 지금 상태 요약

### 맞게 가고 있는 축

- 본선 서비스 루프는 살아 있습니다.
- 결과 확인 UX와 upload assist UX는 오늘 기준으로 더 제품형에 가까워졌습니다.
- web이 canonical `contracts`와 `template-spec`을 직접 읽기 시작해서, 이후 drift 가능성도 줄었습니다.

### 아직 남아 있는 것

- `demo-store` 안에는 아직 `TemplateId`와 일부 snapshot/local alias가 남아 있습니다.
- upload assist는 build 기준 검증은 끝났지만, 실제 브라우저 클릭 QA는 한 번 더 필요합니다.
- 문제 적합성 검증이나 사용자 인터뷰 쪽은 여전히 약합니다.

## 다음 우선순위

1. `demo-store`의 남은 local alias 정리
2. result/history/upload assist 브라우저 실사용 QA
3. 본선 루프 기준의 사용자 검증 또는 운영 시나리오 점검

## 관련 문서

- `docs/experiments/EXP-87-current-direction-review-and-priority-reset.md`
- `docs/experiments/EXP-88-product-result-media-preview-reconnect.md`
- `docs/experiments/EXP-89-upload-assist-action-ux.md`
- `docs/daily/2026-04-09-codex.md`
