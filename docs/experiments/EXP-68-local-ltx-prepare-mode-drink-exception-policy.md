# EXP-68 Local LTX prepare_mode drink exception policy

## 1. 기본 정보

- 실험 ID: `EXP-68`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `로컬 비디오 연구선 / prepare_mode policy refine`

## 2. 왜 이 작업을 했는가

- `EXP-66`에서 `규카츠=cover_center`, 나머지=`contain_blur` policy가 global baseline보다 낫다는 점을 확인했습니다.
- `EXP-67`에서는 `cover_top`이 전반 해법은 아니었지만, `커피` 1건만은 더 좋았습니다.
- 따라서 이번에는 전역 baseline을 뒤집지 않고, 기존 policy 위에 `커피만 cover_top` 예외를 얹었을 때 안전하게 이득이 생기는지 확인했습니다.

## 3. baseline

### 고정한 조건

1. 모델: `LTX-Video 2B / GGUF`
2. seed: `7`
3. prompt: 음식 라벨 + current LTX baseline prompt
4. negative prompt: 기본값
5. frames / steps / fps: `25 / 6 / 8`
6. 이미지:
   - `규카츠`
   - `라멘`
   - `순두부짬뽕`
   - `장어덮밥`
   - `커피`
   - `아이스크림`

### 이번에 바꾼 레버

- `prepare_mode policy` 한 군데만 바꿨습니다.
- baseline policy:
  - `규카츠`: `cover_center`
  - 나머지: `contain_blur`
- variant policy:
  - `규카츠`: `cover_center`
  - `커피`: `cover_top`
  - 나머지: `contain_blur`

## 4. 무엇을 바꿨는가

1. `scripts/local_video_ltx_prepare_mode_drink_exception.py`
   - baseline policy와 `커피만 cover_top` variant policy를 비교하는 실험 스크립트를 추가했습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-68-local-ltx-prepare-mode-drink-exception-policy/summary.json`

### 이미지별 결과

1. 규카츠
   - 변화 없음
2. 라멘
   - 변화 없음
3. 순두부짬뽕
   - 변화 없음
4. 장어덮밥
   - 변화 없음
5. 커피
   - variant policy가 더 좋았습니다.
   - mid-frame MSE delta: `+32.27`
6. 아이스크림
   - 변화 없음

### aggregate

- variant policy가 더 나은 이미지는 `6개 중 1개`였습니다.
- average mid-frame MSE delta는 `+5.38`이었습니다.
- average edge variance delta는 `+56.40`이었습니다.

### 확인된 것

1. `커피만 cover_top` 예외는 전체 회귀 없이 작은 개선을 추가합니다.
2. 즉 현재 데이터 기준 prepare_mode baseline은 아래처럼 더 구체화할 수 있습니다.
   - `규카츠` 같은 tray/full-plate: `cover_center`
   - `커피` 같은 glass drink: `cover_top`
   - 그 외 preserve-shot: `contain_blur`
3. 지금 단계에서는 prompt보다 `입력 프레이밍 정책`이 더 강한 레버입니다.

## 6. 실패/제약

1. drink 샘플이 아직 `커피` 1장뿐이라 일반화 근거는 약합니다.
2. aggregate 개선은 작고, 본질적으로 `1장 개선 + 5장 유지` 패턴입니다.
3. seed `7` 고정 기준입니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - `커피`처럼 세로 드링크 컷에는 `cover_top` 예외를 둘 가치가 있습니다.
  - 다만 지금은 `drink general rule`이라기보다 `glass drink candidate rule` 정도로 보는 편이 맞습니다.

## 8. 다음 액션

1. 다음 레버는 `shot type auto classification` 또는 `glass drink 샘플 추가 검증`입니다.
2. 사용자가 다른 구도 사진은 없다고 했으므로, 다음도 prompt보다 `prepare_mode policy` 축에서 좁혀 가는 편이 맞습니다.
