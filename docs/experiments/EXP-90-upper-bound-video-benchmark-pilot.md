# EXP-90 Upper-bound video benchmark pilot

## 1. 기본 정보

- 실험 ID: `EXP-90`
- 작성일: `2026-04-09`
- 작성자: Codex
- 관련 기능: `상위 hosted video baseline 점검 / local LTX vs Veo vs Sora upper-bound pilot`

## 2. 왜 이 작업을 했는가

- 최근 local LTX 연구는 `prepare_mode`, `framing`, `prompt phrase` 기준선은 어느 정도 정리됐지만, 정작 사용자가 느끼는 문제는 `영상이 충분히 좋아 보이지 않는다`는 쪽에 더 가깝습니다.
- 그래서 지금 필요한 질문은 `LTX를 더 깎으면 되는가`가 아니라 `single-photo 음식/음료 I2V라는 접근 자체가 현재 baseline으로 충분한가`였습니다.
- 이 질문에 답하려면 local baseline만 반복하는 대신, `상위 hosted model upper-bound`와 최소 비교를 시도해 봐야 합니다.

## 3. 기준과 가설

### 이번에 검증한 가설

1. local LTX baseline은 일부 샘플에서 스틸 프레임은 버티더라도, 실제 motion은 너무 약하거나 거의 정지 화면에 가까울 수 있습니다.
2. hosted upper-bound가 같은 샘플에서 확실히 더 좋아 보이면 병목은 `로컬 모델 ceiling`에 가깝습니다.
3. hosted upper-bound도 크게 다르지 않으면 병목은 `single-photo 음식/음료 I2V 과제 자체`에 더 가깝습니다.

### 이번 pilot의 고정 조건

1. 비교 샘플
   - `규카츠`
   - `맥주`
2. 공통 prompt family
   - tray/full-plate는 `product preservation + gentle steam + minimal motion`
   - drink는 `shape preservation + realistic liquid/glass detail + minimal drift`
3. local baseline
   - `LTX-Video 2B / GGUF`
   - `25 frames / 8 fps / 6 steps / seed 7`
   - prepare mode: `auto`
4. hosted upper-bound target
   - `Veo 3.1` image-to-video
   - `Sora 2` image-to-video

## 4. 무엇을 만들고 바꿨는가

### 스크립트

1. `scripts/video_benchmark_common.py`
   - 공통 샘플 라이브러리
   - upper-bound prompt builder
   - prepare mode 적용
   - frame metric 계산
   - contact sheet 생성
2. `scripts/hosted_video_veo31_first_try.py`
   - `GEMINI_API_KEY` 기반 Veo 3.1 image-to-video 실행
   - prepared input 저장
   - mp4 다운로드
   - first/mid frame 추출 및 metric 저장
3. `scripts/hosted_video_sora2_first_try.py`
   - `OPENAI_API_KEY` 기반 Sora 2 image-to-video 실행
   - prepared input 저장
   - mp4 다운로드
   - first/mid frame 추출 및 metric 저장
4. `scripts/video_upper_bound_benchmark.py`
   - `local_ltx`, `veo31`, `sora2`, `manual_veo`를 같은 샘플/프롬프트로 비교
   - provider별 summary/contact sheet를 한 artifact root에 정리

### 문서

1. 이 문서 `EXP-90`
2. `docs/testing/test-scenario-92-upper-bound-video-benchmark-pilot.md`

## 5. 실행 결과

artifact root:

- `docs/experiments/artifacts/exp-90-upper-bound-video-benchmark/`

대표 artifact:

- `summary.json`
- `local_ltx/규카츠/contact_sheet.png`
- `local_ltx/맥주/contact_sheet.png`
- `sora2/규카츠/contact_sheet.png`
- `sora2/맥주/contact_sheet.png`
- `manual_veo/규카츠/contact_sheet.png`
- `manual_veo/맥주/contact_sheet.png`

### local LTX pilot 결과

#### 규카츠

- status: `completed`
- elapsed: `41.24s`
- prepare mode: `cover_center`
- mid-frame MSE: `254.76`
- 관찰:
  - mid-frame 정지 이미지만 보면 구조는 꽤 보존됩니다.
  - 그러나 contact sheet 기준으로는 4개 프레임이 거의 같은 화면이고, 실제 motion이 거의 느껴지지 않습니다.
  - 즉 `움직이는 영상`이라기보다 `거의 멈춘 음식 사진`에 가깝습니다.

#### 맥주

