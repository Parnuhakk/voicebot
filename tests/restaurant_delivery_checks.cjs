// Local Chromium + the published restaurant app and isolated SQLite fixture only.
// node tests/restaurant_delivery_checks.cjs /path/to/playwright /path/to/python [case filter]
const assert = require('node:assert/strict');
const {spawn} = require('node:child_process');
const net = require('node:net');
const path = require('node:path');
const {chromium} = require(process.argv[2] || 'playwright');
const root = path.resolve(__dirname, '..');
const cases = [], test = (name, run) => cases.push({name, run});
const receipt = 'a'.repeat(32), sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const posts = (f, endpoint) => f.requests.filter(r => r.path === endpoint && r.method === 'POST');
async function start(page) {
  await page.locator('#demo-start').click();
  await page.waitForFunction(() => state.sessionId && !state.turnBusy);
}
async function send(page) {
  await page.locator('#demo-text').fill('A table for four tomorrow at 14:00');
  await page.locator('#demo-send').click();
  await page.waitForFunction(() => !state.turnBusy);
}
async function prepare(page) {
  await page.locator('#reservation-time').fill('14:00');
  await page.locator('#reservation-party').fill('4');
  await page.locator('#reservation-prepare').click();
  await page.waitForFunction(() => !reservation.busy);
}
async function read(page) {
  await page.locator('#reservation-read').click();
  await page.waitForFunction(() => !reservation.busy);
}
async function confirm(page) {
  await page.locator('#reservation-confirm').click();
  await page.waitForFunction(() => !reservation.busy);
}
async function capture(page) {
  await page.evaluate(async () => {
    const context = new AudioContext(), source = context.createOscillator(), sink = context.createMediaStreamDestination(), gain = context.createGain();
    gain.gain.value = .08; source.connect(gain); gain.connect(sink); source.start(); await context.resume();
    window.fixtureCapture = {context, source, stream:sink.stream};
    navigator.mediaDevices.getUserMedia = async () => sink.stream;
  });
  await page.locator('#demo-mic').click();
  await page.waitForFunction(() => state.mic?.frames >= 8192);
}

for (const input of ['form', 'example']) test(`${input} text retires earlier capture before a new recap`, async (page, f) => {
  await start(page);
  if (input === 'form') await page.locator('#demo-text').fill('A table for four tomorrow at 14:00');
  await capture(page);
  if (input === 'form') {
    assert(await page.locator('#demo-text').isDisabled(), 'active capture did not lock ordinary text input');
    await page.locator('#demo-form').evaluate(form => form.requestSubmit());
    await page.waitForFunction(() => !state.turnBusy);
  }
  else {
    const example = page.locator('[data-example=reservation]');
    assert(await example.isDisabled(), 'active capture did not lock ordinary example input');
    await example.evaluate(button => button.dispatchEvent(new MouseEvent('click', {bubbles:true})));
    await page.waitForFunction(() => !state.turnBusy);
  }
  await page.locator('#demo-recap-read').click();
  assert.equal(await page.evaluate(() => state.recapDeliveryId), receipt);
  await page.evaluate(async () => {if (state.mic) await toggleMic();});
  const leaked = posts(f, '/api/turn').filter(r => r.body.audio_b64 && r.body.recap_delivery_id === receipt);
  assert.equal(leaked.length, 0, 'audio begun before the text recap inherited its new delivery receipt');
  assert.equal(posts(f, '/api/turn').length, 1, 'retired capture uploaded another input');
  assert(await page.evaluate(() => !state.mic && fixtureCapture.stream.getTracks().every(track => track.readyState === 'ended')), 'text input left the earlier microphone live');
});

test('a fresh capture can carry only a previously delivered recap', async (page, f) => {
  await start(page); await send(page); await page.locator('#demo-recap-read').click();
  await capture(page); await page.locator('#demo-mic').click();
  await page.waitForFunction(() => !state.micStarting && !state.turnBusy);
  const audio = posts(f, '/api/turn').at(-1).body, wav = Buffer.from(audio.audio_b64, 'base64');
  assert.equal(audio.recap_delivery_id, receipt); assert.equal(wav.toString('ascii', 0, 4), 'RIFF');
  assert.equal(wav.readUInt32LE(24), 16000); assert.equal(wav.readUInt16LE(22), 1);
  assert.equal(posts(f, '/api/turn').length, 2);
});

