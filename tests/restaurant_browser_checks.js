async page => {
  const assert = require('node:assert/strict');
  const errors = [], requests = [];
  const waitBooking=async(id,label)=>page.waitForFunction(({id,label})=>!state.readBusy && Array.from(document.querySelectorAll('#bookings .booking-row')).some(row=>row.dataset.bookingId===id && row.textContent.includes(label)),{id:String(id),label});
  page.on('pageerror', error => errors.push(error.message));
  page.on('request', request => {
    if (request.method() === 'POST' && request.url().includes('/api/')) requests.push({path:new URL(request.url()).pathname,body:request.postDataJSON()});
  });
  await page.setViewportSize({width:1440,height:1000});
  await page.goto('http://127.0.0.1:8766/dashboard', {waitUntil:'networkidle'});
  const familyInformation = await (await page.request.get('http://127.0.0.1:8766/api/public/restaurant')).json();
  assert.deepEqual(familyInformation.restaurant.family_facilities, {drawing:true,toys:true,play_corner:true,children_menu:true});
  assert.equal(familyInformation.customer_questions_version, 'reviewed-service-v1');
  assert.equal(await page.locator('a[href]').evaluateAll(links=>links.some(link=>new URL(link.href).hostname==='meretuule.arleserver.cfd')),false,'Robot navigation still opens the removed demo site');
  const chooseLanguage = async code => page.locator('.language-option').filter({
    has: page.locator('input[value="' + code + '"]'),
  }).click();
  const assertReceipt = async (container, time, identifier, action = 'confirmed') => {
    const receipt = container.locator('.booking-receipt').last();
    assert(await receipt.isVisible(), 'saved reservation details were not shown immediately');
    assert.equal(await receipt.getAttribute('data-action'), action);
    const details = await receipt.locator('dd').allTextContents();
    assert.equal(details[0], await page.evaluate(()=>formatBookingDate(tallinnDay(1))));
    assert.equal(details[1], time);
    assert.equal(details[2], '4');
    assert.equal(details[3], 'Table 3');
    assert.equal(details[4], '#' + identifier);
    assert.equal(await receipt.locator('dt').count(), 5);
  };
  assert.equal(await page.getByRole('radio').count(), 3);
  assert(await page.getByRole('radio', {name:'Eesti', exact:true}).isChecked());
  for (const [code, name] of [['en','English'], ['ru','Русский'], ['et','Eesti']]) {
    assert(await page.getByRole('radio', {name, exact:true}).isVisible());
    assert(await page.getByRole('radio', {name, exact:true}).isEnabled());
    await chooseLanguage(code);
    assert.equal(await page.locator('html').getAttribute('lang'), code);
    const guidance = {
      et: ['Lehe ja tervituse keel', 'Esimene sõnum määrab keele', 'palu abilist'],
      en: ['Page and greeting language', 'Your first message sets the language', 'Ask to switch'],
      ru: ['Язык страницы и приветствия', 'первое сообщение', 'Для смены попросите'],
    }[code];
    assert.equal(await page.locator('#demo-language legend').textContent(), guidance[0]);
    for (const phrase of guidance.slice(1)) assert((await page.locator('#language-help').textContent()).includes(phrase));
    assert.equal(await page.evaluate(()=>state.demoLanguage), code);
    assert.equal(await page.evaluate(()=>state.connected), false);
  }
  // Native radio keyboard navigation changes the same authoritative selection.
  await page.getByRole('radio', {name:'Eesti', exact:true}).focus();
  await page.keyboard.press('ArrowRight');
  assert(await page.getByRole('radio', {name:'English', exact:true}).isChecked());
  assert.equal(await page.locator('html').getAttribute('lang'), 'en');
  await page.keyboard.press('ArrowRight');
  assert(await page.getByRole('radio', {name:'Русский', exact:true}).isChecked());
  assert.equal(await page.locator('html').getAttribute('lang'), 'ru');
  await chooseLanguage('et');
  assert.equal(requests.length, 0, 'choosing a language called a provider before sign-in');
  assert.equal(await page.locator('aside.sidebar').count(),1,'restaurant adaptation removed the dashboard sidebar');
  assert.equal(await page.locator('.sidebar nav a').count(),5,'dashboard navigation is missing');
  assert(await page.locator('.sidebar nav a[href="/booking-calendar.html"]').isVisible(),'calendar navigation is missing');
  for (const href of await page.locator('.sidebar nav a').evaluateAll(links=>links.map(link=>link.getAttribute('href')))) {
    if (!href.startsWith('#')) continue;
    assert(await page.locator(href).isVisible(),`navigation target ${href} is missing`);
  }
  const sidebarBox=await page.locator('.sidebar').boundingBox();
  const mainBox=await page.locator('main').boundingBox();
  assert(sidebarBox.x+sidebarBox.width<=mainBox.x,'desktop sidebar overlaps the workspace');
  assert.equal(await page.locator('.sidebar').evaluate(element=>getComputedStyle(element).position),'fixed');
  assert(await page.locator('.topbar').isVisible(),'dashboard topbar is missing');
  assert(await page.locator('#demo-start').isDisabled());
  assert(await page.locator('#reservation-prepare').isDisabled());
  assert.equal(await page.locator('#menu-list li').count(),3);
  const languages = [
    {code:'en', greeting:'Hello!', menu:'What is on the menu?', soup:'Vegetable soup', confirmed:'confirmed', cancelled:'cancelled'},
    {code:'et', greeting:'Tere!', menu:'Milline on menüü?', soup:'Köögiviljasupp', confirmed:'kinnitatud', cancelled:'tühistatud'},
    {code:'ru', greeting:'Здравствуйте!', menu:'Что есть в меню?', soup:'Овощной суп', confirmed:'подтверждено', cancelled:'отменено'},
  ];
  let releaseCatalog;
  const catalogGate = new Promise(resolve=>{releaseCatalog=resolve;});
  await page.route('**/api/demo/voices', async route=>{
    await catalogGate;
    await route.continue();
  });
  await page.locator('#operator-token').fill('restaurant-fixture-operator');
  await page.locator('#connect').click();
  await page.waitForFunction(()=>state.connected && state.voicesLoading);
  assert(await page.locator('#demo-start').isDisabled());
  assert(await page.locator('#demo-mic').isDisabled());
  assert(await page.locator('#demo-voice-preview').isDisabled());
  releaseCatalog();
  await page.waitForFunction(()=>state.connected && !state.readBusy);
  let gatedBookings=false, releaseBookings;
  const bookingGate=new Promise(resolve=>{releaseBookings=resolve;});
  await page.route('**/api/bookings?**',async route=>{if(gatedBookings)await bookingGate;await route.continue();});
  await page.waitForFunction(()=>state.voiceCatalog);
  assert.equal(await page.locator('#demo-voice option:not(:disabled)').count(), 7);
  assert.equal(await page.locator('#demo-voice').inputValue(), 'azure-conversational');
  await page.unroute('**/api/demo/voices');
  for (const code of ['en', 'ru', 'et']) {
    await chooseLanguage(code);
    assert.equal(await page.locator('#demo-voice').inputValue(), 'azure-conversational');
  }
  await chooseLanguage('et');
  for (const profile of ['azure-male', 'azure-calm', 'azure-male-calm', 'azure-male-warm']) {
    await page.locator('#demo-voice').selectOption(profile);
    await page.locator('#demo-voice-preview').click();
    await page.waitForFunction(()=>!state.previewBusy && !document.getElementById('demo-audio').hidden);
    assert.equal(requests.at(-1).path, '/api/demo/voices/preview');
    assert.equal(requests.at(-1).body.voice, profile);
    assert.equal(await page.evaluate(()=>state.sessionId), null, 'audition created a conversation');
    await page.waitForFunction(()=>document.getElementById('demo-audio').duration > 0);
    assert((await page.locator('#demo-voice-result').textContent()).includes(profile==='azure-calm' ? 'Anu' : 'Kert'));
  }
  assert(await page.locator('#demo-voice option[value="azure-brian"]').isDisabled());
  assert(await page.locator('#demo-voice option[value="azure-ryan"]').isDisabled());
  await chooseLanguage('en');
  assert.equal(await page.locator('#demo-voice option:not(:disabled)').count(), 9);
  for (const code of ['en', 'ru', 'et']) {
    await chooseLanguage(code);
    for (const [profile, names] of [
      ['azure-conversational', {et:'Nova Turbo',en:'Emma',ru:'Эмма'}],
      ['azure-conversational-male', {et:'Kert',en:'Andrew',ru:'Эндрю'}],
    ]) {
      await page.locator('#demo-voice').selectOption(profile);
      await page.locator('#demo-voice-preview').click();
      await page.waitForFunction(()=>!state.previewBusy && !document.getElementById('demo-audio').hidden);
      assert.equal(requests.at(-1).body.voice, profile);
      assert.equal(requests.at(-1).body.language, code);
      assert((await page.locator('#demo-voice-result').textContent()).includes(names[code]));
      assert.equal(await page.evaluate(()=>state.sessionId), null);
    }
  }
  await chooseLanguage('en');
  for (const [profile, name] of [['azure-male-calm','Davis'], ['azure-male-warm','Andrew'], ['azure-brian','Brian'], ['azure-ryan','Ryan']]) {
    await page.locator('#demo-voice').selectOption(profile);
    await page.locator('#demo-voice-preview').click();
    await page.waitForFunction(()=>!state.previewBusy && !document.getElementById('demo-audio').hidden);
    assert.equal(requests.at(-1).body.language, 'en');
    assert((await page.locator('#demo-voice-result').textContent()).includes(name));
  }
  await chooseLanguage('et');
  assert.equal(await page.locator('#demo-voice').inputValue(), 'azure');
  await page.evaluate(()=>loadVoices());
  assert.equal(await page.locator('#demo-voice').inputValue(), 'azure', 'catalog refresh replaced an explicit selection');
  await page.locator('#demo-voice').selectOption('azure-male-calm');
  await page.screenshot({path:'output/playwright/natural-voices-desktop.png',fullPage:true});
  await page.setViewportSize({width:390,height:844});
  assert(await page.locator('#demo-voice-preview').isVisible());
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.screenshot({path:'output/playwright/natural-voices-mobile.png',fullPage:true});
  await page.setViewportSize({width:1440,height:1000});
  await page.route('**/api/demo/voices/preview', route=>route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({detail:'voice_preview_unavailable'})}));
  await page.locator('#demo-voice-preview').click();
  await page.waitForFunction(()=>!state.previewBusy);
  assert((await page.locator('#demo-status').textContent()).includes('Proovi uuesti'));
  assert.equal(await page.evaluate(()=>state.sessionId), null);
  await page.unroute('**/api/demo/voices/preview');
  await page.locator('#demo-voice').selectOption('azure');
  // Slow or failed operator reads must not keep a completed voice turn busy.
  await page.locator('#demo-start').click();
  await page.waitForFunction(()=>state.sessionId && !state.turnBusy);
  let releaseReads;
  const readGate = new Promise(resolve=>{releaseReads=resolve;});
  let bookingsSeen, historySeen;
  const bookingsRequested = new Promise(resolve=>{bookingsSeen=resolve;});
  const historyRequested = new Promise(resolve=>{historySeen=resolve;});
  const blockRead = signal => async route => {
    signal();
    await readGate;
    await route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({detail:'fixture_read_unavailable'})}).catch(()=>{});
  };
  const blockedBookings = blockRead(bookingsSeen), blockedHistory = blockRead(historySeen);
  await page.route('**/api/bookings?**',blockedBookings);
  await page.route('**/api/call-history?**',blockedHistory);
  try {
    await page.locator('#demo-text').fill('Mis kell restoran avatakse?');
    await page.locator('#demo-send').click();
    await Promise.all([bookingsRequested,historyRequested]);
    assert.equal(await page.evaluate(()=>state.turnBusy),false,'secondary reads kept a completed voice turn busy');
    assert(await page.locator('#demo-send').isEnabled(),'secondary reads blocked the next answer');
    assert(await page.locator('#demo-mic').isEnabled(),'secondary reads blocked the next microphone turn');
    await page.locator('#demo-text').fill('Kas koeraga võib tulla?');
    await page.locator('#demo-send').click();
    await page.waitForFunction(()=>!state.turnBusy && document.querySelector('#demo-messages .message:last-child span').textContent.includes('Koeraga võib tulla'));
    assert.equal(await page.evaluate(()=>state.recapDeliveryId),null,'background reads granted booking consent');
  } finally {
    releaseReads();
    await page.waitForFunction(()=>!state.readBusy);
    await page.unroute('**/api/bookings?**',blockedBookings);
    await page.unroute('**/api/call-history?**',blockedHistory);
  }
  assert.equal(await page.evaluate(()=>state.turnBusy),false);
  assert.equal(await page.locator('#demo-status').evaluate(element=>element.classList.contains('error')),false,'failed secondary reads marked a successful voice answer failed');
  await page.locator('#demo-end').click();
  await page.waitForFunction(()=>!state.sessionId && !state.turnBusy);
  // An older successful or failed history read must not overwrite a newer one.
  for (const oldStatus of [200,503]) {
    let releaseOld, oldRequested;
    const oldGate = new Promise(resolve=>{releaseOld=resolve;});
    const oldSeen = new Promise(resolve=>{oldRequested=resolve;});
    let historyRequests = 0;
    await page.route('**/api/call-history?**',async route=>{
      const order = ++historyRequests;
      if (order === 1) {oldRequested(); await oldGate;}
      const failed = order === 1 && oldStatus === 503;
      await route.fulfill({status:failed?503:200,contentType:'application/json',body:JSON.stringify(failed
        ? {detail:'fixture_read_unavailable'}
        : {items:[{channel:'web',language:'et',turns:order,outcome:order===1?'in_progress':'completed'}]})});
    });
    try {
      await page.evaluate(()=>{window.latencyOldHistoryRead=loadHistory();});
      await oldSeen;
      await page.evaluate(()=>loadHistory());
      assert((await page.locator('#call-history').textContent()).includes('2 sõnumit'));
      assert((await page.locator('#call-history').textContent()).includes('Lõpetatud'));
      releaseOld();
      await page.evaluate(()=>window.latencyOldHistoryRead);
      assert((await page.locator('#call-history').textContent()).includes('2 sõnumit'),'older history response replaced the newest result');
      assert.equal(await page.locator('#history-status').evaluate(element=>element.classList.contains('error')),false,'older history failure replaced the newest successful status');
    } finally {
      releaseOld();
      await page.evaluate(async()=>{await window.latencyOldHistoryRead;delete window.latencyOldHistoryRead;});
      await page.unroute('**/api/call-history?**');
    }
  }
  for (const language of languages) {
    await chooseLanguage(language.code);
    assert.equal(await page.locator('html').getAttribute('lang'),language.code);
    await page.locator('#demo-start').click();
    await page.waitForFunction(()=>state.sessionId && !state.turnBusy);
    const pageLanguageHelp = {et: 'Lehe keele', en: 'page language', ru: 'язык страницы'}[language.code];
    assert((await page.locator('#language-help').textContent()).includes(pageLanguageHelp));
    assert((await page.locator('#demo-messages').textContent()).includes(language.greeting));
    assert(!/demo|testbroneering|test reservation|тестов|демо/i.test(await page.locator('#demo-messages .message').last().locator('span').textContent()), 'greeting narrated internal test status');
    assert.equal(requests.at(-1).body.language,language.code);
    const recoveryPrompts = {
      et: ['Ma ei saanud päris aru. Palun korda oma vastust.', 'Ma ei saanud ikka aru. Palun kirjuta oma vastus eesti, vene või inglise keeles.'],
      en: ["I didn't quite catch that. Please repeat your answer.", "I still couldn't understand. Please type your answer in Estonian, Russian or English."],
      ru: ['Не удалось разобрать ответ. Повторите, пожалуйста.', 'Всё ещё не удалось понять. Напишите ответ по-эстонски, по-русски или по-английски.'],
    }[language.code];
    for (const prompt of recoveryPrompts) {
      const before = requests.length;
      await page.evaluate(() => sendTurn(
        {audio_b64: btoa('fixture-unsupported-recovery')},
        {generation:state.generation, session:state.sessionId, micEpoch:state.micEpoch},
      ));
      await page.waitForFunction(() => !state.turnBusy);
      assert.equal(requests.length, before + 1, 'owned fixture audio did not exercise the backend');
      assert.equal(await page.locator('#demo-status').textContent(), prompt);
      assert((await page.locator('#demo-messages .message').last().textContent()).includes(prompt));
    }
    assert.equal(await page.locator('#demo-messages .message').count(), 3, 'unsupported speech added an empty caller message');
    assert.equal(await page.evaluate(() => state.recap), null);
    const hoursQuestions = {
      et: ['Mis kellani te lahti olete?', 'Aga nädalavahetusel?', 'Esmaspäevast neljapäevani'],
      en: ['What are your opening hours?', 'And on weekends?', 'Monday through Thursday'],
      ru: ['До скольки вы работаете?', 'А в выходные?', 'С понедельника по четверг'],
    }[language.code];
    for (const question of hoursQuestions.slice(0, 2)) {
      await page.locator('#demo-text').fill(question);
      await page.locator('#demo-send').click();
      await page.waitForFunction(()=>!state.turnBusy);
      const answer = await page.locator('#demo-messages .message').last().textContent();
      if (question === hoursQuestions[0]) assert(answer.includes(hoursQuestions[2]));
      else assert(answer.includes('23') && answer.includes('20') && !answer.includes('21'));
      assert.equal(await page.evaluate(()=>state.recap), null);
    }
    const petQuestions = {
      et: ['Tahaks tulla koeraga.', 'Kas kutsuga võib tulla?', 'Koeraga võib tulla. Teiste lemmikloomade kohta palun küsige restorani töötajalt.'],
      en: ['Can I bring my dog?', 'Can we bring a puppy?', 'Dogs are welcome. Please ask the restaurant team about other pets.'],
      ru: ['Можно прийти с собакой?', 'Можно с питомцем?', 'Можно прийти с собакой. О других питомцах спросите сотрудника ресторана.'],
    }[language.code];
    for (const question of petQuestions.slice(0, 2)) {
      await page.locator('#demo-text').fill(question);
      await page.locator('#demo-send').click();
      await page.waitForFunction(()=>!state.turnBusy);
      assert.equal(await page.locator('#demo-messages .message').last().locator('span').textContent(), petQuestions[2]);
      assert.equal(await page.evaluate(()=>state.recap), null);
    }
    const familyQuestions = {
      et: ['Kas lastele on joonistamisvõimalus?', 'Kas lastemenüü on olemas?'],
      en: ['Can children do some drawing?', "Do you have a children's menu?"],
      ru: ['Дети могут порисовать?', 'Есть детское меню?'],
    }[language.code];
    for (const question of familyQuestions) {
      await page.locator('#demo-text').fill(question);
      await page.locator('#demo-send').click();
      await page.waitForFunction(()=>!state.turnBusy);
      assert.equal(await page.locator('#demo-messages .message').last().locator('span').textContent(), familyInformation.family_facilities_summary[language.code]);
      assert.equal(await page.evaluate(()=>state.recap), null, 'family answer created a booking proposal');
    }
    const customerQuestions = {
      et: [['Kas kassiga võib tulla?', 'teiste lemmikloomade'], ['Millised allergeenid on lastemenüüs?', 'lastemenüü koostise'], ['Kas seda kõnet salvestatakse?', 'andmete säilitamise'], ['Mis kell mängunurk avatud on?', 'mängunurga eraldi'], ['Kas lõhe on täna veel saadaval?', 'tänase saadavuse'], ['Lapsel on raske hingata, mida teha?', '112']],
      en: [['Can I bring a cat?', 'pets other than dogs'], ["What allergens are in the children's menu?", "children's menu ingredients"], ['Is this call being recorded?', 'retention'], ["What are the play corner's opening hours?", 'separate opening hours'], ['Is the salmon still available today?', "today's dish availability"], ['My child is struggling to breathe. What should I do?', '112']],
      ru: [['Можно прийти с кошкой?', 'другими домашними животными'], ['Какие аллергены есть в детском меню?', 'составе детского меню'], ['Этот звонок записывается?', 'хранения данных'], ['В какие часы открыт игровой уголок?', 'отдельных часах работы'], ['Лосось сегодня ещё есть?', 'наличии блюд сегодня'], ['Ребёнку трудно дышать. Что делать?', '112']],
    }[language.code];
    for (const [question, expected] of customerQuestions) {
      await page.locator('#demo-text').fill(question);
      await page.locator('#demo-send').click();
      await page.waitForFunction(()=>!state.turnBusy);
      const answer = await page.locator('#demo-messages .message').last().locator('span').textContent();
      assert(answer.includes(expected), `customer question ${question}: ${answer}`);
      assert.equal(await page.evaluate(()=>state.recap), null, 'service question created a booking proposal');
      assert.equal(await page.locator('#demo-recap-read').isVisible(), false);
    }
    const timeQuestions = {
      en: ["I'd like a table tomorrow at 6 o clock", 'in the evening', 'Do you mean AM or PM?', 'How many of you are coming, including children?'],
      et: ['Soovin homme lauda kell kuus', 'õhtul', 'Kas mõtlete hommikul või õhtul?', 'Mitu inimest tuleb, lapsed kaasa arvatud?'],
      ru: ['Хочу столик завтра в шесть часов', 'вечером', 'Вы имеете в виду утром или вечером?', 'Сколько вас будет, вместе с детьми?'],
    }[language.code];
    for (let index = 0; index < 2; index++) {
      await page.locator('#demo-text').fill(timeQuestions[index]);
      await page.locator('#demo-send').click();
      await page.waitForFunction(()=>!state.turnBusy);
      assert((await page.locator('#demo-messages .message').last().locator('span').textContent()).includes(timeQuestions[index + 2]));
      assert.equal(await page.evaluate(()=>state.recap), null);
    }
    await page.locator('#demo-text').fill(language.menu);
    await page.locator('#demo-send').click();
    await page.waitForFunction(()=>!state.turnBusy);
    assert((await page.locator('#demo-messages').textContent()).includes(language.soup));
    const reasoningExample = {
      et: ['Üks meist on vegan, teisele meeldivad seened. Mida soovitaksite ja miks?',
           'Veganile soovitan köögiviljasuppi. Seenerisoto sobib taimetoitlasele, kuid sisaldab piima.'],
      en: ['One of us is vegan, another likes mushrooms. What would you recommend and why?',
           "I'd suggest vegetable soup for the vegan guest. Mushroom risotto suits a vegetarian, but contains milk."],
      ru: ['Один из нас веган, другой любит грибы. Что вы посоветуете и почему?',
           'Для вегана я предложу овощной суп. Грибное ризотто подходит вегетарианцу, но содержит молоко.'],
    }[language.code];
    await page.locator('[data-example="recommendation"]').click();
    await page.waitForFunction(()=>!state.turnBusy);
    assert.equal(await page.locator('#demo-messages .message').nth(-2).locator('span').textContent(), reasoningExample[0]);
    const recommendation = await page.locator('#demo-messages .message').last().locator('span').textContent();
    assert(recommendation.startsWith(reasoningExample[1]));
    assert(recommendation.endsWith({
      et:timeQuestions[3],
      en:timeQuestions[3],ru:timeQuestions[3],
    }[language.code]));
    assert.equal(await page.evaluate(()=>state.recap), null, 'reasoning response created a booking proposal');
    assert(await page.getByRole('radio', {name:'Eesti', exact:true}).isDisabled());
    await page.evaluate(code => {
      const input = document.querySelector('input[name="demo-language"][value="' + code + '"]');
      input.checked = true;
      input.dispatchEvent(new Event('change', {bubbles:true}));
    }, language.code === 'et' ? 'en' : 'et');
    assert.equal(await page.evaluate(()=>state.demoLanguage), language.code, 'active conversation language changed');
    assert.equal(await page.locator('input[name="demo-language"]:checked').inputValue(), language.code);
    assert(await page.locator('#demo-voice-preview').isDisabled(), 'audition interrupted an active conversation');
    await page.locator('#demo-end').click();
    await page.waitForFunction(()=>!state.sessionId && !state.turnBusy);
    // Exercise the actual controls against the local backend, with provider doubles.
    await page.locator('#demo-start').click();
    await page.waitForFunction(()=>state.sessionId && !state.turnBusy);
    const temporalAnswers = {
      et: ['Soovin lauda', 'kahe päeva pärast', 'kell kuueks õhtul', 'meid tuleb neli', 'Mis päevaks', 'Mis kell', 'Mitu inimest'],
      en: ["I'd like to book a table", 'in two days', 'at six and a half PM', 'for a party of four', 'What date', 'What time', 'How many'],
      ru: ['Хочу забронировать столик', 'через два дня', 'в половине седьмого вечера', 'нас будет четверо', 'На какой день', 'Во сколько', 'Сколько вас'],
    }[language.code];
    for (let index = 0; index < 4; index++) {
      await page.locator('#demo-text').fill(temporalAnswers[index]);
      await page.locator('#demo-send').click();
      await page.waitForFunction(()=>!state.turnBusy);
      if (index < 3) {
        const answer = await page.locator('#demo-messages .message').last().locator('span').textContent();
        assert(answer.includes(temporalAnswers[index + 4]), `incorrect ${language.code} temporal follow-up`);
        assert.equal(await page.evaluate(()=>state.recap), null);
        const sideQuestions = [hoursQuestions[0], language.menu, {
          et:'Kus saab parkida?',en:'Where can I park?',ru:'Где парковка?',
        }[language.code]];
        await page.locator('#demo-text').fill(sideQuestions[index]);
        await page.locator('#demo-send').click();
        await page.waitForFunction(()=>!state.turnBusy);
        const resumed = await page.locator('#demo-messages .message').last().locator('span').textContent();
        assert(resumed.endsWith(answer), `side question lost ${language.code} booking prompt`);
        assert(resumed.length > answer.length, 'side question was ignored');
        assert.equal(await page.evaluate(()=>state.recap), null);
      }
    }
    const temporalRecap = await page.evaluate(()=>state.recap && state.recap.reply);
    assert(!/demo|testbroneering|test reservation|тестов|демо/i.test(temporalRecap), 'recap narrated internal test status');
    assert(temporalRecap && (language.code === 'ru' ? temporalRecap.includes('на четырёх гостей') : /4\s+(?:guests|külalist|inimesele)/.test(temporalRecap)));
    if (language.code === 'ru') {
      assert(temporalRecap.includes('на полтора часа'));
      assert(temporalRecap.endsWith('Вам подходит?'));
      assert(!temporalRecap.includes('Возможное время на ту же дату'));
    }
    assert(temporalRecap.includes({et:'18:00',en:'6:30 PM',ru:'18:30'}[language.code]));
    const oldReceipt = await page.evaluate(()=>state.recap.id);
    await page.locator('#demo-text').fill(language.menu);
    await page.locator('#demo-send').click();
    await page.waitForFunction(()=>!state.turnBusy);
    const resumedRecap = await page.evaluate(()=>state.recap && state.recap.reply);
    assert(resumedRecap && resumedRecap.endsWith(temporalRecap));
    assert(resumedRecap.startsWith({et:'Menüüs',en:'The menu',ru:'В меню'}[language.code]));
    assert.notEqual(await page.evaluate(()=>state.recap.id),oldReceipt,'old recap receipt survived question');
    assert(await page.locator('#demo-recap-read').isVisible(), 'new booking recap is missing');
    assert(temporalRecap.endsWith({et:'Kas teile sobib?',en:'Does that work for you?',ru:'Вам подходит?'}[language.code]));
    await page.locator('#demo-recap-read').click();
    const affirmative = {et:'See aeg sobib, paneme kirja!',en:'thats perfect',ru:'Давайте так и сделаем!'}[language.code];
    for (let index = 0; index < 2; index++) {
      await page.locator('#demo-text').fill(affirmative);
      await page.locator('#demo-send').click();
      await page.waitForFunction(()=>!state.turnBusy && !state.readBusy);
      if (!index) {
        assert.equal(await page.locator('#demo-messages .booking-receipt[data-action="confirmed"]').count(),1);
        const summary=await page.locator('#demo-messages .message').last().locator('span').textContent();
        assert(summary.includes('Meretuule') && summary.includes('Esimene Külaline'));
        assert(summary.includes({et:'18:00',en:'6:30 PM',ru:'18:30'}[language.code]));
        assert(summary.includes({et:'4 inimesele',en:'4 guests',ru:'четырёх гостей'}[language.code]));
        assert(summary.includes(language.code==='ru'?'полтора часа':'90'));
        assert(!summary.includes('?'),'confirmed reservation asked another question');
      }
      assert.equal(await page.locator('#bookings .booking-recent').count(),1);
    }
    const naturalBooking = await page.evaluate(()=>state.latestBooking);
    assert(naturalBooking && naturalBooking.date === await page.evaluate(()=>tallinnDay(2)));
    assert.equal(await page.locator('#bookings .booking-recent').getAttribute('data-booking-id'),naturalBooking.id);
    await page.locator('#demo-text').fill({et:'Jah, tühista.',en:'Yes, cancel.',ru:'Да, отмените.'}[language.code]);
    await page.locator('#demo-send').click();
    await page.waitForFunction(()=>!state.turnBusy);
    await page.locator('#demo-end').click();
    await page.waitForFunction(()=>!state.sessionId && !state.turnBusy);
    await page.locator('#reservation-time').fill('14:00');
    await page.locator('#reservation-party').fill('4');
    await page.locator('#reservation-prepare').click();
    await page.waitForFunction(()=>reservation.holdId && !reservation.busy);
    assert((await page.locator('#reservation-recap-text').textContent()).includes({et:'Külalisi: 4',en:'Guests: 4',ru:'Гостей: 4'}[language.code]));
    assert(await page.locator('#reservation-date').isDisabled(),'held recap allowed editable dates');
    assert(await page.getByRole('radio', {name:'Eesti', exact:true}).isDisabled(),'owned booking language changed');
    assert(await page.locator('#reservation-confirm').isDisabled(),'recap automatically granted consent');
    await page.locator('#reservation-read').click();
    await page.waitForFunction(()=>reservation.acknowledged && !reservation.busy);
    assert.equal(requests.at(-1).path,'/api/booking/recap');
    // A previously selected later page must not hide a newly saved reservation.
    await page.evaluate(()=>{state.page=2;});
    gatedBookings=language.code==='en';
    await page.locator('#reservation-confirm').click();
    await page.waitForFunction(()=>reservation.bookingId && !reservation.busy);
    const directBooking=await page.evaluate(()=>reservation.bookingId);
    try {
      if(gatedBookings) {
        assert.equal(await page.evaluate(()=>state.readBusy),true,'post-write read was not gated');
        assert(await page.locator('#reservation-cancel').isEnabled(),'successful write controls waited for readback');
        assert.equal(await page.locator(`#bookings [data-booking-id="${directBooking}"]`).count(),0,'gated readback appeared complete');
      }
      gatedBookings=false;releaseBookings();
      await waitBooking(directBooking,language.confirmed);
      assert((await page.locator('#bookings').textContent()).includes(language.confirmed));
    } finally {gatedBookings=false;releaseBookings();}
    assert.equal(await page.locator('#booking-page').textContent(),'1');
    assert.equal(await page.locator('#bookings .booking-recent').count(),1);
    assert(await page.locator('#reservation-status .booking-link').isVisible());
    const formBooking = await page.evaluate(()=>reservation.bookingId);
    await assertReceipt(page.locator('#reservation-status'), '14:00–15:30', formBooking);
    assert(await page.locator('#reservation-prepare').isDisabled(),'new preparation lost owned cancellation');
    await page.locator('#reservation-cancel').click();
    await page.waitForFunction(()=>!reservation.bookingId && !reservation.busy);
    await waitBooking(directBooking,language.cancelled);
    assert((await page.locator('#bookings').textContent()).includes(language.cancelled));
    await assertReceipt(page.locator('#reservation-status'), '14:00–15:30', formBooking, 'cancelled');
    await page.locator('#reservation-end').click();
    await page.waitForFunction(()=>!reservation.sessionId && !reservation.busy);
    assert(!(await page.getByRole('radio', {name:'Eesti', exact:true}).isDisabled()));
  }
  const send = async text => {await page.locator('#demo-text').fill(text);await page.locator('#demo-send').click();await page.waitForFunction(()=>!state.turnBusy);};
  // First caller speech selects English despite the initial Estonian picker.
  await chooseLanguage('et');
  await page.locator('#demo-start').click();
  await page.waitForFunction(()=>state.sessionId && !state.turnBusy);
  for (const [text, expected] of [
    ['Hi! I would like to book a table.', 'What date'],
    ['Tomorrow', 'What time'],
    ['At 2 pm', 'How many'],
    ['Milline on menüü?', 'Vegetable soup'],
  ]) {
    await send(text);
    assert.equal(await page.evaluate(()=>state.replyLanguage),'en');
    assert((await page.locator('#demo-messages .message').last().textContent()).includes(expected));
    assert.equal(await page.evaluate(()=>state.demoLanguage),'et');
    assert.equal(await page.evaluate(()=>state.recap),null);
  }
  await send('Please speak Russian');
  assert.equal(await page.evaluate(()=>state.replyLanguage),'ru');
  assert((await page.locator('#demo-messages .message').last().textContent()).includes('Сколько вас будет'));
  await page.locator('#demo-end').click();
  await page.waitForFunction(()=>!state.sessionId && !state.turnBusy);
  // Real browser capture, filtering and 16k mono WAV encoding; recognition is a double.
  await chooseLanguage('en');
  await page.locator('#demo-start').click();
  await page.waitForFunction(()=>state.sessionId && !state.turnBusy);
  assert(await page.locator('#demo-voice').isDisabled(),'voice selection changed an active conversation');
  await page.evaluate(()=>{window.restaurantOriginalPlay=HTMLMediaElement.prototype.play;HTMLMediaElement.prototype.play=function(){return Promise.reject(new Error('fixture autoplay denied'));};});
  await send("I'd like to reserve a table");
  assert((await page.locator('#demo-messages .message').last().textContent()).includes('What date'));
  const englishNamedDate = await page.evaluate(()=>{
    const words = ['first','second','third','fourth','fifth','sixth','seventh','eighth','ninth','tenth','eleventh','twelfth','thirteenth','fourteenth','fifteenth','sixteenth','seventeenth','eighteenth','nineteenth','twentieth','twenty-first','twenty-second','twenty-third','twenty-fourth','twenty-fifth','twenty-sixth','twenty-seventh','twenty-eighth','twenty-ninth','thirtieth','thirty-first'];
    const day = Number(tallinnDay(1).slice(-2));
    const month = 'Janury Februry Marhc Aprli Maay Juune Jully Augsut Septmber Octobre Novembr Decemeber'.split(' ')[Number(tallinnDay(1).slice(5,7))-1];
    return 'the ' + words[day-1] + ' of ' + month;
  });
  await send(englishNamedDate);
  assert((await page.locator('#demo-messages .message').last().textContent()).includes('What time'));
  await send('6 o clock');
  assert((await page.locator('#demo-messages .message').last().textContent()).includes('AM or PM'));
  assert.equal(await page.evaluate(()=>state.recap),null,'ambiguous time prepared a booking');
  await send('in the evening');
  assert((await page.locator('#demo-messages .message').last().textContent()).includes('How many'));
  await send('for two adults and two children');
  assert(await page.locator('#demo-recap-read').isVisible());
  assert((await page.locator('#demo-messages .message').last().textContent()).includes('4 guests'));
  assert.equal(await page.evaluate(()=>state.recapDeliveryId),null,'failed autoplay authorized a booking');
  await page.locator('#demo-recap-read').click();
  const voiceReceipt=await page.evaluate(()=>state.recapDeliveryId);
  assert(voiceReceipt);
  await page.evaluate(()=>{state.page=2;document.getElementById('booking-date').value=tallinnDay();});
  await send('Thats absolutely perfect, thank you!');
  const confirmedVoice=requests.findLast(request=>request.body.recap_delivery_id);
  assert.equal(confirmedVoice.body.recap_delivery_id,voiceReceipt);
  assert((await page.locator('#demo-messages .message').last().textContent()).includes('confirmed'));
  const confirmationSummary=await page.locator('#demo-messages .message').last().textContent();
  assert(confirmationSummary.includes('Meretuule') && confirmationSummary.includes('6:00 PM') && confirmationSummary.includes('4 guests') && confirmationSummary.includes('90 minutes') && confirmationSummary.includes('Esimene Külaline'));
  assert(!confirmationSummary.includes('?'),'confirmation asked another question');
  const voiceBooking=await page.evaluate(()=>state.latestBooking);
  assert(voiceBooking && voiceBooking.date===await page.evaluate(()=>tallinnDay(1)));
  await waitBooking(voiceBooking.id,'confirmed');
  assert.equal(await page.locator('#booking-page').textContent(),'1');
  assert.equal(await page.locator('#bookings .booking-recent').getAttribute('data-booking-id'),voiceBooking.id);
  await assertReceipt(page.locator('#demo-messages'), '18:00–19:30', voiceBooking.id);
  await page.locator('#demo-messages .booking-receipt').last().scrollIntoViewIfNeeded();
  await page.screenshot({path:'output/playwright/booking-confirmation-desktop.png',fullPage:true});
  await page.setViewportSize({width:320,height:844});
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'receipt overflows 320px layout');
  await page.screenshot({path:'output/playwright/booking-confirmation-mobile.png',fullPage:true});
  await page.setViewportSize({width:1440,height:1000});
  await page.locator('#demo-messages .booking-link').last().click();
  await page.waitForFunction(()=>document.activeElement?.dataset.bookingId===state.latestBooking.id);
  assert.equal(await page.locator('#booking-date').inputValue(),voiceBooking.date);
  await send('Yes, cancel.');
  await waitBooking(voiceBooking.id,'cancelled');
  assert((await page.locator('#demo-messages .message').last().textContent()).includes('cancelled'));
  await assertReceipt(page.locator('#demo-messages'), '18:00–19:30', voiceBooking.id, 'cancelled');
  assert.equal(await page.locator('.booking-receipt[data-action="confirmed"]').count(),0,'cancellation left a stale confirmed receipt');
  await page.evaluate(()=>{HTMLMediaElement.prototype.play=restaurantOriginalPlay;});
  await page.evaluate(()=>{
    window.installRestaurantAudio = () => {
      const context=new AudioContext(),sink=context.createMediaStreamDestination(),source=context.createOscillator(),gain=context.createGain();
      source.frequency.value=300;gain.gain.value=.08;source.connect(gain);gain.connect(sink);source.start();
      window.restaurantAudio={context,source,stream:sink.stream};
      Object.defineProperty(navigator.mediaDevices,'getUserMedia',{configurable:true,value:async()=>sink.stream});
    };
    installRestaurantAudio();
  });
  await page.locator('#demo-mic').click();
  await page.waitForFunction(()=>state.mic && state.mic.frames>4096);
  assert(await page.locator('#demo-send').isDisabled(),'text input remained active during microphone capture');
  assert(await page.locator('.example-button').first().isDisabled(),'example could overlap a microphone turn');
  const turnsBeforeRecordingText=requests.length;
  await page.evaluate(()=>{
    window.retiredRestaurantCapture = {generation:state.generation,session:state.sessionId,micEpoch:state.micEpoch};
  });
  await page.evaluate(()=>sendTurn({text:'unintended overlapping turn'}));
  await page.waitForFunction(()=>!state.turnBusy && !state.mic);
  assert.equal(requests.length,turnsBeforeRecordingText+1,'central text retirement did not send exactly one text turn');
  assert.equal(requests.at(-1).body.text,'unintended overlapping turn');
  assert(await page.evaluate(()=>restaurantAudio.stream.getTracks().every(track=>track.readyState==='ended')),'text left retired capture live');
  await page.evaluate(()=>sendTurn({audio_b64:btoa('retired-capture')},retiredRestaurantCapture));
  assert.equal(requests.length,turnsBeforeRecordingText+1,'retired capture uploaded stale audio');
  await page.evaluate(async()=>{
    restaurantAudio.source.stop();await restaurantAudio.context.close();installRestaurantAudio();
  });
  await page.locator('#demo-mic').click();
  await page.waitForFunction(()=>state.mic && state.mic.frames>4096);
  await page.locator('#demo-mic').click();
  await page.waitForFunction(()=>!state.micStarting && !state.turnBusy);
  const audioRequest=requests.findLast(request=>request.body.audio_b64);
  assert(audioRequest,'microphone sent no encoded audio');
  const wav=Buffer.from(audioRequest.body.audio_b64,'base64');
  assert.equal(wav.toString('ascii',0,4),'RIFF');assert.equal(wav.readUInt32LE(24),16000);assert.equal(wav.readUInt16LE(22),1);
  await page.evaluate(async()=>{restaurantAudio.source.stop();await restaurantAudio.context.close();});
  await page.locator('#demo-end').click();
  await page.waitForFunction(()=>!state.sessionId && !state.turnBusy);
  // Russian mixed cases use the same real routes and visible SQLite ledger.
  await chooseLanguage('ru');
  await page.locator('#demo-start').click();
  await page.waitForFunction(()=>state.sessionId && !state.turnBusy);
  await page.evaluate(()=>{HTMLMediaElement.prototype.play=function(){return Promise.reject(new Error('fixture autoplay denied'));};});
  const russianNamedDate = await page.evaluate(()=>{
    const words = ['первому','второму','третьему','четвёртому','пятому','шестому','седьмому','восьмому','девятому','десятому','одиннадцатому','двенадцатому','тринадцатому','четырнадцатому','пятнадцатому','шестнадцатому','семнадцатому','восемнадцатому','девятнадцатому','двадцатому','двадцать первому','двадцать второму','двадцать третьему','двадцать четвёртому','двадцать пятому','двадцать шестому','двадцать седьмому','двадцать восьмому','двадцать девятому','тридцатому','тридцать первому'];
    const day = Number(tallinnDay(1).slice(-2));
    const month = 'янврая феврля марат аперля маай июння июлля авгусат сентябаря октябиря ноябрья декабяря'.split(' ')[Number(tallinnDay(1).slice(5,7))-1];
    return words[day-1] + ' ' + month;
  });
  await send('Забронируйте столик на ' + russianNamedDate + ' в 15:00 для четырёх гостей');
  assert(await page.locator('#demo-recap-read').isVisible());
  await page.locator('#demo-recap-read').click();
  await send('Да, всё отлично!');
  assert.equal(await page.evaluate(()=>state.latestBooking.date),await page.evaluate(()=>tallinnDay(1)));
  const russianBooking=await page.evaluate(()=>state.latestBooking.id);
  await waitBooking(russianBooking,'подтверждено');
  assert.equal(await page.locator('#bookings .booking-recent').getAttribute('data-booking-id'),russianBooking);
  assert((await page.locator('#demo-messages .message').last().textContent()).includes('подтверждено'));
  await send('Да, отмените.');
  await waitBooking(russianBooking,'отменено');
  assert((await page.locator('#demo-messages .message').last().textContent()).includes('отменено'));
  await page.locator('#demo-end').click();
  await page.waitForFunction(()=>!state.sessionId && !state.turnBusy);
  await page.evaluate(()=>{HTMLMediaElement.prototype.play=restaurantOriginalPlay;});
  // The Estonian ASR spelling uses the actual confirmation route and becomes
  // visible on the website. No external speech provider is used in this fixture.
  await chooseLanguage('et');
  await page.locator('#demo-start').click();
  await page.waitForFunction(()=>state.sessionId && !state.turnBusy);
  await page.evaluate(()=>{HTMLMediaElement.prototype.play=function(){return Promise.reject(new Error('fixture autoplay denied'));};});
  const estonianImperfectDate = await page.evaluate(()=>{
    const day = tallinnDay(1);
    const month = 'jaanar veebrur maerts april maai juunu juulu auguts septembr oktobte noveber detsembr'.split(' ')[Number(day.slice(5,7))-1];
    return Number(day.slice(-2)) + ' ' + month;
  });
  await send('Soovin lauaks ' + estonianImperfectDate + ' kell 17.00 nelja inimesega');
  assert(await page.locator('#demo-recap-read').isVisible(), 'Estonian imperfect date: ' + await page.locator('#demo-messages .message').last().textContent());
  await page.locator('#demo-recap-read').click();
  await send('ja kinnitää');
  assert((await page.locator('#demo-messages .message').last().textContent()).includes('Teie lauabroneering on kinnitatud.'));
  assert.equal(await page.evaluate(()=>state.latestBooking.date),await page.evaluate(()=>tallinnDay(1)));
  const estonianBooking=await page.evaluate(()=>state.latestBooking.id);
  await waitBooking(estonianBooking,'kinnitatud');
  assert.equal(await page.locator('#bookings .booking-recent').count(),1);
  await assertReceipt(page.locator('#demo-messages'), '17:00–18:30', estonianBooking);
  await page.locator('#demo-end').click();
  await page.waitForFunction(()=>!state.sessionId && !state.turnBusy);
  await page.reload({waitUntil:'networkidle'});
  assert.equal(await page.locator('#bookings .booking-row').count(),0,'reload exposed private bookings without sign-in');
  await page.locator('#operator-token').fill('restaurant-fixture-operator');
  await page.locator('#connect').click();
  await page.waitForFunction(()=>state.connected && !state.readBusy);
  await page.locator('#booking-date').fill(await page.evaluate(()=>tallinnDay(1)));
  await page.locator('#booking-date').dispatchEvent('change');
  await page.waitForFunction(()=>!state.readBusy);
  assert((await page.locator(`#bookings [data-booking-id="${estonianBooking}"]`).textContent()).includes('kinnitatud'));
  assert((await page.locator(`#bookings [data-booking-id="${estonianBooking}"]`).textContent()).includes('17:00–18:30'));
  assert((await page.locator(`#bookings [data-booking-id="${estonianBooking}"]`).textContent()).includes('4'));
  await page.screenshot({path:'output/playwright/restaurant-desktop.png',fullPage:true});
  await page.setViewportSize({width:390,height:844});
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'mobile horizontal overflow');
  assert(await page.locator('.sidebar nav').isVisible(),'mobile dashboard navigation is missing');
  assert.equal(await page.locator('.sidebar').evaluate(element=>getComputedStyle(element).position),'static','mobile sidebar covers the controls');
  await page.locator('.sidebar nav a[href="#demo-section"]').click();
  assert.equal(new URL(page.url()).hash,'#demo-section');
  assert(await page.locator('#demo-start').isVisible(),'mobile navigation does not reach voice controls');
  await page.screenshot({path:'output/playwright/restaurant-mobile.png',fullPage:true});
  await page.setViewportSize({width:320,height:844});
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'320px horizontal overflow');
  await page.setViewportSize({width:390,height:844});
  // A failed mutation cannot display a success receipt or become auto-retryable.
  await page.locator('#reservation-time').fill('18:00');
  await page.locator('#reservation-party').fill('4');
  await page.locator('#reservation-prepare').click();
  await page.waitForFunction(()=>reservation.holdId && !reservation.busy);
  await page.locator('#reservation-read').click();
  await page.waitForFunction(()=>reservation.acknowledged && !reservation.busy);
  await page.route('**/api/booking/confirm', route=>route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({error:'write_outcome_unknown',ok:false})}));
  await page.locator('#reservation-confirm').click();
  await page.waitForFunction(()=>reservation.uncertain && !reservation.busy);
  assert.equal(await page.locator('#reservation-status .booking-receipt').count(),0);
  assert(await page.locator('#reservation-confirm').isDisabled());
  assert((await page.locator('#reservation-status').getAttribute('class')).includes('error'));
  await page.unroute('**/api/booking/confirm');
  // A late private reply must not restore data after disconnect.
  let release; const gate=new Promise(resolve=>{release=resolve;});
  await page.route('**/api/bookings?**',async route=>{await gate;await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({items:[],has_more:false})}).catch(()=>{});});
  await page.locator('#refresh').click();
  await page.waitForFunction(()=>state.readBusy);
  await page.locator('#logout').click();release();
  await page.waitForFunction(()=>!state.connected && !state.readBusy);
  assert.equal(await page.locator('#bookings .booking-row').count(),0);
  assert.equal(await page.locator('#demo-messages .message').count(),0);
  assert.equal(await page.locator('.booking-receipt').count(),0);
  assert(await page.locator('#reservation-confirm').isDisabled());
  // Russian operator layout must also fit the sidebar breakpoint.
  await page.setViewportSize({width:801,height:844});
  await chooseLanguage('ru');
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'801px Russian dashboard overflow');
  await page.setViewportSize({width:390,height:844});
  const fixtureOrigin=new URL(page.url()).origin;
  // Exercise the actual app's retired-host guard, not a substituted website.
  for(const path of ['/','/restaurant.js','/api/public/restaurant','/api/bookings','/health']){
    const retired=await page.request.get(fixtureOrigin+path,{
      headers:{Host:'meretuule.arleserver.cfd'},maxRedirects:0
    });
    assert.equal(retired.status(),410,`retired hostname still serves ${path}`);
    assert.equal((await retired.body()).length,0,'retired hostname returned content');
    assert.equal(retired.headers()['cache-control'],'no-store');
    assert.equal(retired.headers().location,undefined,'retired hostname redirected');
  }
  assert.deepEqual(errors,[]);
  return {languages:3,familyFacilities:true,groundedAnswers:3,bookingSideQuestions:12,calendarSpellingRepair:true,backgroundReadsNonblocking:true,failedBackgroundReadsRecover:true,historyRefreshOrderGuard:true,multilingualStepwiseDateTimeAndParty:true,unsupportedLanguagePrompts:3,confirmed:3,cancelled:3,voiceReservation:true,englishSpokenDates:true,englishClockClarification:true,russianMixedDateCases:true,estonianDateCaseForms:true,estonianAsrConfirmation:true,bookingVisibleAfterReload:true,bookingPageReset:true,gatedReadback:true,recapReceipt:true,microphoneWav:true,logoutIsolation:true,desktop:true,mobile:true,retiredHostDenied:true,pageErrors:errors.length};
}
