# EXP-07 OVAT 재개 전 시각 baseline 재구축

## 1. 기본 정보

- 실험 ID: `EXP-07`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: 영상 renderer baseline 재구축, 텍스트 overflow/겹침 완화

## 2. 왜 이 실험을 추가했는가

- `EXP-06`까지의 결과는 방향성은 보여줬지만, 렌더 품질 자체가 낮아 OVAT를 계속할 수 없는 상태였습니다.
- 특히 기존 `owner_made_safe`는
  - 우측 텍스트 clipping
  - 강조 원과 텍스트 겹침
  - 글자 수 기반 줄바꿈으로 인한 어색한 line break
  문제가 동시에 드러났습니다.
- 따라서 이번 실험은 “레버 하나 조정”이 아니라 **시각 baseline 자체를 다시 세우는 작업**으로 정의했습니다.

## 3. baseline 실험 조건 고정

| 항목 | 고정값 |
|---|---|
| 업종 | `restaurant` |
| 목적 | `promotion` |
| 스타일 | `b_grade_fun` |
| 템플릿 | `T02` |
| 자산 세트 | `docs/sample/음식사진샘플(규카츠).jpg`, `docs/sample/음식사진샘플(맥주).jpg` |
| baseline | `legacy_owner_made_safe` |
| candidate | `structured_bgrade_v2` |
| 실험 성격 | OVAT 아님, baseline rebuild |

## 4. 이번에 갈아엎은 것

### legacy baseline

- 고정 좌표 중심 배치
- 글자 수 기준 `balance_text()`
- 우측 패널 폭이 좁아 긴 문구에서 clipping 발생

### rebuilt baseline

- `text fit` 기반으로 폰트 크기와 줄 수를 다시 계산
- 사진 영역과 텍스트 영역을 명확히 분리한 safe zone 레이아웃
- CTA를 하단 footer strip으로 고정
- B급 요소는 남기되 상품 영역을 침범하지 않도록 분리

## 5. 구현 절차

1. 기존 `owner_made_safe`의 문제를 코드와 산출물 기준으로 다시 확인했습니다.
2. `video_harness.py`에 `structured_bgrade_v2` overlay mode를 추가했습니다.
3. 다음 helper를 추가했습니다.
   - `fit_text_block`
   - `wrap_text_by_pixels`
   - `truncate_to_width`
   - `draw_block`
   - `draw_scribble_oval`
4. `EXP-07`을 실행해 legacy baseline과 rebuilt baseline을 같은 시나리오로 비교했습니다.
5. 첫 씬과 CTA 씬을 직접 검토했습니다.

## 6. 결과

### artifact

- `docs/experiments/artifacts/exp-07-visual-baseline-rebuild-before-ovat/summary.json`

### 정량 결과

| 케이스 | overlay mode | layout integrity | product visibility | service-loop fit |
|---|---|---|---|---|
| legacy | `owner_made_safe` | `44.0` | `88.0` | `84.4` |
| rebuilt | `structured_bgrade_v2` | `94.0` | `94.0` | `90.6` |

### 질적 비교

| 항목 | legacy owner-made | structured v2 |
|---|---|---|
| 우측 헤드라인 clipping | 자주 발생 | 크게 완화 |
| 텍스트/강조요소 겹침 | 자주 발생 | 구조적으로 분리 |
| 사진 가시성 | 비교적 좋음 | 더 안정적 |
| CTA 읽힘 | 하단 메모형 | 하단 strip으로 더 명확 |
| B급 감성 | 손맛은 있으나 어수선 | 다소 정돈됐지만 아직 유지 |

## 7. 관찰 내용

### 확인된 것

1. 지금 필요한 것은 개별 레버보다 `text fit + safe zone + CTA footer` 구조였습니다.
2. `structured_bgrade_v2`는 기존 baseline보다 확실히 덜 깨집니다.
3. 상품 사진과 텍스트가 분리되면서 실제 음식 사진에서도 안정감이 올라갔습니다.

### 아직 남은 문제

1. 우측 note(`사장님이 직접 쓴 느낌`)는 아직 줄바꿈이 예쁘지 않습니다.
2. CTA 씬 headline은 clipping은 줄었지만 여전히 line break가 조금 뻣뻣합니다.
3. B급 강도를 높이되 다시 지저분해지지 않게 만드는 2차 조정이 필요합니다.

## 8. 실패/제약

1. 이번 실험은 baseline rebuild라 여러 요소를 동시에 바꿨습니다. 따라서 OVAT 비교 실험은 아닙니다.
2. 현재 `layout_integrity_score`는 heuristic 기반이라, 이후에는 실제 overflow 검출을 붙이는 편이 좋습니다.
3. 아직 production renderer에는 반영하지 않았고 `experiments` 경로에만 있습니다.

## 9. 결론

- 가설 충족 여부: **충족**
- 판단:
  - OVAT를 멈추고 baseline을 먼저 갈아엎은 판단이 맞았습니다.
  - `structured_bgrade_v2`는 다음 실험의 출발점으로 삼을 수 있습니다.
  - 다만 바로 production 반영보다는 2차 polish와 실제 사진 다건 검증이 더 필요합니다.

## 10. 다음 액션

1. `structured_bgrade_v2`를 기준 candidate로 고정합니다.
2. 다음은 `headline/secondary/note`의 line-break polish를 한 번 더 다듬습니다.
3. 그 다음에야 `subtitle_density`나 `motion` 같은 OVAT 실험을 재개합니다.
