# GPT Manager UI Design System

## 1. 디자인 목표

GPT Manager는 교사가 학교 공용 생성형 AI 사용을 예약하고, 사용 기록을 남기고, BYOK 방식으로 프롬프트를 정리하는 업무 플랫폼이다. UI는 과한 AI 서비스처럼 보이기보다 학교 업무 도구로 신뢰 가능해야 한다.

목표는 다음과 같다.

- 교사용 AI 업무 플랫폼에 맞는 차분한 전문성
- 과하지 않은 SaaS 느낌
- 신뢰감 있는 AI 도구
- 관리 화면과 결과 화면의 높은 정보 밀도와 명확한 상태 표현
- AI가 작동하고 있다는 느낌을 주는 실행 흐름, 진행 상태, 결과 비교 구조
- 기존 Flask, Jinja2, Tailwind CDN, Vanilla JavaScript 구조 유지

## 2. 참고 디자인 우선순위

### ★★★★★ Apple

적용 범위:

- Typography
- Spacing
- Hierarchy
- Whitespace
- 읽기 쉬운 화면

적용 방식:

- 한국어 본문 가독성을 최우선으로 한다.
- 본문은 충분한 line-height를 유지한다.
- 화면별 H1, 섹션 제목, 카드 제목 위계를 명확히 분리한다.
- 장식보다 콘텐츠와 실제 화면을 우선한다.

제한:

- Apple식 제품 사진 중심 레이아웃은 적용하지 않는다.
- 과한 풀뷰포트 타일 구조는 관리형 업무 화면에는 적용하지 않는다.

### ★★★★★ Vercel

적용 범위:

- Landing
- Hero
- CTA
- Feature Section
- 카드와 미세한 애니메이션

적용 방식:

- Landing은 첫 화면에서 프로젝트 이름, 한 줄 설명, CTA, 실제 화면 미리보기를 보여준다.
- CTA는 한 화면에 너무 많이 배치하지 않는다.
- 카드 hover는 1-2px 이동, 약한 shadow, border 변화 정도로 제한한다.

제한:

- Vercel식 대형 mesh gradient는 사용하지 않는다.
- 개발자 플랫폼처럼 과도하게 기술 브랜드화하지 않는다.

### ★★★★★ GitHub

적용 범위:

- Dashboard
- Table
- Settings
- Badge
- Log
- Status

적용 방식:

- 관리자, 사용자, 예약, 로그, 테스트 결과 화면은 GitHub처럼 정보 우선으로 설계한다.
- 표는 행 높이, sticky header, 상태 badge, 우측 작업 열을 일관되게 유지한다.
- 상태 색상은 텍스트와 함께 사용한다.

### ★★★★★ Linear

적용 범위:

- Status Card
- Issue Card
- Activity
- Timeline
- Professional SaaS 느낌

적용 방식:

- Dashboard와 Admin은 상태 카드, 최근 활동, 빠른 작업을 Linear식 SaaS 카드 흐름으로 구성한다.
- 카드의 목적, 상태, 다음 행동이 한눈에 보이게 한다.
- 이 프로젝트에서는 dark marketing canvas 대신 light operational SaaS surface를 유지한다.

### ★★★★ Cursor

적용 범위:

- AI 실행 화면
- Prompt 비교
- Model 선택
- AI 실행 과정 Timeline

적용 방식:

- 프롬프트 실행은 입력, 준비, Provider 호출, 비교, 완료를 timeline으로 표현한다.
- Timeline 색상은 실행 단계에만 제한적으로 사용한다.
- 코드/프롬프트 영역은 monospace를 사용한다.

### ★★★★ Perplexity

적용 범위:

- 결과 화면
- 비교 화면
- Citation
- Source Card
- Answer Layout

적용 방식:

- 결과 화면은 원본 요청, 모델별 응답, 비교 요약, 위험 요소, 개선 제안을 분리한다.
- 근거/참고는 별도 Source Card로 제공한다.
- 긴 결과는 읽기 폭을 제한하고 line-height를 넉넉히 둔다.

### ★★★ Raycast

적용 범위:

- Prompt 입력
- Command Palette
- AI Action

적용 방식:

- 프롬프트 입력 화면은 빠른 실행, 템플릿 선택, Provider 선택을 키보드 친화적으로 배치한다.
- 입력 영역과 실행 버튼의 위치를 예측 가능하게 유지한다.

