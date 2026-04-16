# EXP-261 — 병렬 에이전트 4종 전방위 감사: 기획 정렬도 · 실험 드리프트 · 제품 코드 · 모델 전략

**날짜**: 2026-04-14  
**감사 방법**: 메인 에이전트가 4개 서브에이전트를 병렬 실행 후 종합  
**목적**: "이 방향이 서비스 출시로 이어질 수 있는가"를 처음부터 다시 심판  
**선행 감사**: EXP-259, EXP-260 (같은 날 다른 에이전트가 독립 작성)

---

## 감사 구성

| 서브에이전트 | 담당 범위 |
|---|---|
| **Agent A** | 기획 문서 / ADR / HISTORY 정렬도 |
| **Agent B** | 실험 품질·유효성·드리프트 (EXP-00 ~ EXP-260) |
| **Agent C** | 제품 코드 (worker / api / web) E2E 플로우 생존도 |
| **Agent D** | 모델 전략 / 상용 모델 접근성 (웹 검색 기반 실시간 확인) |

---

## 1. 현재 진행방향 총평

### 판정: **일부는 맞지만, 핵심에서 이탈 중 (정렬도 약 48/100)**

기획의 핵심 약속은 "사진 몇 장 → AI 자동 숏폼 영상 생성 → SNS 업로드"였다.
현재 실제 진행은 "선택형 입력 → 템플릿 기반 패키징 + zoompan 모션 → 하이브리드 overlay → 업로드 보조"다.

이 차이는 실수가 아니다. 기술적 한계에 부딪혀 현실적으로 수렴한 결과다.
문제는 이 수렴을 **공식적으로 인정하지 않은 채 실험과 구현이 계속됐다**는 것이다.

**근거:**
- ADR-005~008 구간에서 "B급 감성 영상 실험 우선화 → Pillow 거절 → HTML/CSS 전환 → scene-lab 장기화"의 이탈 연쇄가 발생했다.
- EXP-39(2026-04-08)와 EXP-87(2026-04-09)에서 이미 드리프트를 명시적으로 경고했으나, 이후 약 150개 실험이 추가됐다.
- EXP-259, EXP-260에서야 "사실상 제품 정의가 변경됐다"는 공식 인정이 이뤄졌다.

---

## 2. 서비스 출시 가능성 판정

### A. 현재 비전 그대로 ("완전 자동 숏폼 영상 생성")

**현재 자원 기준: 사실상 어려움**

| 근거 항목 | 판단 |
|---|---|
| 로컬 LTX-Video (54개 실험 후) | near-static 수준. 상업 광고 motion 미달 |
| Sora 2 (i2v, EXP-91~93 + EXP-240~242) | API는 작동하나 보존성↑↔motion↓ trade-off 구조적으로 해결 불가 |
| Sora 2 repeatability | 동일 입력에서 avg_rgb_diff 1.6~21 편차. production baseline 불가 |
| Sora API 지속성 | **2026-09-24 폐지 예정** (OpenAI 공식) |
| Veo 3.1 | 429 RESOURCE_EXHAUSTED. 현재 키로 접근 불가 |
| Seedance 2.0 | fal.ai API는 존재하나 OpenAI key만으로 접근 불가 |

**상위 모델(Veo/Seedance) 접근이 열릴 경우: 조건부 가능 (단, 리스크 잔존)**

- Manual Veo 결과(EXP-90): 맥주는 고품질, 규카츠는 QR·배경 재해석 → 원본 보존 실패 사례 있음
- 보존 vs 광고 감성 trade-off는 모델 품질만의 문제가 아님 (EXP-94 결론)
- Veo 3.1 Standard: $0.40/초. 10초 클립 = $4. 대량 생성 비용 부담
- Seedance 2.0 (fal.ai): $3.03/10초. 별도 결제 계정 필요

