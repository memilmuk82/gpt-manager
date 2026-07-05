# GPT Manager Design Decisions

## 1. 선택한 디자인 방향

### Apple을 전체 가독성과 여백 기준으로 선택한 이유

Apple의 강점은 읽기 쉬운 typography, 명확한 hierarchy, 넉넉한 whitespace다. GPT Manager는 교사가 업무 중 반복적으로 확인하는 시스템이므로 과한 장식보다 피로도가 낮은 읽기 경험이 중요하다. 본 프로젝트에서는 Apple의 제품 사진 중심 연출이 아니라 가독성, 간격, 정보 위계만 채택한다.

영향:

- 한국어 본문 line-height 유지
- H1, section title, card title 위계 명확화
- 불필요한 장식 최소화

### Vercel을 Landing 기준으로 선택한 이유

Vercel은 첫 화면에서 제품 가치, CTA, 기능 섹션을 빠르게 전달한다. GPT Manager의 Landing도 로그인 전 사용자가 서비스 목적과 다음 행동을 즉시 이해해야 한다.

영향:

- Landing은 프로젝트명, 한 줄 설명, CTA, 핵심 기능 4개를 우선한다.
- 실제 구현 범위의 운영 미리보기만 표시하고, AI 비교 예시는 미구현 기능처럼 보일 수 있어 제외한다.

제한:

- Vercel식 대형 gradient는 이 프로젝트의 학교 업무 맥락과 맞지 않아 제외한다.

### GitHub를 관리 화면 기준으로 선택한 이유

GitHub의 관리 화면은 table, badge, log, status 표현이 명확하고 밀도가 좋다. GPT Manager의 관리자 화면은 사용자, 예약, 로그, 테스트, 백업, 감사 로그를 다루므로 GitHub식 정보 구조가 적합하다.

영향:

- table은 dense하지만 읽기 가능한 row height를 유지한다.
- 상태는 badge + text로 표현한다.
- log와 test output은 monospace block으로 표시한다.

### Linear를 SaaS 카드와 상태 표현 기준으로 선택한 이유

Linear는 복잡한 업무 상태를 차분한 card와 status 표현으로 정리한다. GPT Manager Dashboard와 Admin section launcher는 상태와 다음 행동을 빠르게 보여줘야 하므로 Linear의 SaaS card 언어가 적합하다.

영향:

- Status Card, Quick Action Card, Admin Card를 표준화한다.
- 카드 안에는 목적, 상태, 다음 행동을 명확히 둔다.

### Cursor를 AI 실행 흐름 기준으로 선택한 이유

Cursor는 AI가 현재 무엇을 하고 있는지 단계적으로 보여주는 경험이 좋다. GPT Manager의 프롬프트 정리 기능은 현재 단일 Provider 호출이지만, 향후 GPT/Gemini/Claude 비교 실행으로 확장할 경우 timeline이 필요하다.

영향:

- Prompt 실행은 현재 단일 Provider 단계형 흐름으로 설계한다.
- 실행 중에는 버튼 비활성화와 `처리 중`, `aria-busy=true`로 상태를 표시한다.

제한:

- 실제 multi-provider 실행은 현재 구현이 아니므로 문서와 UI 모두 future pattern으로 분리한다.

### Perplexity를 결과 화면 기준으로 선택한 이유

Perplexity의 강점은 답변과 근거, source, citation을 분리해 신뢰를 만든다는 점이다. GPT Manager의 결과 화면도 단순 AI 출력이 아니라 원본 요청, 정리 결과, 위험 요소, 개선 제안, 근거를 분리해야 한다.

영향:

- Result 화면은 원본과 결과를 구분한다.
- 향후 비교 결과는 요약, 차이점, 위험 요소, 개선 제안, 근거를 별도 영역으로 둔다.

### Raycast를 Prompt 입력 경험 기준으로 선택한 이유

Raycast는 빠른 command 입력, keyboard-first action, compact control에 강하다. 교사가 프롬프트를 빠르게 입력하고 템플릿을 선택하는 화면은 Raycast의 입력 경험을 참고할 수 있다.

영향:

- Prompt 입력 화면은 템플릿 선택, Provider 선택, 실행 액션을 예측 가능한 위치에 둔다.
- 향후 command palette형 템플릿 검색을 고려한다.

## 2. 제외하거나 제한한 디자인

### OpenCode를 제외한 이유

OpenCode는 mono-only, terminal-native, ASCII 중심 디자인이다. 개발자에게는 강한 정체성이 있지만 교사용 AI 업무 플랫폼에는 지나치게 기술적이고 차갑다.

결정:

- 전체 mono typography, ASCII bullet, terminal-only 분위기는 적용하지 않는다.
- pytest output, prompt/code block처럼 실제 monospace가 필요한 영역에만 제한적으로 참고한다.

