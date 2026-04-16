# Test Scenario 96 - reference-first video direction review

## 목적

- 외부 레퍼런스와 상위권 시스템 설명을 기준으로, 현재 연구선이 왜 `reference-first`로 재정렬돼야 하는지 재현 가능하게 검토합니다.

## 입력 자료

1. 내부 문서
   - `docs/experiments/EXP-90-upper-bound-video-benchmark-pilot.md`
   - `docs/experiments/EXP-91-sora2-motion-prompt-family-ovaat.md`
   - `docs/experiments/EXP-92-sora2-input-framing-ovaat.md`
   - `docs/experiments/EXP-93-sora2-edit-motion-recovery-ovaat.md`
   - `docs/experiments/EXP-94-reference-first-video-direction-review.md`
2. 외부 레퍼런스
   - `https://youtube.com/shorts/dWDBSbwlReI?si=Rsuce3bfSMNRw3zU`
   - `https://youtube.com/shorts/P4Zx3JrgA30?si=4bcrQIrRsO24OhH-`
   - `https://youtube.com/shorts/1wi_KY5zopY?si=iyY-DUJLi9BCDySS`
   - `https://www.genre.ai/`
   - `https://deepmind.google/models/veo/prompt-guide/`
   - `https://developers.googleblog.com/id/introducing-veo-3-1-and-new-creative-capabilities-in-the-gemini-api`
   - `https://higgsfield.ai/ai-video`

## 절차

1. `EXP-90`을 읽고 manual Veo가 `비교용 upper-bound`일 뿐 production answer가 아니라는 점을 다시 확인합니다.
2. `EXP-91`, `EXP-92`, `EXP-93`을 읽고 현재 연구선의 핵심 병목이 `preserve-motion trade-off`라는 점을 확인합니다.
3. 외부 유튜브 레퍼런스 3개를 열어 제목과 첫 인상을 확인합니다.
4. 아래 항목을 기준으로 각 레퍼런스를 짧게 메모합니다.
   - hook 유형
   - product hero 표현 여부
   - B급 감성의 방식
   - 텍스트/카피 사용 여부
   - 원본 보존이 핵심인지, 재해석이 허용되는지
5. Veo/Higgsfield 공개 자료를 읽고, 이 시스템들이 `단일 모델`보다 `control/workflow`를 얼마나 전면에 두는지 확인합니다.
6. `EXP-94`의 결론과 비교해 아래 판단을 체크합니다.
   - 현재 연구선은 raw prompt digging만으로는 한계가 있는가
   - reference-first 방향 전환이 필요한가
   - strict preserve와 creative reinterpretation을 분리해야 하는가

## 기대 결과

1. 상위권 결과물은 `좋은 모델 1개`보다 `모델 + reference control + creative workflow + ad grammar` 조합일 가능성이 높다는 결론에 도달합니다.
2. 현재 내부 연구선은 `원본 보존` 요구가 강해서, 외부 레퍼런스의 성격과 목표가 완전히 같지 않다는 점을 명시합니다.
3. 다음 연구는 `prompt를 한 번 더 깎는 것`보다 `reference teardown + objective split`이 우선이라는 판단을 재현합니다.

## 판정 기준

- 아래 3개가 모두 맞으면 통과입니다.
  1. manual Veo를 production baseline처럼 해석하지 않았는가
  2. preserve와 creative quality를 분리해서 봤는가
  3. 다음 액션을 `reference-first` 기준으로 다시 정리했는가
