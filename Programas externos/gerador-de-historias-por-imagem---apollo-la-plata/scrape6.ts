import puppeteer from 'puppeteer';
(async () => {
  const browser = await puppeteer.launch({ args: ['--no-sandbox'] });
  const page = await browser.newPage();
  await page.goto('https://docs.comfy.org/api-reference/cloud/overview', { waitUntil: 'networkidle2' });
  const text = await page.evaluate(() => Array.from(document.querySelectorAll('a')).map(a => a.href).join('\n'));
  console.log(text);
  await browser.close();
})();
