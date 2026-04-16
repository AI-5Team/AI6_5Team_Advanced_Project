# Test Scenario 122 - Scene Preview Clean Mode Entry

## 목적

- `scene preview` 카드에서 opening / closing scene 각각에 대해 일반 보기와 clean mode 진입 링크를 바로 제공하는지 확인합니다.

## 확인 항목

1. `ScenePlanPreviewLinks`
   - 오프닝 씬에 `일반 보기`, `clean mode` 링크가 모두 보입니다.
   - 마감 씬에 `일반 보기`, `clean mode` 링크가 모두 보입니다.
2. 링크 경로
   - 일반 링크는 `/scene-frame/...?...projectId=...`
   - clean 링크는 `/scene-frame/...?...projectId=...&clean=1`
3. web build
   - 타입 오류 없이 `next build`가 통과합니다.

## 실행

```powershell
npm run build:web
```

## 기대 결과

- preview 카드에서 URL을 직접 고치지 않고도 일반 검토 모드와 clean mode를 바로 선택할 수 있습니다.
