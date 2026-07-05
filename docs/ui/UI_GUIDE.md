# GPT Manager UI Guide

이 문서는 실제 코드 기준의 화면별 UI/UX 설계 문서다. 문서와 코드가 충돌하면 실제 코드를 우선한다.

## 공통 구조

- 기술: Flask, Jinja2, Tailwind CDN, `app/static/styles.css`, Vanilla JavaScript
- 공통 레이아웃: `app/templates/base.html`
- 공통 CSS: `app/static/styles.css`
- 주요 내비게이션: 홈, 사용 신청, 오늘 예약, 예약 캘린더, 내 예약, 프롬프트 정리, 사용 안내, 관리자
- 모바일 내비게이션: 홈, 사용 신청, 오늘 예약, 더보기
- 공통 보안: CSRF meta + submit hook, Flask flash, Jinja escaping

## Landing

관련 파일:

- `app/templates/index.html`
- `app/routes/main.py`

화면 목적:

- 비로그인 사용자에게 서비스 목적을 설명하고 로그인/등록 요청으로 안내한다.

주요 사용자:

- 교사
- 관리자
- 리뷰/시연 사용자

주요 기능:

- 프로젝트 이름 표시
- 한 줄 설명
- Google 로그인, 로컬 로그인, 등록 요청 CTA
- 핵심 기능 4개 소개

핵심 컴포넌트:

- Hero panel
- CTA button group
- Feature card grid

배치 규칙:

- Apple식 가독성과 Vercel식 Landing 구조를 참고한다.
- 첫 viewport에서 프로젝트명, 설명, CTA가 보여야 한다.
- 현재 Landing은 실제 구현 범위 안의 운영 미리보기만 표시한다. AI 비교 예시는 미구현 기능처럼 보일 수 있어 표시하지 않는다.

상태 표현:

- 비로그인 상태만 전제로 한다.
- OAuth 미설정 시 로그인 흐름에서 flash error로 안내한다.

빈 상태:

- 없음.

오류 상태:

- 로그인 실패, OAuth 설정 오류는 Auth 화면과 flash로 처리한다.

모바일 대응:

- CTA는 세로 stack 우선, 넓은 화면에서 row로 전환한다.

현재 구현 메모:

- Hero 오른쪽 미리보기는 예약, 기록, 단일 Provider 프롬프트 정리 흐름만 표현한다.
- 기능 카드는 인증, 예약, AI, 보안 4개로 정리한다.
- Vercel식 CTA 구조는 적용하되 대형 gradient와 개발자 플랫폼 톤은 제외한다.

## Login / Auth

관련 파일:

- `app/templates/auth/login.html`
- `app/templates/auth/register.html`
- `app/templates/auth/pending.html`
- `app/auth/routes.py`

화면 목적:

- 로컬 로그인, Google 로그인, 등록 요청, 승인 대기 상태를 처리한다.

주요 사용자:

- 교사
- 리뷰용 관리자
- 승인 대기 사용자

주요 기능:

- Google 로그인
- 이메일/비밀번호 로그인
- 등록 요청
- 승인 대기 안내
- 정지 계정 차단

핵심 컴포넌트:

- Auth card
- Form
- Flash alert
- Pending status card

배치 규칙:

- Login은 좁은 중앙 column을 유지한다.
- Register는 업무 정보 입력 흐름이므로 label/help text를 명확히 둔다.
- 리뷰용 계정 안내는 경고 card로 표시한다.

상태 표현:

- 성공: 로그인/회원가입 완료
- Warning: 승인 대기
- Danger: 로그인 실패, 정지 계정

빈 상태:

- 해당 없음.

오류 상태:

- 필수 입력 누락, 비밀번호 길이 부족, 중복 이메일, 잘못된 로그인 정보는 flash와 status code로 처리한다.

모바일 대응:

- form field는 full width, CTA는 44px 이상 높이를 유지한다.

## Dashboard

관련 파일:

- `app/templates/dashboard.html`
- `app/routes/main.py`

화면 목적:

- 승인된 사용자가 오늘의 운영 상태와 본인 작업 흐름을 빠르게 파악한다.

주요 사용자:

- 일반 사용자
- 보조관리자
- 관리자

