(() => {
  "use strict";

  const $ = (id) => document.getElementById(id);
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
  let credential = "";
  let controller;
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

  function clearPrivate(message) {
    requestVersion++;
    controller?.abort();
    clearTimeout(staleTimer);
    state.loaded = false;
    state.bookings = [];
    $("table-dialog").close();
    $("table-dialog-detail").textContent = "";
    $("table-dialog-description").textContent = "";
    $("calendar-status").textContent = message;
  }

  function disconnect() {
    credential = "";
    $("operator-key").value = "";
    $("refresh-calendar").disabled = true;
    $("disconnect-calendar").disabled = true;
    clearPrivate("Occupancy unknown. Connect to read the calendar. Credentials stay only in page memory.");
    if (state.mode === "live") renderTables();
  }

  function configureRoom() {
    tables = state.mode === "preview" ? previewTables : (venue?.tables || []).map(table => ({ ...table, number: String(table.id).padStart(2, "0") }));
    DINING_MINUTES = state.mode === "preview" ? 90 : (venue?.reservation_duration_minutes || 90);
    const capacities = state.mode === "preview" ? [4, 2, 8] : [...new Set(tables.map(table => table.capacity))].sort((a, b) => a - b);
    const tabs = ["all", ...capacities].map(capacity => {
      const tab = element("button", "", capacity === "all" ? "All tables " : `${capacity} people `);
      tab.id = `capacity-${capacity}`;
      tab.type = "button";
      tab.dataset.capacity = capacity;
      tab.setAttribute("role", "tab");
      tab.setAttribute("aria-selected", String(capacity === "all"));
      tab.setAttribute("aria-controls", "table-content");
      tab.tabIndex = capacity === "all" ? 0 : -1;
      tab.append(element("span", "", String(capacity === "all" ? tables.length : tables.filter(t => t.capacity === capacity).length)));
      return tab;
    });
    document.querySelector(".capacity-tabs").replaceChildren(...tabs);
    state.capacity = "all";
    $("table-content").setAttribute("aria-labelledby", "capacity-all");
    $("total-seats").textContent = tables.reduce((sum, table) => sum + table.capacity, 0);
    $("dining-duration").textContent = DINING_MINUTES;
    $("seating-description").textContent = state.mode === "preview" ? "Twelve fictional tables. Preview inventory only." : `Configured tables · maximum party ${venue?.maximum_party_size || "—"}`;
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
    $("timeline-note").textContent = state.mode === "preview" ? "Fictional reservations include a 90-minute dining window." : "Read-only snapshot: confirmed reservations and active holds. Unknown when disconnected or stale.";
    $("venue-rules").textContent = venue ? `${venue.timezone} · ${DINING_MINUTES} minutes per reservation · maximum party ${venue.maximum_party_size}. ${hours ? `Open ${hours.start}–${hours.end} on this date.` : "Closed on this date."}` : "Venue configuration unavailable.";
  }

  function usableWindow() {
    if (state.mode === "preview") return true;
    const hours = openingHours();
    const localNow = new Date().toLocaleTimeString("en-GB", { timeZone: venue?.timezone || "Europe/Tallinn", hour12: false });
    return Boolean(hours && state.date >= today() && (state.date !== today() || state.time > localNow.slice(0, 5)) && minutes(state.time) >= minutes(hours.start) && minutes(state.time) + DINING_MINUTES <= minutes(hours.end));
  }

  async function loadCalendar() {
    if (state.mode !== "live" || !credential) return;
    clearPrivate("Reading calendar… Occupancy unknown.");
    renderTables();
    const version = requestVersion;
    controller = new AbortController();
    try {
      const response = await fetch(`/api/restaurant/calendar?date=${encodeURIComponent(state.date)}`, { headers: { Authorization: `Bearer ${credential}` }, cache: "no-store", signal: controller.signal });
      if (!response.ok) throw new Error("read failed");
      const data = await response.json();
      if (version !== requestVersion || state.mode !== "live" || !credential) return;
      if (data.date !== state.date || !Array.isArray(data.items) || !Array.isArray(data.restaurant?.tables)) throw new Error("invalid calendar");
      venue = data.restaurant;
      configureRoom();
      state.bookings = data.items.map(item => ({ table: item.table_id, date: item.start.slice(0, 10), time: item.start.slice(11, 16), end: item.end, start: item.start, party: item.party_size, name: item.status === "held" ? "Held" : "Confirmed reservation", source: "live", status: item.status, expires: item.expires_at }));
      state.loaded = true;
      $("calendar-status").textContent = `Updated ${new Date(data.fetched_at).toLocaleTimeString("en-GB", { timeZone: venue.timezone })} · ${venue.timezone}. Read-only synthetic inventory; refresh before booking.`;
      const expiry = Math.min(Date.now() + 60000, ...state.bookings.filter(b => b.expires).map(b => Date.now() + Date.parse(b.expires) - Date.parse(data.fetched_at)));
      staleTimer = setTimeout(() => { clearPrivate("Snapshot expired. Occupancy unknown; refresh to read current bookings and holds."); renderTables(); }, Math.max(0, expiry - Date.now()));
      renderTables();
    } catch (error) {
      if (version !== requestVersion) return;
      clearPrivate("Calendar unavailable. Occupancy unknown; check the credential and refresh to retry.");
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
      if (!venue && state.mode === "live") $("calendar-status").textContent = "Venue configuration unavailable. Occupancy unknown; reload to retry.";
    }
  }

  function changeMode(mode) {
    stopStory();
    clearTimeout(toastTimer);
    $("toast").hidden = true;
    $("booking-dialog").close();
    if (state.mode === "preview") previewBookings = state.bookings;
    disconnect();
    state.mode = mode;
    state.bookings = mode === "preview" ? previewBookings : [];
    state.highlighted = null;
    state.date = mode === "preview" ? INITIAL_DATE : today();
    state.time = "19:00";
    $("mode-badge").textContent = mode === "preview" ? "Fictional preview" : "Live operator view";
    $("mode-notice").textContent = mode === "preview" ? "PREVIEW ONLY: twelve fictional tables, samples and animation are not stored bookings. Nothing here reserves the configured restaurant inventory." : "Live view of saved synthetic restaurant bookings and active holds. Occupancy is private until connected.";
    $("calendar-auth").hidden = mode !== "live";
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
    use.setAttribute("href", `#${name}`);
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
    return dateObject(value).toLocaleDateString("en-GB", { timeZone: "UTC", ...options });
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

  function visibleTables() {
    return tables.filter((table) => state.capacity === "all" || table.capacity === Number(state.capacity));
  }

  function showToast(message) {
    clearTimeout(toastTimer);
    $("toast").textContent = message;
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
    $("table-dialog-title").textContent = `Table ${table.number}`;
    $("table-dialog-description").textContent = `${table.capacity} seats. ${state.mode === "live" ? "Configured synthetic venue; read-only snapshot." : "All details are fictional preview samples."}`;
    if (state.mode === "live") {
      $("table-dialog-detail").textContent = !state.loaded ? "Occupancy unknown. Connect or refresh the calendar." : booking ? `${booking.name}\n${booking.party} guests\n${booking.start.slice(11, 16)}–${booking.end.slice(11, 16)} · ${venue.timezone}` : !usableWindow() ? "Outside the booking window. Check opening hours and choose a future arrival." : "No conflict in this snapshot. Prepare a reservation in the dashboard; the allocator rechecks inventory before explicit consent.";
      $("table-dialog").showModal();
      return;
    }
    $("table-dialog-detail").textContent = booking
      ? `${booking.name}\n${booking.party} guests · ${dateLabel(booking.date, { day: "numeric", month: "long" })}\n${timeLabel(booking.time)}–${endTime(booking.time)}\n${booking.source === "voicebot" ? "Booked in the voicebot animation" : "Sample reservation"}`
      : state.highlighted === table.id && state.stage === "offering"
        ? `Suggested for the sample call.\nWaiting for the guest to confirm.`
        : `Available for ${dateLabel(state.date, { day: "numeric", month: "long" })}\n${timeLabel(state.time)}–${endTime(state.time)}`;
    $("table-dialog").showModal();
  }

  function renderFloor() {
    const fragment = document.createDocumentFragment();
    for (const table of visibleTables()) {
      const booking = bookingFor(table);
      const highlighted = state.highlighted === table.id;
      const unknown = state.mode === "live" && !state.loaded;
      const status = unknown ? "Unknown" : booking ? (booking.status === "held" ? "Held" : "Reserved") : highlighted ? "Selected" : !usableWindow() ? "Outside booking hours" : state.mode === "live" ? "No conflict" : "Available";
      const button = element("button", `table-button${unknown || (!booking && !usableWindow()) ? " unknown" : ""}${booking ? " reserved" : ""}${highlighted ? " highlighted" : ""}`);
      button.type = "button";
      button.dataset.table = table.id;
      button.setAttribute("aria-label", `Table ${table.number}, ${table.capacity} people, ${status}${highlighted ? ", voicebot booking" : ""}`);
      const shape = element("span", `table-shape seats-${table.capacity}`);
      shape.setAttribute("aria-hidden", "true");
      shape.append(element("strong", "", `T${table.number}`), element("span", "", `${table.capacity} seats`));
      for (let index = 0; index < table.capacity; index++) shape.append(element("i", "chair"));
      if (highlighted && booking) {
        const check = element("b", "table-confirmed");
        check.append(icon("check"));
        shape.append(check);
      }
      button.append(shape, element("span", "table-caption", highlighted ? (booking ? "Just booked" : "Table found") : status));
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
    heading.append(element("span", "", "Table"), hours);
    fragment.append(heading);
    for (const table of visibleTables()) {
      const row = element("div", "timeline-row");
      const label = element("button", "timeline-table-label", `${table.id} · ${table.capacity} seats`);
      label.type = "button";
      label.setAttribute("aria-label", `View table ${table.number} details`);
      label.addEventListener("click", () => openTable(table));
      const track = element("div", "timeline-track");
      for (const booking of state.bookings.filter((item) => item.date === state.date && item.table === table.id)) {
        const start = minutes(booking.time) - TIMELINE_START;
        const visibleStart = Math.max(0, start);
        const visibleEnd = Math.min(TIMELINE_MINUTES, start + (booking.source === "live" ? (Date.parse(booking.end) - Date.parse(booking.start)) / 60000 : DINING_MINUTES));
        if (visibleEnd <= visibleStart) continue;
        const block = element("button", `timeline-block${booking.source === "voicebot" ? " voicebot" : ""}`, `${timeLabel(booking.time)} ${booking.name}`);
        block.type = "button";
        block.style.left = `${(visibleStart / TIMELINE_MINUTES) * 100}%`;
        block.style.width = `${((visibleEnd - visibleStart) / TIMELINE_MINUTES) * 100}%`;
        block.setAttribute("aria-label", `${booking.name}, ${table.id}, ${timeLabel(booking.time)} to ${endTime(booking.time)}, ${booking.party} guests`);
        block.addEventListener("click", () => {
          if (state.mode === "live") { openTable(table, booking); return; }
          $("table-dialog-title").textContent = `Table ${table.number} reservation`;
          $("table-dialog-description").textContent = "Fictional demo reservation.";
          $("table-dialog-detail").textContent = `${booking.name}\n${booking.party} guests · ${dateLabel(booking.date, { day: "numeric", month: "long" })}\n${timeLabel(booking.time)}–${endTime(booking.time)}`;
          $("table-dialog").showModal();
        });
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
    $("table-summary").textContent = `${visible.length} tables · ${seats} seats`;
    $("availability-count").textContent = state.mode === "live" && !state.loaded ? "Occupancy unknown" : !usableWindow() ? "Outside booking hours" : state.mode === "live" ? `${available} tables with no conflict · snapshot` : `${available} ${available === 1 ? "table" : "tables"} available`;
    if (focusedTable) $("tables").querySelector(`[data-table="${focusedTable}"]`)?.focus({ preventScroll: true });
  }

  function setStage(stage, status, caption, progress) {
    state.stage = stage;
    $("voice-stage").dataset.stage = stage;
    $("voice-status").textContent = status;
    $("voice-caption").textContent = caption;
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
    const date = dateLabel(state.date, { day: "numeric", month: "long" });
    $("guest-message").querySelector("p").textContent = `“A table for four on ${date}, at ${timeLabel(state.time)}, please.”`;
    $("request-date").textContent = dateLabel(state.date, { day: "numeric", month: "short" });
    $("request-time").textContent = timeLabel(state.time);
    setStage("ready", "Ready for a sample call", "Play the booking animation", 0);
  }

  function changeDate(value) {
    if (!validDate(value)) return;
    stopStory();
    state.date = value;
    if (state.mode === "live") {
      clearPrivate("Occupancy unknown. Connect or refresh for this date.");
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
    setStage("ready", "A guest is calling…", "Watch a booking come together", 0);
    renderTables();
    const version = state.storyVersion;
    const candidate = [tables[2], ...tables.filter((table) => table.capacity === 4 && table.id !== "T03")].find((table) => !bookingFor(table));
    const schedule = (delay, action) => {
      state.timers.push(setTimeout(() => { if (version === state.storyVersion) action(); }, delay));
    };
    schedule(650, () => setStage("listening", "Listening to the guest", "Date, time, and a table for four", 20));
    schedule(2100, () => {
      setStage("checking", "Finding the right table…", "Checking the 90-minute dining window", 45);
      $("assistant-reply").textContent = "Let me find you a lovely spot.";
      $("assistant-message").hidden = false;
      showLatestMessage();
    });
    schedule(3600, () => {
      if (!candidate) {
        stopStory();
        setStage("unavailable", "The four-person tables are full", "Choose another time and replay", 100);
        $("assistant-reply").textContent = "There isn’t a four-person table for this time. Shall we try another time?";
        showLatestMessage();
        return;
      }
      state.highlighted = candidate.id;
      const date = dateLabel(state.date, { day: "numeric", month: "long" });
      $("assistant-reply").textContent = `Table ${candidate.number} for four on ${date}, at ${timeLabel(state.time)}. Does that work for you?`;
      setStage("offering", `Table ${candidate.number} is a perfect fit`, "Waiting for the guest’s confirmation", 70);
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
        setStage("unavailable", "That table is no longer available", "Choose another time and replay", 100);
        renderTables();
        return;
      }
      state.bookings.push({ id: "voice-demo", table: candidate.id, date: state.date, time: state.time, party: 4, name: "Alex Morgan", source: "voicebot" });
      setStage("confirmed", "All set. We’ll see you soon.", "A warm welcome starts here", 100);
      $("result-details").textContent = `Table ${candidate.number} · 4 guests · ${timeLabel(state.time)}`;
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
      state.view = tab.id === "floor-tab" ? "floor" : "timeline";
      $("floor-view").hidden = state.view !== "floor";
      $("timeline-view").hidden = state.view !== "timeline";
    }
  }

  for (const tablist of document.querySelectorAll('[role="tablist"]')) {
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
  document.querySelectorAll("[data-close]").forEach((button) => button.addEventListener("click", () => $(button.dataset.close).close()));
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
    const fail = (message) => { $("booking-error").textContent = message; $("booking-error").hidden = false; };
    if (!name) return fail("Enter a guest name to continue.");
    if (!validDate(date)) return fail("Choose a valid date to continue.");
    if (![...$("booking-time").options].some((option) => option.value === time) || ![2, 4, 8].includes(party)) return fail("Choose a listed arrival time and party size.");
    const table = tables.find((item) => item.capacity === party && !bookingFor(item, date, time));
    if (!table) return fail(`All tables for ${party} people are reserved during this dining window. Try another arrival time or date.`);
    state.bookings.push({ id: `manual-${++bookingSequence}`, table: table.id, date, time, party, name, source: "manual" });
    state.date = date;
    state.time = time;
    $("time-select").value = time;
    resetStoryView();
    state.highlighted = table.id;
    renderWeek();
    renderTables();
    $("booking-dialog").close();
    showToast(`Demo booking added: ${name}, table ${table.number}, ${timeLabel(time)}.`);
  });
  for (let index = 0; index < 25; index++) {
    const bar = element("i");
    const distance = Math.abs(index - 12);
    bar.style.setProperty("--height", `${12 + (12 - distance) * 2.7 + ((index * 7) % 11)}px`);
    bar.style.setProperty("--delay", `${-(index * 0.11)}s`);
    $("waveform").append(bar);
  }
  $("calendar-mode").addEventListener("change", event => changeMode(event.target.value));
  $("calendar-auth").addEventListener("submit", event => {
    event.preventDefault();
    const entered = $("operator-key").value.trim();
    disconnect();
    credential = entered;
    if (!credential) return;
    $("operator-key").value = "";
    $("refresh-calendar").disabled = false;
    $("disconnect-calendar").disabled = false;
    loadCalendar();
  });
  $("refresh-calendar").addEventListener("click", loadCalendar);
  $("disconnect-calendar").addEventListener("click", disconnect);
  window.addEventListener("pagehide", () => { stopStory(); clearTimeout(toastTimer); disconnect(); });
  configureRoom();
  renderWeek();
  renderTables();
  loadVenue();
})();
