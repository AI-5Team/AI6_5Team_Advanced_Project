# EXP-226 Current Direction Review Before Video Baseline

## 1. 목적

- 다음 영상 실험을 바로 실행하기 전에, 현재 진행방향이 서비스 기획 의도와 맞는지 다시 점검했습니다.
- 핵심 질문은 `이제 영상 baseline으로 우선순위를 옮기는 것이 맞는가`입니다.
- 이번 문서는 새 생성 실험이 아니라 방향성 감사 문서입니다.

## 2. 검토한 기준 문서

- `HISTORY.md`
- `docs/daily/2026-04-09-codex.md`
- `docs/daily/2026-04-13-codex.md`
- `docs/planning/README.md`
- `docs/planning/01_SERVICE_PROJECT_PLAN.md`
- `docs/planning/03_CONTENT_PIPELINE_AND_TEMPLATE_SPEC.md`
- `docs/planning/06_EVALUATION_TEST_AND_OPERATIONS.md`
- `docs/planning/08_DOCUMENTATION_POLICY.md`
- `docs/adr/ADR-002-deterministic-copy-and-render-baseline.md`
- `docs/adr/ADR-005-b-grade-video-first-experiment-priority.md`
- `docs/adr/ADR-006-service-loop-aligned-b-grade-experiment-baseline.md`
- `docs/adr/ADR-009-bound-renderer-spike-and-resume-generation-experiments.md`
- `docs/experiments/EXP-87-current-direction-review-and-priority-reset.md`
- `docs/experiments/EXP-90-upper-bound-video-benchmark-pilot.md`
- `docs/experiments/EXP-91-sora2-motion-prompt-family-ovaat.md`
- `docs/experiments/EXP-92-sora2-input-framing-ovaat.md`
- `docs/experiments/EXP-93-sora2-edit-motion-recovery-ovaat.md`
- `docs/experiments/EXP-94-reference-first-video-direction-review.md`
- `docs/experiments/EXP-95-reference-teardown-pattern-matrix.md`
- `docs/experiments/EXP-96-reference-template-fit-scorecard.md`
- `docs/experiments/EXP-97-self-serve-ai-ad-platform-patterns.md`
- `docs/experiments/EXP-225-video-baseline-reset-after-copy-freeze.md`

## 3. 총평

- 결론부터 말하면, 영상 baseline으로 우선순위를 옮기는 것은 맞습니다.
- 다만 의미를 좁혀야 합니다. 다음 작업은 `생성형 영상 모델을 본선으로 삼기 위한 실험`이 아니라, `본선 템플릿 숏폼 대비 생성형 영상이 보조 또는 대체 후보가 될 수 있는지 판정하는 baseline`이어야 합니다.
- `docs/planning/01_SERVICE_PROJECT_PLAN.md`는 핵심 제작 방식을 `템플릿 기반 영상 조합 우선`으로 고정하고, 생성형 비디오는 `메인 기능이 아닌 실험 모듈`로 분리합니다.
- 따라서 다음 영상 baseline은 제품 본선을 흔드는 방향이 아니라, 본선의 약점을 보완할 수 있는지 검증하는 제한된 비교로 설계해야 합니다.

## 4. 지금 맞는 축

### 4.1 카피 baseline 동결

- `EXP-221`, `EXP-222` 이후 prompt baseline quick-option catalog는 `exact_match=24`, quick option gap `0`까지 정리됐습니다.
- `EXP-223`, `EXP-224`는 review fallback 판단을 모델 품질이 아니라 transport repeatability 관점으로 다시 정리했습니다.
- 따라서 카피를 더 미세조정하기보다 영상 품질 / 보존성 / 반복 안정성으로 질문을 옮긴 `EXP-225` 판단은 타당합니다.

### 4.2 영상 문제를 다시 본선 병목으로 보는 판단

- `EXP-90`은 local LTX가 구조 보존은 일부 되지만 실제 motion 설득력이 약하다는 점을 확인했습니다.
- `EXP-91`은 Sora 2에서 motion prompt를 강하게 써도 motion 회복이 되지 않고 near-static 쪽으로 수렴한다는 점을 보였습니다.
- `EXP-92`는 input framing을 타이트하게 만들수록 보존성은 좋아지지만 motion은 더 줄어드는 trade-off를 확인했습니다.
- `EXP-93`은 edit 2단계도 motion을 일부 회복할 수는 있지만 보존성 손실이 커 production 후보로 보기 어렵다고 정리했습니다.
- 즉 `single-photo + preserve image` 조건의 한계가 여러 번 반복 확인됐기 때문에, 이 지점에서 영상 baseline을 다시 잡는 것은 맞습니다.

### 4.3 레퍼런스를 템플릿으로 환원하려는 흐름

- `EXP-94`부터 `EXP-97`까지의 흐름은 잘 맞습니다.
- 외부 레퍼런스를 `좋아 보이는 영상`으로만 보지 않고, `hook / shot / motion / packaging / self-serve 반복 생산성`으로 쪼갰기 때문입니다.
- 특히 `EXP-96`의 template-fit scorecard는 서비스 목표인 `자영업자가 쉽게 반복 생산`하는 방향과 잘 맞습니다.

