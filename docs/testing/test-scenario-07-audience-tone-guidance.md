# 테스트 시나리오 07 - Audience/Tone Guidance 레버 검증

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-07`

## 2. 테스트 목적

- 공통 baseline prompt에서 `audience_guidance`만 바뀌는지 확인합니다.
- `Gemma 4`가 고객 상황 지시를 실제 문구에 반영하는지 확인합니다.
- production deterministic 경로가 그대로 유지되는지 확인합니다.

## 3. 사전 조건

- `GEMINI_API_KEY` 설정
- 샘플 자산 존재
- EXP-01 harness 코드 적용 완료

## 4. 수행 항목

1. `npm run worker:test`
2. `uv run --project services/worker python scripts/run_prompt_experiment.py --experiment-id EXP-02`
3. `npm run check`

## 5. 결과

- worker test: 통과
- EXP-02 artifact 생성: 통과
- 전체 check: 통과
- artifact:
  - `docs/experiments/artifacts/exp-02-gemma-4-prompt-lever-experiment-audience-tone-guidance.json`

## 6. 관찰 내용

- audience/tone variant는 `서울숲 산책`, `오후의 여유`, `소중한 사람과 함께` 같은 맥락을 더 자주 사용했습니다.
- 공통 baseline prompt는 여전히 지역 반복이 4회로 늘어나는 경향이 있었고, audience/tone variant는 3회로 줄었습니다.
- 반면 CTA는 `지금 매장에서 만나요`처럼 더 부드러운 표현으로 바뀌어 액션 강도는 낮아졌습니다.

## 7. 실패/제약

1. 자동 점수는 둘 다 `92.9`라서 표현 차이를 수치 하나로 설명하기 어렵습니다.
2. CTA 품질 평가는 현재 heuristic 기반이라 사람 검수와 어긋날 수 있습니다.
3. 응답 시간이 baseline prompt보다 더 길었습니다.

## 8. 개선 포인트

1. 다음 실험에서 CTA 강도를 별도 레버로 분리합니다.
2. audience/tone 실험은 정량 점수 외에 사람이 보는 short rubric을 추가할 필요가 있습니다.
