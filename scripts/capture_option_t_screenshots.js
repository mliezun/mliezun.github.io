const puppeteer = require('puppeteer-core');
const path = require('path');

const OUT = '/opt/cursor/artifacts/screenshots/option-t';
const BASE = 'http://localhost:8853';

const pages = [
  { name: 'home-light', url: '/', theme: 'light' },
  { name: 'home-dark', url: '/', theme: 'dark' },
  { name: 'post-code-light', url: '/2024/01/04/new-markdown-generator.html', theme: 'light' },
];

(async () => {
  const browser = await puppeteer.launch({
    executablePath: '/usr/local/bin/google-chrome',
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  for (const spec of pages) {
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 900, deviceScaleFactor: 2 });
    await page.goto(BASE + spec.url, { waitUntil: 'networkidle0', timeout: 30000 });
    await page.evaluate((theme) => {
      localStorage.setItem('theme', theme);
      document.documentElement.setAttribute('data-theme', theme);
      const link = document.getElementById('hljs-theme');
      if (link) {
        const base = 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/styles/';
        link.href = theme === 'dark' ? base + 'atom-one-dark.min.css' : base + 'github.min.css';
      }
    }, spec.theme);
    await page.reload({ waitUntil: 'networkidle0', timeout: 30000 });
    await new Promise((r) => setTimeout(r, 500));
    await page.screenshot({
      path: path.join(OUT, `${spec.name}.png`),
      fullPage: true,
    });
    await page.close();
    console.log('Saved', spec.name);
  }

  await browser.close();
})();