주요 기능:

- 접속 계정 표시
- 오늘 예약, 내 월간 예약, 내 월간 로그, 프롬프트 정리, 로그 미작성 KPI
- 현재 사용중/다음 예약
- 로그 작성 필요 안내
- 빠른 이동
- 오늘 예약 일부 표시

핵심 컴포넌트:

- Status Card
- Current/Next reservation card
- Warning card
- Quick action card
- Reservation list card

배치 규칙:

- GitHub + Linear 참고.
- KPI는 한 줄 scan이 가능해야 한다.
- Warning 상태는 KPI 카드와 별도 alert section으로 중복 인지 가능하게 한다.
- 빠른 실행은 실제 사용 빈도순으로 정렬한다.

상태 표현:

- 현재 사용중 있음/없음
- 다음 예약 있음/없음
- 로그 미작성 있음/없음

빈 상태:

- 현재 사용중 없음
- 다음 예약 없음
- 오늘 예약 없음

오류 상태:

- Dashboard 자체 오류 상태는 route level에서 처리하지 않는다.

모바일 대응:

- KPI grid는 단일 column 또는 2-column으로 줄인다.
- 긴 예약 제목은 줄바꿈 허용.

현재 구현 메모:

- Dashboard는 `gm-page-header`, `gm-stat-card`, `gm-action-card`, `gm-badge`를 사용한다.
- 빠른 실행은 사용 신청, 오늘 예약, 예약 캘린더, 프롬프트 정리, 사용 안내 순서로 배치한다.
- 카드 안에 큰 카드를 중첩하지 않고 목록/행 구조를 우선한다.

향후 개선:

- 최근 Prompt, 최근 테스트, 최근 활동 feed 추가

## Prompt 입력

관련 파일:

- `app/templates/prompts/new.html`
- `app/prompts/routes.py`

화면 목적:

- 사용자가 거친 요청을 입력하고 Provider/모델/API Key 실행 조건을 선택한다.

주요 사용자:

- 일반 사용자
- 관리자

주요 기능:

- Provider 선택
- 모델 선택
- 일회성 API Key 입력 또는 서버 저장 키 사용
- 정리 템플릿 선택
- 정리 목표 입력
- 정리 대상 요청 입력
- 개인정보/평가 자료 입력 금지 안내

핵심 컴포넌트:

- Provider select
- Model select
- Prompt textarea
- Template select
- Security warning card
- Execute button

배치 규칙:

- Raycast의 prompt 입력 경험을 참고한다.
- 입력 영역은 화면에서 가장 크고 안정적인 영역이어야 한다.
- Provider/모델은 prompt보다 위에 배치하되, 너무 많은 설명으로 입력을 밀어내지 않는다.

상태 표현:

- 저장 키 활성/비활성/없음
- 실행 중 button disabled + `처리 중`

빈 상태:

- prompt 미입력 시 서버가 error flash를 반환한다.

오류 상태:

- 입력 없음
- 길이 초과
- API Key 없음
- Provider 오류
- 연속 요청 제한/일일/월간 제한

모바일 대응:

- select 2열은 mobile에서 1열
- 실행 버튼과 목록/설정 버튼은 wrap

향후 개선:

- Command palette 형태의 템플릿 검색
- Prompt 품질 점검 checklist

## Prompt 실행

현재 실제 구현:

- form submit 후 서버에서 단일 Provider를 호출한다.
- submit button은 `처리 중`으로 바뀌고 disabled 되며 `aria-busy=true`를 갖는다.
- 오른쪽 보조 panel은 Prompt 입력, 실행 준비, 선택 Provider 실행, 결과 저장, 완료의 단일 Provider 단계만 표시한다.
- streaming, multi-provider 병렬 실행, 모델 비교 timeline은 구현하지 않는다.

향후 설계:

- multi-provider 비교가 백엔드에 추가될 때만 Cursor + Raycast식 단계 timeline을 확장한다.

핵심 컴포넌트:

- Timeline
- Progress Step
- Provider status badge
- Loading skeleton
- Error recovery action

상태 표현:

- 대기
- 실행 중
- 성공
- 실패
- 건너뜀

오류 상태:

