# ADR-008 수제 Pillow 시각 baseline은 채택하지 않는다

- 상태: 승인
- 날짜: 2026-04-08

## 배경

`EXP-07`, `EXP-08`을 통해 기존 고정 좌표 기반 renderer보다 나은 시도는 만들었지만, 사용자 피드백 기준으로는 여전히 제품 baseline으로 채택할 수준이 아닙니다.

문제는 단순히 문구나 한두 개 레버가 아닙니다.

1. 전반적인 미감이 낮습니다.
2. 장식 문구와 시각 장치가 실제 제품 가치와 어긋납니다.
3. Pillow 기반 수제 합성 방식이 현대적인 타이포그래피/레이아웃 품질을 만들기 어렵습니다.

특히 `사장님 손글씨` 같은 문구는 기획 요구사항이 아니라 실험 중 과도하게 붙인 장식으로, 제품 baseline에 포함되면 안 됩니다.

## 결정

1. `structured_bgrade_v2`를 포함한 현재 Pillow 실험 결과물은 **기술적 안정화 참고물**로만 두고, 제품 시각 baseline으로 채택하지 않습니다.
2. 이후 baseline 탐색은 `Pillow 고도화`보다 **렌더 surface 전환**을 우선 검토합니다.
3. 다음 우선 후보는 아래 두 축입니다.
   - `HTML/CSS 기반 compositing renderer`
   - `멀티모달 모델 기반 layout planning + deterministic renderer`
4. 모델 교체는 보조 수단으로만 검토합니다.
   - 카피 모델만 바꿔도 미감 문제는 해결되지 않기 때문입니다.
5. 향후 실험에서는 근거 없는 장식 문구를 제거합니다.
   - 예: `사장님 손글씨`

## 근거

1. 현재 worker는 사실상 `Pillow` 하나로 시각 품질을 만들고 있습니다.
2. 이런 방식은 정교한 grid, responsive typography, spacing system, component composition을 만들기 불리합니다.
3. 시각 퀄리티 문제는 prompt보다 render surface와 design system의 문제에 더 가깝습니다.

## 결과

1. `EXP-07`, `EXP-08`은 “현재 방식의 한계와 기술적 개선 폭”을 보여주는 참고 기록으로 유지합니다.
2. 다음 baseline 연구는 `renderer strategy pivot` 문서와 새 실험으로 이어갑니다.
3. 현재 baseline candidate 표현은 더 이상 사용하지 않습니다.
