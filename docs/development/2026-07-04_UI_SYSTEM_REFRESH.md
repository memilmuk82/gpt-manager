# 2026-07-04 UI 시스템 개선 기록

## 1. 현재 UI 분석

```text
프레임워크: Flask + Jinja2 + Tailwind CDN
정적 CSS: 기존에는 app/static/.gitkeep만 존재
스타일 방식: 템플릿별 Tailwind 유틸리티 직접 작성
공통 레이아웃: app/templates/base.html
주요 화면 수: 22개 Jinja 템플릿
```

화면 목록:

```text
공통: base, index, dashboard, guide, legal/document, partials/_auth_info
인증: auth/login, auth/register, auth/pending
예약: reservations/index, reservations/new, reservations/today, reservations/calendar
사용 로그: logs/index, logs/new, logs/show
프롬프트 점검: prompts/index, prompts/new, prompts/show
설정: settings/api_key, settings/macros
관리자: admin/dashboard, admin/users
```

공통 컴포넌트 목록:

```text
Header, Navigation, Footer, Flash Alert, Card, Action Card, Button, Link Button,
Input, Textarea, Select, Checkbox, Badge, Table, Empty State, Search/Filter Form,
Admin Dashboard Section, Monthly Report Preview, Code/Pre Block
```

## 2. 발견된 문제점

```text
디자인 토큰 부재: 색상, 반경, 그림자, 포커스 링이 템플릿마다 직접 작성됨
중복 CSS 패턴: rounded-2xl, border-slate-200, bg-white, shadow-sm 조합 반복
버튼 상태 부족: hover는 있으나 pressed, disabled, focus-visible 일관성이 낮음
테이블 가독성 부족: sticky header, row hover, 모바일 overflow 기준이 전역화되어 있지 않음
폼 상태 부족: focus ring과 disabled 표현이 화면마다 다름
접근성 보완 필요: 본문 바로가기, alert role 등 기본 보조 장치 부족
문구 톤 혼재: 일부 영어 eyebrow 텍스트가 학교 업무 시스템 톤과 맞지 않음
반응형 기준 분산: 화면별 grid는 있으나 공통 모바일 보정 레이어가 없음
```

## 3. 개선 계획

```text
1. app/static/styles.css에 CSS Variables 기반 디자인 토큰 구축
2. base.html에서 공통 stylesheet 로드
3. 기존 Tailwind 클래스 위에 공통 컴포넌트 상태 레이어 적용
4. Header/Navigation에 약한 blur와 sticky depth 적용
5. Card/Button/Form/Table/Alert/Focus/Motion/Responsive 스타일 통합
6. 첫 화면과 사용 로그 화면 문구를 학교 업무 시스템 톤으로 정리
7. 접근성 보조 장치 추가: skip-link, role=alert, focus-visible 유지
```

## 4. 적용 원칙

```text
기능 변경 없음
API 변경 없음
라우팅 변경 없음
인증/예약/관리자 권한/DB 변경 없음
새 라이브러리 추가 없음
Tailwind CDN 유지
템플릿의 기존 action, name, href 유지
```

## 5. 검증 기준

```text
uv run pytest
npm run test:e2e
Docker Compose rebuild
/healthz 확인
데스크톱/모바일 주요 화면 렌더링 확인
```

## 6. 관리자 화면 추가 보완

```text
관리자 대시보드 카드에 현재 섹션 active 상태 추가
관리자 전용 admin-shell scope 추가
관리자 카드 밀도 조정 및 hover/depth 일관화
관리자 테이블 최소 폭, 행 높이, sticky header, focus-within 상태 보정
관리자 폼/fieldset 배경과 입력 밀도 조정
```
