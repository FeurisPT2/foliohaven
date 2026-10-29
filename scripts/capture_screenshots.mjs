import { pathToFileURL } from 'node:url';
const cdpPath = pathToFileURL('C:/Users/epicg/.gemini/config/skills/design-taste-frontend/scripts/lib/cdp.mjs').href;
const { Browser, sleep } = await import(cdpPath);
import { createServer } from 'node:http';
import { createReadStream, statSync, existsSync, mkdirSync, writeFileSync } from 'node:fs';
import { resolve, join, extname } from 'node:path';

const outDir = resolve('app/assets');
mkdirSync(outDir, { recursive: true });

// Start local static server for app
const root = resolve('app');
const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.json': 'application/json'
};

const server = createServer((req, res) => {
  try {
    let p = resolve(join(root, decodeURIComponent(new URL(req.url, 'http://x').pathname)));
    if (statSync(p).isDirectory()) p = join(p, 'index.html');
    res.writeHead(200, { 'content-type': MIME[extname(p).toLowerCase()] || 'application/octet-stream' });
    createReadStream(p).pipe(res);
  } catch {
    res.writeHead(404);
    res.end();
  }
});

await new Promise(r => server.listen(0, '127.0.0.1', r));
const port = server.address().port;
const url = `http://127.0.0.1:${port}/index.html`;

const browser = await Browser.launch();
const page = await browser.newPage({ width: 1440, height: 900, dpr: 1 });
await page.goto(url);
await sleep(1000);

// Screenshot 1: Library View
await page.screenshot({ path: join(outDir, 'foliohaven-library.png'), format: 'png' });
console.log('Saved foliohaven-library.png');

// Open a book to reader
await page.eval(`
  const firstBook = document.querySelector('.book-card');
  if (firstBook) firstBook.click();
`);
await sleep(1000);

// Screenshot 2: Reader Canvas
await page.screenshot({ path: join(outDir, 'foliohaven-reader.png'), format: 'png' });
console.log('Saved foliohaven-reader.png');

// Trigger In-Book Search Drawer
await page.eval(`
  const searchBtn = document.getElementById('btn-toggle-search');
  if (searchBtn) searchBtn.click();
  const searchInput = document.getElementById('inbook-search-input');
  if (searchInput) {
    searchInput.value = 'Alice';
    searchInput.dispatchEvent(new Event('input'));
  }
`);
await sleep(800);

// Screenshot 3: Search in Book
await page.screenshot({ path: join(outDir, 'foliohaven-search.png'), format: 'png' });
console.log('Saved foliohaven-search.png');

// Close search, trigger Notes Drawer
await page.eval(`
  const closeSearch = document.getElementById('btn-close-search');
  if (closeSearch) closeSearch.click();
  const notesBtn = document.getElementById('btn-toggle-notes');
  if (notesBtn) notesBtn.click();
`);
await sleep(800);

// Screenshot 4: Notes and Highlights
await page.screenshot({ path: join(outDir, 'foliohaven-notes.png'), format: 'png' });
console.log('Saved foliohaven-notes.png');

await page.close();
await browser.close();
server.close();
console.log('All real app screenshots generated successfully.');
