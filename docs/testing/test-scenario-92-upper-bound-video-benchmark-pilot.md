# Test Scenario 92. Upper-bound video benchmark pilot

## 목적

- local LTX baseline과 hosted upper-bound 후보를 같은 샘플/프롬프트로 비교하는 benchmark 경로가 재현 가능한지 확인합니다.
- 이번 pilot에서는 `규카츠`, `맥주` 2장만 사용합니다.

## 준비물

1. 로컬 LTX 실행 환경
2. `ffmpeg`
3. `GEMINI_API_KEY`
4. `OPENAI_API_KEY`
5. 필요 시 `uv run --with google-genai`
6. 필요 시 `uv run --with openai`

## 실행 절차

### 1. 기본 pilot 실행

```powershell
python scripts/video_upper_bound_benchmark.py
```

### 2. local baseline만 다시 볼 때

```powershell
python scripts/video_upper_bound_benchmark.py --providers local_ltx
```

### 3. Sora 2만 확인할 때

```powershell
python scripts/video_upper_bound_benchmark.py --providers sora2
```

### 4. 단일 이미지로 확인할 때

```powershell
python scripts/video_upper_bound_benchmark.py --images "docs/sample/음식사진샘플(규카츠).jpg"
```

### 5. 수동 Veo 결과를 넣을 폴더

- `docs/experiments/artifacts/exp-90-upper-bound-video-benchmark/manual/veo/규카츠/veo_manual.mp4`
- `docs/experiments/artifacts/exp-90-upper-bound-video-benchmark/manual/veo/맥주/veo_manual.mp4`
- 이 결과는 어디까지나 `비교용 upper-bound reference`로만 봅니다.

## 기대 결과

### 공통

1. artifact root 아래에 `summary.json`이 생성됩니다.
2. provider별 run 폴더에 `prepared_input`, `summary.json`, `contact_sheet`가 생성됩니다.

### local LTX

1. `규카츠`, `맥주` 모두 `completed`가 나와야 합니다.
2. `규카츠`는 `cover_center`, `맥주`는 `cover_bottom`으로 분기되어야 합니다.
3. `contact_sheet.png`가 생성되어야 합니다.

### Veo 3.1

1. 현재 저장소 기준에서는 `RESOURCE_EXHAUSTED`가 발생할 수 있습니다.
2. 이 경우도 benchmark summary에는 `failed` 상태와 에러 메시지가 남아야 합니다.
3. quota가 충분한 환경에서는 `summary.json`에 `first/mid frame`, `contact_sheet`가 채워져야 합니다.

### Sora 2

1. 현재 저장소 기준에서는 실제 generation과 다운로드가 성공해야 합니다.
2. `summary.json`에 `first/mid frame`, `contact_sheet`가 채워져야 합니다.
3. contact sheet상 변화가 매우 작으면, `hosted 상위 모델도 current prompt family에서는 near-static`이라는 관찰로 기록합니다.

### Manual Veo

1. `video_upper_bound_benchmark.py`가 `manual_veo` provider로 자동 편입해야 합니다.
2. 규카츠에서 QR 유입, 주변 오브젝트 재구성처럼 `원본 보존 실패`가 보이면 명시적으로 기록합니다.
3. 맥주처럼 품질은 높지만 보존형 성공은 아닌 경우, `quality reference only`로 분리해서 기록합니다.

## 확인 포인트

1. local 결과의 contact sheet가 거의 정지 화면에 가까운지 확인합니다.
2. Sora 결과도 contact sheet 기준으로 큰 차이가 없다면, 병목은 `로컬 모델만의 문제`가 아닐 수 있습니다.
3. 이 관찰이 반복되면, 병목은 `shot routing`보다 `motion quality ceiling` 또는 `과제 정의`에 더 가깝다고 판단합니다.
4. Veo가 성공하면 같은 샘플/프롬프트 기준으로 local과 구조적 차이가 있는지 바로 비교합니다.
5. 현재 active 비교선은 `local_ltx`, `sora2`, `manual_veo`로 고정합니다.

## 관련 문서

- `docs/experiments/EXP-90-upper-bound-video-benchmark-pilot.md`