- 단일 Provider 실패 시 서버 flash와 기존 오류 흐름으로 안내한다.
- API Key 없음은 설정 화면으로 안내한다.

주의:

- 현재 API 구조는 단일 Provider 실행이다. multi-provider/streaming UI는 백엔드 구현 승인 전까지 추가하지 않는다.

## Prompt 결과

관련 파일:

- `app/templates/prompts/show.html`
- `app/prompts/routes.py`

화면 목적:

- 원본 요청과 AI 정리 결과를 검토하고 Markdown으로 다운로드한다.

주요 사용자:

- 일반 사용자
- 관리자

주요 기능:

- Provider, 모델, 생성일 표시
- 원본 요청 표시
- AI 정리 결과 표시
- Markdown 다운로드

핵심 컴포넌트:

- Result header
- Original Prompt Card
- AI Result Card
- Download button

배치 규칙:

- Perplexity 참고.
- 긴 결과는 읽기 쉬운 width와 line-height를 유지한다.
- 원본과 결과는 desktop에서 2열, mobile에서 1열.

상태 표현:

- 현재 저장된 결과만 표시한다.

빈 상태:

- 존재하지 않는 result는 404.

오류 상태:

- 권한 없는 타 사용자 result 접근은 404.

모바일 대응:

- 2열 grid를 1열로 전환.
- pre 영역은 가로 overflow 없이 `whitespace-pre-wrap`.

현재 구현 메모:

- 결과 화면은 `검토 메모` 영역에서 단일 Provider 결과임을 명확히 표시한다.
- 위험 요소, 개선 제안, History 연결은 보조 inset panel로 제공한다.

향후 개선:

- multi-provider 구현 후 비교 요약, 차이점, 근거/참고 source card 추가

## Model 비교

현재 실제 구현:

- Provider별 API Key와 모델 선택은 가능하다.
- 하나의 prompt를 GPT/Gemini/Claude에 동시에 실행하고 비교하는 화면은 없다.
- 현재 UI에는 비교가 구현된 것처럼 보이는 preview나 CTA를 두지 않는다.

향후 설계:

- Perplexity 결과 비교와 Cursor 실행 흐름을 결합한다.
- 같은 원본 prompt에 대해 모델별 응답 card를 병렬 표시한다.
- 비교 요약, 강점, 누락, 위험 요소를 별도 summary card에 표시한다.

핵심 컴포넌트:

- Model Card
- Comparison Table
- Difference Badge
- Risk Card
- Recommendation Card

모바일 대응:

- 모델별 card를 vertical stack으로 배치한다.

## Test

관련 파일:

- `app/templates/admin/dashboard.html`
- `app/admin/routes.py`

화면 목적:

- 관리자 화면에서 서버의 pytest를 실행한다.

주요 사용자:

- 관리자
- 보조관리자

주요 기능:

- 전체 테스트 실행
- 실행 결과 요약 표시
- 테스트 파일별 설명과 상태 표시
- 상세 pytest output 표시

핵심 컴포넌트:

- Test action header
- Summary Status Card
- Test File Result Table
- Log `pre` block

배치 규칙:

- GitHub + Linear 참고.
- 실행 버튼은 명확히 위험도가 낮은 운영 작업으로 보이게 한다.
- 결과 요약은 PASS/FAIL, 총 테스트, 소요 시간, summary를 4개 카드로 표시한다.

상태 표현:

- PASS
- FAIL
- SKIP
- NOT RUN

빈 상태:

- 실행 전에는 설명과 실행 버튼만 표시한다.

오류 상태:

- subprocess 예외 시 returncode -1, summary, output 표시.

모바일 대응:

- summary card는 stack.
- test file table은 horizontal scroll 허용.

## Test Result

관련 파일:

- `app/templates/admin/dashboard.html`
- `app/admin/routes.py`

포함해야 할 정보:

- 테스트 이름: 현재 `tests/test_*.py`
- 테스트 설명: `TEST_FILE_DESCRIPTIONS`
- 상태: PASS/FAIL/SKIP/NOT RUN
- 실행 시간: 현재 전체 duration만 있음
- 대상 기능: `target`
- 결과: status badge
- 실패 원인: pytest `FAILED`/`ERROR` summary line과 첫 오류 line을 요약해 카드와 파일별 표에 표시
- 해결 힌트: 파일별 기본 힌트와 template/url_for/assertion/CSRF/SQLAlchemy/import 오류 유형별 힌트 표시
- 최근 실행 이력: DB에 별도 저장하지 않고 현재 실행의 전체 duration만 파일별 표에 함께 표시