> **이 두 판정을 절대 섞지 말 것:** 현재 자원으로는 어렵고, 상위 모델이 있어도 보존/감성 문제는 별도 해결 과제다.

---

### B. Scope를 줄인 경우 ("하이브리드 패키징 + 업로드 보조 도구")

**현재 자원 기준: 조건부 출시 가능**

- 이미 구현돼 있는 것: zoompan 모션 + template overlay + caption/hashtag + upload assist
- LLM 카피 생성: gpt-5-mini로 OpenAI key만 있으면 가능 (단, 코드 연결 미완성)
- SNS 자동 업로드: Instagram은 실제 API 연동 필요 (현재 mock 수준)
- 출시까지 남은 작업: 2~3주 집중 시 가능
- **이 방향은 "소상공인 SNS 광고 패키징 보조 도구"이지 "완전 자동 영상 생성 서비스"가 아님**
- 공식 제품 정의 재선언이 선행되어야 한다

---

## 3. 맞게 가고 있는 축

### 3-1. 기본 서비스 루프 (O)
- 사진 업로드 → 템플릿/스타일 선택 → 생성 → 결과 확인 → 빠른 수정 → 게시/보조
- worker pipeline이 실제 동작하는 코드로 존재 (preprocessing, scene plan, render, packaging)
- Quick action 정책 (highlightPrice, shorterCopy, emphasizeRegion 등) 설계 완료

### 3-2. 텍스트 카피 생성 기반 (O)
- EXP-127 이후 prompt baseline freeze 완료
- gpt-5-mini / Gemma 4 분배 체계 연구 완료
- 단, **코드 경로가 아직 deterministic `_build_copy_bundle()` 수준** — LLM 연결이 실제로 안 됐다

### 3-3. 실험 문서화 규율 (O)
- ADR, EXP, daily, testing 체계 유지
- EXP-259, EXP-260, EXP-261 같은 자기 감사 실험이 존재한다는 것 자체가 긍정적

### 3-4. 모션 렌더링 기반 (O)
- `services/worker/renderers/media.py` - zoompan_control, hybrid_video 실제 구현
- `services/worker/renderers/framing.py` - shot classifier (tray/drink/preserve) 정책 안정화
- T02/T04 x 8샘플 baseline matrix 재현 가능

---

## 4. 방향이 샌 축

### 4-1. 로컬 LTX OVAT 과잉 투자 — 가장 큰 드리프트

**EXP-34~EXP-86 (53개)**

- 동일한 "보존 vs 모션" 문제를 prompt 길이, steps, frames, steam, texture, camera motion, negative prompt, food category, prepare mode로 나눠서 53번 반복
- EXP-39에서 이미 "diminishing return"이라고 판정했음에도 계속됨
- 결론은 EXP-73에서 나왔다: "준비 모드 자동 분류는 안정화됐으나, motion 수준은 near-static"
- EXP-74~86은 사실상 동일 결론의 재확인

**멈췄어야 할 시점**: EXP-73 직후 (EXP-74부터 중단했다면 13개 실험 절약)

### 4-2. 카피 coverage audit 과포화

**EXP-140~EXP-220 (약 80개)**

- coverage audit → quick option gap priority → profile snapshot 패턴이 템플릿 조합마다 반복됨
- 개별 실험은 각각 정당하나, 전체적으로 "같은 검증 도구의 순차 적용"이어서 새 인사이트가 거의 없음
- 이 패턴에 80개 실험을 쓰는 동안 실제 LLM 카피 생성 코드 연결(production 경로)은 방치됨

### 4-3. 제품 정의 공식 재선언 부재

- EXP-39, EXP-87에서 이미 경고 → EXP-259, EXP-260에서 공식 인정
- 그 사이에 약 170개 실험이 "사실상 변경된 제품 정의" 위에서 진행됐으나, 기획 문서는 갱신 안 됨
- 기획 문서 01_SERVICE_PROJECT_PLAN.md는 여전히 "완전 자동 숏폼 영상 생성"으로 명시돼 있음

