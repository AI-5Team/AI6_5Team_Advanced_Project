# EXP-10 HTML/CSS Scene Lab Prototype

## 1. 기본 정보

- 실험 ID: `EXP-10`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: 렌더 surface 전환, HTML/CSS 기반 scene prototype

## 2. 왜 이 실험을 추가했는가

- 현재 Pillow 기반 합성은 기술적 개선을 해도 제품 baseline으로 채택할 수준의 미감에 미치지 못했습니다.
- 따라서 다음 본선 방향으로 정리한 `HTML/CSS compositor`를 바로 코드로 시험할 필요가 있었습니다.

## 3. 이번 실험에서 바꾼 것

1. `apps/web`에 `/scene-lab` 페이지를 추가했습니다.
2. 실제 샘플 사진을 브라우저에서 직접 볼 수 있도록 `/api/sample-assets/[sample]` 라우트를 추가했습니다.
3. scene lab에서는 아래 원칙을 적용했습니다.
   - 억지 장식 문구 제거
   - 상품 사진, 혜택 텍스트, CTA만으로 장면 구성
   - 광고처럼 보이는 typography와 block composition 우선

## 4. 구현 파일

- `apps/web/src/app/scene-lab/page.tsx`
- `apps/web/src/app/api/sample-assets/[sample]/route.ts`
- `apps/web/src/components/app-nav.tsx`

## 5. 결과

### 확인된 것

1. 같은 샘플 자산이라도 HTML/CSS composition 쪽이 Pillow 실험보다 훨씬 자연스럽게 정돈된 장면을 만들 수 있는 기반이 있습니다.
2. 실제 사진을 직접 페이지에 연결해서 visual direction을 빠르게 바꿔볼 수 있게 됐습니다.
3. `사장님 손글씨` 같은 실험성 문구 없이도 scene이 성립하도록 방향을 바꿨습니다.

## 6. 실패/제약

1. 아직 worker 렌더 파이프라인과 연결한 것은 아닙니다.
2. 현재는 web prototype이며, 실제 영상 frame capture까지는 구현하지 않았습니다.
3. 브라우저 기반 screenshot/capture 자동화는 다음 단계입니다.

## 7. 결론

- 가설 충족 여부: **부분 충족**
- 판단:
  - Pillow보다 다른 렌더 surface가 맞다는 방향성은 더 강해졌습니다.
  - 이제 필요한 것은 `scene lab -> 실제 frame render`로 이어지는 연결입니다.

## 8. 다음 액션

1. HTML/CSS scene을 screenshot/frame으로 캡처하는 경로를 붙입니다.
2. 같은 자산으로 Pillow 결과와 HTML/CSS 결과를 직접 비교하는 실험을 만듭니다.
