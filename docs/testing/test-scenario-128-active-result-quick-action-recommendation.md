# Test Scenario 128 - Active Result Quick Action Recommendation

## 목적

- 메인 결과 화면이 active result 기준 추천 quick action을 표시하면서도 타입 오류 없이 빌드되는지 확인합니다.

## 확인 항목

1. recommendation helper
   - result, purpose, detailLocation, template, style 기준으로 추천 action 목록을 만듭니다.
2. quick action cards
   - 추천 action에는 badge, priority, 이유가 같이 보입니다.
   - 모든 action은 계속 영향 레이어 preview를 유지합니다.
3. web build
   - 추천 로직 추가 후에도 빌드가 깨지지 않습니다.

## 실행

```powershell
npm run build:web
```

## 기대 결과

- 사용자는 현재 결과를 기준으로 어떤 quick action을 먼저 눌러볼지 화면에서 바로 제안받을 수 있습니다.