### ★★★ Notion

적용 범위:

- 카드 구성
- Feature Grid
- 일부 부드러운 컬러 포인트

적용 방식:

- 안내, 빈 상태, 기능 소개 카드에만 제한적으로 참고한다.
- pastel 색상은 남용하지 않는다.

### 낮은 우선순위

Railway, Fly, Neon:

- 상태 표현 일부만 참고한다.
- 배포/실행/연결 상태처럼 기술 상태를 표시할 때만 사용한다.
- 어두운 개발자 대시보드 분위기는 적용하지 않는다.

Pitch, Arc:

- 일부 모션과 레이아웃만 참고한다.
- 프레젠테이션 도구나 브라우저 특유의 개성은 적용하지 않는다.

OpenCode, Obsidian, Mistral:

- 분위기와 브랜드 색상은 적용하지 않는다.
- OpenCode의 terminal-only / mono-only 감성은 교사용 업무 화면에 맞지 않는다.
- Obsidian의 dark knowledge tool 분위기는 장시간 문서 편집에는 좋지만 이 서비스의 관리/예약 화면 기준으로는 무겁다.
- Mistral의 orange/cream/sunset 브랜드는 현재 프로젝트 브랜드와 충돌한다.

## 3. Color System

현재 프로젝트 브랜드 색상을 우선 유지한다. 현재 CSS는 `--gm-primary: #1f3a5f`를 중심으로 slate 계열과 학교 업무용 차분한 surface를 사용한다. 새 색상은 상태와 AI Provider 구분에 필요한 경우에만 추가한다.

### Core Colors

| Token | 권장값 | 용도 |
| --- | --- | --- |
| Primary | `#1f3a5f` | 주요 CTA, 활성 메뉴, 핵심 링크 |
| Primary Hover | `#18304f` | CTA hover |
| Primary Pressed | `#122640` | CTA active |
| Secondary | `#4f657d` | 보조 버튼, 보조 아이콘 |
| Background | `#f4f6f8` | 전체 페이지 배경 |
| Surface | `#ffffff` | 카드, 폼, 표 컨테이너 |
| Surface Raised | `rgba(255,255,255,0.92)` | 떠 있는 카드, sticky header |
| Surface Muted | `#eef2f6` | 표 head, inset panel |
| Border | `rgba(28,42,58,0.10)` | 카드/표/입력 border |
| Focus Ring | `rgba(31,58,95,0.28)` | keyboard focus |
| Muted Text | `#768293` | 보조 정보 |

### Semantic Colors

| 상태 | Text | Background | Border | 사용 예 |
| --- | --- | --- | --- | --- |
| Success | `#27644f` | `#edf8f3` | `rgba(47,111,87,0.22)` | 활성, 완료, PASS |
| Warning | `#74470f` | `#fff7e8` | `rgba(138,90,22,0.20)` | 승인 대기, 주의, 로그 미작성 |
| Danger | `#923331` | `#fff0f0` | `rgba(159,58,56,0.22)` | 오류, 차단, 삭제, FAIL |
| Info | `#1f3a5f` | `#eef2f6` | `rgba(31,58,95,0.18)` | 안내, 설명, 중립 상태 |
| Muted | `#526070` | `#f4f6f8` | `rgba(28,42,58,0.10)` | 없음, 미등록, NOT RUN |

색상만으로 의미를 전달하지 않는다. 모든 상태 badge는 텍스트를 포함한다.

### AI Model Colors

| Provider | Color | Background | Label |
| --- | --- | --- | --- |
| OpenAI / GPT | `#1f3a5f` | `#eef2f6` | `GPT` |
| Google / Gemini | `#1f6f68` | `#edf9f7` | `Gemini` |
| Anthropic / Claude | `#7a4b20` | `#fff4e8` | `Claude` |
| 기타 모델 | `#526070` | `#f4f6f8` | `기타` |

모델 구분은 색상, 텍스트, 아이콘 또는 약어를 함께 사용한다.

## 4. Typography

한국어 가독성을 우선한다. 기본 font stack은 현재 `ui-sans-serif, -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", "Noto Sans KR", "Apple SD Gothic Neo", Arial, sans-serif`를 유지한다.

