async page => {
  // Real HTTP, SQLite, native MP3 playout and browser mic capture. Speech is synthetic.
  const assert = require('node:assert/strict'), errors = [], requests = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('request', request => {
    if (request.method() === 'POST' && new URL(request.url()).pathname === '/api/turn')
      requests.push(request.postDataJSON());
  });
  const configure = body => page.request.post('http://127.0.0.1:8777/test/confirmation/configure', {
    headers: {Authorization: 'Bearer restaurant-fixture-operator'}, data: body,
  });
  const release = () => page.request.post('http://127.0.0.1:8777/test/confirmation/release', {
    headers: {Authorization: 'Bearer restaurant-fixture-operator'},
  });
  const media = () => page.evaluate(() => {
    const audio = document.getElementById('demo-audio');
    return {ended: audio.ended, duration: audio.duration, time: audio.currentTime,
      played: Array.from({length: audio.played.length}, (_, i) => [audio.played.start(i), audio.played.end(i)]),
      complete: state.playback?.complete, appended: state.playback?.appended,
      interrupted: state.playback?.interrupted,
      receipt: state.recapDeliveryId, trace: window.confirmationMediaTrace};
  });
  const send = async text => {
    await page.locator('#demo-text').fill(text);
    await page.locator('#demo-send').click();
    await page.waitForFunction(() => !state.turnBusy);
  };
  const end = async () => {
    await configure({gated: false});
    await page.locator('#demo-end').click();
    await page.waitForFunction(() => !state.sessionId && !state.turnBusy);
  };
  const start = async language => {
    await page.locator('.language-option').filter({has: page.locator('input[value="' + language + '"]')}).click();
    await page.locator('#demo-start').click();
    await page.waitForFunction(() => state.sessionId && !state.turnBusy);
    await page.evaluate(() => {confirmationMediaTrace.length = 0;});
  };
  const speak = async transcript => {
    await configure({gated: false, transcript});
    await page.evaluate(async () => {
      const context = new AudioContext(), source = context.createOscillator(), sink = context.createMediaStreamDestination(), gain = context.createGain();
      gain.gain.value = .08;
      source.connect(gain); gain.connect(sink); source.start(); await context.resume();
      window.confirmationCapture = {context, source, stream: sink.stream};
      navigator.mediaDevices.getUserMedia = async () => sink.stream;
    });
    await page.locator('#demo-mic').click();
    await page.waitForFunction(() => state.mic?.frames >= 8192);
    await page.locator('#demo-mic').click();
    await page.waitForFunction(() => !state.turnBusy && !state.micStarting && !state.mic);
    await page.evaluate(() => {confirmationCapture.source.stop(); return confirmationCapture.context.close();});
    assert(requests.at(-1).audio_b64, 'voice input was not sent');
    const audio = Buffer.from(requests.at(-1).audio_b64, 'base64');
    assert.equal(audio.toString('ascii', 0, 4), 'RIFF');
    assert.equal(audio.readUInt32LE(24), 16000);
  };
  const assertSummary = async (confirmed, time, party) => {
    const summary = await page.locator('#demo-messages .message').last().textContent();
    assert(summary.includes(confirmed) && summary.includes(time) && summary.includes(party) &&
      summary.includes('Meretuule') && summary.includes('Esimene Külaline') && !summary.includes('?'), summary);
    assert.equal(await page.locator('.booking-receipt[data-action="confirmed"]').count(), 1);
  };
  await page.goto('http://127.0.0.1:8777/dashboard', {waitUntil: 'networkidle'});
  await page.locator('#operator-token').fill('restaurant-fixture-operator');
  await page.locator('#connect').click();
  await page.waitForFunction(() => state.connected && state.voiceCatalog);
  await page.evaluate(() => {
    window.confirmationMediaTrace = [];
    const audio = document.getElementById('demo-audio');
    for (const type of ['playing', 'waiting', 'stalled', 'ended', 'pause'])
      audio.addEventListener(type, () => confirmationMediaTrace.push({type, time: audio.currentTime, busy: state.turnBusy}));
  });
  await start('en');
  await configure({gated: true});
  await page.locator('#demo-text').fill('A table for three tomorrow at 7 pm');
  await page.locator('#demo-send').click();
  await page.waitForFunction(() => state.turnBusy && confirmationMediaTrace.some(event => event.type === 'waiting' && event.time > .1));
  assert.equal(await page.evaluate(() => state.recapDeliveryId), null, 'partial audio armed consent');
  await release();
  await page.waitForFunction(() => !state.turnBusy && document.getElementById('demo-audio').ended);
  const playout = await media();
  assert(playout.receipt, 'Fully played recap lost its receipt: ' + JSON.stringify(playout));
  await speak("That's very good.");
  assert(requests.at(-1).recap_delivery_id, 'natural agreement omitted the delivered recap');
  await assertSummary('confirmed', '7:00 PM', '3 guests');
  await end();
  for (const scenario of [
    {language: 'et', request: 'Soovin homme lauda kolmele kell 18.00', agreement: 'See kõlab väga hästi!', confirmed: 'kinnitatud', time: '18:00', party: '3 inimesele'},
    {language: 'ru', request: 'Столик на троих завтра в 17:00', agreement: 'Давайте так и сделаем!', confirmed: 'подтверждена', time: '17:00', party: 'трёх гостей'},
  ]) {
    await start(scenario.language);
    await send(scenario.request);
    await page.waitForFunction(() => document.getElementById('demo-audio').ended);
    assert(await page.evaluate(() => state.recapDeliveryId), 'complete native audio did not acknowledge recap');
    await speak(scenario.agreement);
    assert(requests.at(-1).recap_delivery_id, 'starting microphone discarded completed delivery');
    await assertSummary(scenario.confirmed, scenario.time, scenario.party);
    await end();
  }
  // Typed responses acknowledge the complete displayed recap without a second button.
  await page.evaluate(() => {
    window.confirmationOriginalPlay = HTMLMediaElement.prototype.play;
    HTMLMediaElement.prototype.play = function () {return Promise.reject(new Error('fixture autoplay blocked'));};
  });
  for (const scenario of [
    {language: 'en', request: 'A table for three tomorrow at 2 pm', agreement: 'thats perfect', confirmed: 'confirmed', time: '2:00 PM', party: '3 guests'},
    {language: 'et', request: 'Soovin homme lauda kolmele kell 15.00', agreement: 'See aeg sobib, paneme kirja!', confirmed: 'kinnitatud', time: '15:00', party: '3 inimesele'},
    {language: 'ru', request: 'Столик на троих завтра в 16:00', agreement: 'Это идеально!', confirmed: 'подтверждена', time: '16:00', party: 'трёх гостей'},
  ]) {
    await start(scenario.language);
    await send(scenario.request);
    assert.equal(await page.evaluate(() => state.recapDeliveryId), null, 'blocked audio counted as played');
    assert(await page.locator('#demo-recap-read').isVisible());
    await send(scenario.agreement);
    assert(requests.at(-1).recap_delivery_id, 'typed answer to a visible recap required a separate read click');
    await assertSummary(scenario.confirmed, scenario.time, scenario.party);
    await send(scenario.agreement);
    assert.equal(await page.locator('.booking-receipt[data-action="confirmed"]').count(), 1, 'repeated agreement duplicated a booking');
    await end();
  }
  await page.evaluate(() => {HTMLMediaElement.prototype.play = confirmationOriginalPlay;});
  // Actually interrupted voice cannot commit; it must keep all requested details.
  await start('en');
  await send('A table for three tomorrow at noon');
  assert(await page.evaluate(() => state.recap?.id), 'interruption test did not receive an available table');
  const proposal = await page.locator('#demo-messages .message').last().textContent();
  await page.waitForFunction(() => document.getElementById('demo-audio').currentTime > .2);
  await page.locator('#demo-audio').evaluate(async audio => {audio.pause(); await audio.play();});
  await page.waitForFunction(() => document.getElementById('demo-audio').ended);
  assert.equal(await page.evaluate(() => state.recapDeliveryId), null, 'user pause was mistaken for full uninterrupted delivery');
  await speak('thats perfect');
  assert(!requests.at(-1).recap_delivery_id);
  assert.equal(await page.locator('.booking-receipt').count(), 0, 'unacknowledged proposal committed');
  assert.equal(await page.locator('#demo-messages .message').last().textContent(), proposal, 'undelivered agreement lost the date, time or guest count');
  await page.waitForFunction(() => document.getElementById('demo-audio').ended);
  await speak('thats perfect');
  await assertSummary('confirmed', '12:00 PM', '3 guests');
  await end();
  assert.deepEqual(errors, []);
  return {result: 'passed', languages: ['et', 'en', 'ru'], microphone: true,
    typedWithoutReadButton: true, naturalConfirmationAfterBuffering: true, interruptedProposalRetained: true, errors};
}
