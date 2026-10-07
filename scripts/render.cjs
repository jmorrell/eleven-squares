// Render an SVG to PNG with headless Chromium: node scripts/render.cjs in.svg out.png [scale]
const { chromium } = require('playwright');
const { readFileSync } = require('fs');
(async () => {
const [,, inp, outp, scale = '1'] = process.argv;
const svg = readFileSync(inp, 'utf8');
const vb = svg.match(/viewBox="0 0 (\d+) (\d+)"/);
const [w, h] = [+vb[1], +vb[2]];
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: +scale });
await page.setContent(`<html><body style="margin:0;background:#111">${svg.replace(/width="[^"]*in" height="[^"]*in"/, `width="${w}" height="${h}"`)}</body></html>`);
await page.screenshot({ path: outp, omitBackground: true, clip: { x: 0, y: 0, width: w, height: h } });
await browser.close();
})();
