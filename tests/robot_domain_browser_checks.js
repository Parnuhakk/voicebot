async (page) => {
  // Read-only public acceptance: Restobot landing/workspace and old-host compatibility.
  const tab = await page.context().newPage();
  const check = (ok, message) => { if (!ok) throw new Error(message); };
  const origin = 'https://restobot.arleserver.cfd';
  const retiredHost = 'meretuule.arleserver.cfd';
  const errors = [];
  tab.on('pageerror', error => errors.push(error.message));
  try {
    const landing = await tab.goto(origin + '/', {waitUntil:'networkidle',timeout:30000});
    check(landing?.status() === 200 && tab.url() === origin + '/', 'Restobot landing did not load directly');
    check(await tab.locator('a[href="/dashboard#demo-section"]').count() > 0, 'Landing has no voice-demo action');
    check(await tab.locator('a[href="/booking-calendar.html"]').count() > 0, 'Landing has no calendar action');
    const oldRoot = await tab.request.get('https://robot.arleserver.cfd/?source=public-check', {maxRedirects:0});
    check(oldRoot.status() === 308 && oldRoot.headers().location === origin + '/?source=public-check', 'Old root redirect failed');
    const response = await tab.goto(origin + '/dashboard', {waitUntil:'networkidle',timeout:30000});
    check(response?.status() === 200 && tab.url() === origin + '/dashboard', 'Restobot workspace did not load directly');
    const links = await tab.locator('a[href]').evaluateAll(elements => elements.map(el => el.href));
    check(links.every(url => new URL(url).hostname !== retiredHost), 'Robot advertises the removed website');
    for (const id of ['operator-token','demo-start','demo-mic','reservation-prepare']) {
      check(await tab.locator('#' + id).count() === 1, `Missing robot control: ${id}`);
    }
    const urls = await tab.locator('script[src], link[rel="stylesheet"][href], link[as="font"][href], img[src]').evaluateAll(elements =>
      [...new Set(elements.map(el => el.src || el.href))]
    );
    const assets = [];
    for (const url of urls) {
      check(new URL(url).origin === origin, `Unexpected external asset: ${url}`);
      const asset = await tab.request.get(url);
      check(asset.status() === 200, `Asset returned ${asset.status()}: ${url}`);
      const content = await asset.body();
      const sha256 = await tab.evaluate(async bytes => {
        const hash = await crypto.subtle.digest('SHA-256', new Uint8Array(bytes));
        return [...new Uint8Array(hash)].map(value => value.toString(16).padStart(2, '0')).join('');
      }, [...content]);
      const version = new URL(url).searchParams.get('v');
      if (version) check(sha256.slice(0,12) === version, `Stale versioned asset: ${url}`);
      assets.push({url,status:asset.status(),bytes:content.length,sha256});
    }
    await tab.waitForFunction(() => document.querySelectorAll('#menu-list li').length > 0);
    check((await tab.locator('#opening-hours').textContent()).length > 0, 'Opening hours did not load');
    check((await tab.locator('#restaurant-policies').textContent()).length > 0, 'Restaurant policies did not load');
    check(await tab.locator('#reservation-prepare').isDisabled(), 'Unauthenticated booking controls are active');
    const publicData = await tab.request.get(origin + '/api/public/restaurant');
    const property = await publicData.json();
    check(publicData.status() === 200 && property.business_type === 'restaurant' && property.synthetic === true, 'Wrong public business data');
    for (const path of ['/api/bookings','/api/calls','/api/call-history']) {
      const denied = await tab.request.get(origin + path);
      check(denied.status() === 403 && denied.headers()['cache-control'] === 'no-store', `Private API denial failed: ${path}`);
    }
    const health = await tab.request.get(origin + '/health');
    check(health.status() === 200 && (await health.json()).ok === true, 'Robot health failed');
    for (const path of ['/hotel','/hotel/','/hotel?via=old-demo']) {
      const old = await tab.request.get(origin + path, {maxRedirects:0});
      check(old.status() === 410 && !old.headers().location, `Retired hotel path still redirects: ${path}`);
    }
    const retired = [];
    for (const path of ['/','/restaurant.js','/api/public/restaurant','/health']) {
      const unavailable = await tab.request.get('https://' + retiredHost + path, {maxRedirects:0});
      check([404,410,421,503].includes(unavailable.status()) && !unavailable.headers().location, `Removed hostname still publishes ${path}: ${unavailable.status()}`);
      retired.push({path,status:unavailable.status()});
    }
    check(errors.length === 0, `Browser errors: ${errors.join('; ')}`);
    return {pass:true,url:tab.url(),status:response.status(),title:await tab.title(),assets,
      menuItems:await tab.locator('#menu-list li').count(),retired,privateRoutesDenied:true,robotHealthy:true,errors};
  } finally { await tab.close(); }
}
