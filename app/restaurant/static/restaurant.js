"use strict";
const $ = (id) => document.getElementById(id);
const state = {
  credential: "",
  connected: false,
  generation: 0,
  controllers: new Set(),
  sessionId: null,
  callId: null,
  turnBusy: false,
  audioUrl: null,
  audioEpoch: 0,
  playback: null,
  turnController: null,
  recap: null,
  demoVoice: "azure",
  voiceSelected: false,
  voiceCatalog: null,
  voicesLoading: false,
  previewBusy: false,
  endpointingMs: 500,
  mic: null,
  micStarting: false,
  micEpoch: 0,
  recapDeliveryId: null,
  awaitingRecapId: null,
  demoLanguage: "et",
  replyLanguage: "et",
  readBusy: false,
  page: 1,
  hasMore: false,
  restaurant: null,
  voiceReady: false,
  audioReady: false,
  bookingReady: false,
  telephoneRelease: null,
  bookingView: 0,
  historyView: 0,
  latestBooking: null,
};
const reservation = {
  sessionId: null,
  holdId: null,
  recapDeliveryId: null,
  recapText: null,
  recapLanguage: null,
  bookingId: null,
  acknowledged: false,
  busy: false,
  uncertain: false,
  date: null,
  epoch: 0,
};
const TEXT = {
  telephoneInSync: [
    "Telefoniroboti versioon ühtib veebiga viimase kontrolli järgi.",
    "The telephone assistant matches the website as of the last check.",
    "По последней проверке телефонный помощник использует ту же версию, что и сайт.",
  ],
  telephoneOutOfSync: [
    "Telefonirobot kasutab teist versiooni või seadistust.",
    "The telephone assistant has a different version or configuration.",
    "У телефонного помощника другая версия или настройки.",
  ],
  telephoneStale: [
    "Telefoniroboti versioon vajab uut kontrolli.",
    "The telephone assistant version needs a fresh check.",
    "Версию телефонного помощника нужно проверить снова.",
  ],
  telephoneUnverified: [
    "Telefoniroboti versiooni vastavus pole veel kinnitatud.",
    "The telephone assistant version has not been verified yet.",
    "Соответствие версии телефонного помощника пока не подтверждено.",
  ],
  demoWebsite: ["Vaata restorani demo ↗", "Visit the restaurant demo ↗", "Открыть демонстрацию ресторана ↗"],
  voice: ["Abilise hääl", "Assistant voice", "Голос помощника"],
  voicePreview: ["Kuula häält", "Listen to voice", "Послушать голос"],
  voicePreviewLoading: ["Valmistan hääleproovi…", "Preparing voice sample…", "Готовлю образец голоса…"],
  voicePreviewReady: ["Hääleproov on valmis.", "Voice sample is ready.", "Образец голоса готов."],
  voicePreviewFailed: [
    "Hääleproovi ei saanud luua. Proovi uuesti või vali teine hääl.",
    "Could not prepare the voice sample. Try again or choose another voice.",
    "Не удалось подготовить образец. Попробуйте ещё раз или выберите другой голос.",
  ],
  voiceSelectorHelp: [
    "Vali ja kuula häält enne vestlust. Kerti variandid muudavad kõnestiili; inglise keeles saad valida eri meeshääli.",
    "Choose and listen before starting. English offers different male speakers; Kert and Dmitry also have calm and lively delivery options.",
    "Выберите и послушайте голос до разговора. У Дмитрия есть спокойный и более живой варианты; разные мужские голоса доступны на английском.",
  ],
  voiceFallback: [
    "Kasutati varuhäält",
    "Fallback voice used",
    "Использован резервный голос",
  ],
  endReservation: [
    "Lõpeta broneerimisvestlus",
    "End reservation session",
    "Завершить сеанс бронирования",
  ],
  bookingMissing: [
    "Lauabroneeringute teenus pole aktiveeritud.",
    "Table reservations are not enabled.",
    "Бронирование столиков не включено.",
  ],
  guests: ["külalist", "guests", "гостей"],
  reservationReady: [
    "Vali laua kuupäev, saabumisaeg ja külaliste koguarv.",
    "Choose the table date, arrival time and total guest count.",
    "Выберите дату, время прибытия и общее число гостей.",
  ],
  browserConversation: [
    "Veebivestlus",
    "Browser conversation",
    "Разговор в браузере",
  ],
  telephoneConversation: [
    "Telefonikõne",
    "Telephone call",
    "Телефонный звонок",
  ],
  messages: ["sõnumit", "messages", "сообщений"],
  completed: ["Lõpetatud", "Completed", "Завершено"],
  needsAttention: [
    "Vajab kontrollimist",
    "Needs attention",
    "Требует проверки",
  ],
  active: ["Pooleli", "In progress", "В процессе"],
  booked: ["kinnitatud", "confirmed", "подтверждено"],
  cancelledState: ["tühistatud", "cancelled", "отменено"],
  receiptTitle: ["Broneering kinnitatud", "Reservation confirmed", "Бронирование подтверждено"],
  receiptCancelledTitle: ["Broneering tühistatud", "Reservation cancelled", "Бронирование отменено"],
  receiptSaved: ["Salvestatud demosüsteemi.", "Saved in the demo system.", "Сохранено в демосистеме."],
  receiptCancelled: ["Tühistamine salvestatud demosüsteemi.", "Cancellation saved in the demo system.", "Отмена сохранена в демосистеме."],
  receiptDate: ["Kuupäev", "Date", "Дата"],
  receiptTime: ["Kellaaeg (Tallinn)", "Time (Tallinn)", "Время (Таллинн)"],
  receiptGuests: ["Külalisi", "Guests", "Гостей"],
  receiptTable: ["Laud", "Table", "Столик"],
  receiptNumber: ["Broneeringu number", "Reservation number", "Номер бронирования"],
  skip: ["Hüppa sisu juurde", "Skip to content", "Перейти к содержимому"],
  brand: ["Restorani vastuvõtt", "Restaurant reception", "Ресепшн ресторана"],
  title: [
    "Restorani kõneabiline",
    "Your restaurant voice assistant",
    "Голосовой помощник ресторана",
  ],
  intro: [
    "Üks abiline laua leidmiseks ja külaliste küsimustele vastamiseks.",
    "One assistant for finding a table and answering your guests' questions.",
    "Один помощник для бронирования столика и ответов на вопросы гостей.",
  ],
  language: [
    "Vali vestluse keel",
    "Choose your conversation language",
    "Выберите язык разговора",
  ],
  languageHelp: [
    "Abiline alustab ja vastab valitud keeles.",
    "The assistant starts and replies in your chosen language.",
    "Помощник начинает разговор и отвечает на выбранном языке.",
  ],
  languageLocked: [
    "Keele vahetamiseks lõpeta pooleliolev vestlus.",
    "End the active conversation before changing language.",
    "Завершите текущий разговор перед сменой языка.",
  ],
  demo: [
    "Fiktiivne restoranidemo.",
    "Fictional restaurant demo.",
    "Демонстрация вымышленного ресторана.",
  ],
  demoNotice: [
    "Kasuta ainult näidiskülalisi. Broneeringud ei anna õigust päris külastusele.",
    "Use fictional guests only. Reservations do not entitle you to a real visit.",
    "Используйте только тестовых гостей. Бронирование не даёт права на настоящее посещение.",
  ],
  connectTitle: [
    "Ühenda töölaud",
    "Connect your workspace",
    "Подключите рабочее пространство",
  ],
  connectHelp: [
    "Operaatori tunnus avab lauabroneeringud ja kõneproovi.",
    "Your operator token opens table reservations and the voice demo.",
    "Токен оператора открывает бронирования столиков и голосовую демонстрацию.",
  ],
  token: ["Operaatori tunnus", "Operator token", "Токен оператора"],
  connect: ["Ühenda", "Connect", "Подключить"],
  logout: ["Lõpeta ühendus", "Disconnect", "Отключиться"],
  tokenHelp: [
    "Tunnust hoitakse ainult selle lehe mälus.",
    "The token is kept only in this page's memory.",
    "Токен хранится только в памяти этой страницы.",
  ],
  voiceTitle: [
    "Proovi kõneabilist",
    "Try the voice assistant",
    "Попробуйте голосового помощника",
  ],
  voiceHelp: [
    "Küsi laua, menüü või lahtiolekuaegade kohta. Toidusoovituseks ütle oma eelistus.",
    "Ask about a table, the menu or opening hours. Mention your dietary preferences for menu suggestions.",
    "Спросите о столике, меню или часах работы. Для рекомендации блюда расскажите о своих предпочтениях.",
  ],
  voiceBadge: ["Tekst ja mikrofon", "Text and microphone", "Текст и микрофон"],
  start: ["Alusta vestlust", "Start conversation", "Начать разговор"],
  end: ["Lõpeta vestlus", "End conversation", "Завершить разговор"],
  signIn: [
    "Ühenda esmalt operaatori tunnusega.",
    "Connect with your operator token first.",
    "Сначала подключитесь с токеном оператора.",
  ],
  exampleTable: ["Lauabroneering", "Table reservation", "Бронирование столика"],
  exampleMenu: ["Menüü", "Menu", "Меню"],
  exampleRecommendation: ["Toidusoovitus", "Food recommendation", "Совет по меню"],
  exampleHours: ["Lahtiolekuajad", "Opening hours", "Часы работы"],
  message: ["Sõnum abilisele", "Message the assistant", "Сообщение помощнику"],
  send: ["Saada", "Send", "Отправить"],
  placeholder: [
    "Näiteks: soovin homseks lauda nelja inimesega kell 19.00",
    "For example: a table for tomorrow at 5 pm for four",
    "Например: столик на завтрашний день в 17:00 для четырёх гостей",
  ],
  transcript: [
    "Selle lehe vestlus",
    "Conversation on this page",
    "Разговор на этой странице",
  ],
  audio: ["Abilise vastus", "Assistant's reply", "Ответ помощника"],
  micStart: [
    "Alusta häälvestlust",
    "Start voice conversation",
    "Начать голосовой разговор",
  ],
  micReady: [
    "Luba mikrofon ja räägi",
    "Enable your microphone and speak",
    "Включите микрофон и говорите",
  ],
  micStop: [
    "Lõpeta ja saada heli",
    "Stop and send audio",
    "Остановить и отправить аудио",
  ],
  micLevel: ["Mikrofoni helitase", "Microphone level", "Уровень микрофона"],
  micHelp: [
    "Räägi loomulikult. Kõnepaus saadab heli; teine vajutus saadab kohe. Üks salvestis kestab kuni 15 sekundit.",
    "Speak naturally. A pause sends your audio; press again to send immediately. Each recording lasts up to 15 seconds.",
    "Говорите естественно. Пауза отправляет аудио; повторное нажатие отправляет сразу. Запись длится до 15 секунд.",
  ],
  consentTitle: [
    "Kuidas kinnitamine töötab?",
    "How does confirmation work?",
    "Как работает подтверждение?",
  ],
  recapRead: [
    "Olen kokkuvõtte läbi lugenud",
    "I have read the recap",
    "Я прочитал(а) итог",
  ],
  reservationTitle: [
    "Broneeri laud",
    "Reserve a table",
    "Забронировать столик",
  ],
  reservationHelp: [
    "Vali kuupäev, saabumisaeg ja külaliste koguarv.",
    "Choose a date, arrival time and total number of guests.",
    "Выберите дату, время прибытия и общее число гостей.",
  ],
  date: ["Kuupäev", "Date", "Дата"],
  time: ["Saabumisaeg", "Arrival time", "Время прибытия"],
  party: [
    "Külalisi koos lastega",
    "Guests including children",
    "Гостей, включая детей",
  ],
  prepare: ["Kontrolli lauda", "Check for a table", "Проверить столик"],
  reservationInitial: [
    "Ühenda, et proovida lauabroneeringut.",
    "Connect to try a table reservation.",
    "Подключитесь, чтобы попробовать бронирование.",
  ],
  recapTitle: ["Kontrolli kokkuvõtet", "Review your recap", "Проверьте итог"],
  confirm: [
    "Kinnita lauabroneering",
    "Confirm table reservation",
    "Подтвердить бронирование",
  ],
  cancel: [
    "Tühista see broneering",
    "Cancel this reservation",
    "Отменить это бронирование",
  ],
  capacityHelp: [
    "Suure grupi ja erisoovid peab kinnitama personal.",
    "Staff must confirm large groups and special requests.",
    "Большие группы и особые пожелания подтверждает персонал.",
  ],
  bookingsTitle: [
    "Lauabroneeringud",
    "Table reservations",
    "Бронирования столиков",
  ],
  bookingsHelp: [
    "Demo kõnes ja siin kinnitatud lauad ilmuvad sellesse loendisse.",
    "Tables confirmed in the demo conversation or here appear in this list.",
    "Столики, подтверждённые в демонстрационном разговоре или здесь, появляются в этом списке.",
  ],
  viewBooking: ["Vaata broneeringut", "View reservation", "Посмотреть бронь"],
  refresh: ["Uuenda", "Refresh", "Обновить"],
  private: [
    "Andmed on privaatsed. Ühenda esmalt.",
    "This information is private. Connect first.",
    "Это частные данные. Сначала подключитесь.",
  ],
  previous: ["Eelmine", "Previous", "Назад"],
  next: ["Järgmine", "Next", "Далее"],
  infoTitle: [
    "Restorani teave",
    "Restaurant information",
    "Информация о ресторане",
  ],
  menuTitle: ["Menüü", "Menu", "Меню"],
  hoursTitle: ["Lahtiolekuajad", "Opening hours", "Часы работы"],
  historyTitle: ["Kõneajalugu", "Call history", "История звонков"],
  historyHelp: [
    "Salvestatakse tehnilised sündmused ja toimingute tulemused, mitte heli ega vestluse sisu.",
    "History stores technical events and action results. Audio and conversation content are not stored.",
    "История хранит технические события и результаты действий. Аудио и содержание разговора не сохраняются.",
  ],
  footer: [
    "Restorani demo · Eesti, English, Русский",
    "Restaurant demo · Eesti, English, Русский",
    "Демонстрация ресторана · Eesti, English, Русский",
  ],
  disconnected: ["Ühendamata", "Disconnected", "Не подключено"],
  connected: ["Ühendatud", "Connected", "Подключено"],
  loading: ["Laadin…", "Loading…", "Загрузка…"],
  failed: [
    "Toiming ebaõnnestus. Kontrolli ühendust või proovi hiljem uuesti.",
    "The request failed. Check your connection or try again later.",
    "Запрос не удался. Проверьте подключение или попробуйте позже.",
  ],
  authFailed: [
    "Tunnus ei sobi või teenus pole saadaval.",
    "The token was rejected or the service is unavailable.",
    "Токен отклонён или сервис недоступен.",
  ],
  empty: [
    "Selleks päevaks lauabroneeringuid ei ole.",
    "There are no table reservations for this date.",
    "На эту дату бронирований столиков нет.",
  ],
  noHistory: [
    "Kõnesid veel ei ole.",
    "No conversations yet.",
    "Разговоров пока нет.",
  ],
  ready: [
    "Vestlus valmis. Kirjuta või räägi mikrofoniga.",
    "Conversation ready. Type or speak into your microphone.",
    "Разговор готов. Напишите или говорите в микрофон.",
  ],
  responding: [
    "Abiline vastab…",
    "The assistant is replying…",
    "Помощник отвечает…",
  ],
  you: ["Sina", "You", "Вы"],
  assistant: [
    "Restorani abiline",
    "Restaurant assistant",
    "Помощник ресторана",
  ],
  ended: [
    "Vestlus lõpetatud. Võid valida teise keele.",
    "Conversation ended. You can choose another language.",
    "Разговор завершён. Можно выбрать другой язык.",
  ],
  textFallback: [
    "Heli pole saadaval; tekst on alles.",
    "Audio is unavailable; the text is still available.",
    "Аудио недоступно; текст сохранён на странице.",
  ],
  noRetry: [
    "Ära korda võimalikku kinnitust; kontrolli broneeringute loendit.",
    "Do not repeat a possible confirmation; check the reservation list.",
    "Не повторяйте возможное подтверждение; проверьте список бронирований.",
  ],
  acknowledged: [
    "Kokkuvõte loetud. Nüüd saad eraldi kinnitada.",
    "Recap read. You can now confirm separately.",
    "Итог прочитан. Теперь можно отдельно подтвердить.",
  ],
  confirmed: [
    "Teie broneering on tehtud.",
    "Your reservation is confirmed.",
    "Ваше бронирование подтверждено.",
  ],
  cancelled: [
    "Testbroneering tühistatud.",
    "Test reservation cancelled.",
    "Тестовое бронирование столика отменено.",
  ],
  unknown: [
    "Tulemus on ebaselge. Ära korda toimingut; palu personalil kontrollida.",
    "The result is uncertain. Do not repeat the action; ask staff to check.",
    "Результат неизвестен. Не повторяйте действие; попросите персонал проверить.",
  ],
  unavailable: [
    "Soovitud ajal sobivat lauda ei ole. Proovi teist aega või kuupäeva.",
    "No suitable table is available at that time. Try another time or date.",
    "На это время подходящего столика нет. Попробуйте другое время или дату.",
  ],
  micPermission: [
    "Ootan mikrofoni luba…",
    "Waiting for microphone permission…",
    "Ожидание разрешения микрофона…",
  ],
  micListening: [
    "Kuulan… räägi ja tee siis paus.",
    "Listening… speak, then pause.",
    "Слушаю… говорите, затем сделайте паузу.",
  ],
  micSilent: [
    "Salvestises ei tuvastatud heli. Kontrolli mikrofoni.",
    "No audio was detected. Check your microphone.",
    "Звук не обнаружен. Проверьте микрофон.",
  ],
  micEmpty: ["Salvestis on tühi.", "The recording is empty.", "Запись пуста."],
  micEncoding: [
    "Heli ettevalmistamine ei õnnestunud.",
    "Audio preparation failed.",
    "Подготовка аудио не удалась.",
  ],
  micDenied: [
    "Mikrofoni ei saanud avada. Kontrolli luba või kirjuta sõnum.",
    "The microphone could not be opened. Check permission or type a message.",
    "Не удалось открыть микрофон. Проверьте разрешение или напишите сообщение.",
  ],
  micQuiet: [
    "Heli on väga vaikne.",
    "The audio is very quiet.",
    "Звук очень тихий.",
  ],
  micSignal: [
    "Mikrofon töötab.",
    "Microphone audio detected.",
    "Микрофон обнаружил звук.",
  ],
  replyPlayed: ["Vastus esitatud.", "Reply played.", "Ответ воспроизведён."],
  audioError: [
    "Heli esitamine ebaõnnestus.",
    "Audio playback failed.",
    "Не удалось воспроизвести аудио.",
  ],
  autoplay: [
    "Vajuta heli esitamiseks mängimisnuppu.",
    "Press play to hear the audio.",
    "Нажмите воспроизведение, чтобы услышать аудио.",
  ],
  audioInvalid: [
    "Vastuse heli pole saadaval.",
    "Reply audio is unavailable.",
    "Аудио ответа недоступно.",
  ],
  closed: ["suletud", "closed", "закрыто"],
  voiceConfigured: [
    "Kõneproovi teenused seadistatud",
    "Voice demo services configured",
    "Сервисы голосовой демонстрации настроены",
  ],
  voiceMissing: [
    "Kõneproovi teenused pole seadistatud",
    "Voice demo services are not configured",
    "Сервисы голосовой демонстрации не настроены",
  ],
};
const DAYS = {
  et: [
    "Esmaspäev",
    "Teisipäev",
    "Kolmapäev",
    "Neljapäev",
    "Reede",
    "Laupäev",
    "Pühapäev",
  ],
  en: [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
  ],
  ru: [
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница",
    "Суббота",
    "Воскресенье",
  ],
};
function uiLanguage() {
  return state.demoLanguage === "auto" ? "et" : state.demoLanguage;
}
function demoCopy(language = uiLanguage()) {
  const index = { et: 0, en: 1, ru: 2 }[language];
  return Object.fromEntries(
    Object.entries(TEXT).map(([key, values]) => [key, values[index]]),
  );
}
function status(id, text, kind = "") {
  const element = $(id);
  element.textContent = text;
  element.className = "status " + kind;
}
function tallinnDay(offset = 0) {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Europe/Tallinn",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(new Date());
  const value = (key) => parts.find((part) => part.type === key).value;
  const date = `${value("year")}-${value("month")}-${value("day")}`;
  return new Date(Date.parse(date + "T12:00:00Z") + offset * 86400000)
    .toISOString()
    .slice(0, 10);
}
function presentation() {
  $("mic-feedback").hidden = !state.mic;
}
function localize() {
  const copy = demoCopy();
  document.documentElement.lang = uiLanguage();
  document.title = copy.title + " · Voicebot";
  for (const element of document.querySelectorAll("[data-copy]"))
    element.textContent = copy[element.dataset.copy];
  for (const element of document.querySelectorAll("[data-placeholder]"))
    element.placeholder = copy[element.dataset.placeholder];
  for (const element of document.querySelectorAll("[data-aria]"))
    element.setAttribute("aria-label", copy[element.dataset.aria]);
  $("connection-state").textContent = state.connected
    ? copy.connected
    : copy.disconnected;
  $("consent-help").textContent = {
    et: "Kuula või loe broneeringu kokkuvõte. Kui see sobib, vasta jaatavalt või vajuta kinnitamisnuppu. „Jah, tühista.” tühistab ainult selles vestluses loodud broneeringu. Ära sisesta päris kontakte.",
    en: 'Listen to or read the reservation recap. If it works for you, answer affirmatively or press the confirmation button. "Yes, cancel." cancels only a reservation created in this conversation. Do not enter real contacts.',
    ru: "Прослушайте или прочитайте итог бронирования. Если всё подходит, ответьте утвердительно или нажмите кнопку подтверждения. «Да, отмените.» отменяет только бронирование из этого разговора. Не вводите настоящие контакты.",
  }[uiLanguage()];
  renderInformation();
  renderVoices();
  controls();
}
function controls() {
  const locked = state.turnBusy || state.micStarting || state.previewBusy;
  $("connect").disabled = !!state.credential;
  $("logout").disabled = !state.connected;
  $("demo-language").disabled =
    !!state.sessionId ||
    locked ||
    !!state.mic ||
    reservation.busy ||
    !!reservation.sessionId;
  for (const input of $("demo-language").querySelectorAll("input"))
    input.checked = input.value === state.demoLanguage;
  $("language-help").textContent =
    state.sessionId || reservation.sessionId
      ? demoCopy().languageLocked
      : demoCopy().languageHelp;
  $("demo-start").disabled =
    !state.connected || !state.voiceReady || state.voicesLoading || !!state.sessionId || locked;
  $("demo-end").disabled = !state.sessionId || locked;
  $("demo-voice").disabled =
    !state.connected || state.voicesLoading || !!state.sessionId || locked || !!state.mic;
  $("demo-voice-preview").disabled =
    $("demo-voice").disabled || !Array.from($("demo-voice").options).some(
      option => option.value === state.demoVoice && !option.disabled,
    );
  $("demo-voice-preview").textContent = state.previewBusy
    ? demoCopy().voicePreviewLoading : demoCopy().voicePreview;
  for (const id of ["demo-text", "demo-send"])
    $(id).disabled = !state.sessionId || locked || !!state.mic;
  $("demo-mic").disabled = !state.connected || !state.audioReady || state.voicesLoading || locked;
  if (!state.mic)
    $("demo-mic").textContent = state.sessionId
      ? demoCopy().micReady
      : demoCopy().micStart;
  $("demo-recap-read").disabled = !currentRecap(state.recap) || locked || !!state.mic;
  $("refresh").disabled = !state.connected || state.readBusy;
  $("booking-prev").disabled =
    !state.connected || state.readBusy || state.page <= 1;
  $("booking-next").disabled =
    !state.connected || state.readBusy || !state.hasMore;
  for (const element of $("reservation-form").elements)
    element.disabled =
      !state.connected ||
      !state.bookingReady ||
      reservation.busy ||
      reservation.uncertain ||
      !!reservation.holdId ||
      !!reservation.bookingId;
  $("reservation-read").disabled =
    !currentReservationRecap() ||
    !reservation.recapDeliveryId ||
    reservation.busy ||
    reservation.uncertain ||
    reservation.acknowledged;
  $("reservation-confirm").disabled =
    !reservation.holdId ||
    !reservation.acknowledged ||
    reservation.busy ||
    reservation.uncertain;
  $("reservation-cancel").disabled =
    !reservation.bookingId || reservation.busy || reservation.uncertain;
  $("reservation-end").disabled =
    !reservation.sessionId || reservation.busy || reservation.uncertain;
  for (const button of document.querySelectorAll(".example-button"))
    button.disabled = !state.sessionId || locked || !!state.mic;
  presentation();
}
function requireDemoConnection() {
  if (state.connected) return true;
  status("demo-status", demoCopy().signIn, "error");
  $("operator-token").focus();
  return false;
}
const VOICE_LABELS = {
  azure: ["Tavahääl", "Standard voice", "Обычный голос"],
  "azure-conversational": ["Anu · vestluslik", "Emma · conversational", "Эмма · разговорный"],
  "azure-conversational-male": ["Kert · vestluslik", "Andrew · conversational", "Эндрю · разговорный"],
  "azure-male": ["Kert · meeshääl", "Guy · male voice", "Дмитрий · мужской голос"],
  "azure-calm": ["Anu · rahulik", "Jenny · calm", "Светлана · спокойный"],
  "azure-male-calm": ["Kert · rahulik meeshääl", "Davis · calm male voice", "Дмитрий · спокойный"],
  "azure-male-warm": ["Kert · elavam meeshääl", "Andrew · warm male voice", "Дмитрий · более живой"],
  "azure-brian": ["Brian · inglise keel (USA)", "Brian · American English", "Брайан · английский (США)"],
  "azure-ryan": ["Ryan · inglise keel (UK)", "Ryan · British English", "Райан · английский (Британия)"],
  elevenlabs: ["ElevenLabs", "ElevenLabs", "ElevenLabs"],
  google: ["Google Chirp", "Google Chirp", "Google Chirp"],
  cartesia: ["Cartesia Sonic", "Cartesia Sonic", "Cartesia Sonic"],
};
function voiceLabel(id) {
  return VOICE_LABELS[id]?.[["et", "en", "ru"].indexOf(uiLanguage())] || "";
}
function renderVoices() {
  const select = $("demo-voice");
  select.replaceChildren();
  const catalog = state.voiceCatalog || [
    { id: "azure", available: state.voiceReady, languages: ["et", "en", "ru"] },
  ];
  for (const profile of [...catalog].sort((a, b) => Number(b.available) - Number(a.available))) {
    const option = document.createElement("option");
    option.value = profile.id;
    option.textContent = voiceLabel(profile.id);
    option.disabled =
      !profile.available || !profile.languages.includes(uiLanguage());
    select.append(option);
  }
  if (
    !state.sessionId &&
    !Array.from(select.options).some(
      (option) => option.value === state.demoVoice && !option.disabled,
    )
  )
    state.demoVoice = "azure";
  select.value = state.demoVoice;
}
async function loadVoices() {
  const generation = state.generation;
  state.voicesLoading = true;
  controls();
  try {
    const data = await api("/api/demo/voices");
    if (generation !== state.generation || !state.connected) return;
    const ids = new Set();
    if (
      !Array.isArray(data.voices) ||
      data.voices.length > Object.keys(VOICE_LABELS).length ||
      data.voices.some(
        (profile) =>
          !profile ||
          !Object.hasOwn(VOICE_LABELS, profile.id) ||
          ids.has(profile.id) ||
          !ids.add(profile.id) ||
          typeof profile.available !== "boolean" ||
          !Array.isArray(profile.languages) ||
          profile.languages.some(
            (language) => !["et", "en", "ru"].includes(language),
          ),
      ) ||
      !ids.has("azure")
    )
      throw new Error("Invalid voice catalog");
    state.voiceCatalog = data.voices;
    if (!state.sessionId && !state.voiceSelected && data.voices.some(
      profile => profile.id === "azure-conversational" && profile.available &&
        profile.languages.includes(uiLanguage()),
    )) state.demoVoice = "azure-conversational";
    state.endpointingMs =
      Number.isInteger(data.endpointing_ms) &&
      data.endpointing_ms >= 300 &&
      data.endpointing_ms <= 2000
        ? data.endpointing_ms
        : 500;
  } catch (_) {
    if (generation !== state.generation || !state.connected) return;
    state.voiceCatalog = null;
  } finally {
    if (generation === state.generation) state.voicesLoading = false;
  }
  renderVoices();
  controls();
}
function renderVoiceResult(data) {
  const profile = data.voice?.effective;
  $("demo-voice-result").textContent =
    !data.tts_failed && Object.hasOwn(VOICE_LABELS, profile)
      ? demoCopy().voice +
        ": " +
        voiceLabel(profile) +
        (data.voice.fallback ? " · " + demoCopy().voiceFallback : "")
      : "";
}
$("demo-voice").addEventListener("change", () => {
  if (
    !state.connected ||
    state.sessionId ||
    state.turnBusy ||
    state.previewBusy ||
    state.micStarting ||
    state.mic
  ) {
    $("demo-voice").value = state.demoVoice;
    return;
  }
  const selected = Array.from($("demo-voice").options).find(
    (option) => option.selected && !option.disabled,
  );
  if (selected) {
    stopAudio();
    state.demoVoice = selected.value;
    state.voiceSelected = true;
    $("demo-voice-result").textContent = "";
  }
  renderVoices();
});
async function previewVoice() {
  if ($("demo-voice-preview").disabled) return;
  const generation = state.generation;
  state.previewBusy = true;
  stopAudio();
  controls();
  status("demo-status", demoCopy().voicePreviewLoading);
  try {
    const data = await post("/api/demo/voices/preview", {
      language: state.demoLanguage,
      voice: state.demoVoice,
    });
    if (generation !== state.generation || !state.connected) return;
    status("demo-status", demoCopy().voicePreviewReady);
    playReply(data);
    renderVoiceResult(data);
  } catch (_) {
    if (generation === state.generation)
      status("demo-status", demoCopy().voicePreviewFailed, "error");
  } finally {
    if (generation === state.generation) {
      state.previewBusy = false;
      controls();
    }
  }
}
$("demo-voice-preview").addEventListener("click", previewVoice);
async function api(path, options = {}) {
  const generation = state.generation;
  const controller = new AbortController();
  state.controllers.add(controller);
  const streaming =
    path === "/api/turn" &&
    new Headers(options.headers || {}).get("Accept") === "application/x-ndjson";
  if (streaming) state.turnController = controller;
  const timeout = setTimeout(
    () => controller.abort(),
    streaming ? 120000 : 45000,
  );
  try {
    const response = await fetch(path, {
      ...options,
      signal: controller.signal,
      headers: {
        Authorization: "Bearer " + state.credential,
        ...options.headers,
      },
    });
    if (generation !== state.generation)
      throw new DOMException("Cancelled", "AbortError");
    const data =
      response.ok &&
      streaming &&
      response.headers.get("Content-Type")?.startsWith("application/x-ndjson")
        ? await readTurnStream(response, controller)
        : await response.json();
    if (generation !== state.generation || controller.signal.aborted)
      throw new DOMException("Cancelled", "AbortError");
    if (!response.ok) {
      const error = new Error(demoCopy().failed);
      error.status = response.status;
      error.code = typeof data.detail === "string" ? data.detail : data.error;
      throw error;
    }
    return data;
  } finally {
    clearTimeout(timeout);
    state.controllers.delete(controller);
    if (state.turnController === controller) state.turnController = null;
  }
}
function post(path, body) {
  return api(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}
function currentReservationRecap() {
  return (
    state.connected &&
    !!reservation.sessionId &&
    !!reservation.holdId &&
    !$("reservation-recap").hidden &&
    reservation.recapLanguage === state.demoLanguage &&
    !!reservation.recapText &&
    $("reservation-recap-text").textContent === reservation.recapText
  );
}
function clearReservationRecap() {
  reservation.epoch++;
  reservation.holdId = reservation.recapDeliveryId = null;
  reservation.recapText = reservation.recapLanguage = null;
  reservation.acknowledged = false;
  $("reservation-recap").hidden = true;
  $("reservation-recap-text").textContent = "";
}
function clearReservation() {
  clearReservationRecap();
  Object.assign(reservation, {
    sessionId: null,
    holdId: null,
    bookingId: null,
    acknowledged: false,
    busy: false,
    uncertain: false,
    date: null,
  });
  $("reservation-cancel").hidden = true;
}
function logout() {
  state.generation++;
  for (const controller of state.controllers) controller.abort();
  state.controllers.clear();
  stopMic();
  stopAudio();
  state.credential = "";
  state.connected = false;
  state.sessionId = state.callId = null;
  state.turnBusy = state.readBusy = state.previewBusy = false;
  state.page = 1;
  state.hasMore = false;
  state.latestBooking = null;
  state.demoVoice = "azure";
  state.voiceSelected = false;
  state.voiceCatalog = null;
  state.voicesLoading = false;
  clearReservation();
  for (const id of ["demo-messages", "bookings", "call-history"])
    $(id).replaceChildren();
  $("operator-token").value = $("demo-text").value = "";
  localize();
  for (const id of [
    "auth-status",
    "demo-status",
    "booking-status",
    "history-status",
    "reservation-status",
  ])
    status(id, demoCopy().signIn);
}
async function connect() {
  const credential = $("operator-token").value.trim();
  if (!credential) return;
  state.credential = credential;
  $("operator-token").value = "";
  const generation = state.generation;
  controls();
  status("auth-status", demoCopy().loading);
  try {
    await api("/api/catalogue");
    if (generation !== state.generation) return;
    state.connected = true;
    localize();
    status("auth-status", demoCopy().tokenHelp, "success");
    status("demo-status", demoCopy().ready);
    status(
      "reservation-status",
      state.bookingReady
        ? demoCopy().reservationReady
        : demoCopy().bookingMissing,
    );
    await Promise.allSettled([loadBookings(), loadHistory(), loadVoices()]);
  } catch (error) {
    if (generation === state.generation) {
      logout();
      status("auth-status", demoCopy().authFailed, "error");
    }
  } finally {
    if (generation === state.generation) controls();
  }
}
function addMessage(label, text) {
  const element = document.createElement("div");
  element.className = "message" + (label === demoCopy().you ? " user" : "");
  element.lang = state.replyLanguage;
  const heading = document.createElement("strong");
  heading.textContent = label;
  const content = document.createElement("span");
  content.textContent = String(text || "");
  element.append(heading, content);
  $("demo-messages").append(element);
  element.scrollIntoView({ block: "nearest" });
  return element;
}
function selectBooking(change) {
  if (
    !change ||
    !["confirmed", "cancelled"].includes(change.action) ||
    !/^[1-9]\d*$/.test(String(change.id)) ||
    !/^\d{4}-\d{2}-\d{2}$/.test(change.date)
  )
    return false;
  state.latestBooking = { id: String(change.id), date: change.date };
  $("booking-date").value = change.date;
  state.page = 1;
  state.hasMore = false;
  return true;
}
function formatBookingDate(day, language = uiLanguage()) {
  return new Intl.DateTimeFormat({ et: "et-EE", en: "en-GB", ru: "ru-RU" }[language], {
    day: "numeric", month: "long", year: "numeric", timeZone: "UTC",
  }).format(new Date(day + "T12:00:00Z"));
}
function updateBookingReceiptStatus(receipt, action) {
  const copy = demoCopy(receipt.lang);
  const cancelled = action === "cancelled";
  receipt.dataset.action = action;
  receipt.querySelector(".receipt-title").textContent = cancelled
    ? copy.receiptCancelledTitle : copy.receiptTitle;
  receipt.querySelector(".receipt-saved").textContent = cancelled
    ? copy.receiptCancelled : copy.receiptSaved;
}
function appendBookingReceipt(container, change) {
  if (!selectBooking(change)) return;
  const generation = state.generation;
  for (const receipt of document.querySelectorAll(".booking-receipt")) {
    if (receipt.dataset.bookingId === String(change.id))
      updateBookingReceiptStatus(receipt, change.action);
  }
  // Only the committed backend receipt supplies these fields. Missing metadata
  // keeps the link available without guessing details from the conversation.
  if (
    change.timezone === "Europe/Tallinn" &&
    typeof change.start_local === "string" &&
    typeof change.end_local === "string" &&
    change.start_local.slice(0, 10) === change.date &&
    Number.isFinite(Date.parse(change.date + "T12:00:00Z")) &&
    /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(change.start_local) &&
    /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(change.end_local) &&
    Number.isInteger(change.party_size) && change.party_size > 0 &&
    typeof change.table_name === "string"
  ) {
    const copy = demoCopy();
    const receipt = document.createElement("div");
    receipt.className = "booking-receipt";
    receipt.lang = uiLanguage();
    receipt.dataset.bookingId = String(change.id);
    const title = document.createElement("strong");
    title.className = "receipt-title";
    const saved = document.createElement("p");
    saved.className = "receipt-saved";
    const details = document.createElement("dl");
    for (const [label, value] of [
      [copy.receiptDate, formatBookingDate(change.date)],
      [copy.receiptTime, `${change.start_local.slice(11, 16)}–${change.end_local.slice(11, 16)}`],
      [copy.receiptGuests, change.party_size],
      [copy.receiptTable, change.table_name],
      [copy.receiptNumber, `#${change.id}`],
    ]) {
      const item = document.createElement("div");
      const term = document.createElement("dt");
      term.textContent = label;
      const detail = document.createElement("dd");
      detail.textContent = String(value);
      item.append(term, detail);
      details.append(item);
    }
    receipt.append(title, saved, details);
    updateBookingReceiptStatus(receipt, change.action);
    container.append(receipt);
  }
  const button = document.createElement("button");
  button.type = "button";
  button.className = "secondary booking-link";
  button.textContent = `${demoCopy().viewBooking} #${change.id}`;
  button.addEventListener("click", async () => {
    if (generation !== state.generation || !state.connected) return;
    selectBooking(change);
    await loadBookings();
    if (generation !== state.generation || !state.connected) return;
    const row = Array.from($("bookings").children).find(
      (element) => element.dataset.bookingId === String(change.id),
    );
    const target = row || $("bookings-title");
    target.scrollIntoView({ block: "center" });
    target.focus({ preventScroll: true });
  });
  container.append(button);
  container.scrollIntoView({ block: "nearest" });
}
function recapPlayedMessage() {
  return {
    et: "Kokkuvõte esitatud. Kui broneering sobib, vasta jaatavalt.",
    en: 'Recap delivered. If the reservation works for you, answer affirmatively.',
    ru: "Итог озвучен. Если бронирование подходит, ответьте утвердительно.",
  }[state.replyLanguage];
}
async function startDemo() {
  if (
    !requireDemoConnection() ||
    !state.voiceReady ||
    state.sessionId ||
    state.turnBusy ||
    state.previewBusy
  )
    return;
  const generation = state.generation;
  state.turnBusy = true;
  stopAudio();
  controls();
  try {
    const data = await post("/api/demo/session", {
      language: state.demoLanguage,
      voice: state.demoVoice,
    });
    if (generation !== state.generation) return;
    state.sessionId = data.session_id;
    state.callId = data.call_id;
    state.replyLanguage = data.language;
    $("demo-messages").replaceChildren();
    addMessage(demoCopy().assistant, data.greeting);
    status(
      "demo-status",
      data.tts_failed ? demoCopy().textFallback : demoCopy().ready,
    );
    stopAudio();
    playReply(data);
    renderVoiceResult(data);
  } catch (error) {
    if (generation === state.generation)
      status("demo-status", demoCopy().failed, "error");
  } finally {
    if (generation === state.generation) {
      state.turnBusy = false;
      controls();
    }
  }
}
async function sendTurn(input, capture = null) {
  if (
    !state.connected ||
    !state.sessionId ||
    state.turnBusy
  )
    return;
  if (typeof input.text === "string" && input.text.trim()) stopMic();
  else if (
    !input.audio_b64 ||
    !capture ||
    capture.generation !== state.generation ||
    capture.session !== state.sessionId ||
    capture.micEpoch !== state.micEpoch ||
    state.mic ||
    state.micStarting
  )
    return;
  const generation = state.generation,
    session = state.sessionId,
    receipt = currentRecap(state.recap) ? state.recapDeliveryId : null;
  state.turnBusy = true;
  stopAudio();
  controls();
  status("demo-status", demoCopy().responding);
  try {
    const data = await api("/api/turn", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/x-ndjson",
      },
      body: JSON.stringify({
        session_id: session,
        ...input,
        language: state.demoLanguage,
        ...(receipt ? { recap_delivery_id: receipt } : {}),
      }),
    });
    if (generation !== state.generation || session !== state.sessionId) return;
    state.replyLanguage = data.language;
    const heard = data.text_heard ? addMessage(demoCopy().you, data.text_heard) : null;
    const message =
      data._stream?.replyNode || addMessage(demoCopy().assistant, data.reply);
    if (data._stream && heard) $("demo-messages").insertBefore(heard, message);
    $("demo-text").value = "";
    status(
      "demo-status",
      ["unsupported_language", "no_speech"].includes(data.input_status)
        ? data.reply
        : data.outcome === "unknown_outcome"
        ? demoCopy().unknown
        : data.tts_failed
          ? demoCopy().textFallback
          : demoCopy().ready,
      ["unknown_outcome", "tools_failed"].includes(data.outcome) ? "error" : "",
    );
    const recap = renderRecap(data, message, data._stream?.receivedAt);
    if (data._stream) finishStreamPlayback(data, recap);
    else playReply(data, recap);
    renderVoiceResult(data);
    const change = (data.booking_changes || []).at(-1);
    if (change) appendBookingReceipt(message, change);
    // Operator reads must not hold the next voice turn or completed playback.
    void Promise.allSettled([loadBookings(), loadHistory()]);
  } catch (error) {
    if (generation === state.generation && session === state.sessionId) {
      status(
        "demo-status",
        demoCopy().failed + " " + demoCopy().noRetry,
        "error",
      );
      if ([404, 410].includes(error.status)) state.sessionId = null;
    }
  } finally {
    if (generation === state.generation) {
      state.turnBusy = false;
      controls();
    }
  }
}
async function endDemo() {
  if (!state.sessionId || state.turnBusy) return;
  const generation = state.generation;
  stopMic();
  stopAudio();
  state.turnBusy = true;
  controls();
  try {
    await api("/api/demo/session/" + encodeURIComponent(state.sessionId), {
      method: "DELETE",
    });
    if (generation !== state.generation) return;
    state.sessionId = null;
    $("demo-messages").replaceChildren();
    status("demo-status", demoCopy().ended);
  } catch (error) {
    if (generation === state.generation) {
      if ([404, 410].includes(error.status)) state.sessionId = null;
      status("demo-status", demoCopy().failed, "error");
    }
  } finally {
    if (generation === state.generation) {
      state.turnBusy = false;
      controls();
    }
  }
}
async function prepareReservation() {
  if (
    !state.connected ||
    !state.bookingReady ||
    reservation.busy ||
    reservation.uncertain ||
    reservation.holdId ||
    reservation.bookingId
  )
    return;
  clearReservationRecap();
  const generation = state.generation,
    epoch = reservation.epoch;
  reservation.busy = true;
  controls();
  status("reservation-status", demoCopy().loading);
  try {
    if (!reservation.sessionId) {
      const session = await post("/api/booking/session", {
        language: state.demoLanguage,
      });
      if (
        generation !== state.generation ||
        epoch !== reservation.epoch ||
        !state.connected
      )
        return;
      reservation.sessionId = session.session_id;
    }
    const session = reservation.sessionId;
    const data = await post("/api/restaurant/reservation/prepare", {
      session_id: session,
      date: $("reservation-date").value,
      start_time: $("reservation-time").value,
      party_size: Number($("reservation-party").value),
    });
    if (
      generation !== state.generation ||
      epoch !== reservation.epoch ||
      session !== reservation.sessionId ||
      !state.connected
    )
      return;
    if (data.restaurant_unavailable || !data.ok) {
      status(
        "reservation-status",
        demoCopy().unavailable +
          (data.alternatives?.length ? " " + data.alternatives.join(", ") : ""),
        "error",
      );
      return;
    }
    if (
      typeof data.hold_id !== "string" ||
      !data.hold_id ||
      typeof data.recap_text !== "string" ||
      !data.recap_text.trim() ||
      typeof data.recap_delivery_id !== "string" ||
      !/^[a-f0-9]{32}$/.test(data.recap_delivery_id) ||
      typeof data.recap?.date !== "string"
    )
      throw new Error("Missing exact recap receipt");
    reservation.holdId = data.hold_id;
    reservation.recapDeliveryId = data.recap_delivery_id;
    reservation.recapText = data.recap_text;
    reservation.recapLanguage = state.demoLanguage;
    reservation.date = data.recap.date;
    $("reservation-recap-text").textContent = data.recap_text;
    $("reservation-recap").hidden = false;
    status("reservation-status", demoCopy().recapTitle);
  } catch (error) {
    if (generation === state.generation && epoch === reservation.epoch)
      status("reservation-status", demoCopy().failed, "error");
  } finally {
    if (generation === state.generation && epoch === reservation.epoch) {
      reservation.busy = false;
      controls();
    }
  }
}
async function readReservation() {
  if (
    !currentReservationRecap() ||
    !reservation.recapDeliveryId ||
    reservation.busy ||
    reservation.uncertain ||
    reservation.acknowledged
  )
    return;
  const generation = state.generation,
    epoch = reservation.epoch,
    session = reservation.sessionId,
    hold = reservation.holdId,
    receipt = reservation.recapDeliveryId;
  reservation.recapDeliveryId = null;
  reservation.busy = true;
  controls();
  try {
    const data = await post("/api/booking/recap", {
      session_id: session,
      hold_id: hold,
      recap_delivery_id: receipt,
    });
    if (
      generation !== state.generation ||
      epoch !== reservation.epoch ||
      session !== reservation.sessionId ||
      hold !== reservation.holdId
    )
      return;
    if (
      !currentReservationRecap() ||
      data.acknowledged !== true ||
      data.hold_id !== hold
    )
      throw new Error("Exact recap reading was not acknowledged");
    reservation.acknowledged = true;
    status("reservation-status", demoCopy().acknowledged);
  } catch (error) {
    if (
      generation === state.generation &&
      epoch === reservation.epoch &&
      session === reservation.sessionId
    ) {
      clearReservationRecap();
      reservation.busy = false;
      controls();
      status("reservation-status", demoCopy().failed, "error");
    }
  } finally {
    if (
      generation === state.generation &&
      epoch === reservation.epoch &&
      session === reservation.sessionId
    ) {
      reservation.busy = false;
      controls();
    }
  }
}
async function mutateReservation(cancel = false) {
  if (
    reservation.busy ||
    reservation.uncertain ||
    !state.connected ||
    (!cancel && !reservation.acknowledged)
  )
    return;
  const generation = state.generation,
    session = reservation.sessionId;
  let epoch = reservation.epoch;
  reservation.busy = true;
  controls();
  status("reservation-status", demoCopy().loading);
  try {
    const data = await post(
      cancel ? "/api/booking/cancel" : "/api/booking/confirm",
      {
        session_id: session,
        ...(cancel
          ? { booking_id: reservation.bookingId }
          : { hold_id: reservation.holdId }),
        consent: true,
      },
    );
    if (
      generation !== state.generation ||
      session !== reservation.sessionId ||
      epoch !== reservation.epoch
    )
      return;
    if (data.ok !== true || data.error) throw new Error("closed result");
    if (cancel) {
      reservation.bookingId = null;
      $("reservation-cancel").hidden = true;
    } else {
      reservation.bookingId = String(data.booking.id);
      clearReservationRecap();
      epoch = reservation.epoch;
      $("reservation-cancel").hidden = false;
    }
    status(
      "reservation-status",
      cancel ? demoCopy().cancelled : demoCopy().confirmed,
      "success",
    );
    const change = (data.booking_changes || []).at(-1);
    if (change) appendBookingReceipt($("reservation-status"), change);
    void Promise.allSettled([loadBookings(), loadHistory()]);
  } catch (error) {
    if (
      generation === state.generation &&
      session === reservation.sessionId &&
      epoch === reservation.epoch
    ) {
      reservation.uncertain = true;
      status("reservation-status", demoCopy().unknown, "error");
    }
  } finally {
    if (
      generation === state.generation &&
      session === reservation.sessionId &&
      epoch === reservation.epoch
    ) {
      reservation.busy = false;
      controls();
    }
  }
}
async function loadBookings() {
  if (!state.connected) return;
  const generation = state.generation,
    day = $("booking-date").value,
    page = state.page,
    view = ++state.bookingView;
  state.readBusy = true;
  controls();
  status("booking-status", demoCopy().loading);
  try {
    const data = await api(
      `/api/bookings?date=${encodeURIComponent(day)}&page=${page}&length=50`,
    );
    if (
      generation !== state.generation ||
      view !== state.bookingView ||
      day !== $("booking-date").value ||
      page !== state.page
    )
      return;
    $("bookings").replaceChildren();
    for (const row of data.items) {
      const element = document.createElement("div");
      element.className = "booking-row";
      element.dataset.bookingId = String(row.id);
      element.tabIndex = -1;
      if (
        state.latestBooking?.date === day &&
        state.latestBooking.id === String(row.id)
      )
        element.classList.add("booking-recent");
      const label = document.createElement("strong");
      label.textContent = `${formatBookingDate(row.start_local.slice(0, 10))} · ${row.start_local.slice(11, 16)}–${row.end_local.slice(11, 16)} · ${row.provider_name}`;
      const detail = document.createElement("span");
      detail.textContent = `${row.service_id} ${demoCopy().guests} · ${row.status === "confirmed" ? demoCopy().booked : demoCopy().cancelledState} · #${row.id}`;
      element.append(label, detail);
      $("bookings").append(element);
    }
    state.hasMore = data.has_more === "unknown";
    $("booking-page").textContent = String(page);
    status(
      "booking-status",
      data.items.length ? `${data.items.length}` : demoCopy().empty,
    );
  } catch (error) {
    if (generation === state.generation && view === state.bookingView) {
      $("bookings").replaceChildren();
      status("booking-status", demoCopy().failed, "error");
    }
  } finally {
    if (generation === state.generation && view === state.bookingView) {
      state.readBusy = false;
      controls();
    }
  }
}
async function loadHistory() {
  if (!state.connected) return;
  const generation = state.generation,
    view = ++state.historyView;
  try {
    const data = await api("/api/call-history?page=1&length=10");
    if (
      generation !== state.generation ||
      view !== state.historyView ||
      !state.connected
    )
      return;
    $("call-history").replaceChildren();
    for (const call of data.items) {
      const element = document.createElement("div");
      element.className = "booking-row";
      const label = document.createElement("strong");
      label.textContent = `${call.channel === "telephone" ? demoCopy().telephoneConversation : demoCopy().browserConversation} · ${{ et: "Eesti", en: "English", ru: "Русский" }[call.language] || ""} · ${call.turns} ${demoCopy().messages}`;
      const detail = document.createElement("span");
      detail.textContent =
        call.outcome === "in_progress"
          ? demoCopy().active
          : [
                "ok",
                "tools_ok",
                "completed",
                "booking_confirmed",
                "booking_cancelled",
                "hold_created",
              ].includes(call.outcome)
            ? demoCopy().completed
            : demoCopy().needsAttention;
      element.append(label, detail);
      $("call-history").append(element);
    }
    status(
      "history-status",
      data.items.length ? `${data.items.length}` : demoCopy().noHistory,
    );
  } catch (error) {
    if (generation === state.generation && view === state.historyView)
      status("history-status", demoCopy().failed, "error");
  }
}
function renderInformation() {
  if (!state.restaurant) return;
  const data = state.restaurant,
    language = uiLanguage();
  $("restaurant-name").textContent = data.name;
  $("menu-list").replaceChildren();
  for (const item of data.menu) {
    const element = document.createElement("li");
    element.textContent = item.name[language];
    $("menu-list").append(element);
  }
  $("allergy-notice").textContent = data.allergy_notice[language];
  $("restaurant-policies").textContent = data.policies[language];
  $("opening-hours").replaceChildren();
  [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
  ].forEach((day, index) => {
    const hours = data.opening_hours[day];
    const term = document.createElement("dt"),
      value = document.createElement("dd");
    term.textContent = DAYS[language][index];
    value.textContent = hours
      ? `${hours.start}–${hours.end}`
      : demoCopy().closed;
    $("opening-hours").append(term, value);
  });
  $("reservation-party").max = data.maximum_party_size;
  $("reservation-time").step = data.slot_interval_minutes * 60;
  $("reservation-duration").textContent =
    data.reservation_duration_minutes + " min";
  $("reservation-date").max = tallinnDay(data.advance_days);
  $("service-status").textContent = state.voiceReady
    ? demoCopy().voiceConfigured
    : demoCopy().voiceMissing;
  renderTelephoneStatus();
}
function renderTelephoneStatus() {
  const release = state.telephoneRelease;
  let key = "telephoneUnverified";
  if (release?.status === "out_of_sync") key = "telephoneOutOfSync";
  else if (release?.status === "stale") key = "telephoneStale";
  else if (release?.status === "in_sync") {
    const age = Date.now() / 1000 - release.verified_at;
    key = Number.isFinite(age) && age >= -5 && age <= release.max_age_seconds
      ? "telephoneInSync"
      : "telephoneStale";
  }
  $("telephone-status").textContent = demoCopy()[key];
}
async function refreshTelephoneStatus() {
  try {
    const response = await fetch("/api/status", { cache: "no-store", signal: AbortSignal.timeout(10000) });
    if (!response.ok) throw new Error("unavailable");
    state.telephoneRelease = (await response.json()).telephone?.release ?? null;
  } catch (_) {
    state.telephoneRelease = null;
  }
  renderTelephoneStatus();
}
async function loadPublic() {
  try {
    const [information, response] = await Promise.all([
      fetch("/api/public/restaurant"),
      fetch("/api/status"),
    ]);
    if (!information.ok || !response.ok) throw new Error("unavailable");
    const data = await information.json(),
      services = await response.json();
    state.restaurant = data.restaurant;
    state.bookingReady = data.table_booking_ready === true;
    state.voiceReady = services.capabilities.text_turn_ready === true;
    state.audioReady = services.capabilities.audio_turn_ready === true;
    state.telephoneRelease = services.telephone?.release ?? null;
    renderInformation();
    controls();
    if (!state.bookingReady)
      status("reservation-status", demoCopy().bookingMissing);
  } catch (_) {
    status("information-status", demoCopy().failed, "error");
  }
}
setInterval(() => {
  if (!document.hidden) refreshTelephoneStatus();
}, 60000);
setInterval(renderTelephoneStatus, 1000);
document.addEventListener("visibilitychange", () => {
  renderTelephoneStatus();
  if (!document.hidden) refreshTelephoneStatus();
});
$("auth-form").addEventListener("submit", (event) => {
  event.preventDefault();
  connect();
});
$("logout").addEventListener("click", logout);
$("demo-start").addEventListener("click", startDemo);
$("demo-end").addEventListener("click", endDemo);
$("demo-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const text = $("demo-text").value.trim();
  if (text) sendTurn({ text });
});
$("demo-mic").addEventListener("click", () => toggleMic());
$("demo-language").addEventListener("change", (event) => {
  const selected = event.target;
  if (
    !(selected instanceof HTMLInputElement) ||
    selected.name !== "demo-language" ||
    !["et", "en", "ru"].includes(selected.value)
  )
    return;
  if (
    state.sessionId ||
    state.turnBusy ||
    state.previewBusy ||
    state.micStarting ||
    state.mic ||
    reservation.busy ||
    reservation.sessionId
  ) {
    controls();
    return;
  }
  stopMic();
  clearReservationRecap();
  stopAudio();
  state.demoLanguage = selected.value;
  $("demo-voice-result").textContent = "";
  localize();
  status("demo-status", state.connected ? demoCopy().ready : demoCopy().signIn);
  status(
    "reservation-status",
    state.connected
      ? state.bookingReady
        ? demoCopy().reservationReady
        : demoCopy().bookingMissing
      : demoCopy().signIn,
  );
});
$("demo-recap-read").addEventListener("click", () => {
  acknowledgeRecap(state.recap);
});
for (const button of document.querySelectorAll("[data-example]"))
  button.addEventListener("click", () => {
    const examples = {
      reservation: [
        "Soovin broneerida laua.",
        "I'd like to reserve a table.",
        "Я хочу забронировать столик.",
      ],
      menu: ["Milline on menüü?", "What is on the menu?", "Что есть в меню?"],
      recommendation: [
        "Üks meist on vegan, teisele meeldivad seened. Mida soovitaksite ja miks?",
        "One of us is vegan, another likes mushrooms. What would you recommend and why?",
        "Один из нас веган, другой любит грибы. Что вы посоветуете и почему?",
      ],
      hours: [
        "Millal restoran avatud on?",
        "What are your opening hours?",
        "Какие у вас часы работы?",
      ],
    };
    sendTurn({
      text: examples[button.dataset.example][
        { et: 0, en: 1, ru: 2 }[uiLanguage()]
      ],
    });
  });
