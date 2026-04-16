# EXP-04 사용자 제공 레퍼런스 기반 Owner-made Safe-zone 레이아웃 실험

## 1. 기본 정보

- 실험 ID: `EXP-04`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: B급 영상 레이아웃 개선, 상품 가시성 보호

## 2. 왜 이 실험을 추가했는가

- 기존 접근은 synthetic 샘플과 일반화된 B급 오버레이에 치우쳐 있었습니다.
- 사용자가 `docs/sample/b급sample.png` 레퍼런스 보드를 추가했고, 이 이미지는 실제로 팀이 원하는 B급 방향을 더 구체적으로 보여줍니다.
- 특히 레퍼런스의 `Style A - 사장님이 직접 만든 느낌`은:
  - B급 감성은 살리면서
  - 상품은 크게 보이고
  - 가격/핵심 정보는 오른쪽에 강하게 배치하는
  균형점을 보여줍니다.

## 3. 참고 레퍼런스

- 참조 이미지:
  - `docs/sample/b급sample.png`

### 레퍼런스에서 뽑은 핵심 포인트

1. 상품은 화면에서 크게 살아 있어야 합니다.
2. 텍스트는 상품을 덮기보다 옆으로 밀어 배치합니다.
3. 가격/혜택은 빨간 낙서 원, 형광 텍스트처럼 직접 표시합니다.
4. 완성형 광고라기보다 “사장님이 직접 급하게 만든 전단지” 같은 어설픈 손맛이 중요합니다.

## 4. baseline 실험 조건 고정

| 항목 | 고정값 |
|---|---|
| 스타일 | `b_grade_fun` |
| 템플릿 | `T02` |
| 자산 세트 | `samples/input/cafe/cafe-latte-01.png`, `samples/input/cafe/cafe-dessert-02.png` |
| 기준 비교 대상 | `EXP-03`에서 만든 `bgrade_flyer_overlay` |
| 바뀐 레버 | `product_visibility_protection` 한 가지 |

## 5. 이번 실험에서 바꾼 것

- baseline:
  - `bgrade_flyer_overlay`
  - B급 신호는 강하지만 상품 가시성을 많이 침범
- variant:
  - `owner_made_safe_zone`
  - 사용자 레퍼런스 `Style A`를 참고
  - 상품이 들어간 종이 카드 프레임을 왼쪽에 크게 배치
  - 텍스트와 가격은 오른쪽/하단으로 분리
  - 빨간 낙서 원으로 가격 강조
  - 하단 손글씨형 CTA 메모 추가

## 6. 실험 절차

1. `docs/sample/b급sample.png`를 확인해 방향성을 분해했습니다.
2. `services/worker/experiments/video_harness.py`에 `owner_made_safe` variant를 추가했습니다.
3. `EXP-04`를 실행해 baseline과 variant를 같은 자산/카피로 비교했습니다.
4. 첫 씬 이미지를 직접 검토했습니다.

## 7. 결과

### artifact

- `docs/experiments/artifacts/exp-04-owner-made-safe-zone-layout-experiment/summary.json`

### 정량 결과

| 케이스 | overlay mode | B급 signal score | product visibility score |
|---|---|---|---|
| baseline | `flyer_poster` | `137.8` | `48.0` |
| variant | `owner_made_safe` | `97.2` | `88.0` |

### 질적 비교

| 항목 | flyer poster | owner-made safe zone |
|---|---|---|
| B급 강도 | 더 과장됨 | 약간 덜 과장되지만 충분히 살아 있음 |
| 상품 가시성 | 약함 | 훨씬 좋음 |
| 가격 강조 | 있음 | 레퍼런스와 더 유사 |
| “사장님이 직접 만든 느낌” | 약함 | 강함 |
| 완성도 | 전단지형 쇼크 | 손맛형 B급 밸런스 |

## 8. 관찰 내용

### 확인된 것

- 사용자 레퍼런스를 기준으로 잡으니 방향이 훨씬 선명해졌습니다.
- `owner_made_safe_zone`은 `flyer_poster`보다 상품을 덜 가리면서도 B급 감성을 유지했습니다.
- 즉, 지금 필요한 것은 “더 과한 B급”만이 아니라 **레퍼런스에 가까운 B급 균형점**입니다.

### trade-off

- `flyer_poster`가 첫 인상과 자극성은 더 강합니다.
- 하지만 실제 광고 결과물로는 `owner_made_safe_zone`이 더 쓸 만한 방향일 가능성이 큽니다.
- 결국 다음 문제는 B급 강도 자체보다, **어느 정도까지 세게 가도 상품을 해치지 않는가**입니다.

## 9. 실패/제약

1. 이번 레퍼런스는 1장의 스타일 보드라, 실제 영상 전 장면 일관성까지 보장하지는 않습니다.
2. `owner_made_safe_zone`도 아직 완성형은 아니고, CTA 메모/손글씨 요소는 더 다듬을 수 있습니다.
3. motion, VHS, 노래방 자막 계열은 아직 별도 실험 전입니다.

## 10. 결론

- 가설 충족 여부: **충족**
- 판단:
  - 사용자 제공 레퍼런스를 기준으로 삼는 접근이 지금까지의 synthetic 중심 접근보다 훨씬 낫습니다.
  - 다음 영상 실험은 레퍼런스 기반으로 계속 가는 편이 맞습니다.
  - `owner_made_safe_zone`은 production 후보 방향으로 볼 가치가 있습니다.

## 11. 다음 액션

1. `owner_made_safe_zone`을 기준 candidate로 두고, 다음엔 `motion preset`을 한 변수로 붙입니다.
2. `Style B(90년대 노래방 자막)`와 `Style D(VHS)`는 별도 실험 축으로 분리합니다.
3. 실제 매장 사진 1세트를 받아 같은 실험을 반복하면 훨씬 빨리 판단할 수 있습니다.