향후 개선:

- 각 테스트 카드에 최근 실행 이력 저장
- 실패 시 stderr/traceback 전문을 구조화해 첫 실패와 후속 실패를 분리 표시
- 파일별 duration은 pytest `--durations` 또는 json report 도입 후 표시

## History

관련 파일:

- `app/templates/reservations/index.html`
- `app/templates/logs/index.html`
- `app/templates/prompts/index.html`
- `app/templates/logs/show.html`
- `app/templates/prompts/show.html`

화면 목적:

- 사용자의 예약, 사용 로그, 프롬프트 정리 기록을 조회한다.

주요 사용자:

- 일반 사용자
- 관리자

주요 기능:

- 검색
- 필터
- 목록 table
- 상세 보기
- Markdown 다운로드

핵심 컴포넌트:

- Filter Form
- Data Table
- Status Badge
- Detail Card
- Empty State

배치 규칙:

- GitHub table density를 참고한다.
- 검색/필터는 표 위에 둔다.
- action 열은 우측에 둔다.

상태 표현:

- 예약: 예약/완료/취소
- 로그: 기록 있음/없음
- prompt: Provider/모델/생성일

빈 상태:

- 저장된 기록 없음
- 필터 결과 없음

모바일 대응:

- horizontal scroll table 유지.
- 상세 화면은 card stack.

## Admin

관련 파일:

- `app/templates/admin/dashboard.html`
- `app/admin/routes.py`

화면 목적:

- 시스템 운영 관리 기능을 한 화면 shell 안에서 section 단위로 제공한다.

주요 사용자:

- 관리자
- 보조관리자

주요 기능:

- 설정 관리
- 안내 문구 관리
- 신청 항목 관리
- 사용자 관리
- 등록 요청 관리
- 통계
- 월간 운영 보고서
- CSV 내보내기
- DB 백업
- 감사 로그
- AI Key 상태
- 전체 테스트 실행

핵심 컴포넌트:

- Admin section card
- Form panel
- Filter form
- Data table
- Status badge
- Audit log table
- Backup table

배치 규칙:

- GitHub admin/settings와 Linear card launcher를 참고한다.
- Section launcher는 현재 기능 수가 많으므로 카드 크기와 설명 길이를 일정하게 유지한다.
- table은 dense하지만 row height 48px를 유지한다.

상태 표현:

- 활성/비활성
- 승인 대기
- 관리자/보조관리자/일반 사용자
- PASS/FAIL
- 백업 있음/없음

빈 상태:

- 사용자 없음
- 대기 요청 없음
- 통계 없음
- 백업 없음
- 감사 로그 없음

오류 상태:

- 관리자 권한 없음은 403.
- CSV/백업/테스트 실패는 flash와 결과 panel로 표시한다.

모바일 대응:

- 카드 launcher는 1열 또는 2열.
- 표는 horizontal scroll.
- 작업 버튼은 wrap.

## Settings

관련 파일:

- `app/templates/settings/api_key.html`
- `app/settings/routes.py`
- `app/templates/settings/macros.html`

화면 목적:

- 사용자별 OpenAI, Gemini, Claude Provider/API Key와 모델을 관리한다.

주요 사용자:

- 일반 사용자
- 관리자

주요 기능:

- Provider별 상태 표시
- API Key 암호화 저장
- Provider 활성화
- 브라우저 localStorage 저장 옵션
- 모델 목록 새로고침
- 연결 테스트
- 키 삭제

핵심 컴포넌트:

- Provider Model Card
- Security Warning Card
- API Key Form
- Action Button Row

배치 규칙:

- 보안 안내는 시각적으로 분리한다.
- Provider 상태와 입력 form은 desktop에서 2열, mobile에서 1열.
- API Key 원문은 서버에서 다시 렌더링하지 않는다.

상태 표현:

- 활성
- 비활성
- 미등록
- 마지막 4자리
- 최근 사용일

