async page => {
  const assert = require('node:assert/strict');
  const errors = [], requests = [], external = [], screenshots = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('request', request => {
    const url = new URL(request.url());
    if (url.protocol !== 'blob:' && url.origin !== origin) external.push(url.origin);
    if (request.method() === 'POST' && url.pathname.startsWith('/api/'))
      requests.push({path:url.pathname, body:request.postDataJSON()});
  });
  const origin = 'http://127.0.0.1:8766';
  const languages = [
    {code:'en', date:/date/i, time:/time/i, party:/guest/i, children:/children/i, unavailable:/No suitable table/, failed:/request failed/, question:/What time/},
    {code:'et', date:/kuupäev/i, time:/aeg|aja/i, party:/külali/i, children:/last/i, unavailable:/sobivat lauda ei ole/, failed:/Toiming ebaõnnestus/, question:/Mis kell/},
    {code:'ru', date:/дат/i, time:/врем/i, party:/гост/i, children:/дет/i, unavailable:/подходящего столика нет/, failed:/Запрос не удался/, question:/во сколько|какое время/i},
  ];
  const futureDay = offset => {
    const parts = new Intl.DateTimeFormat('en-CA', {timeZone:'Europe/Tallinn', year:'numeric', month:'2-digit', day:'2-digit'}).formatToParts(new Date());
    const part = key => parts.find(value => value.type === key).value;
    const date = new Date(`${part('year')}-${part('month')}-${part('day')}T12:00:00Z`);
    date.setUTCDate(date.getUTCDate() + offset);
    return date.toISOString().slice(0,10);
  };
  const fields = async () => page.locator('#reservation-form input').evaluateAll(inputs => inputs.map(input => input.value));
  const writes = () => requests.filter(request => ['/api/booking/session','/api/restaurant/reservation/prepare'].includes(request.path));
  const open = async (language, width=1440) => {
    await page.setViewportSize({width,height:width === 1440 ? 1000 : 844});
    await page.goto(origin+'/', {waitUntil:'networkidle'});
    await page.locator('.language-option').filter({has:page.locator('input[value="'+language.code+'"]')}).click();
    await page.locator('#operator-token').fill('restaurant-fixture-operator');
    await page.locator('#connect').click();
    await page.waitForFunction(() => state.connected && !state.readBusy);
  };
  const invalid = async (field, pattern, direct=false) => {
    const before = writes().length, values = await fields();
    if (direct)
      await page.locator('#reservation-form').evaluate(form => form.dispatchEvent(new Event('submit', {bubbles:true,cancelable:true})));
    else await page.locator('#reservation-prepare').click();
    await page.waitForFunction(() => !reservation.busy);
    const input = page.locator('#reservation-'+field);
    assert.equal(writes().length,before,`${field}: invalid fields started a session or prepared a table`);
    assert.equal(await input.getAttribute('aria-invalid'),'true',`${field}: missing accessible localized field error`);
    assert.equal(await page.evaluate(() => document.activeElement.id),'reservation-'+field,`${field}: first invalid field was not focused`);
    const description = (await input.getAttribute('aria-describedby') || '').split(/\s+/);
    assert(description.includes('reservation-'+field+'-error'),`${field}: field is not linked to its error`);
    assert(await page.locator('#reservation-'+field+'-error').isVisible());
    assert.match(await page.locator('#reservation-'+field+'-error').textContent(),pattern);
    assert.match(await page.locator('#reservation-status').textContent(),pattern);
    assert.equal(await page.locator('#reservation-status').getAttribute('aria-live'),'polite');
    assert.deepEqual(await fields(),values,'validation changed the requested date/time/party');
  };
  const prepare = async () => {
    const response = page.waitForResponse(response => new URL(response.url()).pathname === '/api/restaurant/reservation/prepare');
    await page.locator('#reservation-prepare').click();
    const result = await (await response).json();
    await page.waitForFunction(() => !reservation.busy);
    return result;
  };
  const end = async () => {
    await page.locator('#reservation-end').click();
    await page.waitForFunction(() => !reservation.sessionId && !reservation.busy);
  };
  const screenshot = async name => {
    const path = 'output/playwright/restaurant-guest-current-'+name+'.png';
    // Full-page capture from a scrolled field can paint the fixed, offscreen
    // skip link inside the image. Reset scroll without changing field focus.
    await page.evaluate(() => window.scrollTo(0,0));
    await page.screenshot({path,fullPage:true});
    screenshots.push(path);
  };
  // The actual renewal route must pass the same response boundary as prepare.
  // Every altered result starts with an owned, successful server response and
  // a positive server TTL, so a missing lifetime cannot mask a field mismatch.
  await page.clock.install();
  const renewalFailures = [], renewalChecks = [];
  const renew = async () => {
    const response = page.waitForResponse(response => new URL(response.url()).pathname === '/api/restaurant/reservation/renew');
    await page.locator('#reservation-renew').click();
    const result = await (await response).json();
    await page.waitForFunction(() => !reservation.busy);
    return result;
  };
  const receiptChecks = [];
  const invalidReceipts = [
    {name:'missing',mutate:data => {delete data.recap_delivery_id;return data;}},
    {name:'malformed',mutate:data => ({...data,recap_delivery_id:'invalid'})},
    {name:'non-string',mutate:data => ({...data,recap_delivery_id:[data.recap_delivery_id]})},
  ];
  for (const endpoint of ['prepare','renew']) {
    for (const [index,test] of invalidReceipts.entries()) {
      await open(languages[0]);
      await page.locator('#reservation-date').fill(futureDay((endpoint==='prepare'?23:26)+index));
      await page.locator('#reservation-time').fill('14:00');
      await page.locator('#reservation-party').fill('6');
      let original;
      if (endpoint==='renew') {
        original = await prepare();
        assert.equal(original.ok,true);
        await page.locator('#reservation-read').click();
        await page.waitForFunction(() => reservation.acknowledged && !reservation.busy);
      }
      const before=requests.length,values=await fields(),routePattern='**/api/restaurant/reservation/'+endpoint;
      await page.route(routePattern,async route => {
        const response=await route.fetch(),data=await response.json();
        assert.equal(data.ok,true);
        assert.match(data.recap_delivery_id,/^[a-f0-9]{32}$/);
        assert(data.recap_expires_in_s>0);
        if (original) assert.equal(data.hold_id,original.hold_id);
        await route.fulfill({response,json:test.mutate(data)});
      });
      await (endpoint==='prepare'?prepare():renew());
      try {
        assert.match(await page.locator('#reservation-status').textContent(),languages[0].failed);
        assert(await page.locator('#reservation-recap').isHidden());
        assert(await page.locator('#reservation-recap-timer').isHidden());
        assert(await page.locator('#reservation-renew').isHidden());
        assert(await page.locator('#reservation-read').isDisabled());
        assert(await page.locator('#reservation-confirm').isDisabled());
        assert.deepEqual(await page.evaluate(() => [reservation.holdId,reservation.renewalHoldId,reservation.recapDeliveryId,reservation.recapText,reservation.recapLanguage,reservation.proposalRequest,reservation.acknowledged]),[null,null,null,null,null,null,false]);
        assert.deepEqual(await fields(),values);
        assert(!requests.slice(before).some(request=>['/api/booking/recap','/api/booking/confirm'].includes(request.path)));
      } catch(error) {renewalFailures.push({case:endpoint+'-'+test.name+'-receipt',error:error.message});}
      await page.unroute(routePattern);
      await end();
      receiptChecks.push(endpoint+'-'+test.name);
    }
  }
  const renewals = [
    {name:'wrong-hold',mutate:data => ({...data,hold_id:data.hold_id+'-foreign'})},
    {name:'wrong-date',mutate:data => ({...data,recap:{...data.recap,date:futureDay(80)}})},
    {name:'wrong-time',mutate:data => ({...data,recap:{...data.recap,start:data.recap.date+'T16:00:00'}})},
    {name:'wrong-party',mutate:data => ({...data,recap:{...data.recap,party_size:2}})},
    {name:'wrong-timezone',mutate:data => ({...data,recap:{...data.recap,timezone:'UTC'}})},
    {name:'not-synthetic',mutate:data => ({...data,synthetic:false})},
    {name:'missing-guest',mutate:data => ({...data,recap:{...data.recap,guest_name:''}})},
    {name:'missing-table',mutate:data => ({...data,recap:{...data.recap,provider_name:''}})},
    {name:'expired-ttl',mutate:data => ({...data,recap_expires_in_s:0})},
  ];
  for (const [index,test] of renewals.entries()) {
    await open(languages[0]);
    await page.locator('#reservation-date').fill(futureDay(81+index));
    await page.locator('#reservation-time').fill('14:00');
    await page.locator('#reservation-party').fill('6');
    const original = await prepare();
    assert.equal(original.ok,true);
    assert(Number.isFinite(original.recap_expires_in_s) && original.recap_expires_in_s > 0);
    await page.locator('#reservation-read').click();
    await page.waitForFunction(() => reservation.acknowledged && !reservation.busy);
    const values = await fields(), before = requests.length;
    await page.route('**/api/restaurant/reservation/renew',async route => {
      assert.equal(route.request().postDataJSON().hold_id,original.hold_id);
      const response = await route.fetch(), data = await response.json();
      assert.equal(data.ok,true);
      assert.equal(data.hold_id,original.hold_id);
      assert.deepEqual(data.recap,original.recap);
      assert(Number.isFinite(data.recap_expires_in_s) && data.recap_expires_in_s > 0);
      await route.fulfill({response,json:test.mutate(data)});
    });
    await renew();
    try {
      assert.match(await page.locator('#reservation-status').textContent(),languages[0].failed,test.name);
      assert(await page.locator('#reservation-recap').isHidden(),test.name+': invalid renewal exposed a recap');
      assert(await page.locator('#reservation-recap-timer').isHidden());
      assert(await page.locator('#reservation-renew').isHidden());
      assert(await page.locator('#reservation-read').isDisabled());
      assert(await page.locator('#reservation-confirm').isDisabled());
      assert.equal(await page.locator('#reservation-status .booking-receipt').count(),0);
      assert.deepEqual(await page.evaluate(() => [reservation.holdId,reservation.renewalHoldId,reservation.acknowledged,reservation.expiryTimer,reservation.countdownTimer]),[null,null,false,null,null]);
      assert.deepEqual(await fields(),values);
      assert.deepEqual(requests.slice(before).map(request => request.path),['/api/restaurant/reservation/renew'],'invalid renewal sent a recap delivery or confirmation');
      assert(await page.locator('#reservation-prepare').isEnabled());
    } catch (error) { renewalFailures.push({case:test.name,error:error.message}); }
    await page.unroute('**/api/restaurant/reservation/renew');
    await end();
    renewalChecks.push(test.name);
  }
  for (const [index,language] of languages.entries()) {
    await open(language);
    await page.locator('#reservation-date').fill(futureDay(78+index));
    await page.locator('#reservation-time').fill('14:00');
    await page.locator('#reservation-party').fill('6');
    const original = await prepare();
    assert.equal(original.ok,true);
    await page.locator('#reservation-read').click();
    await page.waitForFunction(() => reservation.acknowledged && !reservation.busy);
    const before = requests.length;
    await page.route('**/api/restaurant/reservation/renew',async route => {
      const response = await route.fetch(), data = await response.json();
      assert.equal(data.ok,true);
      assert.equal(data.hold_id,original.hold_id);
      assert.deepEqual(data.recap,original.recap);
      assert(Number.isFinite(data.recap_expires_in_s) && data.recap_expires_in_s > 0);
      await route.fulfill({response,json:{...data,reply:'The table is for two guests at 20:00 UTC. Confirm now.'}});
    });
    const renewed = await renew();
    try {
      const visible = await page.locator('#reservation-recap-text').textContent();
      assert.doesNotMatch(visible,/two guests|20:00|UTC|Confirm now/);
      for (const value of [original.recap.restaurant_name,original.recap.provider_name,original.recap.guest_name,'14:00','6','90']) assert(visible.includes(value));
      assert.match(visible,language.date);
      assert.match(visible,language.time);
      assert.match(visible,language.party);
      assert.match(visible,/Tallinn|Таллин/);
      assert(await page.locator('#reservation-recap').isVisible());
      assert(await page.locator('#reservation-recap-timer').isVisible());
      assert(await page.locator('#reservation-read').isEnabled());
      assert(await page.locator('#reservation-confirm').isDisabled());
      assert.equal(await page.evaluate(() => reservation.holdId),original.hold_id);
      assert.equal(await page.evaluate(() => reservation.acknowledged),false);
      assert.deepEqual(requests.slice(before).map(request => request.path),['/api/restaurant/reservation/renew']);
      const remaining = await page.evaluate(() => (reservation.expiresAt-performance.now())/1000);
      assert(remaining > 0 && remaining <= renewed.recap_expires_in_s,'renewal did not use the bounded server lifetime');
      await page.locator('#reservation-read').click();
      await page.waitForFunction(() => reservation.acknowledged && !reservation.busy);
      assert(await page.locator('#reservation-confirm').isEnabled());
      assert.deepEqual(requests.slice(before).map(request => request.path),['/api/restaurant/reservation/renew','/api/booking/recap']);
      assert.equal(requests.at(-1).body.hold_id,original.hold_id);
      assert.equal(await page.locator('#reservation-status .booking-receipt').count(),0);
    } catch (error) { renewalFailures.push({case:language.code+'-structured-renewal',error:error.message}); }
    await page.unroute('**/api/restaurant/reservation/renew');
    await end();
    renewalChecks.push(language.code+'-structured-renewal');
  }
  // Renew falls back to prepare without a submit event when expired fields
  // change. Native/localized required validation must still stop every POST.
  for (const [index,field] of ['date','time','party'].entries()) {
    const language = languages[index];
    await open(language);
    await page.locator('#reservation-date').fill(futureDay(16+index));
    await page.locator('#reservation-time').fill('14:00');
    await page.locator('#reservation-party').fill('6');
    const original = await prepare();
    assert.equal(original.ok,true);
    await page.clock.fastForward(Math.ceil(original.recap_expires_in_s*1000)+1000);
    assert.equal(await page.evaluate(() => reservation.holdId),null);
    assert(await page.locator('#reservation-renew').isEnabled());
    await page.locator('#reservation-'+field).fill('');
    const values = await fields(), before = requests.length;
    await page.locator('#reservation-renew').click();
    await page.waitForFunction(() => !reservation.busy);
    try {
      assert.equal(requests.length,before,field+': invalid changed form sent a POST from the renewal fallback');
      assert.equal(await page.locator('#reservation-'+field).getAttribute('aria-invalid'),'true');
      assert.equal(await page.evaluate(() => document.activeElement.id),'reservation-'+field);
      assert.match(await page.locator('#reservation-'+field+'-error').textContent(),language[field]);
      assert.match(await page.locator('#reservation-status').textContent(),language[field]);
      assert(await page.locator('#reservation-recap').isHidden());
      assert(await page.locator('#reservation-confirm').isDisabled());
      assert.deepEqual(await fields(),values);
    } catch (error) { renewalFailures.push({case:field+'-invalid-fallback',error:error.message}); }
    await end();
    renewalChecks.push(field+'-invalid-fallback');
  }
  // Real normal responses produce a new one-use receipt for the same hold.
  // A changed displayed bound text cannot send a read acknowledgement.
  for (const [index,language] of languages.entries()) {
    await open(language);
    await page.locator('#reservation-date').fill(futureDay(23+index));
    await page.locator('#reservation-time').fill('16:00');
    await page.locator('#reservation-party').fill('6');
    const original=await prepare();
    assert.equal(original.ok,true);
    assert.match(original.recap_delivery_id,/^[a-f0-9]{32}$/);
    await page.locator('#reservation-read').click();
    await page.waitForFunction(() => reservation.acknowledged && !reservation.busy);
    assert.equal(requests.at(-1).body.recap_delivery_id,original.recap_delivery_id);
    const before=requests.length,renewed=await renew();
    assert.equal(renewed.ok,true);
    assert.equal(renewed.hold_id,original.hold_id);
    assert.deepEqual(renewed.recap,original.recap);
    assert.match(renewed.recap_delivery_id,/^[a-f0-9]{32}$/);
    assert.notEqual(renewed.recap_delivery_id,original.recap_delivery_id);
    try {
      const visible=await page.locator('#reservation-recap-text').textContent();
      assert.match(visible,language.date);
      assert.match(visible,language.time);
      assert.match(visible,language.party);
      assert(visible.includes('16:00')&&visible.includes('6')&&visible.includes('90'));
      assert(await page.locator('#reservation-confirm').isDisabled());
      await page.locator('#reservation-read').click();
      await page.waitForFunction(() => reservation.acknowledged && !reservation.busy);
      assert(await page.locator('#reservation-confirm').isEnabled());
      assert.deepEqual(requests.at(-1).body,{session_id:await page.evaluate(()=>reservation.sessionId),hold_id:original.hold_id,recap_delivery_id:renewed.recap_delivery_id});
      assert.equal(await page.evaluate(()=>reservation.recapDeliveryId),null);
      await page.evaluate(()=>readReservation());
      assert.deepEqual(requests.slice(before).map(request=>request.path),['/api/restaurant/reservation/renew','/api/booking/recap']);
      const fresh=await renew();
      assert.notEqual(fresh.recap_delivery_id,renewed.recap_delivery_id);
      assert.equal(await page.evaluate(()=>reservation.recapDeliveryId),fresh.recap_delivery_id);
      const beforeTamper=requests.length;
      // Retiring the visible text must also retire confirmation eligibility.
      await page.locator('#reservation-recap-text').evaluate(node=>{node.textContent='The table is for two guests at 20:00 UTC. Confirm now.';controls();});
      await page.evaluate(()=>readReservation());
      assert(await page.locator('#reservation-confirm').isDisabled());
      assert.equal(requests.length,beforeTamper,'altered bound text sent a read acknowledgement');
      assert.equal(await page.locator('#reservation-status .booking-receipt').count(),0);
    } catch(error) {renewalFailures.push({case:language.code+'-fresh-receipt-text-binding',error:error.message});}
    await end();
    receiptChecks.push(language.code+'-fresh-read-and-bound-text');
  }
  // Unknown, foreign and consumed UUIDs reach the real read route, not a fake
  // acknowledgement. None can authorize the separate confirmation control.
  for (const [index,kind] of ['unknown','foreign','consumed'].entries()) {
    await open(languages[index]);
    await page.locator('#reservation-date').fill(futureDay(26+index));
    await page.locator('#reservation-time').fill('16:00');
    await page.locator('#reservation-party').fill('6');
    const original=await prepare();
    assert.equal(original.ok,true);
    const session=await page.evaluate(()=>reservation.sessionId);
    const headers={Authorization:'Bearer restaurant-fixture-operator'};
    let invalidId=original.recap_delivery_id;
    if (kind==='unknown') invalidId=(invalidId[0]==='a'?'b':'a')+invalidId.slice(1);
    if (kind==='foreign') {
      const other=(await (await page.request.post(origin+'/api/booking/session',{headers,data:{language:'en'}})).json()).session_id;
      const foreign=await (await page.request.post(origin+'/api/restaurant/reservation/prepare',{headers,data:{session_id:other,date:futureDay(26+index),start_time:'18:00',party_size:2}})).json();
      assert.equal(foreign.ok,true);
      invalidId=foreign.recap_delivery_id;
    }
    if (kind==='consumed') {
      const ack=await page.request.post(origin+'/api/booking/recap',{headers,data:{session_id:session,hold_id:original.hold_id,recap_delivery_id:invalidId}});
      assert.equal(ack.status(),200);
    }
    assert.match(invalidId,/^[a-f0-9]{32}$/);
    await page.evaluate(id=>{reservation.recapDeliveryId=id;},invalidId);
    const before=requests.length,response=page.waitForResponse(response=>new URL(response.url()).pathname==='/api/booking/recap');
    await page.locator('#reservation-read').click();
    assert.equal((await response).status(),409);
    await page.waitForFunction(()=>!reservation.busy);
    assert(await page.locator('#reservation-confirm').isDisabled());
    assert.equal(await page.evaluate(()=>reservation.acknowledged),false);
    assert.equal(await page.evaluate(()=>reservation.recapDeliveryId),null);
    assert.deepEqual(requests.slice(before).map(request=>request.path),['/api/booking/recap']);
    await end();
    receiptChecks.push(kind+'-real-read-denied');
  }
  console.log(JSON.stringify({check:'restaurant_guest_current_browser_checks.js',stage:'renewal-boundary',renewalChecks,renewalFailures}));
  console.log(JSON.stringify({check:'restaurant_guest_current_browser_checks.js',stage:'receipt-boundary',receiptChecks}));
  assert.deepEqual(renewalFailures,[],'renewal must retain strict owned fields, structured read/consent and native fallback validation');
  await open(languages[0]);
  const contrast = await page.locator('small, .helper, #reservation-status').evaluateAll(elements => {
    const luminance = color => {
      const channels = color.match(/[\d.]+/g).slice(0,3).map(Number).map(value => {
        const s = value / 255;
        return s <= .04045 ? s / 12.92 : ((s + .055) / 1.055) ** 2.4;
      });
      return channels[0] * .2126 + channels[1] * .7152 + channels[2] * .0722;
    };
    return elements.filter(element => element.textContent.trim() && element.getClientRects().length).map(element => {
      let parent = element, background;
      while (parent) {
        background = getComputedStyle(parent).backgroundColor;
        if (background !== 'rgba(0, 0, 0, 0)' && background !== 'transparent') break;
        parent = parent.parentElement;
      }
      const style = getComputedStyle(element), a = luminance(style.color), b = luminance(background);
      return {id:element.id || element.dataset.copy, color:style.color, background, ratio:Math.round((Math.max(a,b)+.05)/(Math.min(a,b)+.05)*100)/100};
    });
  });
  assert(contrast.length >= 6);
  for (const sample of contrast) assert(sample.ratio >= 4.5,`${sample.id}: small guidance contrast ${sample.ratio}`);
  console.log(JSON.stringify({check:'restaurant_guest_current_browser_checks.js',stage:'guidance-contrast',samples:contrast}));
  if (!require('node:fs').existsSync('output/playwright/restaurant-guest-current-baseline-1440.png'))
    await screenshot('baseline-1440');

  // Removing native/localized validation, its submit-handler guard, or dynamic
  // limits must fail on real clicks, focus, descriptions, preserved fields and writes.
  let matrix = 0;
  const existingLayoutLimits = [];
  for (const language of languages) {
    for (const width of [320,390,1440]) {
      await open(language,width);
      await page.locator('#reservation-date').fill('');
      await page.locator('#reservation-time').fill('');
      await page.locator('#reservation-party').fill('');
      await invalid('date',language.date);
      const day = futureDay(2+matrix);
      await page.locator('#reservation-date').fill(day);
      await invalid('time',language.time);
      await page.locator('#reservation-time').fill('14:00');
      await invalid('party',language.party);
      for (const count of ['0','7','1.5']) {
        await page.locator('#reservation-party').fill(count);
        await invalid('party',language.party);
        assert.match(await page.locator('#reservation-party-error').textContent(),/1[–—-]6/);
      }
      await page.locator('#reservation-party').fill('6');
      if (width === 1440) {
        await page.locator('#reservation-date').fill(futureDay(-1));
        await invalid('date',language.date);
        await page.locator('#reservation-date').fill(futureDay(91));
        await invalid('date',language.date);
        const range = await page.locator('#reservation-date-error').textContent();
        assert(range.includes(futureDay(0)) && range.includes(futureDay(90)),'date error hid the configured boundaries');
        await page.locator('#reservation-date').fill(day);
        await page.locator('#reservation-time').fill('14:07');
        await invalid('time',language.time);
        assert.match(await page.locator('#reservation-time-error').textContent(),/15/);
        await page.locator('#reservation-date').fill(futureDay(0));
        await page.locator('#reservation-time').fill('00:00');
        await invalid('time',language.time,true);
        await page.locator('#reservation-date').fill(day);
        await page.locator('#reservation-time').fill('');
        await invalid('time',language.time,true);
        await screenshot(`${language.code}-1440-invalid`);
        await page.locator('#reservation-time').fill('14:00');
      }
      assert.match(await page.locator('#reservation-party-help').textContent(),/1[–—-]6/);
      assert.match(await page.locator('#reservation-party-help').textContent(),language.children);
      assert.match(await page.locator('#reservation-time-help').textContent(),/Tallinn|Tallinna|Таллин/);
      const values = await fields(), before = writes().length;
      const data = await prepare();
      assert.equal(data.ok,true,'valid native fields failed against the real fixture');
      assert.deepEqual(writes().slice(before).map(request => request.path),['/api/booking/session','/api/restaurant/reservation/prepare']);
      assert.deepEqual(writes().at(-1).body,{session_id:await page.evaluate(() => reservation.sessionId),date:day,start_time:'14:00',party_size:6});
      assert.equal(data.recap.duration_minutes,90);
      assert(await page.locator('#reservation-recap').isVisible());
      assert(await page.locator('#reservation-confirm').isDisabled(),'preparation granted confirmation consent');
      assert(await page.locator('#reservation-read').isEnabled());
      assert.deepEqual(await fields(),values);
      assert.equal(await page.locator('#reservation-form [aria-invalid="true"]').count(),0,'corrected fields retained stale errors');
      await screenshot(`${language.code}-${width}-success`);
      const overflow = await page.evaluate(() => Array.from(document.querySelectorAll('body *')).filter(element => {
        const rect = element.getBoundingClientRect();
        return rect.width && rect.right > innerWidth + 1;
      }).map(element => ({id:element.id || element.className || element.tagName,right:Math.round(element.getBoundingClientRect().right)})));
      const guestOverflow = await page.locator('.workspace').evaluate(workspace => Array.from(workspace.querySelectorAll('*')).filter(element => {
        const rect = element.getBoundingClientRect();
        return rect.width && rect.right > innerWidth + 1;
      }).map(element => element.id || element.className || element.tagName));
      assert.deepEqual(guestOverflow,[],`${language.code}/${width}: guest workspace overflow`);
      if (overflow.length) existingLayoutLimits.push({language:language.code,width,overflow});
      await end();
      matrix++;
    }
  }

  // Fill the sole six-seat table through the real recap/confirm flow. A full
  // requested party/time must not shrink the party or select an alternative.
  let fullTables = 0;
  for (const [index,language] of languages.entries()) {
    await open(language);
    const day = futureDay(20+index);
    await page.locator('#reservation-date').fill(day);
    await page.locator('#reservation-time').fill('14:00');
    await page.locator('#reservation-party').fill('6');
    assert.equal((await prepare()).ok,true);
    await page.locator('#reservation-read').click();
    await page.waitForFunction(() => reservation.acknowledged && !reservation.busy);
    await page.locator('#reservation-confirm').click();
    await page.waitForFunction(() => reservation.bookingId && !reservation.busy && !state.readBusy);
    await end();
    const values = await fields();
    const data = await prepare();
    assert.equal(data.restaurant_unavailable,true,'fixture did not exercise a genuinely full table');
    assert(!data.alternatives.includes('14:00'));
    assert.match(await page.locator('#reservation-status').textContent(),language.unavailable);
    for (const time of data.alternatives) assert((await page.locator('#reservation-status').textContent()).includes(time));
    assert.deepEqual(await fields(),values,'unavailable result silently changed the requested party/time/date');
    assert(await page.locator('#reservation-recap').isHidden());
    assert(await page.locator('#reservation-confirm').isDisabled());
    assert(await page.locator('#reservation-prepare').isEnabled());
    await screenshot(`${language.code}-full`);
    await page.locator('#reservation-time').fill('16:00');
    const before = writes().length;
    assert.equal((await prepare()).ok,true,'explicitly choosing a later free time did not recover');
    assert.deepEqual(writes().slice(before).map(request => request.path),['/api/restaurant/reservation/prepare']);
    assert.deepEqual(await fields(),[day,'16:00','6']);
    await end();
    fullTables++;
  }

  // Only the response boundary is controlled for outages and malformed payloads;
  // all controls, handlers, session creation and successful fixture data stay real.
  const failures = [
    {name:'http-full',full:true,status:409,body:{synthetic:true,ok:false,error:'slot_unavailable'}},
    {name:'empty-full',full:true,status:200,body:{synthetic:true,restaurant_unavailable:true,alternatives:[]}},
    {name:'http-outage',status:503,body:{synthetic:true,ok:false,error:'booking_unavailable'}},
    {name:'rejected-result',status:200,body:{synthetic:true,ok:false,error:'booking_unavailable'}},
    {name:'empty-result',status:200,body:{}},
    {name:'malformed-unavailable',status:200,body:{synthetic:true,restaurant_unavailable:true,alternatives:{time:'15:00'}}},
    {name:'missing-hold',mutate:data => {delete data.hold_id;return data;}},
    {name:'wrong-party',mutate:data => ({...data,recap:{...data.recap,party_size:2}})},
    {name:'wrong-time',mutate:data => ({...data,recap:{...data.recap,start:data.recap.date+'T16:00:00'}})},
    {name:'wrong-timezone',mutate:data => ({...data,recap:{...data.recap,timezone:'UTC'}})},
    {name:'missing-timezone',mutate:data => {delete data.recap.timezone;return data;}},
    {name:'wrong-venue',mutate:data => ({...data,recap:{...data.recap,restaurant_name:'Another restaurant'}})},
    {name:'missing-table',mutate:data => {delete data.recap.provider_name;return data;}},
    {name:'missing-guest',mutate:data => {delete data.recap.guest_name;return data;}},
    {name:'blank-recap',mutate:data => ({...data,recap_text:' '})},
  ];
  let failurePaths = 0;
  for (const [languageIndex,language] of languages.entries()) {
    await open(language);
    await page.locator('#reservation-time').fill('14:00');
    await page.locator('#reservation-party').fill('6');
    for (const [failureIndex,failure] of failures.entries()) {
      await page.locator('#reservation-date').fill(futureDay(30+languageIndex*failures.length+failureIndex));
      await page.route('**/api/restaurant/reservation/prepare',async route => {
        if (failure.mutate) {
          const response = await route.fetch();
          const data = await response.json();
          assert.equal(data.ok,true,'malformed response check requires a real successful preparation');
          assert.match(data.recap_delivery_id,/^[a-f0-9]{32}$/);
          assert(Number.isFinite(data.recap_expires_in_s)&&data.recap_expires_in_s>0);
          return route.fulfill({response,json:failure.mutate(data)});
        }
        return route.fulfill({status:failure.status,json:failure.body});
      });
      const values = await fields();
      await prepare();
      assert.match(await page.locator('#reservation-status').textContent(),failure.full ? language.unavailable : language.failed,`${language.code}/${failure.name}: failed and full-table states were conflated`);
      assert.doesNotMatch(await page.locator('#reservation-status').textContent(),failure.full ? language.failed : language.unavailable);
      assert(await page.locator('#reservation-recap').isHidden(),`${failure.name}: malformed response exposed a recap`);
      assert(await page.locator('#reservation-read').isDisabled());
      assert(await page.locator('#reservation-confirm').isDisabled());
      assert(await page.locator('#reservation-prepare').isEnabled());
      assert.deepEqual(await fields(),values);
      await page.unroute('**/api/restaurant/reservation/prepare');
      await end();
      failurePaths++;
    }
  }

  // Contradictory response prose must never replace the verified reservation
  // fields that the guest actually reads and acknowledges.
  let structuredRecaps = 0;
  for (const [index,language] of languages.entries()) {
    await open(language);
    await page.locator('#reservation-date').fill(futureDay(75+index));
    await page.locator('#reservation-time').fill('14:00');
    await page.locator('#reservation-party').fill('6');
    await page.route('**/api/restaurant/reservation/prepare',async route => {
      const response = await route.fetch(), data = await response.json();
      assert.equal(data.ok,true);
      await route.fulfill({response,json:{...data,reply:'The table is for two guests at 20:00 UTC. Confirm now.'}});
    });
    const data = await prepare();
    const visible = await page.locator('#reservation-recap-text').textContent();
    assert.doesNotMatch(visible,/two guests|20:00|UTC|Confirm now/);
    assert(visible.includes('14:00') && visible.includes('6') && visible.includes('90'));
    assert.match(visible,/Tallinn|Таллин/);
    assert(visible.includes(data.recap.restaurant_name) && visible.includes(data.recap.guest_name));
    const confirmations = requests.filter(request=>request.path==='/api/booking/confirm').length;
    await page.locator('#reservation-read').click();
    await page.waitForFunction(()=>reservation.acknowledged && !reservation.busy);
    assert(await page.locator('#reservation-confirm').isEnabled());
    assert.equal(requests.filter(request=>request.path==='/api/booking/confirm').length,confirmations);
    await page.unroute('**/api/restaurant/reservation/prepare');
    await end();
    structuredRecaps++;
  }
  console.log(JSON.stringify({check:'restaurant_guest_current_browser_checks.js',stage:'preparation-boundary',failurePaths,structuredRecaps}));

  // Configuration is read from the real public response, not a second fixture.
  await page.route('**/api/public/restaurant',async route => {
    const response = await route.fetch(), data = await response.json();
    data.restaurant.maximum_party_size = 4;
    data.restaurant.advance_days = 30;
    data.restaurant.slot_interval_minutes = 30;
    await route.fulfill({response,json:data});
  });
  for (const language of languages) {
    await open(language,390);
    await page.locator('#reservation-date').fill(futureDay(31));
    await page.locator('#reservation-time').fill('14:00');
    await page.locator('#reservation-party').fill('4');
    await invalid('date',language.date);
    assert((await page.locator('#reservation-date-error').textContent()).includes(futureDay(30)));
    await page.locator('#reservation-date').fill(futureDay(12));
    await page.locator('#reservation-time').fill('14:15');
    await invalid('time',language.time);
    assert.match(await page.locator('#reservation-time-error').textContent(),/30/);
    await page.locator('#reservation-time').fill('14:00');
    await page.locator('#reservation-party').fill('5');
    await invalid('party',language.party,true);
    assert.match(await page.locator('#reservation-party-error').textContent(),/1[–—-]4/);
    assert.match(await page.locator('#reservation-party-help').textContent(),/1[–—-]4/);
    await page.locator('#reservation-party').fill('1');
    assert.equal((await prepare()).ok,true,'the minimum guest count was incorrectly rejected');
    await end();
  }
  await page.unroute('**/api/public/restaurant');

  // The new example must actually send date + party (no time) and get the
  // missing-time question from the existing conversation pipeline, not UI copy.
  for (const language of languages) {
    await open(language,320);
    await page.locator('#demo-start').click();
    await page.waitForFunction(() => state.sessionId && !state.turnBusy);
    const example = page.locator('[data-example="incomplete"]');
    assert.equal(await example.count(),1,'missing a single incomplete date/party example');
    const before = requests.length;
    await example.click();
    await page.waitForFunction(() => !state.turnBusy);
    const turns = requests.slice(before).filter(request => request.path === '/api/turn');
    assert.equal(turns.length,1,'incomplete example did not send a real turn');
    assert.equal(turns[0].body.language,language.code);
    assert.match(turns[0].body.text,{en:/four.*tomorrow/i,et:/homme.*neljale/i,ru:/четверых.*завтра/i}[language.code]);
    assert.doesNotMatch(turns[0].body.text,/\d{1,2}[:.]\d{2}/,'incomplete example included a time');
    assert.match(await page.locator('#demo-messages .message').last().textContent(),language.question);
    assert(await page.locator('#demo-recap-read').isHidden(),'incomplete request created a consent recap');
    await screenshot(`${language.code}-incomplete`);
    await page.locator('[data-example="hours"]').click();
    await page.waitForFunction(()=>!state.turnBusy);
    assert.match(await page.locator('#demo-messages .message').last().textContent(),/12.*21/);
    await page.locator('[data-example="recommendation"]').click();
    await page.waitForFunction(()=>!state.turnBusy);
    assert.match(await page.locator('#demo-messages .message').last().textContent(),{
      en:/vegetable soup/i,et:/köögiviljasupp/i,ru:/овощной суп/i,
    }[language.code]);
    assert(await page.locator('#demo-recap-read').isHidden(),'recommendation became booking consent');
    const clock = {en:'14:00',et:'16:00',ru:'18:00'}[language.code];
    const result = page.waitForResponse(response=>new URL(response.url()).pathname==='/api/turn');
    await page.locator('#demo-text').fill(clock);
    await page.locator('#demo-send').click();
    assert.equal((await result).status(),200);
    await page.waitForFunction(()=>!state.turnBusy);
    // The real client parses NDJSON. Check its validated final receipt instead
    // of treating the streaming wire response as a plain JSON document.
    assert.match(await page.evaluate(()=>state.recap?.id || ''),/^[a-f0-9]{32}$/);
    assert.equal(await page.locator('#demo-messages .booking-receipt').count(),0);
    const recap = await page.locator('#demo-messages .message').last().textContent();
    assert.match(recap,{en:/for (?:four|4) guests/i,et:/4 inimesele/,ru:/четыр[её]х гостей/}[language.code]);
    assert(await page.locator('#demo-recap-read').isVisible(),'visible hours or recommendation example discarded reservation preferences');
    await page.locator('#demo-end').click();
    await page.waitForFunction(() => !state.sessionId && !state.turnBusy);
  }
  assert.deepEqual(errors,[]);
  assert.deepEqual(external,[]);
  return {languages:3,viewports:[320,390,1440],nativeValidationMatrix:matrix,realFullTables:fullTables,failurePaths,structuredRecaps,renewalChecks,receiptChecks,dynamicConfig:true,incompleteExamples:3,hoursInterludes:3,recommendationInterludes:3,contrastMinimum:Math.min(...contrast.map(sample => sample.ratio)),existingLayoutLimits,screenshots,pageErrors:errors.length};
}