| 계층 | 크기 | Weight | Line Height | 용도 |
| --- | --- | --- | --- | --- |
| Hero Title | 36-48px | 800 | 1.15 | Landing 첫 화면 |
| Page Title | 24-32px | 800 | 1.25 | 각 화면 H1 |
| Section Title | 20-24px | 800 | 1.3 | 큰 섹션 제목 |
| Card Title | 16-20px | 700-800 | 1.35 | 카드/패널 제목 |
| Body | 15-16px | 400-500 | 1.65 | 본문 설명 |
| Caption | 12-14px | 500-600 | 1.45 | 보조 정보, 날짜, 도움말 |
| Badge | 12px | 700-800 | 1.2 | 상태 badge |
| Button | 14-16px | 700-800 | 1.2 | 버튼 라벨 |
| Code / Prompt | 13-14px | 400 | 1.6 | 프롬프트, pytest log, Markdown 결과 |

원칙:

- viewport width 기반 font-size는 사용하지 않는다.
- letter-spacing은 기본 0을 유지한다.
- 긴 한국어 문장은 line-height 1.6 이상을 유지한다.
- compact table은 14px를 허용하되 row height는 최소 44px를 지킨다.

## 5. Spacing

| 항목 | 기준 |
| --- | --- |
| Page Container | `max-w-7xl`, 16px mobile gutter, 24-32px desktop inner rhythm |
| Section Padding | 24px mobile, 32px desktop |
| Card Padding | 16px compact, 24px default, 32px emphasis |
| Grid Gap | 12px compact, 16px default, 20-24px dashboard |
| Form Gap | 16-20px field group, 8px label/input |
| Table Row Height | 최소 44px, 관리자 표 48px |
| Mobile Spacing | 카드 padding 16px, section gap 16-20px, sticky header는 static 전환 가능 |

## 6. Radius / Border / Shadow

현재 CSS는 18px 카드 radius를 사용하지만, 향후 구현에서는 반복 업무 화면의 전문성을 위해 카드 radius를 8-12px 중심으로 낮추는 것을 권장한다. 단, 기존 화면과 한 번에 충돌하지 않도록 단계적으로 적용한다.

| 컴포넌트 | Radius | Border | Shadow |
| --- | --- | --- | --- |
| Button | 8-12px | primary 없음, secondary 1px | 약한 shadow 허용 |
| Card | 8-12px | 1px border | `--gm-shadow-sm` 이하 |
| Badge | full 또는 6px | 필요 시 1px ring | 없음 |
| Table | 8-12px outer | row divider | outer shadow만 |
| Modal | 16-20px | 1px border | `--gm-shadow-soft` |
| Toast | 12-16px | semantic border | `--gm-shadow-sm` |
| Input | 8-12px | 1px border, focus ring | inset highlight만 |
| Prompt Box | 8-12px | 1px border | 없음 또는 약한 inset |

## 7. Components

### Button

- Primary: 핵심 저장, 실행, 예약 등록에 사용한다.
- Secondary: 취소, 목록, 설정 이동에 사용한다.
- Danger: 삭제, 비활성화, 반려에 사용한다.
- 모든 버튼은 명확한 동사 라벨을 가진다.
- 아이콘을 사용할 때는 텍스트와 함께 사용한다.
- 최소 높이 40px, 주요 버튼은 44-48px를 권장한다.

### Card

- 한 카드에는 하나의 목적만 둔다.
- 카드 안에 또 다른 큰 카드를 중첩하지 않는다.
- 반복 목록 카드는 제목, 설명, 상태, 다음 행동 순서로 구성한다.

### Status Card

- Dashboard와 Admin의 KPI에 사용한다.
- 숫자, 라벨, 보조 설명, 변화/주의 상태를 분리한다.
- 색상만으로 상태를 표현하지 않는다.

### Result Card

- AI 결과, 테스트 결과, 월간 보고서에 사용한다.
- 원본, 요약, 상세, 다운로드 액션을 분리한다.
- 긴 텍스트는 max-height와 overflow를 제공한다.

### Prompt Card

- 원본 prompt, 정리 목표, Provider, 모델, 실행 상태를 함께 표시한다.
- prompt 본문은 monospace, 13-14px, line-height 1.6을 사용한다.