test('audio without a current capture identity cannot claim a delivered recap', async (page, f) => {
  await start(page); await send(page); await page.locator('#demo-recap-read').click();
  await page.evaluate(() => sendTurn({audio_b64:'UklGRg=='}, {generation:state.generation, session:state.sessionId, micEpoch:state.micEpoch - 1}));
  assert.equal(posts(f, '/api/turn').length, 1, 'stale or unowned capture attached the delivered receipt');
  assert.equal(await page.evaluate(() => state.recapDeliveryId), receipt, 'rejected capture consumed a valid receipt');
});

test('finished turns release controls while independent reads stall', async (page, f) => {
  await start(page); f.stallReads = true;
  await page.locator('#demo-text').fill('A fictional question'); await page.locator('#demo-send').click();
  await page.waitForFunction(() => state.recap?.id); await sleep(100);
  assert(await page.locator('#demo-send').isEnabled(), 'finished turn waited for a stalled readback');
  assert(await page.locator('#demo-mic').isEnabled()); assert(await page.locator('#demo-end').isEnabled());
  assert.equal(posts(f, '/api/turn').length, 1); assert(f.stalled.includes('/api/bookings')); assert(f.stalled.includes('/api/call-history'));
});

for (const cancel of [false, true]) test(`${cancel ? 'cancellation' : 'confirmation'} releases controls while independent reads stall`, async (page, f) => {
  await prepare(page); await read(page);
  if (cancel) await confirm(page);
  f.stallReads = true; await page.locator(cancel ? '#reservation-cancel' : '#reservation-confirm').click();
  await page.waitForFunction(cancel ? () => !reservation.bookingId : () => reservation.bookingId); await sleep(100);
  assert.equal(await page.evaluate(() => reservation.busy), false, 'completed reservation write waited for a stalled readback');
  assert(await page.locator(cancel ? '#reservation-end' : '#reservation-cancel').isEnabled());
  assert.equal(posts(f, '/api/booking/confirm').length, 1); assert.equal(posts(f, '/api/booking/cancel').length, cancel ? 1 : 0);
});

test('a failed write stays uncertain without automatic retry', async (page, f) => {
  await prepare(page); await read(page); f.failWrite = true; await confirm(page); await sleep(100);
  assert.equal(await page.evaluate(() => reservation.uncertain), true);
  for (const id of ['reservation-prepare', 'reservation-confirm', 'reservation-cancel']) assert(await page.locator('#' + id).isDisabled());
  assert.equal(posts(f, '/api/booking/confirm').length, 1);
});

test('direct reading forwards the exact one-use receipt without confirming', async (page, f) => {
  await prepare(page);
  assert.equal(posts(f, '/api/booking/recap').length, 0); assert(await page.locator('#reservation-confirm').isDisabled());
  await read(page);
  assert.deepEqual(posts(f, '/api/booking/recap')[0].body, {session_id:'direct-fixture', hold_id:'hold-fixture', recap_delivery_id:receipt});
  assert.equal(posts(f, '/api/booking/confirm').length, 0);
  assert(await page.locator('#reservation-confirm').isEnabled());
  await page.evaluate(() => readReservation());
  assert.equal(posts(f, '/api/booking/recap').length, 1, 'direct reading replayed its consumed receipt');
});

for (const invalid of ['missing receipt', 'malformed receipt', 'non-string receipt', 'changed text', 'denied acknowledgement', 'foreign hold']) test(`direct recap rejects ${invalid}`, async (page, f) => {
  if (invalid === 'missing receipt') f.receipt = null;
  if (invalid === 'malformed receipt') f.receipt = 'invalid';
  if (invalid === 'non-string receipt') f.receipt = [receipt];
  if (invalid === 'denied acknowledgement') f.acknowledged = false;
  if (invalid === 'foreign hold') f.ackHold = 'foreign-hold';
  await prepare(page);
  if (invalid === 'changed text') await page.locator('#reservation-recap-text').evaluate(node => {node.textContent = 'Changed proposal';});
  await page.evaluate(() => readReservation());
  assert(await page.locator('#reservation-confirm').isDisabled(), 'unscoped recap enabled separate confirmation');
  if (['missing receipt', 'malformed receipt', 'non-string receipt', 'changed text'].includes(invalid)) assert.equal(posts(f, '/api/booking/recap').length, 0, 'unscoped recap sent an acknowledgement');
  assert.equal(posts(f, '/api/booking/confirm').length, 0);
});

test('ending or disconnecting discards direct pending receipts', async (page) => {
  await prepare(page); await page.locator('#reservation-end').click();
  await page.waitForFunction(() => !reservation.busy);
  assert.equal(await page.evaluate(() => reservation.recapDeliveryId), null, 'end retained a direct pending receipt');
  await prepare(page); await page.locator('#logout').click();
  assert.equal(await page.evaluate(() => reservation.recapDeliveryId), null, 'disconnect retained a direct pending receipt');
  assert(await page.locator('#reservation-recap').isHidden());
});