### Obsidian을 제외한 이유

Obsidian은 dark-first knowledge workspace다. 장시간 문서 편집에는 적합하지만, GPT Manager의 예약, 승인, 관리자 table 중심 업무에는 무겁고 power-user 성격이 강하다.

결정:

- dark knowledge graph 분위기는 적용하지 않는다.
- command palette와 markdown readability 일부만 참고 가능하다.

### Mistral을 제한한 이유

Mistral은 sunset orange, cream, editorial serif, photography가 강한 브랜드다. 현재 프로젝트의 차분한 학교 업무 톤과 충돌한다.

결정:

- orange/cream/sunset palette는 적용하지 않는다.
- 8px button, 12px card 같은 sober geometry만 참고할 수 있다.

### Railway/Fly/Neon을 제한적으로만 참고한 이유

세 서비스는 배포/인프라 제품이라 상태 표현, running/idle, progress, log stream에는 참고 가치가 있다. 그러나 dark developer dashboard와 neon accent는 교사용 플랫폼에 맞지 않는다.

결정:

- 실행 상태, 테스트 상태, API 연결 상태 표현만 참고한다.
- 다크 인프라 분위기와 강한 neon/purple/pink palette는 적용하지 않는다.

### Arc/Pitch를 일부만 참고한 이유

Arc는 브라우저 개인화와 motion이 핵심이고, Pitch는 슬라이드 캔버스와 협업 편집이 핵심이다. GPT Manager의 관리형 업무 화면과 직접 맞지는 않는다.

결정:

- Arc의 command/search 접근과 Pitch의 preview 중심 사고는 제한적으로 참고한다.
- 강한 브랜드 모션과 편집기 중심 UI는 적용하지 않는다.

## 3. 프로젝트 맥락

- 대상 사용자는 교사다.
- 목적은 공용 생성형 AI 계정 예약, 사용 기록, 안전 안내, BYOK 프롬프트 정리다.
- 과한 개발자 감성은 피한다.
- AI 서비스 느낌은 필요하지만, 챗봇 서비스처럼 보이면 안 된다.
- 관리 화면은 전문적이고 반복 업무에 적합해야 한다.
- 결과 화면은 신뢰 가능해야 한다.
- 학생 개인정보, 평가 자료, 생활기록부 원문을 입력하지 않도록 지속적으로 안내해야 한다.
- React/Vue/Svelte/TypeScript/Bootstrap은 추가하지 않는다.
- 기존 URL, API, 권한, 데이터 구조, 테스트는 유지한다.

## 4. 의사결정 로그

### 2026-07-05

- 결정: UI/UX 개선은 바로 코드 수정하지 않고 먼저 디자인 시스템 문서로 기준을 세운다.
- 이유: 현재 프로젝트는 기능이 이미 많고, 승인 없이 전체 UI를 변경하면 기능/권한/테스트에 영향을 줄 수 있다.
- 영향 범위: `docs/ui/DESIGN_SYSTEM.md`, `docs/ui/UI_GUIDE.md`, `docs/ui/DESIGN_DECISIONS.md` 신규 생성.
- 대안: 기존 `styles.css`를 바로 수정하는 방식.
- 보류 사항: 실제 UI 구현, screenshots 폴더 정리, Playwright 화면 검증.

### 2026-07-05

- 결정: 디자인 기준은 Apple, Vercel, GitHub, Linear를 최상위로 두고 Cursor, Perplexity, Raycast를 AI 기능 화면에 제한 적용한다.
- 이유: 프로젝트는 교사용 업무 플랫폼이므로 가독성, 관리 화면, 상태 표현이 AI 장식보다 중요하다.
- 영향 범위: 향후 Landing, Dashboard, Admin, Prompt, Result, Test Result 개선 방향.
- 대안: AI 제품처럼 dark/gradient 중심으로 전면 변경.
- 보류 사항: 실제 화면별 시각 디자인 구현은 사용자 승인 후 진행.

### 2026-07-05

- 결정: 현재 브랜드 색상 `#1f3a5f`와 slate 기반 surface를 유지한다.
- 이유: 학교 업무 시스템으로서 차분하고 신뢰감 있는 색 체계가 이미 존재하며, 새 palette를 도입하면 문서/화면 전체 일관성이 깨질 수 있다.
- 영향 범위: 색상 추가는 semantic state와 AI Provider 구분으로 제한.
- 대안: Vercel black/white, Linear dark/lavender, Cursor cream/orange 등 외부 palette 적용.
- 보류 사항: 실제 contrast 점검과 UI screenshot 비교.

### 2026-07-05

