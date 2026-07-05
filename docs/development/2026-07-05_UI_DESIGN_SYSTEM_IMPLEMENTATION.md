# 2026-07-05 UI Design System Implementation

## 배경

`docs/ui/UI_GUIDE.md`, `docs/ui/DESIGN_SYSTEM.md`, `docs/ui/DESIGN_DECISIONS.md`에 정리된 UI 기준을 실제 Flask/Jinja/Tailwind CDN/Vanilla JS 코드에 적용했다. 목표는 GPT Manager를 교사용 학교 업무 플랫폼답게 차분하고 신뢰감 있는 light operational SaaS UI로 정리하는 것이다.

## 적용 원칙

- 기존 브랜드 색상 `#1f3a5f`와 slate 기반 surface 유지
- React/Vue/Svelte/TypeScript/Bootstrap 등 새 프레임워크 추가 없음
- 새 dependency 추가 없음
- URL, route, auth, 권한, DB 모델, API, 서버 로직 변경 없음
- Tailwind CDN과 `app/static/styles.css` 중심으로 적용
- 카드 radius는 8-12px 중심으로 낮춤
- 버튼은 40px 이상, 주요 CTA는 44px 기준 유지
- 상태는 색상과 텍스트 badge를 함께 사용
- table은 GitHub식 정보 밀도와 mobile horizontal scroll 유지
- form label은 visible text 유지
- flash alert `role="alert"`와 CSRF submit hook 유지
- multi-provider 비교, streaming, timeline backend 기능은 새로 만들지 않음

## 주요 변경

### 공통

- `app/static/styles.css`에 `gm-page-header`, `gm-surface`, `gm-inset`, `gm-button-*`, `gm-badge-*`, `gm-table-*`, `gm-alert-*`, `gm-code-panel`, `gm-log-output` 등 공통 클래스 정리
- `--gm-radius-card: 12px`, `--gm-radius-button: 10px`, `--gm-radius-input: 10px`, `--gm-radius-modal: 16px` 적용
- `body` 배경에서 과한 radial/mesh 느낌 제거
- `focus-visible`, `prefers-reduced-motion`, 긴 한국어 줄바꿈, code/pre overflow 보정

### Base Layout

- header/nav/footer spacing과 active nav 상태 정리
- 모바일 내비게이션은 홈, 사용 신청, 오늘 예약, 더보기 구조 유지
- flash alert의 semantic class와 `role="alert"` 유지
- POST form CSRF hidden input submit hook 유지

### Landing/Auth/Dashboard

- Landing preview는 예약, 기록, 단일 Provider 프롬프트 정리 흐름만 표현
- Login/Register/Pending은 중앙 auth shell과 visible label, warning/status card로 정리
- Dashboard는 KPI, 현재 사용중/다음 예약, 로그 미작성 alert, 빠른 실행, 오늘 예약 리스트를 light SaaS 구조로 정리

### Reservations/Logs/Prompt

- 예약/로그/프롬프트 기록은 table density와 horizontal overflow를 적용
- 예약 신청은 기존 자동 충돌 확인 JS를 유지하면서 alert/button/form styling만 정리
- Prompt 입력은 단일 Provider 실행 흐름과 안전 확인 panel을 유지
- Prompt 결과는 `비교 요약` 대신 `검토 메모`로 표현하고, 단일 Provider 결과임을 명확히 표시

### Admin/Test Result

- 관리자 section launcher에 icon slot과 active state를 정리
- Test Result badge는 `PASS`, `FAIL`, `SKIP`, `NOT RUN` 텍스트와 semantic badge를 사용
- pytest 상세 output은 dark terminal canvas 대신 light log panel로 표시

## 검증

```text
git diff --check: PASS
uv run pytest: PASS, 91 passed
npm run test:e2e: PASS, 1 passed
Playwright desktop/mobile overflow check: PASS
```

Playwright overflow check 대상:

```text
Landing
Login
Dashboard
Reservations
Prompt 입력

Desktop 1366x900: 수평 overflow 없음
Mobile 390x844: 수평 overflow 없음
```

## 남은 리스크

- 관리자 전체 section의 모든 조합은 pytest 렌더링과 CSS 규칙으로 보호하지만, 전 section 시각 screenshot 검증은 별도 수행하지 않았다.
- `settings/api_key.html`, `guide.html`, legal 문서는 기존 UI와 공통 CSS 보정으로 유지했으며 대규모 markup 변경은 하지 않았다.
- multi-provider 비교, streaming, backend timeline은 의도적으로 제외했다.