test('late direct reading cannot authorize a replacement proposal', async (page, f) => {
  await prepare(page); f.stallRecap = true; await page.locator('#reservation-read').click();
  for (let i = 0; i < 100 && !f.releaseRecap; i++) await sleep(10);
  assert(f.releaseRecap); f.stallRecap = false; f.receipt = 'b'.repeat(32);
  await page.evaluate(() => {clearReservation(); controls();}); await prepare(page);
  f.releaseRecap(); await sleep(75);
  assert.equal(await page.evaluate(() => reservation.acknowledged), false, 'old reading acknowledged a replacement with the same hold identifier');
  assert(await page.locator('#reservation-confirm').isDisabled());
  assert.equal(await page.evaluate(() => reservation.recapDeliveryId), f.receipt);
});

test('read deadlines do not retry or lock an already completed turn', async (page, f) => {
  await start(page);
  await page.evaluate(() => {const native = setTimeout; window.setTimeout = (fn, delay, ...args) => native(fn, delay === 45000 || delay === 30000 ? 250 : delay, ...args);});
  f.stallReads = true;
  await page.locator('#demo-text').fill('A fictional question'); await page.locator('#demo-send').click();
  await page.waitForFunction(() => state.recap?.id); await sleep(75);
  assert(await page.locator('#demo-send').isEnabled(), 'read deadline also became a turn deadline');
  await page.waitForFunction(() => !state.readBusy);
  assert.equal(posts(f, '/api/turn').length, 1); assert(await page.locator('#demo-send').isEnabled());
});

test('a late history read cannot overwrite a newer readback', async (page, f) => {
  f.gateHistory = true; await page.evaluate(() => {void loadHistory();});
  await page.waitForFunction(() => document.getElementById('call-history') !== null);
  for (let i = 0; i < 100 && !f.releaseHistory; i++) await sleep(10);
  assert(f.releaseHistory); f.gateHistory = false; f.historyTurns = 2; await page.evaluate(() => loadHistory());
  f.releaseHistory(); await sleep(75);
  assert((await page.locator('#call-history').textContent()).includes('2 messages'), 'late history response overwrote the newer readback');
});

for (const statusCode of [200, 503]) test(`private ${statusCode} JSON is retired after body-generation changes`, async (page, f) => {
  f.catalogueStatus = statusCode;
  const result = await page.evaluate(async () => {
    const original = window.fetch;
    window.fetch = async (...args) => {
      const response = await original(...args);
      if (args[0] === '/api/catalogue') {
        const json = response.json.bind(response);
        response.json = async () => {const data = await json(); logout(); return data;};
      }
      return response;
    };
    return api('/api/catalogue').then(() => 'accepted late private body', error => error.name);
  });
  assert.equal(result, 'AbortError', 'API accepted or reported a body from an already-ended operator generation');
  assert.equal(await page.locator('#demo-messages .message').count(), 0);
});

