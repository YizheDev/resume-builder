# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: e2e.spec.js >> Resume Builder E2E >> 1. Homepage loads
- Location: tests/e2e.spec.js:7:3

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('h1')
Expected: visible
Timeout: 10000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 10000ms
  - waiting for locator('h1')

```

# Test source

```ts
  1  | const { test, expect } = require('@playwright/test');
  2  | 
  3  | const BASE = 'http://47.113.110.222:8081';
  4  | 
  5  | test.describe('Resume Builder E2E', () => {
  6  | 
  7  |   test('1. Homepage loads', async ({ page }) => {
  8  |     await page.goto(BASE);
> 9  |     await expect(page.locator('h1')).toBeVisible();
     |                                      ^ Error: expect(locator).toBeVisible() failed
  10 |   });
  11 | 
  12 |   test('2. Full flow: analyze → select → chat → edit', async ({ page }) => {
  13 |     await page.goto(BASE);
  14 | 
  15 |     // Step 1: Input background
  16 |     await page.fill('textarea', '计算机专业大四 Python Java Vue 电商项目');
  17 |     await page.locator('button', { hasText: /生成|analyze/i }).first().click();
  18 | 
  19 |     // Step 2: Wait for recommendations
  20 |     await page.waitForSelector('text=匹配', { timeout: 60000 });
  21 | 
  22 |     // Check recommendations appeared
  23 |     const cards = page.locator('section.bg-gray-50 .grid > div');
  24 |     const cardCount = await cards.count();
  25 |     console.log('Recommendations:', cardCount);
  26 |     expect(cardCount).toBeGreaterThanOrEqual(3);
  27 | 
  28 |     // Step 3: Click first card to select
  29 |     await cards.first().click();
  30 |     await page.waitForTimeout(1000);
  31 | 
  32 |     // Step 4: Click generate button
  33 |     const genBtn = page.locator('button', { hasText: /开始生成/ });
  34 |     await expect(genBtn).toBeVisible({ timeout: 5000 });
  35 |     await genBtn.click();
  36 | 
  37 |     // Step 5: Should navigate to chat
  38 |     await page.waitForURL('**/chat/**', { timeout: 15000 });
  39 |     console.log('Navigated to chat');
  40 | 
  41 |     // Step 6: Fill personal info
  42 |     await page.waitForSelector('input[placeholder="姓名"]', { timeout: 10000 });
  43 |     await page.fill('input[placeholder="姓名"]', '张三');
  44 |     await page.fill('input[placeholder="电话"]', '13800138000');
  45 |     await page.fill('input[placeholder="邮箱"]', 'test@test.com');
  46 |     await page.fill('input[placeholder="城市"]', '北京');
  47 |     await page.locator('button', { hasText: /确认.*继续/ }).click();
  48 |     console.log('Personal submitted');
  49 | 
  50 |     // Step 7: Wait for education options
  51 |     await page.waitForTimeout(5000);
  52 |     let checkboxes = page.locator('input[type="checkbox"]');
  53 |     let cbCount = await checkboxes.count();
  54 |     console.log('Education checkboxes:', cbCount);
  55 |     if (cbCount > 0) {
  56 |       await checkboxes.first().check();
  57 |       await page.locator('button', { hasText: '确认' }).first().click();
  58 |       console.log('Education done');
  59 |     }
  60 | 
  61 |     // Step 8-12: Skip through remaining modules
  62 |     for (let i = 0; i < 5; i++) {
  63 |       await page.waitForTimeout(5000);
  64 |       const body = await page.textContent('body');
  65 |       if (body.includes('简历生成完成') || body.includes('前往编辑')) {
  66 |         console.log('DONE at step', i);
  67 |         break;
  68 |       }
  69 | 
  70 |       checkboxes = page.locator('input[type="checkbox"]');
  71 |       cbCount = await checkboxes.count();
  72 |       if (cbCount > 0) {
  73 |         await checkboxes.first().check();
  74 |         await page.locator('button', { hasText: '确认' }).first().click();
  75 |         console.log('Module', i, 'confirmed');
  76 |       } else {
  77 |         // Try skip
  78 |         const skipBtn = page.locator('button:has-text("跳过")');
  79 |         if (await skipBtn.count() > 0) {
  80 |           await skipBtn.first().click();
  81 |           console.log('Module', i, 'skipped');
  82 |         }
  83 |       }
  84 |     }
  85 | 
  86 |     await page.waitForTimeout(3000);
  87 |     const body = await page.textContent('body');
  88 |     const done = body.includes('简历生成完成') || body.includes('前往编辑');
  89 |     console.log('Final:', done ? 'SUCCESS' : 'NOT DONE');
  90 |     expect(done).toBeTruthy();
  91 |   });
  92 | 
  93 | });
  94 | 
```