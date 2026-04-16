# 테스트 시나리오 78 - local LTX batch runner auto default

## 1. 테스트 정보

- 일자: `2026-04-09`
- 진행자: Codex
- 시나리오 ID: `TS-78`

## 2. 테스트 목적

- reusable batch runner에서 `prepare_mode auto`를 기본값으로 써도 current baseline 정책이 유지되는지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_batch_runner.py --offline`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-75-local-ltx-batch-runner-auto-default/summary.json`

## 5. 관찰 내용

1. 대표 샘플 6장이 모두 정상 완료됐습니다.
2. `규카츠=cover_center`, `커피/맥주=cover_top`, 나머지=`contain_blur`로 분기됐습니다.
3. 즉 `prepare_mode auto`는 reusable runner 기본값으로도 유지됩니다.

## 6. 실패/제약

1. `맥주`는 여전히 결과 품질이 거친 편입니다.

## 7. 개선 포인트

1. 다음은 runner보다 샘플별 후속 레버가 우선입니다.
