/**
 * playwright-devglan.js — reusable Devglan text encryption/decryption via Playwright
 *
 * Usage:
 *   cd /tmp && npm install playwright
 *   cp /path/to/playwright-devglan.js . && node playwright-devglan.js
 *
 * Edit the ENCRYPTED_TEXT and DECRYPTION_KEY constants below for your case.
 */
const { chromium } = require('playwright');

// === CONFIGURE THESE ===
const ENCRYPTED_TEXT = "wwEmdJk1av39Vxnj9MKxAqGNqocmLG/5SYsrlRQxS18=";
const DECRYPTION_KEY = "f09c4f33ac20191b5a7ddc10e9ce467093b51f868252d8c31410e2e4";
const MODE = "decrypt"; // "decrypt" or "encrypt"
const TEST_PLAINTEXT = "hello";
const TEST_KEY = "key123";
// =======================

async function devglanEncrypt(page, plaintext, key) {
  await page.goto('https://www.devglan.com/online-tools/text-encryption-decryption',
    { timeout: 30000, waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  await page.fill('textarea[x-model="textToEncrypt"]', plaintext);
  if (key) {
    const cb = page.locator('#encryptSecretKey');
    if (await cb.isVisible({ timeout: 2000 }).catch(() => false)) {
      if (!await cb.isChecked()) await cb.check();
    }
    await page.waitForTimeout(200);
    await page.fill('#secretKey', key);
  }
  await page.waitForTimeout(200);
  await page.locator('button:has-text("Encrypt")').first().click();
  await page.waitForTimeout(2000);

  return await page.evaluate(() => {
    const el = document.querySelector('[x-model="encryptedText"]');
    return el ? el.value : null;
  });
}

async function devglanDecrypt(page, ciphertext, key) {
  await page.goto('https://www.devglan.com/online-tools/text-encryption-decryption',
    { timeout: 30000, waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  await page.fill('textarea[x-model="textToDecrypt"]', ciphertext);
  if (key) {
    const cb = page.locator('#dSecretKeyRequired');
    if (await cb.isVisible({ timeout: 2000 }).catch(() => false)) {
      if (!await cb.isChecked()) await cb.check();
    }
    await page.waitForTimeout(200);
    await page.fill('#deSecretKey', key);
  }
  await page.waitForTimeout(200);
  await page.locator('button:has-text("Decrypt")').first().click();
  await page.waitForTimeout(3000);

  return await page.evaluate(() => {
    const el = document.querySelector('[x-model="decryptedText"]');
    return el ? el.value : null;
  });
}

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });

  if (MODE === "encrypt") {
    const page = await browser.newPage();
    // Test: encrypt with known key to verify algorithm understanding
    const result = await devglanEncrypt(page, TEST_PLAINTEXT, TEST_KEY);
    if (result) {
      const buf = Buffer.from(result, 'base64');
      console.log(`encrypt("${TEST_PLAINTEXT}", "${TEST_KEY}")`);
      console.log(`  Base64: ${result}`);
      console.log(`  Bytes:  ${buf.length}`);
      console.log(`  Hex:    ${buf.toString('hex')}`);
    }
    await page.close();
  } else {
    const page = await browser.newPage();
    console.log(`Decrypting with key "${DECRYPTION_KEY.substring(0, 16)}..."`);
    const result = await devglanDecrypt(page, ENCRYPTED_TEXT, DECRYPTION_KEY);
    console.log(`  Result: ${result}`);
    await page.close();

    // Also try without key (unchecked) for comparison
    if (DECRYPTION_KEY) {
      const page2 = await browser.newPage();
      console.log(`Decrypting WITHOUT key (embedded key path):`);
      const result2 = await devglanDecrypt(page2, ENCRYPTED_TEXT, null);
      console.log(`  Result: ${result2}`);
      await page2.close();
    }
  }

  await browser.close();
})();
