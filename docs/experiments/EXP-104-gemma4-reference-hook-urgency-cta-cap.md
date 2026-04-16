# EXP-104 Gemma 4 reference hook urgency/CTA cap

## 1. 기본 정보

- 실험 ID: `EXP-104`
- 작성일: `2026-04-10`
- 작성자: Codex
- 관련 축: `Gemma 4 constraint tuning / urgency cap / cta cap`

## 2. 왜 이 작업을 했는가

- `EXP-102`에서 `Gemma 4`는 hook 구조는 안정적이었지만, `urgency`와 `cta`가 길어지고 1회 timeout도 있었습니다.
- 이번 실험은 `reference hook guidance` 위에 `urgency/cta 길이 상한`을 더 직접적으로 얹어 render-ready성을 높일 수 있는지 보는 OVAT입니다.

## 3. 비교축

1. baseline
   - `fixed_reference_hook_pack_guidance_gemma`
2. candidate
   - `reference_hook_pack_urgency_cta_cap_gemma`

## 4. 추가한 constraint

1. `hook`
   - 14자 안팎
2. `benefit`
   - 16자 안팎
3. `urgency`
   - 10자 안팎의 짧은 기간 문구
4. `cta / ctaText`
   - 8자 안팎
   - `지금 바로` 같은 부사는 제거
   - 행동 단어로 시작
5. 긴 설명
   - subText로 이동

## 5. 실행 결과

artifact:

- `docs/experiments/artifacts/exp-104-gemma-4-prompt-lever-experiment-reference-hook-urgency-cta-cap.json`

### baseline

- score: `92.9`
- hook:
  - `규카츠 할인, 오늘만 맞나요?`
- cta:
  - `지금 바로 예약하기`
- over-limit:
  - `s2`
- failed:
  - `region repeated more than allowed`

### candidate

- score: `92.9`
- hook:
  - `오늘 안 오면 손해인가요?`
- cta:
  - `방문하기`
- over-limit:
  - 없음
- failed:
  - `region appears in fewer than required areas`

## 6. 해석

- 길이 cap은 분명히 효과가 있었습니다.
  - over-limit scene이 `1개 -> 0개`로 줄었습니다.
  - CTA도 `지금 바로 예약하기 -> 방문하기`로 짧아졌습니다.
- 하지만 여기서도 region minimum slot 조건을 놓쳤습니다.
- 즉 Gemma 4도 `길이 cap`은 잘 따르지만, region 쪽은 역시 `exact anchor`가 더 필요합니다.

## 7. 결론

- Gemma 4의 약점은 길이였고, 그 부분은 실제로 개선됐습니다.
- 다만 region 조건은 별도 축으로 다시 잡아야 합니다.
- 따라서 다음은 `길이 cap + region anchor`를 함께 고정하는 비교가 맞습니다.