## 5. 방향이 샌 축

### 5.1 생성형 영상 모델 자체를 본선처럼 다루는 해석

- 기획 문서상 본선은 `템플릿 기반 숏폼 + 게시글 + 캡션 세트 + 업로드/업로드 보조`입니다.
- `Veo`, `Sora`, `LTX` 결과를 본선 대체 후보처럼 해석하면 기획과 어긋납니다.
- 특히 `manual Veo`는 맥주 샘플에서 품질 참고점으로는 좋았지만, 규카츠 샘플에서는 QR/주변 객체 재구성으로 원본 보존 요구를 깨뜨렸습니다.
- 따라서 manual Veo는 계속 `quality upper-bound reference only`로만 봐야 합니다.

### 5.2 prompt phrase / crop / edit 미세 OVAT 반복

- `EXP-91`, `EXP-92`, `EXP-93`에서 이미 raw prompt, input framing, edit가 같은 preserve-motion trade-off에 걸린다는 신호가 충분히 나왔습니다.
- 여기서 같은 single-photo 조건 안에서 phrase나 crop만 계속 바꾸는 것은 기획 기준의 `템플릿 기반 생산성`과도 멀어지고, 실험 수익도 작습니다.

### 5.3 본선 control 없이 모델끼리만 비교하는 실험

- 다음 baseline에서 `local LTX`, `Sora 2`, `manual Veo`만 비교하면 여전히 연구선 내부 비교입니다.
- 기획 정렬 관점에서는 반드시 `template motion + compositor` 또는 현재 deterministic renderer 산출물을 control로 둬야 합니다.
- 이유는 이 서비스의 실제 기본값이 생성형 비디오가 아니라 템플릿 기반 숏폼이기 때문입니다.

## 6. 영상 baseline 전환 적합성 판단

- 판단: `조건부 적합`입니다.
- 적합한 이유:
  - 카피 baseline의 추가 수익이 작아졌습니다.
  - 영상 품질 / 보존성 / motion이 현재 사용자가 체감할 병목입니다.
  - `EXP-90`부터 `EXP-93`까지 같은 한계가 반복되어, 다음에는 명확한 baseline 판정이 필요합니다.
- 조건:
  - 생성형 영상 모델을 본선으로 가정하지 않습니다.
  - 본선 control을 같이 둡니다.
  - manual Veo는 production 후보가 아니라 upper-bound reference로만 둡니다.
  - single-photo phrase 미세조정은 중단합니다.
  - 비교 기준은 `원본 보존성`, `실제 motion 체감`, `반복 실행 안정성`, `템플릿/패키징 적합성` 4개로 고정합니다.

## 7. 바로 다음 우선순위 3개

### 1순위: product baseline control 확정

- 다음 영상 비교 전에 현재 본선 control을 먼저 잡아야 합니다.
- 후보는 `template motion + compositor` 또는 현 deterministic renderer 기반 `video.mp4 / post.png / captions / hashtags` 패키지입니다.
- 이유는 생성형 모델 결과가 아무리 좋아도, 본선 템플릿보다 self-serve 반복 생산성과 원본 보존성이 낮으면 서비스 기준에서는 채택하기 어렵기 때문입니다.

### 2순위: 제한된 영상 baseline 비교

- 비교 대상은 `본선 control`, `local LTX current best`, `Sora 2 current best`, `manual Veo reference`로 제한합니다.
- 샘플은 기존과 같이 `규카츠`, `맥주` 2개면 충분합니다.
- 판정 기준은 `보존성 / motion / repeatability / packaging fit`입니다.
- 이 단계에서는 새 모델을 계속 추가하지 않습니다.

### 3순위: 결과에 따른 분기

- 본선 control이 더 안정적이면 `template motion + compositor`를 계속 기본축으로 두고, 생성형 영상은 hero/detail clip 보조 모듈로만 둡니다.
- 생성형 후보가 둘 이상 기준을 통과하면 `input modality change`로 넘어갑니다.
  - 예: first/last frame, multi-reference, masked/local motion
- 생성형 후보가 품질은 좋지만 보존성을 깨면 `creative reinterpretation mode`로 분리하고, 본선에는 넣지 않습니다.

## 8. 다음 실험 설계 가드

- 다음 실험의 질문은 `어느 모델이 더 예쁜가`가 아니어야 합니다.
- 질문은 `자영업자용 템플릿 서비스의 기본 숏폼 생성 경로를 대체하거나 보조할 수 있는가`여야 합니다.
- 따라서 다음 실험 문서에는 아래 4개 항목이 반드시 있어야 합니다.
  1. 본선 control 대비 차이
  2. 원본 보존 실패 사례
  3. 실제 motion 체감
  4. 결과물 패키징 적합성

## 9. 결론

- 영상 baseline으로 이동하는 판단은 맞습니다.
- 그러나 그 baseline은 `AI video model research`가 아니라 `product baseline decision`이어야 합니다.
- 바로 다음 세션에서는 새 모델을 넓히기보다, 본선 control을 세우고 기존 후보군을 제한적으로 비교하는 방식이 가장 기획과 맞습니다.
