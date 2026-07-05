import { expect, type Page, test } from '@playwright/test';

async function expectNoPageOverflow(page: Page) {
  await page.waitForLoadState('networkidle');
  const overflow = await page.evaluate(() => ({
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
    bodyScrollWidth: document.body.scrollWidth,
  }));
  expect(overflow.scrollWidth, JSON.stringify(overflow)).toBeLessThanOrEqual(overflow.clientWidth + 2);
  expect(overflow.bodyScrollWidth, JSON.stringify(overflow)).toBeLessThanOrEqual(overflow.clientWidth + 2);
}

async function registerAndLogin(page: Page, email: string, name: string, password: string) {
  await page.goto('/auth/register');
  await page.getByLabel('이름').fill(name);
  await page.getByLabel('이메일').fill(email);
  await page.getByLabel('비밀번호').fill(password);
  await page.getByRole('button', { name: '등록 요청' }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
}

test('profile, admin sections, and mobile operational UI stay usable without page overflow', async ({ page }) => {
  const password = 'password123';
  const teacherEmail = `ui.teacher.${Date.now()}@senedu.kr`;

  await registerAndLogin(page, teacherEmail, 'UI Teacher', password);

  await page.goto('/profile');
  await expect(page.getByRole('heading', { name: /내 프로필/ })).toBeVisible();
  await expect(page.getByText(teacherEmail)).toBeVisible();
  await expect(page.getByRole('link', { name: 'AI Provider 설정' })).toBeVisible();
  await expectNoPageOverflow(page);

  for (const [url, heading] of [
    ['/guide', '사용 안내'],
    ['/settings/api-key', 'AI Provider 설정'],
    ['/prompt-reviews/new', '새 프롬프트 정리'],
    ['/reservations', '내 예약'],
  ] as const) {
    await page.goto(url);
    await expect(page.getByRole('heading', { name: new RegExp(heading) })).toBeVisible();
    await expectNoPageOverflow(page);
  }

  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/dashboard');
  await expect(page.getByRole('heading', { name: /운영 홈/ })).toBeVisible();
  await expect(page.getByText('더보기')).toBeVisible();
  await expectNoPageOverflow(page);

  await page.goto('/reservations');
  await expect(page.getByRole('heading', { name: /내 예약/ })).toBeVisible();
  await expectNoPageOverflow(page);

  await page.setViewportSize({ width: 1366, height: 900 });
  await page.getByRole('button', { name: '사용 종료' }).click();
  await registerAndLogin(page, 'admin@senedu.kr', 'Admin', password);

  for (const [url, heading] of [
    ['/admin?section=users', '사용자 관리'],
    ['/admin?section=tests', '전체 테스트 실행'],
    ['/admin?section=api-keys', '사용자 AI Key 상태'],
  ] as const) {
    await page.goto(url);
    await expect(page.getByRole('heading', { name: new RegExp(heading) }).last()).toBeVisible();
    await expectNoPageOverflow(page);
  }
});