### Model Card

- Provider 상태와 API Key 상태를 보여준다.
- Provider 이름, 모델, 키 상태, 최근 사용일, 다음 액션을 포함한다.

### Badge

- 상태 텍스트를 반드시 포함한다.
- `예약`, `완료`, `취소`, `활성`, `비활성`, `PASS`, `FAIL`, `SKIP`, `NOT RUN` 등은 표준 라벨로 유지한다.

### Table

- 관리자, 기록, 테스트 결과는 table을 유지한다.
- 행 hover는 약한 background 변화만 사용한다.
- 모바일에서는 horizontal scroll을 허용하고, 핵심 필드는 좌측에 둔다.

### Form

- label은 항상 visible text로 둔다.
- 도움말은 입력 아래에 배치한다.
- 오류는 필드 근처와 상단 alert 양쪽에 표시할 수 있다.
- submit disabled 상태는 opacity와 text로 설명한다.

### Modal

- 현재 프로젝트에는 modal 사용이 제한적이다.
- 도입 시 focus trap, ESC 닫기, aria-modal을 필수로 한다.

### Toast / Flash

- 현재 Flask flash alert 구조를 유지한다.
- 성공/경고/오류는 semantic color와 role alert를 유지한다.

### Empty State

- 빈 예약, 빈 로그, 빈 테스트 결과는 원인과 다음 행동을 같이 보여준다.
- 장식 일러스트보다 작은 아이콘/상태 badge/CTA를 우선한다.

### Loading Skeleton

- `gm-skeleton`을 기준으로 사용한다.
- LLM 실행, 테스트 실행, 충돌 확인처럼 대기 시간이 있는 흐름에 적용한다.

### Timeline

- Prompt 실행 흐름의 핵심 컴포넌트로 사용한다.
- 단계: Prompt 입력 -> 실행 준비 -> GPT 실행 -> Gemini 실행 -> Claude 실행 -> 비교 분석 -> 완료.
- 현재 기능은 단일 Provider 실행이므로 구현 전에는 future pattern으로만 문서화한다.

### Progress

- 테스트 실행, LLM 실행, 백업 생성 등 작업 진행 상태에 사용한다.
- 정량 progress가 없으면 단계형 progress를 사용한다.

### Tabs

- 관리자 section, Provider 선택, Test Result 분류에 사용한다.
- 활성 상태는 `aria-current` 또는 `aria-selected`를 사용한다.

### Sidebar / Navigation

- 현재 상단 navigation 구조를 유지한다.
- 모바일에서는 핵심 3개 메뉴와 더보기 구조를 유지한다.
- 관리자 화면은 카드형 section launcher를 유지하되, 장기적으로 sidebar 또는 tab list로 정리할 수 있다.

### Footer

- 표시 항목은 기관명, 대표번호, 이용약관, 개인정보처리방침으로 제한한다.
- 개인 업무메일과 정보관리책임자 상세 정보는 푸터에 표시하지 않는다.

## 8. Motion

허용 motion:

- Card Hover: `translateY(-1px)` 또는 `-2px`
- Fade In: alert, result card, timeline step에만 제한
- Loading Skeleton: 현재 `gm-skeleton`
- Progress Animation: 테스트/AI 실행에 제한
- Timeline Step Animation: 현재 단계 강조
- Count Up: Dashboard KPI에 제한적으로 허용

원칙:

- motion은 150-220ms 범위로 제한한다.
- 반복 업무 화면에서 scale, bounce, parallax를 사용하지 않는다.
- `prefers-reduced-motion: reduce`를 반드시 고려한다.

## 9. Accessibility

기준:

- WCAG AA 수준
- 모든 interactive element는 keyboard 접근 가능
- `:focus-visible` 유지
- 색상 단독 의미 전달 금지
- table header와 form label 유지
- touch target 44px 권장
- alert는 `role="alert"` 유지
- 긴 결과 텍스트는 복사/다운로드 가능하게 한다.

보안/표시 원칙:

- 사용자 입력은 Jinja escaping을 기본으로 한다.
- 법적 문서 Markdown은 allowlist 렌더링 구조를 유지한다.
- API Key 원문은 프론트엔드로 재전송하지 않는다.
- 결과 화면에 학생 개인정보 입력 금지 안내를 유지한다.
