import { expect, test } from '@playwright/test';

test('release candidate core user workflow persists data across refreshes', async ({ page }) => {
  const email = 'teacher.e2e@senedu.kr';
  const password = 'password123';

  await page.goto('/');
  await expect(page.getByRole('heading', { name: /공용 AI 계정 운영 관리/ })).toBeVisible();

  await page.getByRole('link', { name: 'Register' }).click();
  await page.getByLabel('이름').fill('E2E Teacher');
  await page.getByLabel('이메일').fill(email);
  await page.getByLabel('비밀번호').fill(password);
  await page.getByRole('button', { name: '가입하기' }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByText(email)).toBeVisible();

  await page.getByRole('button', { name: 'Logout' }).click();
  await expect(page.getByRole('link', { name: 'Register' })).toBeVisible();

  await page.getByRole('link', { name: 'Login' }).click();
  await page.getByLabel('이메일').fill(email);
  await page.getByLabel('비밀번호').fill(password);
  await page.getByRole('button', { name: '로그인' }).click();
  await expect(page).toHaveURL(/\/dashboard$/);

  await page.getByRole('link', { name: 'Reservations' }).click();
  await expect(page.getByRole('heading', { name: '내 예약' })).toBeVisible();
  await expect(page.getByText('아직 예약이 없습니다.')).toBeVisible();

  await page.getByRole('link', { name: '새 예약' }).click();
  await page.locator('#resource_id').selectOption({ label: 'GPT Pro 공용 계정 A (OpenAI)' });
  await page.locator('#start_at').fill('2026-07-02T09:00');
  await page.locator('#end_at').fill('2026-07-02T10:00');
  await page.locator('#purpose').fill('RC E2E 예약 검증');
  await page.getByRole('button', { name: '예약 생성' }).click();
  await expect(page).toHaveURL(/\/reservations$/);
  await expect(page.getByText('RC E2E 예약 검증')).toBeVisible();
  await expect(page.getByText('reserved')).toBeVisible();

  await page.reload();
  await expect(page.getByText('RC E2E 예약 검증')).toBeVisible();
  await expect(page.getByText('reserved')).toBeVisible();

  await page.getByRole('button', { name: '완료' }).click();
  await expect(page.getByText('completed')).toBeVisible();
  await page.reload();
  await expect(page.getByText('completed')).toBeVisible();

  await page.getByRole('link', { name: 'Settings' }).click();
  await expect(page.getByRole('heading', { name: 'Gemini API Key' })).toBeVisible();
  await page.locator('#api_key').fill('gemini-e2e-key-1111');
  await page.getByRole('button', { name: '암호화 저장' }).click();
  await expect(page.getByText('저장됨: •••• •••• •••• 1111')).toBeVisible();

  await page.locator('#api_key').fill('gemini-e2e-key-2222');
  await page.getByRole('button', { name: '암호화 저장' }).click();
  await expect(page.getByText('저장됨: •••• •••• •••• 2222')).toBeVisible();
  await page.reload();
  await expect(page.getByText('저장됨: •••• •••• •••• 2222')).toBeVisible();

  await page.getByRole('button', { name: '삭제' }).click();
  await expect(page.getByText('저장된 Gemini API Key가 없습니다.')).toBeVisible();
  await page.reload();
  await expect(page.getByText('저장된 Gemini API Key가 없습니다.')).toBeVisible();
});
