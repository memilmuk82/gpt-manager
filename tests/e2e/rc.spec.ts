import { expect, test } from '@playwright/test';

test('release candidate core user workflow persists data across refreshes', async ({ page }) => {
  const email = 'teacher.e2e@senedu.kr';
  const password = 'password123';

  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'ChatGPT Pro 5X 공동 사용 지원 시스템' })).toBeVisible();
  await expect(page.getByText('Copyright © 2026 GPT Share Manager vNext')).toBeVisible();

  await page.getByRole('link', { name: '이용약관' }).click();
  await expect(page).toHaveURL(/\/terms$/);
  await expect(page.getByRole('heading', { name: '이용약관' }).first()).toBeVisible();
  await page.goBack();

  await page.getByRole('link', { name: '개인정보처리방침' }).click();
  await expect(page).toHaveURL(/\/privacy$/);
  await expect(page.getByRole('heading', { name: '개인정보처리방침' }).first()).toBeVisible();
  await page.goBack();

  await page.getByRole('main').getByRole('link', { name: '등록 요청' }).click();
  await page.getByLabel('이름').fill('E2E Teacher');
  await page.getByLabel('이메일').fill(email);
  await page.getByLabel('비밀번호').fill(password);
  await page.getByRole('button', { name: '등록 요청' }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByText(email)).toBeVisible();

  await page.getByRole('button', { name: '사용 종료' }).click();
  await expect(page.getByRole('banner').getByRole('link', { name: '등록 요청' })).toBeVisible();

  await page.getByRole('link', { name: '로그인', exact: true }).click();
  await page.getByLabel('이메일').fill(email);
  await page.getByLabel('비밀번호').fill(password);
  await page.getByRole('button', { name: '로그인' }).click();
  await expect(page).toHaveURL(/\/dashboard$/);

  await page.getByRole('link', { name: '내 예약' }).click();
  await expect(page.getByRole('heading', { name: '내 예약' })).toBeVisible();
  await expect(page.getByText('아직 예약이 없습니다.')).toBeVisible();

  await page.getByRole('link', { name: '사용 신청' }).click();
  await page.locator('#resource_id').selectOption({ label: 'GPT Pro 공용 계정 A (OpenAI)' });
  await page.locator('#work_type').selectOption({ label: '워크북 개발' });
  await page.locator('#start_at').fill('2026-07-02T09:00');
  await page.locator('#end_at').fill('2026-07-02T10:00');
  await page.locator('#purpose').fill('RC E2E 예약 검증');
  for (const checkbox of await page.locator('input[type=checkbox]').all()) {
    await checkbox.check();
  }
  await page.getByRole('button', { name: '예약 등록' }).click();
  await expect(page).toHaveURL(/\/reservations$/);
  await expect(page.getByText('RC E2E 예약 검증')).toBeVisible();
  await expect(page.getByText('예약', { exact: true })).toBeVisible();

  await page.reload();
  await expect(page.getByText('RC E2E 예약 검증')).toBeVisible();
  await expect(page.getByText('예약', { exact: true })).toBeVisible();

  await page.getByRole('button', { name: '완료' }).click();
  await expect(page.getByText('완료', { exact: true })).toBeVisible();
  await page.reload();
  await expect(page.getByText('완료', { exact: true })).toBeVisible();

  await page.goto('/settings/api-key');
  await expect(page.getByRole('heading', { name: 'AI Provider 설정' })).toBeVisible();
  await page.locator('#api_key').fill('gemini-e2e-key-1111');
  await page.getByRole('button', { name: '암호화 저장' }).click();
  await expect(page.getByText('저장됨: •••• •••• •••• 1111')).toBeVisible();

  await page.locator('#api_key').fill('gemini-e2e-key-2222');
  await page.getByRole('button', { name: '암호화 저장' }).click();
  await expect(page.getByText('저장됨: •••• •••• •••• 2222')).toBeVisible();
  await page.reload();
  await expect(page.getByText('저장됨: •••• •••• •••• 2222')).toBeVisible();

  await page.getByRole('button', { name: '삭제' }).click();
  await expect(page.getByRole('link', { name: /Google Gemini 미등록/ })).toBeVisible();
  await page.reload();
  await expect(page.getByRole('link', { name: /Google Gemini 미등록/ })).toBeVisible();
});
