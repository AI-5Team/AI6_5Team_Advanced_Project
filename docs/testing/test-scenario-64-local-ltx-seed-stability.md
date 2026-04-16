# 테스트 시나리오 64 - local LTX seed stability

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-64`

## 2. 테스트 목적

- 현재 LTX baseline이 seed만 바뀌어도 얼마나 흔들리는지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_seed_stability.py --offline`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-61-local-ltx-seed-stability/summary.json`

## 5. 관찰 내용

1. seed `7`이 가장 나았고, seed `19`가 가장 나빴습니다.
2. 최고/최악 seed 간 mid-frame MSE 차이가 `331.95`로 컸습니다.
3. 실제 중간 프레임을 봐도 seed `19`는 규카츠 경계와 반찬 디테일이 더 흐렸습니다.

## 6. 실패/제약

1. 규카츠 1장만 봤습니다.
2. seed 3개 샘플이라 전체 분포 해석에는 한계가 있습니다.

## 7. 개선 포인트

1. 이후에는 고정 seed 하나만 믿기보다 shortlist 전략을 검토하는 편이 맞습니다.
2. 음식군별 seed 민감도 차이도 따로 확인할 가치가 있습니다.
