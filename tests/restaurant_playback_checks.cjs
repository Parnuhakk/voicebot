// The actual restaurant playback script with controlled media events.
const assert = require('node:assert/strict'), fs = require('node:fs'), vm = require('node:vm');
const testCase = process.argv[2], reply = 'Canonical table recap. Does that work for you?';
let now = 0, urlId = 0;
const audio = {
  src: '', currentSrc: '', ended: false, duration: 2, currentTime: 0,
  played: {length: 0}, paused: true,
  pause() {if (!this.paused) {this.paused = true; this.onpause?.();}},
  load() {this.currentSrc = this.src; this.ended = false; this.played = {length: 0};},
  removeAttribute() {this.src = '';},
  play() {this.currentSrc = this.src; this.paused = false; this.onplaying?.(); return Promise.resolve();},
};
const span = {textContent: reply}, message = {querySelector: () => span};
const elements = new Map([
  ['demo-audio', audio], ['demo-status', {textContent: 'Ready'}],
  ['demo-messages', {contains: node => node === message}],
  ['demo-recap-read', {}], ['demo-recap-timer', {}],
]);
const state = {connected: true, generation: 1, sessionId: 'fixture', audioEpoch: 1,
  recapDeliveryId: null, recap: null, turnBusy: false};
const context = vm.createContext({
  state, $: id => elements.get(id), Blob, atob, btoa, Uint8Array,
  performance: {now: () => now}, window: {},
  URL: {createObjectURL: () => 'blob:fixture/' + ++urlId, revokeObjectURL() {}},
  setTimeout: () => 1, clearTimeout() {}, clearInterval() {},
  proposalCountdown: () => 1, controls() {}, recapPlayedMessage: () => 'Delivered',
  status: (id, text) => {elements.get(id).textContent = text;},
  demoCopy: () => ({replyPlayed: 'Played'}),
});
vm.runInContext(fs.readFileSync('app/restaurant/static/speech-playback.js', 'utf8'), context);
const run = code => vm.runInContext(code, context);
context.data = {reply, outcome: 'ok', recap_delivery_id: 'a'.repeat(32), recap_expires_in_s: 60,
  audio_b64: 'SUQz', audio_type: 'audio/mpeg'};
context.message = message;
run('const recap = renderRecap(data, message); playReply(data, recap);');
const playback = state.playback;
const ended = (through = 2) => {
  audio.currentTime = 2; audio.ended = true;
  audio.played = {length: 1, start: () => 0, end: () => through};
  audio.pause(); audio.onended?.();
};
let expected = null;
if (testCase === 'buffering') {
  audio.currentTime = .5; audio.onwaiting?.(); audio.onstalled?.(); ended(); expected = context.data.recap_delivery_id;
} else if (testCase === 'partial') ended(1);
else if (testCase === 'seek') {audio.onseeking(); ended();}
else if (testCase === 'pause') {audio.pause(); audio.play(); ended();}
else if (testCase === 'terminal_race') {
  playback.recap = null; playback.complete = false; ended();
  assert.equal(state.recapDeliveryId, null);
  playback.complete = true; state.turnBusy = true;
  run('finishStreamPlayback({...data, _stream: {playback: state.playback}}, recap)');
  expected = context.data.recap_delivery_id;
} else if (testCase === 'eof_race') {
  playback.appended = false; ended(); assert.equal(state.recapDeliveryId, null);
  playback.source = {readyState: 'open', endOfStream() {this.readyState = 'ended';}};
  playback.buffer = {updating: false};
  run('pumpStreamAudio(state.playback)'); expected = context.data.recap_delivery_id;
} else if (testCase === 'stale') {
  const oldEnd = audio.onended; run('stopAudio(); playReply(data);'); ended(); oldEnd();
} else if (testCase === 'expired') {now = 61000; ended();}
else if (testCase === 'changed_text') {span.textContent = 'Another table'; ended();}
else throw new Error('Unknown playback case');
assert.equal(state.recapDeliveryId, expected);
console.log(testCase + '_ok');
