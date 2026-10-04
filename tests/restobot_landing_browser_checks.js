// Standalone, no production APIs: node tests/restobot_landing_browser_checks.js /path/to/playwright
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const {createHash} = require('node:crypto');
const root = path.resolve(__dirname, '..');
const staticRoot = path.join(root, 'app/restaurant/static');
const digest = file => createHash('sha256').update(fs.readFileSync(file)).digest('hex').slice(0, 12);

async function run() {
  assert(fs.existsSync(path.join(staticRoot, 'landing.html')), 'public landing.html is missing');
  assert(fs.existsSync(path.join(staticRoot, 'landing.css')), 'landing.css is missing');
  const {chromium} = require(process.argv[2] || 'playwright');
  const files = {
    '/': ['landing.html', 'text/html; charset=utf-8'],
    '/dashboard': ['index.html', 'text/html; charset=utf-8'],
    '/restaurant.css': ['restaurant.css', 'text/css'],
    '/operator-dashboard.css': ['operator-dashboard.css', 'text/css'],
    '/landing.css': ['landing.css', 'text/css'],
    '/favicon.svg': ['favicon.svg', 'image/svg+xml'],
    '/fonts/figtree-latin.woff2': [path.join(root, 'app/dashboard/static/fonts/figtree-latin.woff2'), 'font/woff2'],
    '/fonts/figtree-latin-ext.woff2': [path.join(root, 'app/dashboard/static/fonts/figtree-latin-ext.woff2'), 'font/woff2'],
  };
  const requests = [];
  const server = http.createServer((req, res) => {
    const pathname = new URL(req.url, 'http://localhost').pathname;
    requests.push({pathname, method:req.method});
    const file = files[pathname];
    if (!file) { res.writeHead(404); res.end('Not found'); return; }
    res.writeHead(200, {'Content-Type':file[1]});
    res.end(fs.readFileSync(path.resolve(staticRoot, file[0])));
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const origin = `http://127.0.0.1:${server.address().port}`;
  const screenshots = path.join(root, 'output/playwright');
  fs.mkdirSync(screenshots, {recursive:true});
  let browser;
  const errors = [], external = [];
  try {
    browser = await chromium.launch({headless:true});
    const context = await browser.newContext({javaScriptEnabled:false, serviceWorkers:'block'});
    await context.route('**/*', route => {
      if (new URL(route.request().url()).origin !== origin) {
        external.push(route.request().url());
        return route.abort();
      }
      return route.continue();
    });
    const page = await context.newPage();
    page.on('pageerror', error => errors.push(error.message));
    page.on('response', response => {if (response.status() >= 400) errors.push(`HTTP ${response.status()}: ${response.url()}`);});
    for (const width of [1440, 1024, 800, 540, 390, 320]) {
      await page.setViewportSize({width, height:width === 1440 ? 1000 : 844});
      await page.goto(origin, {waitUntil:'networkidle'});
      assert.equal(await page.locator('html').getAttribute('lang'), 'et');
      assert.equal(await page.getByRole('heading', {level:1}).count(), 1);
      assert(await page.getByRole('heading', {name:'Hea vastuvõtt algab enne saabumist.'}).isVisible());
      assert(await page.getByRole('link', {name:'Proovi kõneabilist', exact:true}).first().isVisible());
      assert.equal(await page.getByRole('link', {name:'Proovi kõneabilist', exact:true}).first().getAttribute('href'), '/dashboard#demo-section');
      assert.equal(await page.getByRole('link', {name:'Vaata lauakalendrit', exact:true}).first().getAttribute('href'), '/booking-calendar.html');
      assert(await page.getByRole('navigation', {name:'Peamenüü'}).getByRole('link', {name:'Töölaud', exact:true}).isVisible());
      // The overview must hand off to real controls, not nonfunctional mock UI.
      for (const [name, target] of [
        ['Broneeri laud', 'reservation-heading'],
        ['Vaata kõneajalugu', 'calls-section'],
        ['Vaata restoraniteavet', 'information-section'],
      ]) {
        const link = page.getByRole('link', {name, exact:true});
        assert.equal(await link.count(), 1, `missing workspace shortcut: ${name}`);
        await link.click();
        await page.waitForLoadState('networkidle');
        assert.equal(page.url(), `${origin}/dashboard#${target}`);
        assert(await page.locator(`#${target}`).isVisible());
        assert(await page.locator(`#${target}`).evaluate(el => {
          const box = el.getBoundingClientRect(); return box.top < innerHeight && box.bottom > 0;
        }), `${name} did not scroll to its controls`);
        await page.goto(origin, {waitUntil:'networkidle'});
      }
      assert(await page.locator('#demo-disclosure').isVisible(), 'fictional demo disclosure is hidden');
      assert.match(await page.locator('#demo-disclosure').textContent(), /Meretuule.*väljamõeldud/s);
      assert.match(await page.locator('#demo-disclosure').textContent(), /päris broneeringut ei tehta/i);
      assert.match(await page.locator('#confirmation-example').textContent(), /Jah, palun kinnita/);
      for (const language of ['Eesti', 'English', 'Русский']) assert(await page.getByText(language, {exact:true}).isVisible());
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true, `${width}px horizontal overflow`);
      assert(await page.locator('.table-name').evaluate(el => parseFloat(getComputedStyle(el).fontSize) * el.getScreenCTM().a >= 12), `${width}px focal table label is too small`);
      await page.evaluate(() => document.fonts.ready);
      assert(await page.evaluate(() => [...document.fonts].some(font => font.family === 'Figtree' && font.status === 'loaded')), 'local Figtree did not load');
      assert.equal(await page.locator('link[rel="preload"][as="font"]').count(), 1, 'critical local font preload is missing');
      assert.equal(await page.locator('link[rel="preload"][as="font"]').getAttribute('href'), `/fonts/figtree-latin.woff2?v=${digest(files['/fonts/figtree-latin.woff2'][0])}`, 'critical font is not preloaded with its content hash');
      assert(await page.evaluate(() => [...document.querySelectorAll('nav a')].every(el => {
        const box = el.getBoundingClientRect(); return box.width >= 44 && box.height >= 44;
      })), 'mobile navigation touch targets are too small');
      assert.equal(await page.locator('script').count(), 0, 'static landing should not need JavaScript');
      assert.equal(await page.locator('form, input').count(), 0, 'landing exposes a credential or booking form');
      const broken = await page.locator('a[href]').evaluateAll(links => links.map(link => link.getAttribute('href')).filter(href => {
        if (href.startsWith('#')) return !document.getElementById(href.slice(1));
        return !['/', '/dashboard', '/dashboard#demo-section', '/dashboard#reservation-heading', '/dashboard#calls-section', '/dashboard#information-section', '/booking-calendar.html'].includes(href);
      }));
      assert.deepEqual(broken, [], 'unapproved URL or broken local anchor');
      const stylesheet = await page.locator('link[rel="stylesheet"]').getAttribute('href');
      assert.equal(stylesheet, `/landing.css?v=${digest(path.join(staticRoot, 'landing.css'))}`);
      // Rendered text contrast catches light-on-mint and muted-on-navy regressions.
      const lowContrast = await page.evaluate(() => {
        const rgb = color => (color.match(/[\d.]+/g) || []).map(Number);
        const luminance = color => color.slice(0, 3).map(value => {
          const channel = value / 255; return channel <= .04045 ? channel / 12.92 : ((channel + .055) / 1.055) ** 2.4;
        }).reduce((sum, value, index) => sum + value * [.2126, .7152, .0722][index], 0);
        return [...document.querySelectorAll('body *')].filter(el => el instanceof HTMLElement &&
          el.getBoundingClientRect().width > 0 && [...el.childNodes].some(node => node.nodeType === Node.TEXT_NODE && node.textContent.trim())
        ).flatMap(el => {
          const style = getComputedStyle(el), foreground = rgb(style.color);
          let background = [255, 255, 255], parent = el;
          while (parent) {
            const color = rgb(getComputedStyle(parent).backgroundColor);
            if (color.length === 3 || color[3] === 1) {background = color; break;}
            parent = parent.parentElement;
          }
          const [light, dark] = [luminance(foreground), luminance(background)].sort((a, b) => b - a);
          const ratio = (light + .05) / (dark + .05);
          const large = parseFloat(style.fontSize) >= 24 || (parseFloat(style.fontSize) >= 18.66 && Number(style.fontWeight) >= 700);
          return ratio + .01 < (large ? 3 : 4.5) ? [{text:el.textContent.trim().slice(0, 60), ratio}] : [];
        });
      });
      assert.deepEqual(lowContrast, [], `${width}px unreadable text`);
      await page.keyboard.press('Tab');
      assert.equal(await page.locator(':focus').textContent(), 'Liigu sisu juurde');
      await page.keyboard.press('Enter');
      assert.equal(await page.locator(':focus').getAttribute('id'), 'main');
      const demo = page.getByRole('link', {name:'Proovi kõneabilist', exact:true}).first();
      await demo.focus();
      assert.equal(await demo.evaluate(el => getComputedStyle(el).outlineStyle), 'solid', 'keyboard focus is not visible');
      await page.getByRole('navigation', {name:'Peamenüü'}).getByRole('link', {name:'Kuidas töötab', exact:true}).focus();
      await page.keyboard.press('Tab');
      assert.equal(await page.locator(':focus').textContent(), 'Lauakalender');
      await page.keyboard.press('Tab');
      assert.equal(await page.locator(':focus').textContent(), 'Töölaud');
      await page.locator('body').click({position:{x:1,y:1}});
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.screenshot({path:path.join(screenshots, `restobot-landing-${width}.png`), fullPage:true});
    }
    await page.emulateMedia({reducedMotion:'reduce'});
    assert.equal(await page.evaluate(() => [...document.querySelectorAll('*')].some(el => {
      const style = getComputedStyle(el); return style.animationName !== 'none' && parseFloat(style.animationDuration) > 0;
    })), false, 'reduced motion still animates');
    // Unhappy path: lost CSS still leaves readable content and working native navigation.
    await page.route('**/landing.css?*', route => route.abort());
    await page.goto(origin, {waitUntil:'networkidle'});
    assert(await page.getByRole('heading', {name:'Hea vastuvõtt algab enne saabumist.'}).isVisible());
    assert(await page.getByRole('navigation', {name:'Peamenüü'}).getByRole('link', {name:'Töölaud', exact:true}).isVisible());
    assert.equal(await page.getByRole('link', {name:'Proovi kõneabilist', exact:true}).first().getAttribute('href'), '/dashboard#demo-section');
    await page.getByRole('link', {name:'Kuidas töötab', exact:true}).focus();
    await page.keyboard.press('Enter');
    assert.equal(page.url(), `${origin}/#how-it-works`, 'keyboard navigation failed without CSS');
    assert.deepEqual(external, [], 'external runtime dependency');
    assert.deepEqual(errors, [], 'browser errors');
    assert(requests.every(req => req.method === 'GET' && !req.pathname.startsWith('/api/')), 'landing accessed private APIs');
    console.log(JSON.stringify({result:'passed', widths:[1440,1024,800,540,390,320], workspaceHandoffs:18, contrast:'passed', javascript:'disabled', reducedMotion:'passed', stylesheetFailure:'passed', externalRequests:0, apiRequests:0, screenshots, browser:browser.version()}));
    await context.close();
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
}
run().catch(error => {console.error(error.message); process.exitCode = 1;});
