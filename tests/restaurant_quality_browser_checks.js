async page => {
  const assert = require('node:assert/strict');
  const errors = [], posts = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('request', request => {
    if (request.method() === 'POST' && request.url().includes('/api/'))
      posts.push({path:new URL(request.url()).pathname, body:request.postDataJSON()});
  });
  await page.clock.install();
  await page.setViewportSize({width:390,height:844});
  await page.goto('http://127.0.0.1:8766/', {waitUntil:'networkidle'});
  const choose = async language => page.locator('.language-option').filter({has:page.locator(`input[value="${language}"]`)}).click();
  for (const [language, sidebar, navigation] of [
    ['et','Töölaua külgriba','Töölaua jaotised'],
    ['en','Workspace sidebar','Workspace sections'],
    ['ru','Боковая панель рабочего стола','Разделы рабочего стола'],
  ]) {
    await choose(language);
    assert.equal(await page.locator('aside.sidebar').getAttribute('aria-label'),sidebar);
    assert.equal(await page.locator('.navigation').getAttribute('aria-label'),navigation);
    assert.equal(await page.locator('html').getAttribute('lang'),language);
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
    await page.screenshot({path:`output/playwright/quality-mobile-${language}-first-screen.png`});
    const startButton = await page.locator('#demo-start').boundingBox();
    assert(startButton.y + startButton.height <= 844, `voice controls are below the first mobile screen in ${language}: ${startButton.y}`);
    const micButton = await page.locator('#demo-mic').boundingBox();
    assert(micButton.y + micButton.height <= 844, `microphone is below the first mobile screen in ${language}: ${micButton.y}`);
  }
  await choose('en');
  await page.screenshot({path:'output/playwright/quality-mobile-unconnected.png',fullPage:true});
  for (const width of [320,390,800,801,1440]) {
    await page.setViewportSize({width,height:844});
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),`overflow at ${width}px`);
  }
  await page.setViewportSize({width:390,height:844});
  assert(await page.locator('#logout').isHidden());
  assert(await page.locator('#demo-mic').isDisabled());
  await page.locator('#operator-token').fill('invalid-review-token');
  await page.locator('#connect').click();
  await page.waitForFunction(()=>!state.credential && document.getElementById('auth-status').classList.contains('error'));
  assert((await page.locator('#auth-status').textContent()).includes('Enter a valid token'));
  await page.locator('#operator-token').fill('restaurant-fixture-operator');
  await page.locator('#connect').click();
  await page.waitForFunction(()=>state.connected && !state.readBusy);
  assert(await page.locator('#operator-token').isHidden());
  assert(await page.locator('#logout').isVisible());
  const prepare = async time => {
    await page.locator('#reservation-date').fill(await page.evaluate(()=>tallinnDay(1)));
    await page.locator('#reservation-time').fill(time);
    await page.locator('#reservation-party').fill('2');
    await page.locator('#reservation-prepare').click();
    await page.waitForFunction(()=>reservation.holdId && !reservation.busy);
  };
  await prepare('14:00');
  const original = await page.evaluate(()=>reservation.holdId);
  assert(await page.locator('#reservation-recap-timer').isVisible());
  assert.equal(await page.locator('#reservation-recap-timer').getAttribute('aria-live'),'off');
  assert((await page.locator('#reservation-recap-timer').textContent()).includes('valid for'));
  await page.evaluate(()=>dispatchEvent(new Event('pagehide')));
  assert.equal(await page.evaluate(()=>reservation.countdownTimer),null);
  await page.evaluate(()=>dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true})));
  assert(await page.evaluate(()=>reservation.countdownTimer!==null));
  assert(await page.locator('#reservation-recap-timer').isVisible());
  await page.locator('#reservation-read').click();
  await page.waitForFunction(()=>reservation.acknowledged && !reservation.busy);
  assert(await page.locator('#reservation-confirm').isEnabled());
  await page.locator('#reservation-renew').click();
  await page.waitForFunction(()=>!reservation.busy && !reservation.acknowledged && document.getElementById('reservation-status').textContent.includes('renewed'));
  assert.equal(await page.evaluate(()=>reservation.holdId),original);
  assert(await page.locator('#reservation-confirm').isDisabled());
  assert.equal(posts.filter(row=>row.path==='/api/booking/confirm').length,0);
  await page.clock.fastForward(65000);
  assert.equal(await page.evaluate(()=>reservation.holdId),null);
  assert(await page.locator('#reservation-recap').isHidden());
  assert(await page.locator('#reservation-confirm').isDisabled());
  assert(await page.locator('#reservation-renew').isEnabled());
  assert((await page.locator('#reservation-status').textContent()).includes('expired'));
  await page.locator('#reservation-renew').click();
  await page.waitForFunction(()=>reservation.holdId && !reservation.busy);
  assert.equal(await page.evaluate(()=>reservation.holdId),original);
  const clockTime = await page.evaluate(()=>Date.now());
  await page.clock.setSystemTime(new Date(clockTime+3600000));
  assert(await page.evaluate(()=>currentReservationProposal()),'wall clock adjustment expired a valid proposal');
  await page.locator('#reservation-read').click();
  await page.waitForFunction(()=>reservation.acknowledged && !reservation.busy);
  await page.locator('#reservation-confirm').click();
  await page.waitForFunction(()=>reservation.bookingId && !reservation.busy);
  assert.equal(posts.filter(row=>row.path==='/api/booking/confirm').length,1);
  assert(await page.locator('#reservation-recap-timer').isHidden());
  assert(await page.locator('#reservation-renew').isHidden());
  await page.locator('#reservation-cancel').click();
  await page.waitForFunction(()=>!reservation.bookingId && !reservation.busy);
  await page.locator('#demo-start').click();
  await page.waitForFunction(()=>state.sessionId && !state.turnBusy);
  const day = await page.evaluate(()=>tallinnDay(1));
  await page.locator('#demo-text').fill(`I'd like a table on ${day} at 3 PM for two people.`);
  await page.locator('#demo-send').click();
  await page.waitForFunction(()=>state.recap && !state.turnBusy);
  assert(await page.locator('#demo-recap-timer').isVisible());
  await page.clock.fastForward(65000);
  assert.equal(await page.evaluate(()=>state.recap),null);
  assert.equal(await page.evaluate(()=>state.recapDeliveryId),null);
  assert(await page.locator('#demo-recap-timer').isHidden());
  assert((await page.locator('#demo-status').textContent()).includes('proposal expired'));
  await page.locator('#demo-end').click();
  await page.waitForFunction(()=>!state.sessionId && !state.turnBusy);
  await prepare('16:00');
  await page.locator('#reservation-read').click();
  await page.waitForFunction(()=>reservation.acknowledged && !reservation.busy);
  let release;
  const gate = new Promise(resolve=>{release=resolve;});
  await page.route('**/api/booking/confirm',async route=>{
    await gate;
    await route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({error:'write_outcome_unknown',ok:false})});
  });
  await page.locator('#reservation-confirm').click();
  await page.waitForFunction(()=>reservation.busy);
  await page.clock.fastForward(65000);
  release();
  await page.waitForFunction(()=>reservation.uncertain && !reservation.busy);
  assert(await page.locator('#reservation-renew').isHidden());
  assert(await page.locator('#reservation-prepare').isDisabled());
  assert((await page.locator('#reservation-status').textContent()).includes('The result is uncertain'));
  await page.setViewportSize({width:1440,height:1000});
  await page.screenshot({path:'output/playwright/quality-desktop.png',fullPage:true});
  await page.locator('#logout').click();
  const endedStatus = await page.locator('#reservation-status').textContent();
  await page.clock.fastForward(130000);
  assert.equal(await page.locator('#reservation-status').textContent(),endedStatus);
  assert.equal(await page.evaluate(()=>reservation.countdownTimer),null);
  assert(await page.locator('#reservation-renew').isHidden());
  assert.deepEqual(errors,[]);
  return {languages:3,translatedLandmarks:true,mobileVoiceOnFirstScreen:true,mobileMicrophoneOnFirstScreen:true,layouts:5,clearAuthErrors:true,serverLifetime:true,monotonicClock:true,pageRestoreResumesTimers:true,expiredConfirmationDenied:true,renewalKeepsTable:true,renewalRequiresNewRead:true,voiceExpiryVisible:true,uncertainMutationCannotRenew:true,logoutStopsTimers:true,pageErrors:0};
}