- status: `completed`
- elapsed: `42.21s`
- prepare mode: `cover_bottom`
- mid-frame MSE: `101.32`
- 관찰:
  - bottle/glass 구조는 유지됩니다.
  - label도 완전히 무너지진 않았습니다.
  - 하지만 contact sheet 기준으로는 여기서도 움직임 변화가 작고, `광고용 motion`으로 느껴질 정도의 설득력은 약합니다.

### Veo 3.1 pilot 결과

- 두 샘플 모두 실행 시도는 됐지만 실제 generation은 시작되지 못했습니다.
- 결과:
  - `규카츠`: `429 RESOURCE_EXHAUSTED`
  - `맥주`: `429 RESOURCE_EXHAUSTED`
- 즉 현재 저장소에 설정된 `GEMINI_API_KEY` 상태에서는 Veo upper-bound를 반복 가능한 benchmark로 돌릴 수 없습니다.

### Sora 2 pilot 결과

#### 규카츠

- status: `completed`
- elapsed: `89.63s`
- prepare mode: `cover_center`
- 관찰:
  - 실제 생성과 다운로드는 성공했습니다.
  - local LTX보다 더 강하게 crop되고 대비도 높아졌습니다.
  - 결과 화면은 더 광고 컷처럼 정리됐지만, contact sheet 기준으로는 여기서도 프레임 변화가 크지 않습니다.
  - 즉 `고품질 still + 약한 motion` 쪽에 더 가깝습니다.

#### 맥주

- status: `completed`
- elapsed: `95.87s`
- prepare mode: `cover_bottom`
- 관찰:
  - bottle / glass / foam은 비교적 안정적으로 재구성됐습니다.
  - 특히 foam과 유리 질감은 local보다 더 그럴듯하게 보입니다.
  - 하지만 contact sheet 기준으로는 움직임 변화가 여전히 제한적입니다.
  - 즉 hosted 상위 모델을 써도, 지금 prompt family와 single-photo 입력 조건에서는 기대한 만큼의 `광고형 motion`이 자동으로 나오진 않았습니다.

### Manual Veo 비교 결과

#### 공통 전제

- 이 manual Veo 결과는 어디까지나 `비교용 upper-bound reference`입니다.
- 프로젝트의 핵심 요구인 `원본 사진을 최대한 유지한 채 영상화`를 만족하는 production 후보로 바로 취급하면 안 됩니다.

#### 규카츠

- 관찰:
  - 품질 자체는 확실히 좋습니다.
  - 하지만 원본 사진 보존 관점에서는 실패에 가깝습니다.
  - 메인 규카츠 컷은 살아 있지만, 주변 요소가 재해석되거나 재구성됐습니다.
  - 특히 메뉴판 쪽 QR이 우측 상단에 로고처럼 들어왔고, 서브 오브젝트도 원본 그대로 유지되지 않았습니다.
  - 따라서 `원본을 유지하면서 motion만 추가`하는 목적에는 맞지 않습니다.

#### 맥주

- 관찰:
  - 이번 비교군 중 체감 품질이 가장 좋았습니다.
  - bottle, glass, foam, 질감, 조명 표현이 강하고, 참고점으로 삼을 가치가 있습니다.
  - 다만 이것도 production 기준에서는 `원본 충실 보존`이 아니라 `고품질 재해석`에 더 가깝습니다.
  - 즉 품질 참고에는 매우 유효하지만, 보존형 생성 성공으로 해석하면 안 됩니다.

## 6. 해석

### 이번 pilot에서 확인된 것

1. 지금 local LTX baseline의 핵심 병목은 `shot routing`보다 `motion quality ceiling`에 더 가깝습니다.
2. `Sora 2`는 실제 생성 성공까지 확인됐지만, 현재 조건에서는 hosted upper-bound라고 해도 `강한 motion`이 자동으로 확보되진 않았습니다.
3. `manual Veo`는 품질 상한선 참고로는 분명 유효합니다.
4. 하지만 특히 `규카츠`에서 보듯, 품질이 올라가도 `원본 사진 보존`은 쉽게 무너질 수 있습니다.
5. 즉 지금 문제는 단순히 `퀄리티가 낮다`만이 아니라, `품질`과 `보존성`이 서로 충돌할 수 있다는 점입니다.
6. 따라서 지금부터 더 많은 micro OVAT를 쌓더라도, 사용자가 느끼는 문제인 `영상 품질 부족`과 `원본 보존 실패`를 동시에 뒤집지 못할 가능성이 큽니다.

### active comparison set 주의