- 결정: 현재 `docs/ui`에는 `screenshots` 폴더가 존재하며, 요청에 적힌 `scrteenshots` 폴더는 확인되지 않았다.
- 이유: 실제 파일 구조를 기준으로 판단해야 하며, 승인 없는 폴더명 변경은 금지되어 있다.
- 영향 범위: 폴더명 변경 없음.
- 대안: `scrteenshots`가 실제 존재할 경우 `screenshots`로 rename.
- 보류 사항: 사용자가 별도로 요청하거나 실제 오타 폴더가 확인될 때만 rename 승인 요청.

### 2026-07-05

- 결정: 프롬프트 multi-model 비교와 실행 timeline은 현재 구현이 아니라 향후 설계로 분리한다.
- 이유: 현재 라우트는 단일 Provider 실행과 저장 구조이며, multi-provider 실행은 백엔드 로직과 테스트 영향이 있다.
- 영향 범위: UI_GUIDE에는 현재 상태와 향후 개선안을 분리 기재.
- 대안: 문서에서 이미 구현된 것처럼 표현.
- 보류 사항: 사용자 승인 후 `app/prompts/routes.py`, prompt result model, tests 영향 검토.


### 2026-07-05

- 결정: 디자인 시스템 문서 기준을 실제 Flask/Jinja/Tailwind CDN/Vanilla JS 코드에 적용한다.
- 이유: 문서만 존재하면 화면과 기준이 분리되므로, 반복 업무 화면의 신뢰감과 정보 밀도를 실제 사용 흐름에 반영해야 한다.
- 영향 범위: `app/static/styles.css`, `app/templates/base.html`, Landing/Auth/Dashboard/Reservations/Logs/Prompts/Admin Test 관련 Jinja 템플릿, `tests/test_prompt_reviews.py`.
- 유지 범위: URL, route, auth, 권한, DB 모델, API, 서버 로직, dependency는 변경하지 않는다.
- 검증: 최초 적용 시 `uv run pytest` 91 passed, `npm run test:e2e` 1 passed, Playwright desktop/mobile overflow 점검 PASS. 최신 검증 수치는 TEST_REPORT와 PROJECT_STATUS를 기준으로 확인한다.

### 2026-07-05

- 결정: Landing과 Prompt Result에서 multi-provider 비교가 구현된 것처럼 보이는 표현을 제거한다.
- 이유: 현재 백엔드는 단일 Provider 실행과 저장 구조이며, UI가 기능 범위를 과장하면 교사용 업무 플랫폼의 신뢰성이 떨어진다.
- 영향 범위: Landing preview는 예약/기록/단일 Provider 정리 흐름으로 제한하고, Prompt Result는 `비교 요약` 대신 `검토 메모`를 사용한다.
- 대안: GPT/Gemini/Claude 병렬 비교 preview 유지.
- 보류 사항: multi-provider 실행, streaming, 비교 summary는 백엔드 설계와 테스트 승인 후 별도 구현한다.

### 2026-07-05

- 결정: 개인 프로필 화면은 읽기 전용 운영 요약으로 추가하고, 헤더 사용자 badge의 목적지를 `/profile`로 변경한다.
- 이유: 교사용 업무 플랫폼에서는 개인 계정/권한/최근 활동/API Key 상태를 한 곳에서 확인하는 것이 설정 화면 직행보다 자연스럽다.
- 영향 범위: `app/routes/main.py`, `app/templates/profile.html`, `app/templates/base.html`, 프로필/헤더 pytest와 Playwright 검증.
- 유지 범위: 사용자 권한, API Key 원문 비노출, 기존 `/settings/api-key` URL과 Provider 설정 흐름은 유지한다.

### 2026-07-05

- 결정: 관리자 테스트 결과는 실패 원인 요약과 해결 힌트를 제공하되, 테스트 실행 이력 DB 저장은 만들지 않는다.
- 이유: 현재 요구는 실행 직후 원인 파악 보조이며, 영속 이력은 새 데이터 구조와 운영 정책이 필요하다.
- 영향 범위: `app/admin/routes.py`, `app/templates/admin/dashboard.html`, `tests/test_admin.py`.
- 보류 사항: 파일별 duration, 테스트 실행 이력 저장, 구조화 traceback viewer는 별도 승인 후 진행한다.

### 2026-07-05

- 결정: 사이트 성격을 바꾸는 비추천 기능은 제외하고, Playwright 검증 범위만 Profile/Admin/mobile overflow로 확장한다.
- 이유: multi-provider 비교, streaming, 자유형 챗봇은 현재 단일 Provider 학교 업무 플랫폼 흐름과 다른 제품 인상을 만든다.
- 영향 범위: `tests/e2e/ui.spec.ts`, 문서의 제외 기능과 향후 개선 항목.
- 보류 사항: 해당 기능들은 백엔드/데이터/권한 설계가 승인될 때까지 UI에 암시하지 않는다.
