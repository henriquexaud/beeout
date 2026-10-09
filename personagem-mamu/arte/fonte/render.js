// Renderiza SVG -> PNG com o Chromium do Playwright.
// uso: node render.js entrada.svg saida.png [escala]
let chromium;
try { ({ chromium } = require('playwright')); } catch { ({ chromium } = require('/opt/node22/lib/node_modules/playwright')); }
const fs = require('fs');
(async () => {
  const [inp, out, scale] = process.argv.slice(2);
  const svg = fs.readFileSync(inp, 'utf8');
  const [, w, h] = svg.match(/viewBox="0 0 (\d+) (\d+)"/).map(Number);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: +(scale || 1) });
  await page.setContent(`<html><body style="margin:0;background:transparent">${svg}</body></html>`);
  await page.screenshot({ path: out, omitBackground: true, clip: { x: 0, y: 0, width: w, height: h } });
  await browser.close();
})();