(async () => {
  const probe = net.createServer(); await new Promise((resolve, reject) => {probe.once('error', reject); probe.listen(0, '127.0.0.1', resolve);});
  const port = probe.address().port; await new Promise(resolve => probe.close(resolve));
  const origin = `http://127.0.0.1:${port}`;
  const server = spawn(process.argv[3] || 'python3', ['-m', 'uvicorn', 'tests.restaurant_browser_fixture:create_app', '--factory', '--host', '127.0.0.1', '--port', String(port), '--no-access-log'], {
    cwd:root, env:{PATH:'/usr/local/bin:/usr/bin:/bin', HOME:'/tmp/opencode', TMPDIR:'/tmp/opencode', PYTHONDONTWRITEBYTECODE:'1'}, stdio:['ignore', 'ignore', 'pipe'],
  });
  let diagnostics = '', spawnError = null, browser, failed = 0, passed = 0;
  server.on('error', error => {spawnError = error;}); server.stderr.on('data', chunk => {diagnostics = (diagnostics + chunk).slice(-4000);});
  try {
    let ready = false;
    for (let i = 0; i < 100; i++) {
      try {if ((await fetch(origin + '/api/status', {signal:AbortSignal.timeout(1000)})).ok) {ready = true; break;}} catch (_) {}
      if (spawnError || server.exitCode !== null) break;
      await sleep(100);
    }
    if (!ready) throw new Error('local restaurant fixture failed: ' + (spawnError?.message || diagnostics));
    browser = await chromium.launch({headless:true});
    for (const {name, run} of cases.filter(item => !process.argv[4] || item.name.includes(process.argv[4]))) {
      const context = await browser.newContext({serviceWorkers:'block'}), external = [], errors = [];
      const f = {requests:[], stalled:[], reads:[], receipt, acknowledged:true, historyTurns:1};
      await context.route('**/*', route => {
        const url = new URL(route.request().url());
        if (url.origin !== origin && url.protocol !== 'blob:') {external.push(url.origin); return route.abort('blockedbyclient');}
        return route.continue();
      });
      const page = await context.newPage(); page.setDefaultTimeout(5000); page.on('pageerror', error => errors.push(error.message));
      await page.route('**/api/**', async route => {
        const request = route.request(), endpoint = new URL(request.url()).pathname;
        const body = request.postData() ? request.postDataJSON() : null;
        f.requests.push({path:endpoint, method:request.method(), body});
        const json = (data, status = 200) => route.fulfill({status, contentType:'application/json', body:JSON.stringify(data)}).catch(() => {});
        if (endpoint === '/api/bookings' || endpoint === '/api/call-history') {
          const data = endpoint === '/api/bookings' ? {items:[], has_more:false} : {items:[{channel:'browser', language:'en', turns:f.historyTurns, outcome:'completed'}]};
          if (f.stallReads) {f.stalled.push(endpoint); await new Promise(resolve => f.reads.push(resolve));}
          if (endpoint === '/api/call-history' && f.gateHistory) await new Promise(resolve => {f.releaseHistory = resolve;});
          return json(data);
        }
        if (endpoint === '/api/catalogue' && f.catalogueStatus) return json({detail:'fixture failure'}, f.catalogueStatus);
        if (endpoint === '/api/turn') return json({reply:'Fictional restaurant recap: four guests, 90 minutes.', language:'en', text_heard:body.text || 'Fictional audio', outcome:'tts_failed', tts_failed:true, audio_b64:'', recap_delivery_id:posts(f, endpoint).length === 1 ? receipt : null, recap_expires_in_s:60, booking_changes:[]});
        if (endpoint === '/api/booking/session') return json({session_id:'direct-fixture'});
        if (endpoint === '/api/restaurant/reservation/prepare') return json({ok:true, hold_id:'hold-fixture', recap_delivery_id:f.receipt, recap:{date:body.date}, recap_text:'Fictional table for four guests at 14:00; 90 minutes.'});
        if (endpoint === '/api/booking/recap') {
          if (f.stallRecap) await new Promise(resolve => {f.releaseRecap = resolve;});
          return json({acknowledged:f.acknowledged, hold_id:f.ackHold || body.hold_id});
        }
        if (endpoint === '/api/booking/confirm' || endpoint === '/api/booking/cancel') return f.failWrite ? json({detail:'write_outcome_unknown'}, 503) : json({ok:true, booking:{id:'reservation-fixture'}});
        if (endpoint === '/api/demo/session/direct-fixture') return json({ok:true});
        return route.continue();
      });
      try {
        await page.goto(origin, {waitUntil:'networkidle'});
        assert.equal(await page.locator('#menu-list li').count(), 3, 'published public menu did not load before authentication');
        assert.equal(await page.locator('#reservation-duration').textContent(), '90 min');
        await page.locator('.language-option').filter({has:page.locator('input[value="en"]')}).click();
        await page.locator('#operator-token').fill('restaurant-fixture-operator'); await page.locator('#connect').click();
        await page.waitForFunction(() => state.connected && !state.readBusy && state.voiceCatalog);
        await run(page, f); assert.deepEqual(errors, []); assert.deepEqual(external, []); passed++; console.log('PASS ' + name);
      } catch (error) {failed++; console.error('FAIL ' + name + ': ' + error.message);}
      finally {
        f.reads.forEach(resolve => resolve()); f.releaseHistory?.(); f.releaseRecap?.();
        await page.evaluate(async () => {if (window.fixtureCapture) {fixtureCapture.source.stop(); await fixtureCapture.context.close();}}).catch(() => {});
        await context.close();
      }
    }
    console.log(JSON.stringify({passed, failed, browser:browser.version(), localRestaurantFixture:true, syntheticAudio:true, externalRequests:0}));
    if (failed) process.exitCode = 1;
  } finally {
    if (browser) await browser.close();
    if (server.pid && server.exitCode === null && server.signalCode === null) {server.kill('SIGTERM'); await new Promise(resolve => server.once('exit', resolve));}
  }
})().catch(error => {console.error(error.message); process.exitCode = 1;});