$("reservation-form").addEventListener("submit", (event) => {
  event.preventDefault();
  prepareReservation();
});
$("reservation-read").addEventListener("click", readReservation);
$("reservation-confirm").addEventListener("click", () => mutateReservation());
$("reservation-cancel").addEventListener("click", () =>
  mutateReservation(true),
);
$("reservation-end").addEventListener("click", async () => {
  if (!reservation.sessionId || reservation.busy || reservation.uncertain)
    return;
  clearReservationRecap();
  const generation = state.generation,
    session = reservation.sessionId,
    epoch = reservation.epoch;
  reservation.busy = true;
  controls();
  try {
    await api(
      "/api/demo/session/" + encodeURIComponent(session),
      { method: "DELETE" },
    );
    if (
      generation !== state.generation ||
      session !== reservation.sessionId ||
      epoch !== reservation.epoch
    )
      return;
    clearReservation();
    controls();
    status("reservation-status", demoCopy().ended);
  } catch (error) {
    if (
      generation === state.generation &&
      session === reservation.sessionId &&
      epoch === reservation.epoch
    ) {
      if ([404, 410].includes(error.status)) {
        clearReservation();
        controls();
      }
      status("reservation-status", demoCopy().failed, "error");
    }
  } finally {
    if (
      generation === state.generation &&
      session === reservation.sessionId &&
      epoch === reservation.epoch
    ) {
      reservation.busy = false;
      controls();
    }
  }
});
$("refresh").addEventListener("click", () =>
  Promise.allSettled([loadBookings(), loadHistory()]),
);
$("booking-date").addEventListener("change", () => {
  state.page = 1;
  loadBookings();
});
$("booking-prev").addEventListener("click", () => {
  state.page--;
  loadBookings();
});
$("booking-next").addEventListener("click", () => {
  state.page++;
  loadBookings();
});
document.addEventListener("visibilitychange", () => {
  if (document.hidden) {
    stopMic();
    $("demo-audio").pause();
  }
});
window.addEventListener("pagehide", () => {
  stopMic();
  stopAudio();
  for (const controller of state.controllers) controller.abort();
});
$("booking-date").value = tallinnDay();
$("reservation-date").value = tallinnDay(1);
$("reservation-date").min = tallinnDay();
$("reservation-date").max = tallinnDay(90);
localize();
loadPublic();
