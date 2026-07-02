import { expect, test } from '@playwright/test';

test('release candidate core user workflow persists data across refreshes', async ({ page }) => {
  const email = 'teacher.e2e@senedu.kr';
  const password = 'password123';

  await page.goto('/');
  await expect(page.getByRole('heading', { name: '생성형 AI 계정 공동 사용 지원 시스템' })).toBeVisible();
  await expect(page.getByText('Copyright © 2026 GPT Share Manager vNext')).toBeVisible();

  await page.getByRole('link', { name: '이용약관' }).click();
  await expect(page).toHaveURL(/\/terms$/);
  await expect(page.getByRole('heading', { name: '이용약관' }).first()).toBeVisible();
  await page.goBack();

  await page.getByRole('link', { name: '개인정보처리방침' }).click();
  await expect(page).toHaveURL(/\/privacy$/);
  await expect(page.getByRole('heading', { name: '개인정보처리방침' }).first()).toBeVisible();
  await page.goBack();

  await page.getByRole('main').getByRole('link', { name: '회원가입' }).click();
  await page.getByLabel('이름').fill('E2E Teacher');
  await page.getByLabel('이메일').fill(email);
  await page.getByLabel('비밀번호').fill(password);
  await page.getByRole('button', { name: '가입하기' }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByText(email)).toBeVisible();

  await page.getByRole('button', { name: '사용 종료' }).click();
  await expect(page.getByRole('banner').getByRole('link', { name: '회원가입' })).toBeVisible();

  await page.getByRole('link', { name: '로그인', exact: true }).click();
  await page.getByLabel('이메일').fill(email);
  await page.getByLabel('비밀번호').fill(password);
  await page.getByRole('button', { name: '로그인' }).click();
  await expect(page).toHaveURL(/\/dashboard$/);

  await page.getByRole('link', { name: '내 예약' }).click();
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

  await page.getByRole('link', { name: '설정' }).click();
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
