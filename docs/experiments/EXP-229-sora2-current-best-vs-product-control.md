# EXP-229 Sora 2 Current Best Vs Product Control

## 1. 기본 정보

- 실험 ID: `EXP-229`
- 작성일: `2026-04-13`
- 작성자: Codex
- 관련 기능: `Sora 2 current best 추가 / product control 기준선 비교 / credential 상태 확인`

## 2. 왜 이 작업을 했는가

- `EXP-228`까지는 `product_control`, `local_ltx`, `manual_veo`만 같은 기준선에 올라와 있었습니다.
- 다음 순서는 `Sora 2 current best`를 같은 scorecard에 올려서, 실제 본선 control보다 나은 후보인지 확인하는 것이었습니다.
- 이번 실험의 목표는 `motion을 더 잘 만드는가`만이 아니라, `product control보다 광고 체감 품질을 올리면서 원본 보존도 유지하는가`를 보는 것이었습니다.

## 3. 이번에 바꾼 것

### 3.1 benchmark 스크립트 확장

- `scripts/video_upper_bound_benchmark.py`
  - `sora2_current_best` provider를 추가했습니다.
  - 현재 기준 `current best`는 `hero_tight_zoom` preserve candidate로 정의했습니다.
  - 각 샘플에 대해 `auto prepare -> hero_tight crop -> Sora 2 실행` 경로를 자동화했습니다.

### 3.2 current best 정의

- 이번 라운드에서 `Sora 2 current best`는 `EXP-92`와 `EXP-93` 기준으로 아래처럼 잡았습니다.
  - `prompt`: `EXP-90` baseline prompt 재사용
  - `input`: `hero_tight_zoom`
  - 이유:
    - `EXP-92`에서 가장 높은 preserve를 보였음
    - `EXP-93` edit 계열은 motion은 조금 회복했지만 preserve loss가 커 본선 후보로 보기 어려웠음

## 4. 실행 조건

1. 샘플
   - `규카츠`
   - `맥주`
2. 비교군
   - `product_control`
   - `local_ltx`
   - `sora2_current_best`
   - `manual_veo`
3. artifact root
   - `docs/experiments/artifacts/exp-229-sora2-current-best-vs-product-control/`

## 5. 실행 커맨드

```bash
python -m py_compile scripts/video_upper_bound_benchmark.py
python scripts/video_upper_bound_benchmark.py --benchmark-id EXP-229-sora2-current-best-vs-product-control --providers product_control local_ltx sora2_current_best manual_veo --output-dir docs/experiments/artifacts/exp-229-sora2-current-best-vs-product-control
```

## 6. 실행 결과

### 6.1 product_control / local_ltx / manual_veo

- 세 비교군은 `EXP-228`과 동일 구조로 정상 완료됐습니다.
- 요약:
  - `product_control`
    - 본선 control로 계속 유효
  - `local_ltx`
    - 보존성은 강하지만 near-static
  - `manual_veo`
    - 품질 upper-bound reference

### 6.2 sora2_current_best

#### 규카츠

- status: `failed`
- elapsed: `1.13s`
- resolved prepare mode: `cover_center`
- 오류:
  - `401 invalid_api_key`

#### 맥주

- status: `failed`
- elapsed: `1.04s`
- resolved prepare mode: `cover_bottom`
- 오류:
  - `401 invalid_api_key`

### 6.3 이번 실행에서 확인된 사실

1. benchmark 경로 자체는 정상 연결됐습니다.
2. `hero_tight_zoom` prepared input도 샘플별로 정상 생성됐습니다.
3. 현재 저장소에서 live Sora 비교를 막는 원인은 `current best strategy`가 아니라 `OPENAI_API_KEY 상태`입니다.

## 7. scorecard 기준 중간 판단

### product_control

| 항목 | 판정 | 메모 |
| --- | --- | --- |
| 보존성 | pass | 원본 정체성 유지 |
| 광고 체감 | pass | 컷/오버레이/CTA가 분명함 |
| 반복성 | pass | deterministic control |
| 서비스 적합성 | pass | 본선 패키징과 직접 연결 |
| 최종 역할 | 본선 | 유지 |

### local_ltx

| 항목 | 판정 | 메모 |
| --- | --- | --- |
| 보존성 | pass | 원본 구조 유지 강함 |
| 광고 체감 | hold | near-static 성격이 강함 |
| 반복성 | hold | 현재 baseline 수준에서는 제한적 |
| 서비스 적합성 | hold | 본선 control 대체로는 아직 약함 |
| 최종 역할 | 보조 후보 | 유지 |

### manual_veo

| 항목 | 판정 | 메모 |
| --- | --- | --- |
| 보존성 | fail | 규카츠에서 QR/주변 오브젝트 재구성 |
| 광고 체감 | pass | 품질 상한선 참고로는 강함 |
| 반복성 | hold | manual reference only |
| 서비스 적합성 | fail | production path에는 부적합 |
| 최종 역할 | reference only | 유지 |

### sora2_current_best

| 항목 | 판정 | 메모 |
| --- | --- | --- |
| 보존성 | blocked | live 실행 실패 |
| 광고 체감 | blocked | live 실행 실패 |
| 반복성 | blocked | live 실행 실패 |
| 서비스 적합성 | blocked | credential 복구 후 재평가 |
| 최종 역할 | 보류 | 키 복구 후 재실행 필요 |

## 8. 해석

### 8.1 이번에 실제로 얻은 것

1. `Sora 2 current best`를 다시 실험선에 올릴 수 있는 benchmark 구조는 갖춰졌습니다.
2. 현재 비교를 막는 병목은 실험 설계가 아니라 credential입니다.
3. 따라서 지금 단계에서 `Sora 2가 product control보다 나은가`에 대한 live 결론은 새로 내릴 수 없습니다.

### 8.2 이번 결과가 의미하는 것

- 현재 기준 active 판단은 아래와 같습니다.
  - `product_control`: 계속 본선 기준선
  - `local_ltx`: 보조 후보이나 광고 체감은 아직 부족
  - `manual_veo`: quality upper-bound reference only
  - `sora2_current_best`: 실험 구조는 준비됨, live 평가는 credential 복구 후 진행

## 9. 결론

- 이번 실험은 `부분 완료`입니다.
- `Sora 2 current best`를 benchmark 구조에는 넣었지만, 현재 `OPENAI_API_KEY`가 `401 invalid_api_key` 상태라 live 비교를 끝내지 못했습니다.
- 다만 이 경로는 이제 같은 커맨드로 바로 재실행 가능하므로, 키만 복구되면 `product control` 기준 scorecard 비교를 즉시 이어갈 수 있습니다.

## 10. 다음 액션

1. `OPENAI_API_KEY` 상태를 복구합니다.
2. 같은 커맨드로 `EXP-229`를 그대로 재실행합니다.
3. 재실행 후 `Sora 2 current best`를 `EXP-227` scorecard에 실제 판정으로 채웁니다.
4. 그 결과가 `product_control`을 못 넘으면, 본선은 계속 `template motion + compositor`를 기준선으로 유지합니다.

## 11. 대표 artifact

- `docs/experiments/artifacts/exp-229-sora2-current-best-vs-product-control/summary.json`
- `docs/experiments/artifacts/exp-229-sora2-current-best-vs-product-control/sora2_current_best/규카츠/prepared_variants/hero_tight_zoom.png`
- `docs/experiments/artifacts/exp-229-sora2-current-best-vs-product-control/sora2_current_best/맥주/prepared_variants/hero_tight_zoom.png`