빈 상태:

- 저장된 API Key 없음.

오류 상태:

- 저장할 키 없음
- 암호화 실패
- 연결 테스트 실패
- 모델 목록 refresh fallback

모바일 대응:

- Provider card list와 form stack.
- 버튼은 wrap.

## Profile / User

현재 개인 Profile 화면을 제공한다.

관련 파일:

- `app/routes/main.py`
- `app/templates/profile.html`
- `app/templates/base.html`

관련 화면:

- Header 사용자 badge: 승인된 사용자는 `/profile`로 이동
- Profile: 계정 정보, 부서, 내선, 권한, 승인 상태, 이번 달 예약/로그/프롬프트 정리, API Key 상태, 최근 예약/로그/프롬프트 정리 표시
- Settings API Key 화면: Profile의 CTA로 연결
- Admin 사용자 관리와 Pending 사용자 화면은 기존 권한/승인 흐름 유지

제약:

- Profile은 읽기 전용 요약 화면이며 사용자 권한, DB 모델, API Key 원문 노출 정책을 변경하지 않는다.
- API Key는 provider, 마지막 4자리, 선택 모델, 활성 상태만 표시한다.

## Guide / 안내

관련 파일:

- `app/templates/guide.html`
- `app/templates/partials/_auth_info.html`
- `app/routes/main.py`
- `app/defaults.py`

화면 목적:

- 적합 업무, 부적합 업무, 개인정보/민감정보, 평가 보안, 학생부 안내 등을 사용자에게 제공한다.

주요 사용자:

- 일반 사용자
- 승인 대기 사용자
- 관리자

주요 기능:

- 안내 intro
- guide anchor link
- GuideItem 기반 섹션 출력
- GPT 접속/인증번호 안내 partial

핵심 컴포넌트:

- Guide intro card
- Anchor button
- Guide section card
- Auth info partial

배치 규칙:

- Notion식 읽기 쉬운 guide card를 참고하되 과한 pastel은 피한다.
- 민감정보/평가 보안 안내는 warning tone을 유지한다.

상태 표현:

- guide item 활성/비활성은 관리자 화면에서 관리된다.

빈 상태:

- 표시할 사용 안내가 없습니다.

오류 상태:

- 없음.

모바일 대응:

- anchor button wrap.
- guide body는 1열로 전환.

## 2026-07-05 실제 구현 반영 범위

이번 UI 디자인 시스템 적용에서 실제 수정한 범위:

1. 공통 Layout: `app/templates/base.html`, `app/static/styles.css`
2. Typography / Color / Spacing / Radius: `app/static/styles.css`
3. Button / Card / Badge / Table / Alert / Empty State: `app/static/styles.css`, 각 template class
4. Landing: `app/templates/index.html`
5. Auth: `app/templates/auth/login.html`, `app/templates/auth/register.html`, `app/templates/auth/pending.html`
6. Dashboard: `app/templates/dashboard.html`
7. Reservations: `app/templates/reservations/index.html`, `new.html`, `today.html`, `calendar.html`
8. Logs: `app/templates/logs/index.html`, `new.html`, `show.html`
9. Prompt 입력/결과/기록: `app/templates/prompts/new.html`, `show.html`, `index.html`
10. Profile: `app/templates/profile.html`
11. Admin/Test Result: `app/templates/admin/dashboard.html`
12. 테스트 기대 문구: `tests/test_prompt_reviews.py`, `tests/test_app.py`, `tests/test_admin.py`

유지한 범위:

- URL, route, auth, 권한, DB 모델, API, 서버 로직 변경 없음
- React/Vue/Svelte/TypeScript/Bootstrap 등 새 프레임워크와 새 dependency 추가 없음
- flash alert의 `role="alert"` 유지
- CSRF meta와 submit hook 유지
- multi-provider 비교, streaming, backend timeline 기능 미구현 유지

검증 결과:

- `git diff --check`: PASS
- `uv run pytest`: PASS, 92 passed
- `npm run test:e2e`: PASS, 2 passed
- Playwright desktop/mobile overflow 점검: PASS, Landing/Login/Dashboard/Reservations/Prompt 입력/Profile/Admin sections에서 수평 overflow 없음
