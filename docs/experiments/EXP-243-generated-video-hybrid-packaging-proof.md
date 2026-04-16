# EXP-243 Generated Video Hybrid Packaging Proof

## 1. 기본 정보

- 실험 ID: `EXP-243`
- 작성일: `2026-04-14`
- 작성자: Codex
- 관련 기능: `generated shot + template overlay hybrid packaging proof`

## 2. 왜 이 작업을 했는가

- `EXP-242`까지로 `edit path`도 tray lane에서 의미 있는 해답이 아니라는 점이 확인됐습니다.
- 하지만 이 서비스의 목표는 `모델이 raw clip 하나를 완벽하게 만들게 하는 것`이 아니라, `자영업자가 템플릿 기반 숏폼 광고를 쉽게 만들게 하는 것`입니다.
- 따라서 다음 질문은 `raw 생성컷 품질을 더 깎을 것인가`가 아니라, `생성컷을 템플릿 오버레이 안에 넣었을 때 서비스 적합성이 올라가는가`였습니다.

## 3. 실험 질문

1. raw Sora clip 위에 `b_grade_fun` 오버레이를 얹으면 광고 문법이 더 분명해지는가
2. 이 방식이 현재 `product control`과 `real video lane` 사이의 현실적인 중간안이 될 수 있는가
3. 생성 품질 문제와 패키징 문제를 분리해 다룰 가치가 있는가

## 4. 실행 조건

### 4.1 source clip

- `EXP-241 baseline_auto / 규카츠`

선정 이유:

- tray lane Sora 결과 중 이번 세션에서 가장 무난했던 raw clip입니다.
- 같은 source 하나를 고정하고 packaging 효과만 보기에 적합합니다.

### 4.2 하이브리드 방식

1. source video는 그대로 유지
2. `HOOK`, `DETAIL`, `CTA` lower-third overlay PNG를 시간대별로 분리 생성
3. `ffmpeg overlay`로 4초 클립 위에 순차적으로 얹음

즉 이번 proof는 `생성된 배경 영상 + 템플릿형 B급 오버레이`만 검증합니다.

### 4.3 실행 커맨드

```bash
python -m py_compile scripts/generated_video_hybrid_packaging_proof.py
python scripts/generated_video_hybrid_packaging_proof.py --source-video "docs/experiments/artifacts/exp-241-sora2-gyukatsu-input-framing-live-ovaat/baseline_auto/규카츠/sora2_first_try.mp4" --output-dir "docs/experiments/artifacts/exp-243-generated-video-hybrid-packaging-proof"
ffmpeg -y -loglevel error -i "docs/experiments/artifacts/exp-243-generated-video-hybrid-packaging-proof/hybrid_packaged.mp4" -vf "fps=2,scale=320:-1,tile=8x1" -frames:v 1 "docs/experiments/artifacts/exp-243-generated-video-hybrid-packaging-proof/hybrid_contact_sheet_8up.png"
ffmpeg -y -loglevel error -i "docs/experiments/artifacts/exp-241-sora2-gyukatsu-input-framing-live-ovaat/baseline_auto/규카츠/sora2_first_try.mp4" -vf "fps=2,scale=320:-1,tile=8x1" -frames:v 1 "docs/experiments/artifacts/exp-243-generated-video-hybrid-packaging-proof/raw_contact_sheet_8up.png"
```

## 5. 실행 결과

artifact root:

- `docs/experiments/artifacts/exp-243-generated-video-hybrid-packaging-proof/`

### 5.1 raw source clip

- 관찰:
  - raw 상태에서는 규카츠 컷 자체는 그럭저럭 보이지만, 광고 문법은 약합니다.
  - `왜 이 영상을 봐야 하는지`, `무슨 행동을 해야 하는지`가 바로 보이지 않습니다.

### 5.2 hybrid packaged clip

- 적용 요소:
  - `HOOK`
  - `DETAIL`
  - `CTA`
  - `b_grade_fun` lower-third / badge
- 관찰:
  - raw clip 대비 `이게 광고 결과물이다`라는 인식이 훨씬 빨라집니다.
  - 첫 프레임부터 hook badge가 붙고, 중반 detail, 후반 CTA로 서비스 템플릿 문법에 더 가까워졌습니다.
  - raw source의 생성 품질 자체를 바꾸진 않지만, 서비스 적합성은 분명히 올라갑니다.

### 5.3 중요한 한계

1. 이 proof는 생성 quality 문제를 해결하지 않습니다.
2. source가 불안정하면 overlay를 얹어도 그 불안정성은 남습니다.
3. 즉 하이브리드는 `모델 품질 대체`가 아니라 `패키징 적합성 보강`입니다.

## 6. 해석

1. `real video lane`의 문제를 전부 모델 하나로 해결하려고 하면 계속 막힙니다.
2. 반대로 `생성된 shot`과 `광고 패키징`을 분리하면, 적어도 서비스가 원하는 최종 산출물에 더 가까워질 수 있습니다.
3. 이번 proof는 `raw generation 품질이 완벽하지 않아도, packaging layer를 얹으면 서비스 fit을 실질적으로 끌어올릴 수 있다`는 방향성을 보여줍니다.
4. 따라서 지금 시점의 더 현실적인 연구선은 `더 화려한 prompt`보다 `하이브리드 packaging pipeline`입니다.

## 7. 결론

- 이번 실험의 결론은 `hybrid packaging`이 현재까지 본 축들 중 서비스 기획과 가장 정렬된 다음 단계라는 것입니다.
- `prompt phrase`: 실패
- `input framing`: repeatability 약함
- `edit path`: tray lane에서 비효율
- `hybrid packaging`: 생성 quality를 대체하진 않지만, 서비스 적합성은 즉시 끌어올림

## 8. 다음 액션

1. 다음 구현/실험은 `generated clip을 본선 renderer/packaging 경로에 어떻게 연결할지`를 보는 쪽이 맞습니다.
2. 우선순위는 아래 순서가 적절합니다.
   1. generated clip을 scene background로 받는 hybrid renderer spike
   2. overlay/CTA timing을 템플릿 scene spec과 맞추는 최소 bridge
   3. 그 다음에야 다시 model lane을 비교

## 9. 대표 artifact

- `docs/experiments/artifacts/exp-243-generated-video-hybrid-packaging-proof/summary.json`
- `docs/experiments/artifacts/exp-243-generated-video-hybrid-packaging-proof/hybrid_packaged.mp4`
- `docs/experiments/artifacts/exp-243-generated-video-hybrid-packaging-proof/hybrid_contact_sheet_8up.png`
- `docs/experiments/artifacts/exp-243-generated-video-hybrid-packaging-proof/raw_contact_sheet_8up.png`
