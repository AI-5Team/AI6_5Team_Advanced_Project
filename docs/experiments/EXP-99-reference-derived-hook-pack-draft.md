# EXP-99 Reference-derived hook pack draft

## 1. 기본 정보

- 실험 ID: `EXP-99`
- 작성일: `2026-04-10`
- 작성자: Codex
- 관련 축: `reference-derived copy pack / hook slot draft`

## 2. 왜 이 작업을 했는가

- `EXP-98`까지로 현재 템플릿을 `hook / body / cta` 레이어로 읽는 기준은 생겼습니다.
- 다음 필요한 것은 그 hook 자리에 실제로 꽂아볼 수 있는 `reference-derived hook 후보`입니다.
- 이번 작업은 외부 레퍼런스에서 뽑은 curiosity/B급/정보형 문법을 현재 템플릿의 hook slot에 맞게 데이터 초안으로 정리하는 단계입니다.

## 3. 무엇을 추가했는가

### 3.1 데이터 초안

- 파일: `packages/template-spec/manifests/reference-hook-pack-v1.json`
- 성격:
  - `draft-v1`
  - runtime 미사용
  - 기존 `copy-rules/*.json`과 별개인 proposal 데이터

### 3.2 README 보강

- 파일: `packages/template-spec/README.md`
- 추가 내용:
  - `reference-hook-pack-v1.json`이 외부 레퍼런스 기반 hook 후보 초안이라는 점

## 4. 이번 hook pack의 구성 원칙

1. 최대한 짧고 반복 가능한 문장
2. `region`, `product_name`, `benefit` 같은 토큰 기반 치환 가능 구조
3. 현재 템플릿 `T01`~`T04`에 바로 매핑 가능한 hook만 우선
4. `좋아 보이는 문장`보다 `자영업자가 반복 생산 가능한 문장`을 우선

## 5. 10개 hook의 성격

### 템플릿 적합 후보

1. `hk01`
   - `{region}에서 이거 보셨나요?`
   - 범용 curiosity 질문형
2. `hk02`
   - `오늘 안 오면 손해인가요?`
   - B급 프로모션형
3. `hk03`
   - `{product_name}, 진짜 나왔습니다`
   - 신메뉴 공개형
4. `hk04`
   - `퇴근길에 왜 {region}로 오죠?`
   - 방문 유도형
5. `hk05`
   - `"한 번 먹고 기억나요"`
   - 후기 인용형
6. `hk06`
   - `{benefit}, 오늘만 맞나요?`
   - 혜택 질문형
7. `hk07`
   - `{region}에서 요즘 이게 뜹니다`
   - 지역 트렌드형
8. `hk09`
   - `"{region} 오면 여기부터 가요"`
   - 지역 후기형

### 부분 차용 후보

1. `hk08`
   - `다들 왜 이걸 또 찾죠?`
   - 톤은 강하지만 업종에 따라 과할 수 있음
2. `hk10`
   - `{product_name}, 생각보다 더 셉니다`
   - 카피는 강하지만 body가 잘 받쳐줘야 함

## 6. 지금 당장 어떻게 쓸 수 있는가

### T01 `신메뉴 티저형`

- 잘 맞는 hook:
  - `hk01`
  - `hk03`
  - `hk07`

### T02 `오늘만 할인형`

- 잘 맞는 hook:
  - `hk01`
  - `hk02`
  - `hk06`

### T03 `동네 방문 유도형`

- 잘 맞는 hook:
  - `hk04`
  - `hk07`
  - `hk09`

### T04 `한줄 후기형`

- 잘 맞는 hook:
  - `hk05`
  - `hk09`
  - `hk08`

## 7. 왜 기존 copy-rules를 바로 바꾸지 않았는가

1. 현재 runtime은 `copy-rules/*.json`의 `sampleHooks`를 단순 참고값으로만 쓰고 있습니다.
2. 이번 단계 목표는 production 카피 생성 로직을 당장 바꾸는 것이 아니라, `reference-derived hook 후보군`을 먼저 분리하는 것입니다.
3. 그래서 기존 source of truth를 건드리지 않고, 별도 manifest로 초안을 두는 쪽이 안전합니다.

## 8. 다음 단계 제안

### 1순위

- 이 hook pack을 바탕으로 `purpose x style`별 top 2 후보를 다시 좁히기

### 2순위

- `copy_rules/*.json`의 `sampleHooks`를 이 draft 기준으로 갱신할지 검토하기

### 3순위

- worker의 `_build_copy_bundle()` 또는 prompt harness에서 이 hook pack을 소비하는 실험 경로 만들기

## 9. 결론

- 이번 작업으로 `reference-derived hook`을 실제 데이터 형태로 쌓기 시작했습니다.
- 즉 이제부터는 외부 광고 레퍼런스를 보고 `좋아 보인다`에서 끝나는 게 아니라, `어떤 hook 후보를 템플릿 slot에 넣을 수 있는가`까지 바로 연결할 수 있습니다.