- 현재 활성 비교선은 `local LTX`, `Sora 2`, `manual Veo reference`입니다.
- `manual Veo`는 어디까지나 `비교용 upper-bound reference`입니다.
- `Seedance`는 크레딧 이슈로 이번 비교선에서는 제외했습니다.

### 이번 pilot에서 아직 확인하지 못한 것

1. `Veo 3.1`이 실제로 얼마나 더 나은지
2. `Sora 2`에서 prompt family를 더 공격적으로 바꾸면 motion이 살아나는지
3. `Veo`에서 QR / 배경 객체 오염을 줄이는 보존형 프롬프트가 가능한지
4. single-photo가 아니라 multi-reference 또는 first/last frame 조건이면 결과가 달라지는지

즉 hosted 비교는 일부 열렸지만, 아직 `확실한 상한선 승자`를 말할 정도는 아닙니다.

## 7. 제약과 운영 리스크

1. `Veo 3.1`은 공식적으로 image-to-video와 `4/6/8s`, `720p/1080p/4k`를 지원합니다.
2. 하지만 usage tier와 billing 상태에 따라 rate limit이 달라지고, 현재 키 상태에서는 `RESOURCE_EXHAUSTED`가 발생했습니다.
3. `Sora 2`는 현재 키 상태에서 실제 생성까지 가능했습니다.
4. 다만 이번 prompt family에서는 `움직임 설득력`이 기대만큼 강하지 않았습니다.
5. `manual Veo`는 quality reference로는 의미 있었지만, 규카츠에서는 QR과 주변 객체 재해석이 들어와 보존성 문제가 분명했습니다.
6. `Higgsfield`는 아직 키가 없어서 이번 pilot에는 포함하지 못했습니다.
7. 참고로 Higgsfield 공식 SDK 문서의 `HF_KEY`, `HF_API_KEY`, `HF_API_SECRET` 표기는 현재 저장소의 Hugging Face 관련 `HF_*` 이름과 충돌 여지가 있으므로, 실제 연동 시에는 `HIGGSFIELD_API_KEY`, `HIGGSFIELD_API_SECRET` 같은 별도 이름을 쓰는 편이 안전합니다.

## 8. 결론

- 가설 충족 여부: **부분 충족**
- 판단:
  - local baseline만 봐도, 현재 병목은 `분기 정책`보다 `실제 motion 품질`입니다.
  - 즉 `이 정도 품질로 어떻게 실험을 쌓나`라는 문제의식은 타당합니다.
  - 그리고 `hosted 상위 모델이면 자동으로 해결된다`도 아직 아닙니다.
  - 실제로 `Sora 2`는 실행에 성공했지만, 현재 조건에서는 결과가 여전히 near-static 성격을 보였습니다.
  - `manual Veo`는 품질 면에서 특히 맥주 샘플이 강한 참고점이 됐습니다.
  - 하지만 규카츠처럼 `원본 유지`가 깨지는 순간, 이건 production 후보가 아니라 `비교용 상한선`으로만 써야 합니다.
  - 따라서 지금은 `모델 교체`만이 아니라 `입력 방식`, `prompt family`, `과제 정의`, `보존성 요구`까지 같이 재검토해야 합니다.

## 9. 다음 액션

1. `manual Veo`는 앞으로도 `비교용 upper-bound reference`로만 취급합니다.
2. `Sora 2`에서 `minimal motion` 계열 prompt 대신 더 직접적인 motion prompt family를 별도 OVAT로 확인합니다.
3. `Veo`는 quota/credential을 먼저 확보합니다.
4. 확보 즉시 같은 benchmark 스크립트로 `규카츠/맥주`를 재실행합니다.
5. hosted 결과가 local보다 확실히 좋으면:
   - 문제는 `로컬 모델 ceiling`에 더 가깝습니다.
6. hosted 결과도 비슷하게 약하면:
   - 문제는 `single-photo 음식/음료 I2V 과제 자체`에 더 가깝습니다.
7. 그 경우 본선은 `템플릿 motion + compositor + 선택적 생성형 삽입` 쪽으로 더 빠르게 기울여야 합니다.

## 10. 참고 자료

- Veo 3.1 official video generation docs:
  - https://ai.google.dev/gemini-api/docs/video
- Gemini API rate limits / usage tiers:
  - https://ai.google.dev/gemini-api/docs/rate-limits
- OpenAI video generation docs:
  - https://platform.openai.com/docs/guides/video
- Higgsfield SDK docs:
  - https://docs.higgsfield.ai/how-to/sdk
