// Exporta cada .slide de um slides.html como PNG 1080x1350.
// Uso: node ferramentas/carrossel/exportar.mjs conteudo/estaticos/<slug>/slides.html [pasta-saida]
import { createRequire } from 'node:module';
import { mkdirSync } from 'node:fs';
import { resolve, dirname, join } from 'node:path';
import { pathToFileURL } from 'node:url';

// Playwright instalado globalmente (NODE_PATH) não é visível para import ESM.
const { chromium } = createRequire(import.meta.url)('playwright');

const entrada = resolve(process.argv[2]);
const saida = resolve(process.argv[3] ?? join(dirname(entrada), 'png'));
mkdirSync(saida, { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1500, height: 1000 }, deviceScaleFactor: 2.5 });
await page.goto(pathToFileURL(entrada).href, { waitUntil: 'load' });
await page.evaluate(() => document.fonts.ready);
const slides = page.locator('.slide');
const n = await slides.count();
for (let i = 0; i < n; i++) {
  const arq = join(saida, `slide-${String(i + 1).padStart(2, '0')}.png`);
  await slides.nth(i).screenshot({ path: arq });
  console.log(arq);
}
await browser.close();