### 4-4. 사용자 검증 부재

- 기획 평가 기준 최우선: "타깃 사용자 3명 이상 인터뷰"
- 현재 기준: 0건
- 기술 실험 260개, 사용자 피드백 0건 — 이 불균형은 제품보다 연구에 가까운 상태를 의미

---

## 5. 실험 축 정리 (진짜 남는 것 / 닫아야 할 것 / 방향이 샌 것)

### 진짜 남는 실험

| 실험 | 이유 |
|---|---|
| EXP-01~39 (초기 기초) | 서비스 구조(템플릿, hook/body/CTA, 선택형 입력)의 기반을 닦음 |
| EXP-39 (Midpoint Review) | 최초 드리프트 경고. 지금도 유효한 분석 |
| EXP-87 (Direction Review) | 본선 코드 전수 점검. 현재도 참고 가치 높음 |
| EXP-90 (Upper-bound Benchmark) | Local LTX vs Sora vs Veo 품질 비교. 핵심 한계 명확화 |
| EXP-94 (Reference-first Direction) | "프롬프트 깎기가 아니라 광고 문법 벤치마킹"으로의 패러다임 전환 |
| EXP-127 (Prompt Baseline Freeze) | 카피 생성 baseline 고정. 실제 production에 연결만 하면 됨 |
| EXP-231~236 (Shot-aware Renderer) | `zoompan_control + framing policy` = 현재 production baseline |
| EXP-243~244 (Hybrid Packaging Proof) | 생성형 영상 + template overlay 결합 가능성 증명 |
| EXP-259, EXP-260 (자기 감사) | 정직한 자기 평가. 방향 재정립의 토대 |

### 이제 닫아야 할 실험

| 실험 범위 | 이유 |
|---|---|
| 로컬 LTX OVAT 추가 실험 | EXP-73에서 결론 완료. 새 파라미터 시도는 추가 인사이트 없음 |
| Sora 2 motion prompt 추가 OVAT | EXP-91~93, EXP-240~242에서 결론 완료. 구조적 trade-off는 prompt로 해결 불가 |
| 카피 coverage audit 추가 사이클 | EXP-161 이후 신규 P1/P2 공백 없음. 기존 체계로 충분 |

### 방향이 샌 실험

| 실험 범위 | 드리프트 유형 |
|---|---|
| EXP-40~86 (LTX OVAT 53개) | 기술적 낙관주의 — "더 나은 파라미터가 있을 것"이라는 반복 |
| EXP-140~220 (coverage audit 80개) | 수단의 목적화 — 검증 도구 실행이 목적이 됨 |
| scene-lab 장기화 (EXP-10~14 이후) | ADR-008의 결과. HTML/CSS baseline이 production에 안 올라온 채 연구만 됨 |

---

## 6. 현재 기준의 핵심 baseline 정리

### Product/Service Baseline
- **상태**: 잡힘 (조건부)
- 실제: 사진 업로드 → zoompan 모션 + template overlay 렌더링 → caption/hashtag 패키징 → 업로드 보조
- 공백: LLM 카피 생성 코드 연결 미완, SNS API 실 연동 미완 (Instagram mock 수준)
- **진짜 baseline이라 부를 수 있는가**: "데모 가능한 prototype"은 맞지만, production은 아님

### Prompt/Copy Baseline
- **상태**: 잡힘
- 실제: gpt-5-mini (promotion) + Gemma 4 (review) 분배. EXP-127 freeze.
- 공백: worker 코드 경로에 실제 LLM 호출이 없음 (_build_copy_bundle()이 stub 수준)
- **진짜 baseline이라 부를 수 있는가**: 연구 baseline은 맞음. Production 연결은 별도 작업 필요

