# 테스트 시나리오 66 - local LTX multi-seed shortlist

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-66`

## 2. 테스트 목적

- fixed seed 하나보다 짧은 multi-seed shortlist가 현재 LTX baseline에 실제로 도움이 되는지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_multi_seed_shortlist.py --offline`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-63-local-ltx-multi-seed-shortlist/summary.json`

## 5. 관찰 내용

1. 규카츠/라멘/장어덮밥은 fixed seed `7`이 그대로 best였습니다.
2. 순두부짬뽕만 seed `19`가 fixed seed `7`보다 나았습니다.
3. aggregate 기준으로는 shortlist 개선 폭이 크지 않았습니다.

## 6. 실패/제약

1. shortlist 후보 seed가 3개뿐입니다.
2. oracle로 input 대비 MSE를 썼기 때문에 제품 실시간 기준과는 다릅니다.

## 7. 개선 포인트

1. seed strategy보다 음식군별 prompt template 분리가 더 우선일 가능성이 큽니다.
2. shortlist는 이후 보조 전략으로만 재검토하는 편이 맞습니다.
