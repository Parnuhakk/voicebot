"use strict";
window.createBookingCalendar = (root, { readCalendar, language = "et" }) => {

  const $ = (id) => root.querySelector(`#cal-${id}`);
  const COPY = {
    title: ["Lauakalender", "Table calendar", "Календарь столиков"],
    intro: ["Lauad ja broneeringud ühes vaates.", "Tables and reservations in one view.", "Столики и бронирования в одном месте."],
    prepare: ["Kontrolli lauda", "Prepare a reservation", "Подготовить бронирование"],
    newBooking: ["Uus näidisbroneering", "New preview booking", "Новое тестовое бронирование"],
    mode: ["Kalendri vaade", "Calendar mode", "Режим календаря"],
    live: ["Operaatori kalender", "Live operator calendar", "Календарь оператора"],
    liveBadge: ["Operaatori vaade", "Live operator view", "Режим оператора"],
    preview: ["Fiktiivne eelvaade", "Fictional preview", "Вымышленный пример"],
    refresh: ["Uuenda", "Refresh", "Обновить"],
    liveNotice: ["Salvestatud demobroneeringud ja aktiivsed hoidmised. Täituvus on privaatne kuni ühendamiseni.", "Live view of saved synthetic restaurant bookings and active holds. Occupancy is private until connected.", "Сохранённые демобронирования и активные удержания. Занятость доступна только после подключения."],
    previewNotice: ["AINULT EELVAADE: 12 fiktiivset lauda, näidised ja animatsioon ei ole salvestatud broneeringud. Siin ei broneerita restorani laudu.", "PREVIEW ONLY: twelve fictional tables, samples and animation are not stored bookings. Nothing here reserves the configured restaurant inventory.", "ТОЛЬКО ПРИМЕР: 12 вымышленных столиков, образцы и анимация не являются сохранёнными бронированиями. Столики ресторана здесь не бронируются."],
    arrival: ["Saabumisaeg", "Arrival time", "Время прибытия"],
    previousWeek: ["Eelmine nädal", "Previous week", "Предыдущая неделя"],
    nextWeek: ["Järgmine nädal", "Next week", "Следующая неделя"],
    chooseDate: ["Vali broneeringu kuupäev", "Choose booking date", "Выберите дату бронирования"],
    chooseDay: ["Vali päev", "Select a day", "Выберите день"],
    room: ["Saal", "The dining room", "Обеденный зал"],
    view: ["Kalendri vaade", "Booking view", "Вид бронирований"],
    floor: ["Saaliplaan", "Floor plan", "План зала"],
    timeline: ["Ajajoon", "Timeline", "Временная шкала"],
    capacity: ["Laua mahutavus", "Table capacity", "Вместимость столика"],
    all: ["Kõik lauad", "All tables", "Все столики"],
    people: ["{count} külalist", "{count} people", "{count} гостей"],
    seats: ["{count} kohta", "{count} seats", "{count} мест"],
    summary: ["{tables} lauda · {seats} kohta", "{tables} tables · {seats} seats", "{tables} столиков · {seats} мест"],
    window: ["Aknaäärsed kohad", "Window seating", "Места у окна"],
    entrance: ["Sissepääs", "Entrance", "Вход"],
    noConflict: ["Konflikti pole", "No conflict", "Нет конфликта"],
    reservedHeld: ["Broneeritud / hoitud", "Reserved / held", "Забронировано / удерживается"],
    unknown: ["Teadmata", "Unknown", "Неизвестно"],
    occupancyUnknown: ["Täituvus teadmata", "Occupancy unknown", "Занятость неизвестна"],
    held: ["Hoitud", "Held", "Удерживается"],
    reserved: ["Broneeritud", "Reserved", "Забронировано"],
    confirmed: ["Kinnitatud broneering", "Confirmed reservation", "Подтверждённое бронирование"],
    selected: ["Valitud", "Selected", "Выбран"],
    available: ["Vaba", "Available", "Свободен"],
    outside: ["Väljaspool broneerimisaega", "Outside booking hours", "Вне времени бронирования"],
    justBooked: ["Äsja broneeritud", "Just booked", "Только что забронирован"],
    found: ["Laud leitud", "Table found", "Столик найден"],
    noConflicts: ["{count} lauda konfliktita · hetktõmmis", "{count} tables with no conflict · snapshot", "{count} столиков без конфликта · снимок"],
    availableCount: ["{count} vaba lauda", "{count} tables available", "{count} свободных столиков"],
    table: ["Laud {number}", "Table {number}", "Столик {number}"],
    tableAria: ["Laud {number}, {count} külalist, {status}", "Table {number}, {count} people, {status}", "Столик {number}, {count} гостей, {status}"],
    voiceBooking: [", kõneabilise broneering", ", voicebot booking", ", бронирование помощника"],
    viewTable: ["Vaata laua {number} andmeid", "View table {number} details", "Посмотреть сведения о столике {number}"],
    timelineAria: ["{name}, {table}, {start}–{end}, {party} külalist", "{name}, {table}, {start}–{end}, {party} guests", "{name}, {table}, {start}–{end}, {party} гостей"],
    assistant: ["Kõneabiline", "Your voice assistant", "Ваш голосовой помощник"],
    callToTable: ["Kõnest lauani.", "From a call to a table.", "От звонка до столика."],
    conversation: ["Näidiskõne vestlus", "Sample call conversation", "Пример телефонного разговора"],
    guest: ["Külaline", "Guest", "Гость"],
    fourGuests: ["4 külalist", "4 guests", "4 гостя"],
    consent: ["„Jah, see sobib.”", "“Yes, that sounds perfect.”", "«Да, это подходит.»"],
    demoConfirmed: ["Näidisbroneering kinnitatud", "Demo booking confirmed", "Тестовое бронирование подтверждено"],
    replay: ["Esita uuesti", "Replay booking", "Повторить бронирование"],
    sampleNotice: ["Näidiskõne. Päris broneeringut ei tehta.", "A sample call. No real reservation is made.", "Пример звонка. Настоящее бронирование не создаётся."],
    liveHeading: ["Broneeringud ilma oletusteta.", "Bookings, without guesswork.", "Бронирования без догадок."],
    snapshotNotice: ["Vaade sisaldab kinnitatud broneeringuid ja kehtivaid hoidmisi. Hetktõmmis, mitte broneeringu garantii. Uuenda enne tegutsemist.", "This read-only view includes confirmed bookings and unexpired holds. It is a snapshot, not a reservation guarantee. Refresh before acting.", "Доступный только для чтения снимок подтверждённых бронирований и действующих удержаний. Это не гарантия бронирования. Обновите перед действием."],
    voiceDemo: ["Proovi kõneabilist", "Try the voice demo", "Попробовать голосового помощника"],
    savedBookings: ["Vaata broneeringuid", "View saved bookings", "Посмотреть сохранённые бронирования"],
    consentNotice: ["Lauad salvestatakse alles pärast kokkuvõtet ja selget kinnitust. Restoran on fiktiivne.", "Reservations are saved only after the recap and explicit consent. This configured venue is fictional.", "Бронирования сохраняются только после просмотра итога и явного согласия. Этот ресторан вымышленный."],
    seating: ["Istekohti kõigile", "Room for everyone", "Место для всех"],
    totalSeats: ["istekohti kokku", "total seats", "всего мест"],
    duration: ["minutit broneeringu kohta", "minutes per reservation", "минут на бронирование"],
    previewInventory: ["12 fiktiivset lauda. Ainult eelvaate inventar.", "Twelve fictional tables. Preview inventory only.", "12 вымышленных столиков. Только для примера."],
    liveInventory: ["Seadistatud lauad · kuni {max} külalist", "Configured tables · maximum party {max}", "Настроенные столики · до {max} гостей"],
    previewTimeline: ["Fiktiivsed broneeringud kestavad 90 minutit.", "Fictional reservations include a 90-minute dining window.", "Вымышленные бронирования рассчитаны на 90 минут."],
    liveTimeline: ["Kirjutuskaitstud hetktõmmis: kinnitatud broneeringud ja aktiivsed hoidmised. Ühendamata või aegununa on täituvus teadmata.", "Read-only snapshot: confirmed reservations and active holds. Unknown when disconnected or stale.", "Снимок только для чтения: подтверждённые бронирования и активные удержания. Без подключения или после истечения срока занятость неизвестна."],
    rules: ["{zone} · {duration} minutit broneeringu kohta · kuni {max} külalist. {hours}", "{zone} · {duration} minutes per reservation · maximum party {max}. {hours}", "{zone} · {duration} минут на бронирование · до {max} гостей. {hours}"],
    open: ["Sel päeval avatud {start}–{end}.", "Open {start}–{end} on this date.", "В этот день открыто {start}–{end}."],
    closed: ["Sel päeval suletud.", "Closed on this date.", "В этот день закрыто."],
    noVenue: ["Restorani seadistus pole saadaval. Täituvus teadmata; laadi leht uuesti.", "Venue configuration unavailable. Occupancy unknown; reload to retry.", "Настройки ресторана недоступны. Занятость неизвестна; перезагрузите страницу."],
    disconnected: ["Täituvus teadmata. Ühenda töölaud, et kalendrit lugeda.", "Occupancy unknown. Connect the workspace to read the calendar.", "Занятость неизвестна. Подключите рабочее пространство для чтения календаря."],
    reading: ["Loen kalendrit… Täituvus teadmata.", "Reading calendar… Occupancy unknown.", "Чтение календаря… Занятость неизвестна."],
    updated: ["Uuendatud {time} · {zone}. Kirjutuskaitstud demoinventar; uuenda enne broneerimist.", "Updated {time} · {zone}. Read-only synthetic inventory; refresh before booking.", "Обновлено {time} · {zone}. Демо-инвентарь только для чтения; обновите перед бронированием."],
    expired: ["Hetktõmmis aegus. Täituvus teadmata; uuenda kalendrit.", "Snapshot expired. Occupancy unknown; refresh to read current bookings and holds.", "Снимок истёк. Занятость неизвестна; обновите календарь."],
    unavailable: ["Kalender pole saadaval. Täituvus teadmata; kontrolli ühendust ja proovi uuesti.", "Calendar unavailable. Occupancy unknown; check the connection and refresh to retry.", "Календарь недоступен. Занятость неизвестна; проверьте подключение и обновите."],
    dateChanged: ["Täituvus teadmata. Ühenda või uuenda selle kuupäeva kalendrit.", "Occupancy unknown. Connect or refresh for this date.", "Занятость неизвестна. Подключитесь или обновите эту дату."],
    closeTable: ["Sulge laua andmed", "Close table details", "Закрыть сведения о столике"],
    back: ["Tagasi saali", "Back to dining room", "Вернуться в зал"],
    closeBooking: ["Sulge näidisbroneering", "Close booking form", "Закрыть форму бронирования"],
    addSample: ["Lisa kalendrisse näidisbroneering.", "Add a sample reservation to your calendar.", "Добавьте тестовое бронирование в календарь."],
    guestName: ["Külalise nimi", "Guest name", "Имя гостя"],
    date: ["Kuupäev", "Date", "Дата"],
    guests: ["Külaliste arv", "Number of guests", "Число гостей"],
    party2: ["2 külalist", "2 people", "2 гостя"],
    party4: ["4 külalist", "4 people", "4 гостя"],
    party8: ["8 külalist", "8 people", "8 гостей"],
    localNotice: ["Ainult eelvaade. Säilib lehel kuni uuesti laadimiseni.", "Demo only. Saved in this page until you reload.", "Только пример. Хранится на этой странице до перезагрузки."],
    addBooking: ["Lisa näidisbroneering", "Add demo booking", "Добавить тестовое бронирование"],
    tableDescription: ["{seats} {notice}", "{seats}. {notice}", "{seats}. {notice}"],
    liveDetailNotice: ["Fiktiivne restoran; kirjutuskaitstud hetktõmmis.", "Configured synthetic venue; read-only snapshot.", "Настроенный вымышленный ресторан; снимок только для чтения."],
    previewDetailNotice: ["Kõik andmed on fiktiivsed näidised.", "All details are fictional preview samples.", "Все сведения — вымышленные примеры."],
    unknownDetail: ["Täituvus teadmata. Ühenda töölaud või uuenda kalendrit.", "Occupancy unknown. Connect or refresh the calendar.", "Занятость неизвестна. Подключитесь или обновите календарь."],
    outsideDetail: ["Väljaspool broneerimisaega. Kontrolli lahtiolekuaegu ja vali tulevane saabumisaeg.", "Outside the booking window. Check opening hours and choose a future arrival.", "Вне времени бронирования. Проверьте часы работы и выберите будущее время."],
    noConflictDetail: ["Hetktõmmises konflikti pole. Kontrolli lauda broneerimisvormis; enne kinnitamist kontrollitakse inventari uuesti.", "No conflict in this snapshot. Prepare a reservation in the dashboard; the allocator rechecks inventory before explicit consent.", "В снимке конфликта нет. Подготовьте бронирование в форме; до подтверждения наличие проверяется снова."],
    guestsCount: ["{count} külalist", "{count} guests", "{count} гостей"],
    animatedBooking: ["Broneeritud kõneanimatsioonis", "Booked in the voicebot animation", "Забронирован в анимации звонка"],
    sampleReservation: ["Näidisbroneering", "Sample reservation", "Тестовое бронирование"],
    suggested: ["Soovitatud näidiskõnes.\nOotan külalise kinnitust.", "Suggested for the sample call.\nWaiting for the guest to confirm.", "Предложен в примере звонка.\nОжидается подтверждение гостя."],
    availableDetail: ["Vaba {date}\n{start}–{end}", "Available for {date}\n{start}–{end}", "Свободен на {date}\n{start}–{end}"],
    guestRequest: ["„Palun laud neljale {date} kell {time}.”", "“A table for four on {date}, at {time}, please.”", "«Столик на четверых на {date} в {time}, пожалуйста.»"],
    ready: ["Näidiskõneks valmis", "Ready for a sample call", "Готов к примеру звонка"],
    play: ["Esita broneerimisanimatsioon", "Play the booking animation", "Запустить анимацию бронирования"],
    calling: ["Külaline helistab…", "A guest is calling…", "Гость звонит…"],
    watch: ["Vaata, kuidas broneering sünnib", "Watch a booking come together", "Посмотрите, как создаётся бронирование"],
    listening: ["Kuulan külalist", "Listening to the guest", "Слушаю гостя"],
    request: ["Kuupäev, kellaaeg ja laud neljale", "Date, time, and a table for four", "Дата, время и столик на четверых"],
    checking: ["Otsin sobivat lauda…", "Finding the right table…", "Поиск подходящего столика…"],
    checkingWindow: ["Kontrollin 90-minutilist söögiaega", "Checking the 90-minute dining window", "Проверяю 90-минутный интервал"],
    replyChecking: ["Leian teile sobiva laua.", "Let me find you a lovely spot.", "Сейчас найду вам подходящий столик."],
    full: ["Neljakohalised lauad on täis", "The four-person tables are full", "Все столики на четверых заняты"],
    tryAgain: ["Vali teine aeg ja esita uuesti", "Choose another time and replay", "Выберите другое время и повторите"],
    replyFull: ["Sel ajal pole neljakohalist lauda. Kas proovime teist aega?", "There isn’t a four-person table for this time. Shall we try another time?", "На это время нет столика на четверых. Попробуем другое время?"],
    replyOffer: ["Laud {number} neljale {date} kell {time}. Kas sobib?", "Table {number} for four on {date}, at {time}. Does that work for you?", "Столик {number} на четверых на {date} в {time}. Подходит?"],
    offering: ["Laud {number} sobib hästi", "Table {number} is a perfect fit", "Столик {number} отлично подходит"],
    waiting: ["Ootan külalise kinnitust", "Waiting for the guest’s confirmation", "Ожидаю подтверждения гостя"],
    noLonger: ["See laud pole enam vaba", "That table is no longer available", "Этот столик больше не доступен"],
    allSet: ["Kõik valmis. Kohtumiseni!", "All set. We’ll see you soon.", "Всё готово. До скорой встречи."],
    welcome: ["Soe vastuvõtt algab siit", "A warm welcome starts here", "Тёплый приём начинается здесь"],
    result: ["Laud {number} · 4 külalist · {time}", "Table {number} · 4 guests · {time}", "Столик {number} · 4 гостя · {time}"],
    nameRequired: ["Sisesta külalise nimi.", "Enter a guest name to continue.", "Введите имя гостя."],
    dateRequired: ["Vali kehtiv kuupäev.", "Choose a valid date to continue.", "Выберите допустимую дату."],
    optionsRequired: ["Vali loetletud aeg ja külaliste arv.", "Choose a listed arrival time and party size.", "Выберите время и число гостей из списка."],
    fullError: ["Kõik lauad {party} külalisele on sel ajal broneeritud. Proovi teist aega või kuupäeva.", "All tables for {party} people are reserved during this dining window. Try another arrival time or date.", "Все столики на {party} гостей заняты в этом интервале. Попробуйте другое время или дату."],
    added: ["Näidisbroneering lisatud: {name}, laud {number}, {time}.", "Demo booking added: {name}, table {number}, {time}.", "Тестовое бронирование добавлено: {name}, столик {number}, {time}."],
  };
  const t = (key, values = {}) => COPY[key][{ et: 0, en: 1, ru: 2 }[language]].replace(/\{(\w+)\}/g, (_, name) => values[name]);
  const locale = () => ({ et: "et-EE", en: "en-GB", ru: "ru-RU" })[language];
  let connected = false;
  let statusKey = "disconnected", statusValues = {};
  let dialogTable = null, dialogBooking;
  let stageCopy, replyCopy, resultCopy, errorCopy, toastCopy;
  function calendarStatus(key, values = {}) {
    statusKey = key;
    statusValues = values;
    $("calendar-status").textContent = t(key, values);
  }
  let DINING_MINUTES = 90;
  let TIMELINE_START = 17 * 60;
  let TIMELINE_MINUTES = 330;
  const INITIAL_DATE = "2026-10-07";
  const previewTables = Array.from({ length: 12 }, (_, index) => ({
    id: `T${String(index + 1).padStart(2, "0")}`,
    number: String(index + 1).padStart(2, "0"),
    capacity: index < 4 ? 4 : index < 10 ? 2 : 8,
  }));
  let tables = [];
  let venue;
  let requestVersion = 0;
  let staleTimer;
  let previewBookings;
  const today = () => new Date().toLocaleDateString("en-CA", { timeZone: "Europe/Tallinn" });
  const state = {
    mode: "live",
    loaded: false,
    date: today(),
    time: "19:00",
    capacity: "all",
    view: "floor",
    highlighted: null,
    stage: "ready",
    storyVersion: 0,
    timers: [],
    bookings: [
      { id: "sample-1", table: "T06", date: INITIAL_DATE, time: "18:30", party: 2, name: "Jamie Lee", source: "sample" },
      { id: "sample-2", table: "T12", date: INITIAL_DATE, time: "19:00", party: 8, name: "Taylor Reed", source: "sample" },
    ],
  };
  let toastTimer;
  let bookingSequence = 0;
  previewBookings = state.bookings;
  state.bookings = [];

  function clearPrivate(key = "disconnected") {
    requestVersion++;
    clearTimeout(staleTimer);
    state.loaded = false;
    state.bookings = [];
    dialogTable = null;
    dialogBooking = undefined;
    $("table-dialog").close();
    $("table-dialog-title").textContent = "";
    $("table-dialog-detail").textContent = "";
    $("table-dialog-description").textContent = "";
    $("timeline-grid").replaceChildren();
    calendarStatus(key);
  }

  function setConnected(value) {
    connected = Boolean(value);
    $("refresh-calendar").disabled = !connected;
    if (!connected) clear();
    else if (state.mode === "live") loadCalendar();
  }

  function configureRoom() {
    tables = state.mode === "preview" ? previewTables : (venue?.tables || []).map(table => ({ ...table, number: String(table.id).padStart(2, "0") }));
    DINING_MINUTES = state.mode === "preview" ? 90 : (venue?.reservation_duration_minutes || 90);
    const capacities = state.mode === "preview" ? [4, 2, 8] : [...new Set(tables.map(table => table.capacity))].sort((a, b) => a - b);
    const tabs = ["all", ...capacities].map(capacity => {
      const tab = element("button", "", (capacity === "all" ? t("all") : t("people", { count: capacity })) + " ");
      tab.id = `cal-capacity-${capacity}`;
      tab.type = "button";
      tab.dataset.capacity = capacity;
      tab.setAttribute("role", "tab");
      tab.setAttribute("aria-selected", String(String(capacity) === state.capacity));
      tab.setAttribute("aria-controls", "cal-table-content");
      tab.tabIndex = String(capacity) === state.capacity ? 0 : -1;
      tab.append(element("span", "", String(capacity === "all" ? tables.length : tables.filter(t => t.capacity === capacity).length)));
      return tab;
    });
    root.querySelector(".capacity-tabs").replaceChildren(...tabs);
    $("table-content").setAttribute("aria-labelledby", `cal-capacity-${state.capacity}`);
    $("total-seats").textContent = tables.reduce((sum, table) => sum + table.capacity, 0);
    $("dining-duration").textContent = DINING_MINUTES;
    $("seating-description").textContent = state.mode === "preview" ? t("previewInventory") : t("liveInventory", { max: venue?.maximum_party_size || "—" });
    updateHours();
  }

  function openingHours() {
    if (!venue || state.mode !== "live") return null;
    const day = dateObject(state.date).toLocaleDateString("en-GB", { weekday: "long", timeZone: "UTC" }).toLowerCase();
    return Object.hasOwn(venue.closures, state.date) ? null : venue.opening_hours[day];
  }

  function updateHours() {
    const hours = openingHours();
    TIMELINE_START = state.mode === "preview" ? 17 * 60 : hours ? minutes(hours.start) : 12 * 60;
    TIMELINE_MINUTES = state.mode === "preview" ? 330 : hours ? minutes(hours.end) - TIMELINE_START : 9 * 60;
    const last = state.mode === "preview" ? 21 * 60 : TIMELINE_START + TIMELINE_MINUTES - DINING_MINUTES;
    const step = state.mode === "preview" ? 30 : (venue?.slot_interval_minutes || 15);
    const options = [];
    for (let time = TIMELINE_START; time <= last; time += step) {
      const value = `${String(Math.floor(time / 60)).padStart(2, "0")}:${String(time % 60).padStart(2, "0")}`;
      const option = element("option", "", timeLabel(value));
      option.value = value;
      options.push(option);
    }
    $("time-select").replaceChildren(...options);
    state.time = options.some(option => option.value === state.time) ? state.time : options[0]?.value || "12:00";
    $("time-select").value = state.time;
    $("booking-time").replaceChildren(...options.map(option => option.cloneNode(true)));
    $("timeline-note").textContent = t(state.mode === "preview" ? "previewTimeline" : "liveTimeline");
    $("venue-rules").textContent = venue ? t("rules", { zone: venue.timezone, duration: DINING_MINUTES, max: venue.maximum_party_size, hours: hours ? t("open", hours) : t("closed") }) : t("noVenue");
  }

  function usableWindow() {
    if (state.mode === "preview") return true;
    const hours = openingHours();
    const localNow = new Date().toLocaleTimeString("en-GB", { timeZone: venue?.timezone || "Europe/Tallinn", hour12: false });
    return Boolean(hours && state.date >= today() && (state.date !== today() || state.time > localNow.slice(0, 5)) && minutes(state.time) >= minutes(hours.start) && minutes(state.time) + DINING_MINUTES <= minutes(hours.end));
  }

  async function loadCalendar() {
    if (state.mode !== "live" || !connected) return;
    clearPrivate("reading");
    renderTables();
    const version = requestVersion;
    const requestedAt = performance.now();
    try {
      const data = await readCalendar(state.date);
      if (version !== requestVersion || state.mode !== "live" || !connected) return;
      if (data.date !== state.date || !Array.isArray(data.items) || !Array.isArray(data.restaurant?.tables)) throw new Error("invalid calendar");
      const fetchedAt = Date.parse(data.fetched_at);
      if (!Number.isFinite(fetchedAt) || data.items.some(item =>
        !["held", "confirmed"].includes(item.status) ||
        !Number.isFinite(Date.parse(item.start)) || !Number.isFinite(Date.parse(item.end)) ||
        Date.parse(item.end) <= Date.parse(item.start) ||
        !data.restaurant.tables.some(table => table.id === item.table_id) ||
        (item.status === "held" && !Number.isFinite(Date.parse(item.expires_at))) ||
        (item.expires_at != null && !Number.isFinite(Date.parse(item.expires_at)))
      )) throw new Error("invalid calendar interval");
      // Server-relative hold lifetime tolerates clock skew; include read latency.
      const lifetime = Math.min(60000, ...data.items.filter(item => item.expires_at != null).map(item => Date.parse(item.expires_at) - fetchedAt)) - (performance.now() - requestedAt);
      if (!(lifetime > 0)) throw new Error("expired calendar");
      venue = data.restaurant;
      configureRoom();
      state.bookings = data.items.map(item => ({ table: item.table_id, date: item.start.slice(0, 10), time: item.start.slice(11, 16), end: item.end, start: item.start, party: item.party_size, source: "live", status: item.status, expires: item.expires_at }));
      state.loaded = true;
      calendarStatus("updated", { time: new Date(data.fetched_at).toLocaleTimeString(locale(), { timeZone: venue.timezone }), zone: venue.timezone });
      staleTimer = setTimeout(() => { clearPrivate("expired"); renderTables(); }, lifetime);
      renderTables();
    } catch (error) {
      if (version !== requestVersion) return;
      clearPrivate("unavailable");
      renderTables();
    }
  }

  async function loadVenue() {
    try {
      const response = await fetch("/api/public/restaurant", { cache: "no-store" });
      if (!response.ok) throw new Error("venue unavailable");
      const data = await response.json();
      if (!venue) venue = data.restaurant;
      if (state.mode === "live") { configureRoom(); renderTables(); }
    } catch (_) {
      if (!venue && state.mode === "live") calendarStatus("noVenue");
    }
  }

  function changeMode(mode) {
    stopStory();
    clearTimeout(toastTimer);
    $("toast").hidden = true;
    $("booking-dialog").close();
    if (state.mode === "preview") previewBookings = state.bookings;
    clearPrivate();
    state.mode = mode;
    state.capacity = "all";
    state.bookings = mode === "preview" ? previewBookings : [];
    state.highlighted = null;
    state.date = mode === "preview" ? INITIAL_DATE : today();
    state.time = "19:00";
    renderMode();
    $("calendar-status").hidden = mode !== "live";
    $("preview-panel").hidden = mode !== "preview";
    $("live-panel").hidden = mode !== "live";
    $("real-booking").hidden = mode !== "live";
    $("new-booking").hidden = mode !== "preview";
    configureRoom();
    resetStoryView();
    renderWeek();
    renderTables();
    if (mode === "preview") playStory();
    else if (connected) loadCalendar();
  }

  function element(tag, className, content) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (content !== undefined) node.textContent = content;
    return node;
  }

  function icon(name) {
    const node = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    node.setAttribute("class", "icon");
    node.setAttribute("aria-hidden", "true");
    const use = document.createElementNS("http://www.w3.org/2000/svg", "use");
    use.setAttribute("href", `#cal-${name}`);
    node.append(use);
    return node;
  }

  function dateObject(value) {
    return new Date(`${value}T12:00:00Z`);
  }

  function validDate(value) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
    const date = dateObject(value);
    return Number.isFinite(date.getTime()) && date.toISOString().slice(0, 10) === value;
  }

  function dateLabel(value, options) {
    return dateObject(value).toLocaleDateString(locale(), { timeZone: "UTC", ...options });
  }

  function addDays(value, days) {
    const date = dateObject(value);
    date.setUTCDate(date.getUTCDate() + days);
    return date.toISOString().slice(0, 10);
  }

  function minutes(value) {
    const [hours, minute] = value.split(":").map(Number);
    return hours * 60 + minute;
  }

  function timeLabel(value) {
    return value.replace(":", ".");
  }

  function endTime(value) {
    const end = minutes(value) + DINING_MINUTES;
    return `${String(Math.floor(end / 60)).padStart(2, "0")}.${String(end % 60).padStart(2, "0")}`;
  }

  function overlaps(booking, date = state.date, time = state.time) {
    if (booking.source === "live") {
      // Local wall times share the server's configured timezone; use the actual interval.
      const start = `${date}T${time}:00`;
      const selectedEnd = `${date}T${endTime(time).replace(".", ":")}:00`;
      return booking.start.slice(0, 19) < selectedEnd && start < booking.end.slice(0, 19);
    }
    return booking.date === date && minutes(booking.time) < minutes(time) + DINING_MINUTES && minutes(time) < minutes(booking.time) + DINING_MINUTES;
  }

  function bookingFor(table, date = state.date, time = state.time) {
    return state.bookings.find((booking) => booking.table === table.id && overlaps(booking, date, time));
  }

  function bookingName(booking) {
    return booking.source === "live" ? t(booking.status === "held" ? "held" : "confirmed") : booking.name;
  }

  function visibleTables() {
    return tables.filter((table) => state.capacity === "all" || table.capacity === Number(state.capacity));
  }

  function showToast(key, values) {
    clearTimeout(toastTimer);
    toastCopy = { key, values };
    $("toast").textContent = t(key, values);
    $("toast").hidden = false;
    toastTimer = setTimeout(() => { $("toast").hidden = true; }, 4500);
  }

  function renderWeek() {
    const weekday = dateObject(state.date).getUTCDay();
    const monday = addDays(state.date, -((weekday + 6) % 7));
    const fragment = document.createDocumentFragment();
    for (let index = 0; index < 7; index++) {
      const value = addDays(monday, index);
      const day = element("button", "day-button");
      day.type = "button";
      day.dataset.date = value;
      day.setAttribute("aria-label", dateLabel(value, { weekday: "long", day: "numeric", month: "long", year: "numeric" }));
      day.setAttribute("aria-pressed", String(value === state.date));
      day.append(element("span", "", dateLabel(value, { weekday: "short" })), element("strong", "", String(dateObject(value).getUTCDate())));
      const dot = element("i");
      dot.setAttribute("aria-hidden", "true");
      day.append(dot);
      fragment.append(day);
    }
    $("week-strip").replaceChildren(fragment);
    $("date-heading").textContent = dateLabel(state.date, { day: "numeric", month: "long" });
    $("year-label").textContent = dateObject(state.date).getUTCFullYear();
    $("month-label").textContent = dateLabel(state.date, { month: "long", year: "numeric" });
    $("date-picker").value = state.date;
  }

  function openTable(table, booking = bookingFor(table)) {
    dialogTable = table;
    dialogBooking = booking;
    $("table-dialog-title").textContent = t("table", { number: table.number });
    $("table-dialog-description").textContent = t("tableDescription", { seats: t("seats", { count: table.capacity }), notice: t(state.mode === "live" ? "liveDetailNotice" : "previewDetailNotice") });
    if (state.mode === "live") {
      $("table-dialog-detail").textContent = !state.loaded ? t("unknownDetail") : booking ? `${bookingName(booking)}\n${t("guestsCount", { count: booking.party })}\n${booking.start.slice(11, 16)}–${booking.end.slice(11, 16)} · ${venue.timezone}` : !usableWindow() ? t("outsideDetail") : t("noConflictDetail");
      $("table-dialog").showModal();
      return;
    }
    $("table-dialog-detail").textContent = booking
      ? `${bookingName(booking)}\n${t("guestsCount", { count: booking.party })} · ${dateLabel(booking.date, { day: "numeric", month: "long" })}\n${timeLabel(booking.time)}–${endTime(booking.time)}\n${t(booking.source === "voicebot" ? "animatedBooking" : "sampleReservation")}`
      : state.highlighted === table.id && state.stage === "offering"
        ? t("suggested")
        : t("availableDetail", { date: dateLabel(state.date, { day: "numeric", month: "long" }), start: timeLabel(state.time), end: endTime(state.time) });
    $("table-dialog").showModal();
  }

  function renderFloor() {
    const fragment = document.createDocumentFragment();
    for (const table of visibleTables()) {
      const booking = bookingFor(table);
      const highlighted = state.highlighted === table.id;
      const unknown = state.mode === "live" && !state.loaded;
      const status = t(unknown ? "unknown" : booking ? (booking.status === "held" ? "held" : "reserved") : highlighted ? "selected" : !usableWindow() ? "outside" : state.mode === "live" ? "noConflict" : "available");
      const button = element("button", `table-button${unknown || (!booking && !usableWindow()) ? " unknown" : ""}${booking ? " reserved" : ""}${highlighted ? " highlighted" : ""}`);
      button.type = "button";
      button.dataset.table = table.id;
      button.setAttribute("aria-label", t("tableAria", { number: table.number, count: table.capacity, status }) + (highlighted ? t("voiceBooking") : ""));
      const shape = element("span", `table-shape seats-${table.capacity}`);
      shape.setAttribute("aria-hidden", "true");
      shape.append(element("strong", "", `T${table.number}`), element("span", "", t("seats", { count: table.capacity })));
      for (let index = 0; index < table.capacity; index++) shape.append(element("i", "chair"));
      if (highlighted && booking) {
        const check = element("b", "table-confirmed");
        check.append(icon("check"));
        shape.append(check);
      }
      button.append(shape, element("span", "table-caption", highlighted ? t(booking ? "justBooked" : "found") : status));
      button.addEventListener("click", () => openTable(table));
      fragment.append(button);
    }
    $("tables").replaceChildren(fragment);
  }

  function renderTimeline() {
    const fragment = document.createDocumentFragment();
    const heading = element("div", "timeline-heading");
    const hours = element("div", "timeline-hours");
    for (let hour = Math.ceil(TIMELINE_START / 60); hour * 60 < TIMELINE_START + TIMELINE_MINUTES; hour++) {
      const label = element("span", "", `${hour}.00`);
      label.style.left = `${((hour * 60 - TIMELINE_START) / TIMELINE_MINUTES) * 100}%`;
      hours.append(label);
    }
    heading.append(element("span", "", t("table", { number: "" }).trim()), hours);
    fragment.append(heading);
    for (const table of visibleTables()) {
      const row = element("div", "timeline-row");
      const label = element("button", "timeline-table-label", `${table.id} · ${t("seats", { count: table.capacity })}`);
      label.type = "button";
      label.setAttribute("aria-label", t("viewTable", { number: table.number }));
      label.addEventListener("click", () => openTable(table));
      const track = element("div", "timeline-track");
      for (const booking of state.bookings.filter((item) => item.date === state.date && item.table === table.id)) {
        const start = minutes(booking.time) - TIMELINE_START;
        const visibleStart = Math.max(0, start);
        const visibleEnd = Math.min(TIMELINE_MINUTES, start + (booking.source === "live" ? (Date.parse(booking.end) - Date.parse(booking.start)) / 60000 : DINING_MINUTES));
        if (visibleEnd <= visibleStart) continue;
        const block = element("button", `timeline-block${booking.source === "voicebot" ? " voicebot" : ""}`, `${timeLabel(booking.time)} ${bookingName(booking)}`);
        block.type = "button";
        block.style.left = `${(visibleStart / TIMELINE_MINUTES) * 100}%`;
        block.style.width = `${((visibleEnd - visibleStart) / TIMELINE_MINUTES) * 100}%`;
        block.setAttribute("aria-label", t("timelineAria", { name: bookingName(booking), table: table.id, start: timeLabel(booking.time), end: booking.source === "live" ? timeLabel(booking.end.slice(11, 16)) : endTime(booking.time), party: booking.party }));
        block.addEventListener("click", () => openTable(table, booking));
        track.append(block);
      }
      row.append(label, track);
      fragment.append(row);
    }
    $("timeline-grid").replaceChildren(fragment);
  }

  function renderTables() {
    // Keep keyboard focus on the same table when an animation updates the room.
    const focusedTable = document.activeElement?.dataset.table;
    renderFloor();
    renderTimeline();
    const visible = visibleTables();
    const seats = visible.reduce((total, table) => total + table.capacity, 0);
    const available = visible.filter((table) => !bookingFor(table)).length;
    $("table-summary").textContent = t("summary", { tables: visible.length, seats });
    $("availability-count").textContent = state.mode === "live" && !state.loaded ? t("occupancyUnknown") : !usableWindow() ? t("outside") : t(state.mode === "live" ? "noConflicts" : "availableCount", { count: available });
    if (focusedTable) $("tables").querySelector(`[data-table="${focusedTable}"]`)?.focus({ preventScroll: true });
  }

  function setStage(stage, status, caption, progress, values = {}) {
    state.stage = stage;
    stageCopy = { status, caption, progress, values };
    $("voice-stage").dataset.stage = stage;
    $("voice-status").textContent = t(status, values);
    $("voice-caption").textContent = t(caption, values);
    $("story-progress").style.width = `${progress}%`;
  }

  function stopStory() {
    state.storyVersion++;
    state.timers.forEach(clearTimeout);
    state.timers = [];
  }

  function showLatestMessage() {
    // Scroll only the transcript; keep the calendar and booking controls still.
    $("conversation").scrollTop = $("conversation").scrollHeight;
  }

  function resetStoryView() {
    state.highlighted = null;
    $("assistant-message").hidden = true;
    $("consent-message").hidden = true;
    $("booking-result").hidden = true;
    $("conversation").scrollTop = 0;
    replyCopy = resultCopy = null;
    renderStoryCopy();
    setStage("ready", "ready", "play", 0);
  }

  function setReply(key, values = {}) {
    replyCopy = { key, values };
    $("assistant-reply").textContent = t(key, values);
  }

  function renderStoryCopy() {
    const date = dateLabel(state.date, { day: "numeric", month: "long" });
    $("guest-message").querySelector("p").textContent = t("guestRequest", { date, time: timeLabel(state.time) });
    $("request-date").textContent = dateLabel(state.date, { day: "numeric", month: "short" });
    $("request-time").textContent = timeLabel(state.time);
    if (replyCopy) $("assistant-reply").textContent = t(replyCopy.key, { ...replyCopy.values, date });
    if (resultCopy) $("result-details").textContent = t("result", resultCopy);
  }

  function changeDate(value) {
    if (!validDate(value)) return;
    stopStory();
    state.date = value;
    if (state.mode === "live") {
      clearPrivate("dateChanged");
      updateHours();
      loadCalendar();
    }
    resetStoryView();
    renderWeek();
    renderTables();
  }

  function playStory() {
    if (state.mode !== "preview") return;
    stopStory();
    // Replace the single story reservation on replay; keep manual demo bookings.
    state.bookings = state.bookings.filter((booking) => booking.id !== "voice-demo");
    resetStoryView();
    setStage("ready", "calling", "watch", 0);
    renderTables();
    const version = state.storyVersion;
    const candidate = [tables[2], ...tables.filter((table) => table.capacity === 4 && table.id !== "T03")].find((table) => !bookingFor(table));
    const schedule = (delay, action) => {
      state.timers.push(setTimeout(() => { if (version === state.storyVersion) action(); }, delay));
    };
    schedule(650, () => setStage("listening", "listening", "request", 20));
    schedule(2100, () => {
      setStage("checking", "checking", "checkingWindow", 45);
      setReply("replyChecking");
      $("assistant-message").hidden = false;
      showLatestMessage();
    });
    schedule(3600, () => {
      if (!candidate) {
        stopStory();
        setStage("unavailable", "full", "tryAgain", 100);
        setReply("replyFull");
        showLatestMessage();
        return;
      }
      state.highlighted = candidate.id;
      const date = dateLabel(state.date, { day: "numeric", month: "long" });
      setReply("replyOffer", { number: candidate.number, date, time: timeLabel(state.time) });
      setStage("offering", "offering", "waiting", 70, { number: candidate.number });
      renderTables();
      showLatestMessage();
    });
    schedule(5200, () => {
      $("consent-message").hidden = false;
      showLatestMessage();
    });
    schedule(6200, () => {
      // Recheck the interval immediately before the simulated confirmation.
      if (!candidate || bookingFor(candidate)) {
        state.highlighted = null;
        setStage("unavailable", "noLonger", "tryAgain", 100);
        renderTables();
        return;
      }
      state.bookings.push({ id: "voice-demo", table: candidate.id, date: state.date, time: state.time, party: 4, name: "Alex Morgan", source: "voicebot" });
      setStage("confirmed", "allSet", "welcome", 100);
      resultCopy = { number: candidate.number, time: timeLabel(state.time) };
      $("result-details").textContent = t("result", resultCopy);
      $("booking-result").hidden = false;
      renderTables();
      showLatestMessage();
    });
  }

  function activateTab(tab) {
    const tablist = tab.closest('[role="tablist"]');
    for (const item of tablist.querySelectorAll('[role="tab"]')) {
      item.setAttribute("aria-selected", String(item === tab));
      item.tabIndex = item === tab ? 0 : -1;
    }
    if (tab.dataset.capacity) {
      state.capacity = tab.dataset.capacity;
      $("table-content").setAttribute("aria-labelledby", tab.id);
      renderTables();
    } else {
      state.view = tab.id === "cal-floor-tab" ? "floor" : "timeline";
      $("floor-view").hidden = state.view !== "floor";
      $("timeline-view").hidden = state.view !== "timeline";
    }
  }

  for (const tablist of root.querySelectorAll('[role="tablist"]')) {
    tablist.addEventListener("click", (event) => {
      const tab = event.target.closest('[role="tab"]');
      if (tab) activateTab(tab);
    });
    tablist.addEventListener("keydown", (event) => {
      if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
      const tabs = [...tablist.querySelectorAll('[role="tab"]')];
      const current = tabs.indexOf(document.activeElement);
      if (current < 0) return;
      event.preventDefault();
      const index = event.key === "Home" ? 0 : event.key === "End" ? tabs.length - 1 : (current + (event.key === "ArrowRight" ? 1 : -1) + tabs.length) % tabs.length;
      activateTab(tabs[index]);
      tabs[index].focus();
    });
  }

  $("week-strip").addEventListener("click", (event) => {
    const button = event.target.closest("[data-date]");
    if (button) {
      changeDate(button.dataset.date);
      $("week-strip").querySelector(`[data-date="${state.date}"]`)?.focus({ preventScroll: true });
    }
  });
  $("previous-week").addEventListener("click", () => changeDate(addDays(state.date, -7)));
  $("next-week").addEventListener("click", () => changeDate(addDays(state.date, 7)));
  $("date-picker").addEventListener("change", (event) => changeDate(event.target.value));
  $("time-select").addEventListener("change", (event) => {
    stopStory();
    state.time = event.target.value;
    resetStoryView();
    renderTables();
  });
  $("replay").addEventListener("click", playStory);
  root.querySelectorAll("[data-close]").forEach((button) => button.addEventListener("click", () => $(button.dataset.close).close()));
  $("booking-time").replaceChildren(...[...$("time-select").options].map((option) => option.cloneNode(true)));
  $("new-booking").addEventListener("click", () => {
    if (state.mode !== "preview") return;
    stopStory();
    resetStoryView();
    renderTables();
    $("booking-date").value = state.date;
    $("booking-time").value = state.time;
    $("booking-error").hidden = true;
    $("booking-dialog").showModal();
  });
  $("booking-form").addEventListener("submit", (event) => {
    event.preventDefault();
    if (state.mode !== "preview") return;
    const name = $("booking-name").value.trim();
    const date = $("booking-date").value;
    const time = $("booking-time").value;
    const party = Number($("booking-party").value);
    const fail = (key, values = {}) => { errorCopy = { key, values }; $("booking-error").textContent = t(key, values); $("booking-error").hidden = false; };
    if (!name) return fail("nameRequired");
    if (!validDate(date)) return fail("dateRequired");
    if (![...$("booking-time").options].some((option) => option.value === time) || ![2, 4, 8].includes(party)) return fail("optionsRequired");
    const table = tables.find((item) => item.capacity === party && !bookingFor(item, date, time));
    if (!table) return fail("fullError", { party });
    state.bookings.push({ id: `manual-${++bookingSequence}`, table: table.id, date, time, party, name, source: "manual" });
    state.date = date;
    state.time = time;
    $("time-select").value = time;
    resetStoryView();
    state.highlighted = table.id;
    renderWeek();
    renderTables();
    $("booking-dialog").close();
    showToast("added", { name, number: table.number, time: timeLabel(time) });
  });
  for (let index = 0; index < 25; index++) {
    const bar = element("i");
    const distance = Math.abs(index - 12);
    bar.style.setProperty("--height", `${12 + (12 - distance) * 2.7 + ((index * 7) % 11)}px`);
    bar.style.setProperty("--delay", `${-(index * 0.11)}s`);
    $("waveform").append(bar);
  }
  $("calendar-mode").addEventListener("change", event => changeMode(event.target.value));
  $("refresh-calendar").addEventListener("click", loadCalendar);

  function renderMode() {
    $("mode-badge").textContent = t(state.mode === "preview" ? "preview" : "liveBadge");
    $("mode-notice").textContent = t(state.mode === "preview" ? "previewNotice" : "liveNotice");
  }

  function setLanguage(value) {
    if (!["et", "en", "ru"].includes(value)) return;
    language = value;
    for (const node of root.querySelectorAll("[data-calendar-copy]")) node.textContent = t(node.dataset.calendarCopy);
    for (const node of root.querySelectorAll("[data-calendar-aria]")) node.setAttribute("aria-label", t(node.dataset.calendarAria));
    const bookingTime = $("booking-time").value;
    configureRoom();
    if (bookingTime) $("booking-time").value = bookingTime;
    renderMode();
    calendarStatus(statusKey, statusValues);
    renderWeek();
    renderTables();
    renderStoryCopy();
    if (stageCopy) setStage(state.stage, stageCopy.status, stageCopy.caption, stageCopy.progress, stageCopy.values);
    if (errorCopy) $("booking-error").textContent = t(errorCopy.key, errorCopy.values);
    if (toastCopy) $("toast").textContent = t(toastCopy.key, toastCopy.values);
    if (dialogTable && $("table-dialog").open) openTable(dialogTable, dialogBooking);
  }

  function clear() {
    stopStory();
    clearTimeout(toastTimer);
    $("toast").hidden = true;
    $("booking-dialog").close();
    if (state.mode === "preview") previewBookings = state.bookings;
    clearPrivate();
    state.highlighted = null;
    if (state.mode === "preview") state.bookings = previewBookings;
    resetStoryView();
    renderTables();
  }

  setLanguage(language);
  resetStoryView();
  loadVenue();
  return { setConnected, setLanguage, refresh: loadCalendar, clear };
};
