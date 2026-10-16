// The /work website gallery's previews: one above-the-fold screenshot of
// each live site in content.SITES, at a desktop viewport.
//
//   node tools/shoot-sites.mjs            # every site
//   node tools/shoot-sites.mjs zen-zone   # just the ones named
//
// The PNG lands in assets/sites/ (gitignored, the original), and ffmpeg makes
// the two renditions build.py's pic() reads: out/img/site-<slug>.webp (1440w)
// and -800. Re-run it when one of the sites changes; nothing else needs to.
import { chromium } from '/root/shot/node_modules/playwright/index.mjs';
import { execFileSync } from 'child_process';
import fs from 'fs';
import path from 'path';

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const sites = JSON.parse(execFileSync('python3', ['-c',
  'import json, content; print(json.dumps(content.SITES))'], { cwd: root }));
const only = process.argv.slice(2);
fs.mkdirSync(path.join(root, 'assets/sites'), { recursive: true });

const browser = await chromium.launch({ args: ['--disable-dev-shm-usage'] });
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
for (const s of sites) {
  if (only.length && !only.includes(s.slug)) continue;
  const page = await ctx.newPage();
  try {
    await page.goto(s.url, { waitUntil: 'networkidle', timeout: 45000 });
  } catch (e) {
    console.log(`${s.slug}: ${e.message.split('\n')[0]} — shooting what loaded`);
  }
  await page.waitForTimeout(2500);            // fonts, hero animations, sliders
  const png = path.join(root, 'assets/sites', `${s.slug}.png`);
  await page.screenshot({ path: png });
  await page.close();
  for (const [suffix, w, q] of [['', 1440, 82], ['-800', 800, 80]]) {
    execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', png, '-vf', `scale=${w}:-2`,
      '-c:v', 'libwebp', '-quality', String(q), '-compression_level', '6',
      path.join(root, 'out/img', `site-${s.slug}${suffix}.webp`)]);
  }
  console.log(`${s.slug}: ok`);
}
await browser.close();