### Local/Open-source Video Baseline
- **상태**: 닫혔음 (실패 확인)
- 실제: LTX-Video 2B GGUF. near-static. 평균 MSE 357, 처리 11.78초
- **진짜 baseline이라 부를 수 있는가**: "이 수준은 광고형 motion에 미달"이라는 결론이 baseline

### Paid Frontier Model Baseline
- **상태**: 미결 (접근 불가)
- Sora 2: repeatability 낮음, API 폐지 예정
- Veo 3.1: quota 초과, 접근 불가
- Seedance 2.0: OpenAI key만으로 불가
- **진짜 baseline이라 부를 수 있는가**: 아니다. 상위 모델도 "보존 + 모션" 동시 달성이 미해결 과제

---

## 7. 모델 전략 판단

### 핵심 판단

> **Veo/Seedance 급 모델이 사실상 필요하다.**  
> 단, 그것이 있다고 해서 "원본 사진 보존 + 광고형 motion"이 자동으로 해결되지는 않는다.

**판단 근거:**
1. LTX near-static = 로컬 경로는 닫힘
2. Sora 2 = 기술적 접근은 됐으나 production baseline 조건 미충족 + API 폐지 예정
3. Manual Veo = 고품질이지만 원본 보존 실패 사례 있음 (규카츠 QR·배경 재해석)
4. "보존 + 모션" 동시 달성은 단일 I2V 모델의 프롬프트로 해결되지 않음 (EXP-94 결론)
5. 더 나은 시스템은 "더 좋은 모델" + "광고 문법 + 다단계 워크플로우 + 제어 인터페이스" 조합

### OpenAI key만 있는 현재 조건에서 가능한 전략

| 전략 | 가능 여부 | 비고 |
|---|---|---|
| gpt-5-mini로 카피 생성 | 가능 | 코드 연결만 하면 됨 |
| Sora 2로 영상 생성 | 제한적 | Tier 2 이상 필요. 폐지 예정 |
| DALL-E로 보조 이미지 생성 | 가능 | 활용 안 됨 |
| FFmpeg + template overlay | 가능 | 현재 production 경로 |
| Veo/Seedance | 불가 | 별도 결제 계정 필요 |

### 결론

> **현재 자원 조건(OpenAI key 중심)에서는 "완전 자동 숏폼 영상 생성" 비전을 그대로 출시할 수 없다.**  
> "템플릿 기반 하이브리드 패키징 + LLM 카피 + 업로드 보조" 모델로 공식 축소해야 한다.  
> 이 방향은 소상공인에게 여전히 실질적인 가치를 제공할 수 있으나, 원래 기획과 다르다는 것을 명확히 선언해야 한다.

---

## 8. 다음 우선순위 제안

### 1순위: 제품 정의 공식 재선언 (1~2일)

**이유**: 지금 팀이 무엇을 만들고 있는지에 대한 공유된 이해가 없으면, 이후 어떤 작업을 해도 방향이 다시 샌다.

**액션**:
- 기획 문서 01_SERVICE_PROJECT_PLAN.md에 제품 정의 v2.0 추가
- "완전 자동 영상 생성" vs "하이브리드 패키징 도구" 중 어느 것인지 명시
- 전자 유지 시: 상위 모델 접근 전략 및 예산 확보 계획 필요
- 후자 선택 시: 실험/연구 표면 대폭 축소 + launch surface 정리로 집중

### 2순위: LLM 카피 생성 production 연결 (2~3일)

**이유**: 카피 생성 연구(EXP-127)는 완료됐으나 실제 코드 경로에 LLM 호출이 없다. 가장 명확하고 현실적인 AI 가치 추가 지점이다.

**액션**:
- `services/worker/pipelines/generation.py`의 `_build_copy_bundle()` stub → gpt-5-mini 실제 호출로 교체
- OpenAI key 있으면 즉시 가능
- 비용: 카피 1세트 생성당 약 $0.001 (gpt-5-mini 기준)

### 3순위: 사용자 검증 착수 (1주)

