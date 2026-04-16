# EXP-93 Sora 2 edit motion recovery OVAT

## 1. 기본 정보

- 실험 ID: `EXP-93`
- 작성일: `2026-04-10`
- 작성자: Codex
- 관련 기능: `Sora 2 edit / motion recovery OVAT / 맥주 샘플`

## 2. 왜 이 작업을 했는가

- `EXP-91`, `EXP-92`를 통해 `prompt`와 `input framing`을 어떻게 만져도 결과는 `보존성이 좋아질수록 motion이 줄어드는 방향`으로 수렴했습니다.
- 그래서 다음 질문은 `image-to-video 한 번으로 끝내지 말고`, `보존성이 좋은 source 영상을 만든 뒤 edit로 motion만 추가할 수 있는가`였습니다.
- 이번 실험은 `EXP-92 hero_tight_zoom` 결과를 source로 두고, `same shot 유지 + motion recovery` edit 2개를 비교하는 OVAT입니다.

## 3. 고정 조건과 비교축

### source 기준선

1. source video: `EXP-92 hero_tight_zoom`
2. source motion avg_rgb_diff: `3.67`
3. source mid-frame MSE: `2369.92`

### 비교축

1. `source_hero_tight`
   - `EXP-92`의 best-preserve source video
2. `baseline_reused`
   - `EXP-90`의 original Sora baseline
3. `manual_veo_reference`
   - 품질 upper-bound 참고선
4. `same_shot_more_motion`
   - 같은 샷을 유지한 채 bubbles / foam / condensation / small drift만 강화
5. `same_shot_push_in_motion`
   - 같은 샷을 유지한 채 push-in과 drift를 조금 더 직접적으로 추가

## 4. 무엇을 만들고 바꿨는가

### 스크립트

1. `scripts/sora2_edit_motion_recovery_ovaat.py`
   - `EXP-92 hero_tight_zoom` summary를 source로 읽습니다.
   - source video id를 바탕으로 Sora `edit` API를 호출합니다.
   - polling, mp4 다운로드, frame/contact sheet 추출, metric 계산까지 자동으로 수행합니다.

### 운영 메모

1. 처음에는 스킬 번들 CLI(`scripts/sora.py edit`)를 그대로 쓰려 했습니다.
2. 하지만 현재 CLI 경로는 `/videos/edits` 응답을 `cast_to=dict`로 파싱하다가 SDK 내부에서 실패했습니다.
3. 그래서 이번 실험 러너는 같은 공식 SDK를 쓰되, low-level `client.post(..., cast_to=dict[str, object])` 경로로 fallback 했습니다.
4. 즉 이번 결과는 `edit API 자체의 성공/실패`를 본 것이고, CLI 파싱 버그는 실험 목적과 분리했습니다.

## 5. 실행 결과

### source_hero_tight

- status: `completed`
- mid-frame MSE: `2369.92`
- motion avg_rgb_diff: `3.67`
- 관찰:
  - 지금까지 Sora 결과 중 원본 보존은 가장 좋은 쪽입니다.
  - 다만 움직임은 거의 약한 수준입니다.

### same_shot_more_motion

- status: `completed`
- mid-frame MSE: `4394.26`
- motion avg_rgb_diff: `4.19`
- source 대비:
  - `mid-frame MSE +2024.34`
  - `avg_rgb_diff +0.52`
- 관찰:
  - source보다 motion은 아주 소폭 늘었습니다.
  - 하지만 label과 bottle 인상, 유리잔 내부 표현이 source보다 다시 많이 바뀌었습니다.
  - 즉 motion recovery는 있었지만, 그 폭에 비해 보존성 손실이 큽니다.

### same_shot_push_in_motion

- status: `completed`
- mid-frame MSE: `6731.35`
- motion avg_rgb_diff: `7.58`
- source 대비:
  - `mid-frame MSE +4361.43`
  - `avg_rgb_diff +3.91`
- 관찰:
  - 두 edit variant 중 motion recovery는 가장 컸습니다.
  - contact sheet에서도 source보다 프레임 변화가 실제로 더 보입니다.
  - 하지만 bottle label, 병 질감, glass 표현이 source보다 훨씬 더 재해석됐습니다.
  - 즉 edit로 motion을 올릴 수는 있었지만, 보존성 훼손이 꽤 큽니다.

### baseline_reused / manual_veo_reference와의 위치

1. `same_shot_more_motion`
   - source보다는 조금 더 움직입니다.
   - 하지만 baseline Sora의 `16.72`, manual Veo의 `16.94`에는 한참 못 미칩니다.
2. `same_shot_push_in_motion`
   - source보다 motion은 유의미하게 늘었습니다.
   - 그래도 original baseline보다는 아직 낮습니다.
   - 대신 보존성 손실은 baseline보다도 더 커진 쪽입니다.

## 6. 해석

### 이번 OVAT에서 확인된 것

1. `image-to-video -> edit` 2단계는 완전히 무의미하진 않았습니다.
2. 적어도 `same_shot_push_in_motion`은 source보다 motion을 실제로 늘렸습니다.
3. 하지만 motion이 올라가는 순간 보존성 손실도 함께 크게 올라갔습니다.
4. 즉 `edit`도 현재는 trade-off를 없애는 해법이 아니라, `보존성을 일부 희생해서 motion을 조금 회복하는 방법`에 가깝습니다.

### 이번 OVAT가 시사하는 것

1. 현재 Sora 조건에서는 `prompt`, `crop`, `edit` 모두 같은 근본 trade-off 안에 있습니다.
2. `source -> edit`는 single-pass보다 약간 더 나은 조절 수단일 수는 있습니다.
3. 하지만 이걸 바로 production 후보로 보기에는, `motion gain 대비 preserve loss`가 아직 큽니다.

## 7. 결론

- 가설 충족 여부: **부분 충족**
- 판단:
  - `edit 2단계`는 `motion을 조금이라도 회복할 수 있는가`라는 질문에는 `예, 제한적으로 가능`이라고 답할 수 있습니다.
  - 하지만 `원본 보존을 유지한 채 motion을 회복할 수 있는가`에는 아직 `아니오에 가깝다`고 봐야 합니다.
  - 따라서 이 경로는 `연구선 보조 후보` 정도로는 남길 수 있지만, 지금 시점의 본선 해답은 아닙니다.

## 8. 다음 액션

1. Sora 연구선은 이제 `same-shot edit`까지 확인했으므로, 다음은 `input modality` 자체를 바꾸는 쪽이 맞습니다.
   - 예: multi-reference, first/last frame, hybrid compositor
2. 본선은 계속 `template motion + deterministic packaging`을 우선 유지합니다.
3. `manual Veo`는 품질 upper-bound 참고선으로만 유지합니다.

## 9. 대표 artifact

- `docs/experiments/artifacts/exp-93-sora2-edit-motion-recovery-ovaat/summary.json`
- `docs/experiments/artifacts/exp-93-sora2-edit-motion-recovery-ovaat/same_shot_more_motion/contact_sheet.png`
- `docs/experiments/artifacts/exp-93-sora2-edit-motion-recovery-ovaat/same_shot_push_in_motion/contact_sheet.png`
- `docs/experiments/artifacts/exp-92-sora2-input-framing-ovaat/hero_tight_zoom/맥주/contact_sheet.png`
