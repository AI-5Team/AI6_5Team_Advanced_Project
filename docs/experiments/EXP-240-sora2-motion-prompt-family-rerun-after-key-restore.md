# EXP-240 Sora 2 Motion Prompt Family Rerun After Key Restore

## 1. 기본 정보

- 실험 ID: `EXP-240`
- 작성일: `2026-04-14`
- 작성자: Codex
- 관련 기능: `Sora motion prompt family rerun / key 복구 후 phrase-level 재검증`

## 2. 왜 이 작업을 했는가

- `EXP-239`까지 확인한 결과, `sora2_current_best`는 샘플별 편차가 컸고 production baseline으로 승격할 근거가 부족했습니다.
- 다만 이 판단을 굳히기 전에, 기존 `EXP-91`에서 이미 봤던 `motion prompt family`가 새 키 기준에서도 같은 trade-off를 보이는지 한 번 더 확인할 필요가 있었습니다.
- 이번 작업의 목적은 새 direction을 더 만드는 것이 아니라, `phrase-level tuning이 정말로 병목이 아닌지`를 재검증하는 것입니다.

## 3. 실험 질문

1. key 복구 후 다시 실행해도 `micro_motion_locked`, `camera_orbit_beats`는 여전히 near-static한가
2. 기존 baseline 대비 motion recovery가 실질적으로 생기는가
3. 다음 우선순위를 `prompt phrase`에서 `input method`로 옮겨도 되는가

## 4. 실행 조건

### 4.1 고정 조건

1. 샘플: `맥주`
2. 모델: `sora-2`
3. 길이: `4초`
4. prepare mode: `cover_bottom`
5. 비교 기준:
   - `baseline_reused`: `EXP-90` Sora 결과 재사용
   - `manual_veo_reference`: 비교용 upper-bound reference

### 4.2 비교축

- `baseline_reused`
- `manual_veo_reference`
- `micro_motion_locked`
- `camera_orbit_beats`

### 4.3 실행 커맨드

```bash
python scripts/sora2_motion_prompt_family_ovaat.py --output-dir docs/experiments/artifacts/exp-240-sora2-motion-prompt-family-rerun-after-key-restore
```

참고:

- 스크립트 내부 `experiment_id`는 기존 호환성 때문에 `EXP-91-sora2-motion-prompt-family-ovaat`를 유지합니다.
- 이번 rerun artifact root는 `docs/experiments/artifacts/exp-240-sora2-motion-prompt-family-rerun-after-key-restore/`로 분리해 기록했습니다.

## 5. 실행 결과

artifact root:

- `docs/experiments/artifacts/exp-240-sora2-motion-prompt-family-rerun-after-key-restore/`

### 5.1 baseline_reused

- status: `completed`
- mid-frame MSE: `4452.34`
- motion avg_rgb_diff: `16.72`
- 관찰:
  - 기존 `EXP-90` baseline 재사용 값입니다.
  - 현재 비교에서 `움직임을 더 살리는 기준선`이 아니라 `Sora 기존 결과가 어느 정도였는지`를 보여주는 참조점입니다.

### 5.2 manual_veo_reference

- status: `completed`
- mid-frame MSE: `5811.95`
- motion avg_rgb_diff: `16.94`
- 관찰:
  - quality upper-bound reference 역할은 그대로 유지됩니다.

### 5.3 micro_motion_locked

- status: `completed`
- elapsed: `91.13s`
- mid-frame MSE: `576.14`
- motion avg_rgb_diff: `1.60`
- baseline 대비:
  - `mid-frame MSE -3876.20`
  - `avg_rgb_diff -15.12`
- 관찰:
  - bottle / glass / label 보존은 매우 강합니다.
  - 하지만 실제 motion은 거의 사라졌습니다.
  - `제품을 지키려 할수록 영상이 정지컷으로 수렴한다`는 trade-off가 다시 재현됐습니다.

### 5.4 camera_orbit_beats

- status: `completed`
- elapsed: `88.54s`
- mid-frame MSE: `1523.60`
- motion avg_rgb_diff: `1.61`
- baseline 대비:
  - `mid-frame MSE -2928.74`
  - `avg_rgb_diff -15.11`
- 관찰:
  - orbit / beat / push-in을 더 명시해도 실제 frame 변화는 거의 살아나지 않았습니다.
  - 일부 frame에서는 foam / glass 표현이 더 재해석되는 기미가 있지만, 그렇다고 motion이 광고형으로 살아나는 것도 아닙니다.
  - 즉 `phrase를 더 세게 쓰면 motion이 살아난다`는 가설은 이번 rerun에서도 지지되지 않았습니다.

## 6. 해석

1. key 복구 후 rerun에서도 `EXP-91`의 핵심 결론이 그대로 재현됐습니다.
2. `micro_motion_locked`는 preserve는 강하지만 motion이 붕괴합니다.
3. `camera_orbit_beats`는 preserve를 조금 더 풀어도 motion recovery가 거의 없습니다.
4. 따라서 현재 병목은 여전히 `phrase-level prompt wording`이 아닙니다.
5. 지금 더 타당한 축은 `input framing`, `edit-based recovery`, `hybrid compositor packaging` 같은 입력/구조 변화입니다.

## 7. 결론

- 이번 실험의 결론은 명확합니다.
  - `Sora motion prompt family를 더 미세조정하는 것`은 지금 우선순위가 아닙니다.
  - key가 정상이어도 preserve image-to-video 조건에서는 같은 trade-off가 반복됩니다.
- 따라서 다음 active 실험은 `prompt phrase 추가`가 아니라 `input method 변경`이어야 합니다.

## 8. 다음 액션

1. `EXP-91` 계열 phrase OVAT는 여기서 일단 닫습니다.
2. 다음 실험은 `hero_tight/input framing`, `edit path`, `hybrid motion packaging` 중 하나로 제한합니다.
3. production baseline은 그 전까지 계속 `product_control_motion`을 유지합니다.

## 9. 대표 artifact

- `docs/experiments/artifacts/exp-240-sora2-motion-prompt-family-rerun-after-key-restore/summary.json`
- `docs/experiments/artifacts/exp-240-sora2-motion-prompt-family-rerun-after-key-restore/micro_motion_locked/맥주/contact_sheet.png`
- `docs/experiments/artifacts/exp-240-sora2-motion-prompt-family-rerun-after-key-restore/camera_orbit_beats/맥주/contact_sheet.png`
- `docs/experiments/artifacts/exp-90-upper-bound-video-benchmark/sora2/맥주/contact_sheet.png`
