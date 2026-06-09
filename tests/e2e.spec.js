const { test, expect } = require('@playwright/test');

const BASE = 'http://localhost:5173';

test.describe('Resume Builder E2E', () => {

  test('1. Homepage loads', async ({ page }) => {
    await page.goto(BASE);
    await expect(page.locator('h1')).toBeVisible();
  });

  test('2. Full flow: analyze → select → chat → edit', async ({ page }) => {
    await page.goto(BASE);

    // Step 1: Input background
    await page.fill('textarea', '计算机专业大四 Python Java Vue 电商项目');
    await page.locator('button', { hasText: /生成|analyze/i }).first().click();

    // Step 2: Wait for recommendations
    await page.waitForSelector('text=匹配', { timeout: 60000 });

    // Check recommendations appeared
    const cards = page.locator('section.bg-gray-50 .grid > div');
    const cardCount = await cards.count();
    console.log('Recommendations:', cardCount);
    expect(cardCount).toBeGreaterThanOrEqual(3);

    // Step 3: Click first card to select
    await cards.first().click();
    await page.waitForTimeout(1000);

    // Step 4: Click generate button
    const genBtn = page.locator('button', { hasText: /开始生成/ });
    await expect(genBtn).toBeVisible({ timeout: 5000 });
    await genBtn.click();

    // Step 5: Should navigate to chat
    await page.waitForURL('**/chat/**', { timeout: 15000 });
    console.log('Navigated to chat');

    // Step 6: Fill personal info
    await page.waitForSelector('input[placeholder="姓名"]', { timeout: 10000 });
    await page.fill('input[placeholder="姓名"]', '张三');
    await page.fill('input[placeholder="电话"]', '13800138000');
    await page.fill('input[placeholder="邮箱"]', 'test@test.com');
    await page.fill('input[placeholder="城市"]', '北京');
    await page.locator('button', { hasText: /确认.*继续/ }).click();
    console.log('Personal submitted');

    // Step 7: Wait for education options
    await page.waitForTimeout(5000);
    let checkboxes = page.locator('input[type="checkbox"]');
    let cbCount = await checkboxes.count();
    console.log('Education checkboxes:', cbCount);
    if (cbCount > 0) {
      await checkboxes.first().check();
      await page.locator('button', { hasText: '确认' }).first().click();
      console.log('Education done');
    }

    // Step 8-12: Skip through remaining modules
    for (let i = 0; i < 8; i++) {
      await page.waitForTimeout(6000);
      const body = await page.textContent('body');
      console.log('Step', i, 'body snippet:', body.substring(0, 200));
      if (body.includes('简历生成完成') || body.includes('前往编辑') || body.includes('编辑优化')) {
        console.log('DONE at step', i);
        break;
      }

      const checkboxes = page.locator('input[type="checkbox"]');
      const cbCount = await checkboxes.count();
      const confirmBtn = page.locator('button:has-text("确认")').filter({ hasNotText: '继续' });
      const skipBtn = page.locator('button:has-text("跳过")');
      const regenBtn = page.locator('button:has-text("换一批")');

      if (cbCount > 0 && await confirmBtn.count() > 0) {
        await checkboxes.first().check();
        await confirmBtn.first().click();
        console.log('Module', i, 'confirmed with', cbCount, 'checkboxes');
      } else if (await skipBtn.count() > 0) {
        await skipBtn.first().click();
        console.log('Module', i, 'skipped');
      } else if (await regenBtn.count() > 0) {
        await regenBtn.first().click();
        console.log('Module', i, 'regenerated');
      } else {
        console.log('Module', i, 'NO ACTION available');
        break;
      }
    }

    await page.waitForTimeout(3000);
    const body = await page.textContent('body');
    const done = body.includes('简历生成完成') || body.includes('前往编辑');
    console.log('Final:', done ? 'SUCCESS' : 'NOT DONE');
    expect(done).toBeTruthy();
  });

});