**이유**: 260개 기술 실험을 했지만 사용자 피드백은 0건이다. 기술 완성도와 무관하게 시장 적합성을 모른다.

**액션**:
- 카페/음식점/미용실 운영자 3~5명 대면 인터뷰
- 현재 시연물 (데모 환경) 사용성 피드백 수집
- "AI가 만들어 주는 광고 숏폼"에 대한 실제 반응 확인

---

## 9. 계속 / 중단 / 보류

### 지금 바로 계속할 것

1. **LLM 카피 생성 코드 연결** — 연구는 끝남. 구현만 남았음
2. **SNS 연동 실 구현** — Instagram OAuth + 실제 업로드 (현재 mock)
3. **결과 화면 UX 정리** — video/post 미리보기 앞배치, 패키지 다운로드 UX
4. **제품 정의 재선언 문서 작성**

### 지금 바로 멈출 것

1. **로컬 LTX 추가 파라미터 OVAT** — EXP-73에서 결론 완료
2. **Sora 2 motion prompt 추가 OVAT** — EXP-93 + EXP-240~242에서 결론 완료
3. **카피 coverage audit 추가 사이클** — EXP-161 이후 새 P1/P2 공백 없음
4. **새 모델 탐색 실험** (Veo/Seedance 접근 불가한 상태에서)

### 판단 유보

1. **상위 모델 접근 전략** — 예산/접근 가능 여부에 따라 결정
2. **생성형 영상 재시도** — 상위 모델 접근이 열리면 EXP-94의 "reference-first + 다단계 워크플로우" 방식으로 재시도
3. **YouTube Shorts/TikTok 자동 업로드** — 출시 후 Phase 2로 검토

---

## 10. 바로 실행 가능한 다음 액션 (다음 세션)

1. **`01_SERVICE_PROJECT_PLAN.md`에 제품 정의 v2.0 섹션 추가**  
   - "현재 출시 범위"와 "Phase 2 이후로 미루는 범위" 명확히 구분  
   - 영상 생성을 "보조 모듈"로 명시

2. **`services/worker/pipelines/generation.py`의 `_build_copy_bundle()` 수정**  
   - gpt-5-mini 실제 호출 연결  
   - EXP-127의 prompt profile manifest를 실제 코드에서 로드하는 구조로 변경

3. **Instagram OAuth 실 구현**  
   - `services/api/app/services/runtime.py`의 publish mock → 실제 Graph API 호출  
   - Access token 저장/갱신 로직 추가

4. **결과 화면 미리보기 개선**  
   - `apps/web/src/components/ResultMediaPreview` — scene plan 링크 대신 실제 video player 앞배치  
   - caption/hashtag 복사 UX 정리

5. **소상공인 사용자 인터뷰 3건**  
   - 현재 시연물 기준 UX 피드백  
   - "이 도구가 실제로 쓸 만한가" 확인

---

## 11. 판정 요약

| 질문 | 판정 |
|---|---|
| 기획 의도와의 정렬도 | **48/100** (부분 정렬, 핵심 이탈 있음) |
| 현재 비전 그대로 출시 가능성 | **어려움** (현재 자원 기준) |
| Scope 축소 시 출시 가능성 | **조건부 가능** (2~3주 집중 필요) |
| 상위 모델 있을 경우 출시 가능성 | **조건부 가능** (보존/감성 trade-off는 별도 해결 과제) |
| 실험선 드리프트 여부 | **있음** (약 130개 실험이 드리프트 또는 과포화) |
| 다음 1순위 | **제품 정의 공식 재선언** |
| 지금 멈춰야 할 것 | **LTX OVAT / Sora OVAT / coverage audit 추가 사이클** |

---

*이 문서는 EXP-259, EXP-260과 독립적으로 작성된 병렬 감사 기록입니다.*  
*다른 에이전트의 문서를 덮어쓰지 않으며, 추가 관점으로 보완 역할을 합니다.*
