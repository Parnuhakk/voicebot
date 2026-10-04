"""Fictional ET/EN/RU native RTC acceptance, not microphone/PSTN proof.

Run only after the parent verifies the deployed worker revision and idle lock.
Speech, audio and credentials remain in memory; cleanup preserves ledger history.
"""

import argparse
import array
import asyncio
from datetime import datetime, timedelta
import gc
import inspect
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import traceback
import uuid
import wave
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).parent))
from app.restaurant_call import COPY, restaurant_spoken_date

REPLY_TIMEOUT = 60
CONVERSATION_TIMEOUT = 240
CLEANUP_STEP_TIMEOUT = 4
CALLER_TTS_TIMEOUT = 40
CREDENTIAL_TIMEOUT = 15
PROCESS_STOP_TIMEOUT = 1

# Fixed child code: keys only in its environment, caller phrase only on stdin,
# WAV only on the private binary pipe. No parent HTTP client/executor thread.
TTS_CODE = """
import json,os,sys
from app.providers.azure_tts import AzureTtsClient
try:
 args=json.load(sys.stdin)
 client=AzureTtsClient(os.environ['AZURE_SPEECH_KEY'],os.environ['AZURE_REGION'],args['voice'],args['locale'],output_format='riff-24khz-16bit-mono-pcm')
 try: audio=client.synthesize(args['text'])
 finally: client.close()
 sys.stdout.buffer.write(audio)
except Exception:
 sys.exit(1)
"""

# Preserve the existing credential source. Its result is captured privately in
# memory, never emitted by this runner; the process also bounds docker inspect.
CREDENTIAL_CODE = """
import json,sys
sys.path.insert(0,'deploy/telephony')
from probe import credentials
try: print(json.dumps(credentials(sys.argv[1])))
except Exception: sys.exit(1)
"""

# A key prefix alone is not ownership. Bind the canonical venue, native hold/key,
# confirmation fingerprint, scoped guest-001 hash and immutable response fields.
OWNED_CODE = r"""
import asyncio,hashlib,json,re,sqlite3,sys,uuid
from pathlib import Path
from app.business import business_type,restaurant_database,restaurant_writes_enabled
from app.demo import load_demo_data,scoped_guest
from app.restaurant_data import load_restaurant_data
from app.booking.restaurant import RestaurantAdapter

def owned(args):
 scope=args['call_id']
 if not isinstance(scope,str) or not re.fullmatch('[a-f0-9]{32}',scope): raise ValueError()
 if type(args.get('cleanup',False)) is not bool or business_type()!='restaurant': raise ValueError()
 data=load_restaurant_data(); venue=data['restaurant_id']; path=Path(restaurant_database())
 if not path.is_absolute() or not path.is_file(): raise ValueError()
 guest=scoped_guest(load_demo_data(),'guest-001',scope)
 guest_hash=hashlib.sha256(guest['email'].encode()).hexdigest()
 prefix='tel-'+scope+'-'
 db=sqlite3.connect(path.as_uri()+'?mode=ro',uri=True,timeout=5); db.row_factory=sqlite3.Row
 try:
  db.execute('BEGIN')
  rows=db.execute('SELECT * FROM restaurant_reservations WHERE restaurant_id=? AND guest_scope_hash=? ORDER BY id LIMIT 65',(venue,guest_hash)).fetchall()
  scoped_actions=db.execute('SELECT key,request_hash,response_json FROM restaurant_actions WHERE restaurant_id=? AND substr(key,1,?)=? LIMIT 65',(venue,len(prefix),prefix)).fetchall()
  if len(rows)>64 or len(scoped_actions)>64: raise ValueError()
  if any(not re.fullmatch(re.escape(prefix)+'[a-f0-9]{64}',action['key']) for action in scoped_actions): raise ValueError()
  actions={action['key']:action for action in scoped_actions}
  items=[]
  for row in rows:
   hold=row['hold_id']
   if not re.fullmatch('restaurant_hold_[a-f0-9]{32}',hold): raise ValueError()
   # CallTools hashes hold-only arguments BEFORE injecting the bound guest.
   native_key=prefix+hashlib.sha256(('confirm_slot_booking'+json.dumps({'hold_id':hold},sort_keys=True)).encode()).hexdigest()
   action=actions.pop(native_key,None)
   if action is None: raise ValueError()
   result=json.loads(action['response_json'])
   if not isinstance(result,dict) or result.get('ok') is not True: raise ValueError()
   booking=result.get('booking')
   if not isinstance(booking,dict) or type(booking.get('id')) is not int or booking['id']<=0: raise ValueError()
   if row['guest_scope_hash']!=guest_hash: raise ValueError()
   if action['request_hash']!=RestaurantAdapter._request_hash('confirm',hold,guest_hash): raise ValueError()
   expected={'id':row['id'],'table_id':row['table_id'],'party_size':row['party_size'],'start':row['start_local'],'end':row['end_local'],'status':'confirmed','synthetic':True}
   if booking!=expected or type(booking.get('party_size')) is not int or booking.get('synthetic') is not True: raise ValueError()
   if row['status'] not in ('confirmed','cancelled'): raise ValueError()
   items.append({**expected,'status':row['status']})
  # A stale/malformed scoped confirmation cannot masquerade as zero rows.
  # The only other canonical native journal response is owned cancellation.
  by_id={str(item['id']):item for item in items}
  for action in actions.values():
   result=json.loads(action['response_json'])
   if not isinstance(result,dict) or set(result)!={'ok','booking_id','status'} or result['ok'] is not True or result['status']!='cancelled': raise ValueError()
   booking_id=result['booking_id']
   if not isinstance(booking_id,str) or booking_id not in by_id or by_id[booking_id]['status']!='cancelled': raise ValueError()
   native_key=prefix+hashlib.sha256(('cancel_slot_booking'+json.dumps({'booking_id':booking_id},sort_keys=True)).encode()).hexdigest()
   if action['key']!=native_key or action['request_hash']!=RestaurantAdapter._request_hash('cancel',booking_id): raise ValueError()
 finally:
  db.close()
 if args.get('cleanup') and any(item['status']=='confirmed' for item in items):
  if not restaurant_writes_enabled(): raise ValueError()
  async def clean():
   adapter=RestaurantAdapter(str(path),data=data,allow_writes=restaurant_writes_enabled())
   try:
    for item in items:
     if item['status']!='confirmed': continue
     key='probe-cleanup-'+scope+'-'+str(item['id'])+'-'+uuid.uuid4().hex
     response=await adapter.cancel(str(item['id']),key)
     if response.get('ok') is not True or response.get('status')!='cancelled' or response.get('booking_id')!=str(item['id']): raise ValueError()
     item['status']='cancelled'
   finally:
    await adapter.close()
  asyncio.run(clean())
 return {'items':items}

try:
 print(json.dumps(owned(json.loads(sys.argv[1]))))
except Exception:
 print(json.dumps({'error':'probe_ledger_read_failed'})); sys.exit(1)
"""


def owned_command(container, call_id, cleanup):
    if not isinstance(call_id, str) or not re.fullmatch(r"[a-f0-9]{32}", call_id):
        raise ValueError("probe_scope_invalid")
    if not isinstance(container, str) or not re.fullmatch(
        r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", container
    ):
        raise ValueError("probe_container_invalid")
    return [
        "docker",
        "exec",
        container,
        "python",
        "-c",
        OWNED_CODE,
        json.dumps({"call_id": call_id, "cleanup": cleanup}),
    ]


def owned_items(raw):
    data = json.loads(raw)
    if (
        not isinstance(data, dict)
        or set(data) != {"items"}
        or not isinstance(data["items"], list)
    ):
        raise ValueError()
    return data["items"]


def read_owned(container, call_id, *, cleanup=False):
    command = owned_command(container, call_id, cleanup)
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode:
            raise ValueError()
        return owned_items(result.stdout)
    except (OSError, ValueError, TypeError, subprocess.TimeoutExpired):
        raise RuntimeError("probe_ledger_read_failed") from None


def child_environment():
    return {
        "HOME": "/home/arle",
        "PATH": "/usr/bin:/bin",
        "TMPDIR": "/tmp/opencode",
        "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
        "PYTHONDONTWRITEBYTECODE": "1",
    }


async def stop_process(process):
    if process.returncode is not None:
        return
    try:
        process.terminate()
    except ProcessLookupError:
        pass
    try:
        async with asyncio.timeout(PROCESS_STOP_TIMEOUT):
            await process.wait()
    except TimeoutError:
        pass
    finally:
        if process.returncode is None:
            try:
                process.kill()
            except ProcessLookupError:
                pass
            async with asyncio.timeout(PROCESS_STOP_TIMEOUT):
                await process.wait()


async def process_bytes(command, *, timeout, code, data=None, env=None):
    process, communication = None, None
    try:
        async with asyncio.timeout(timeout):
            process = await asyncio.create_subprocess_exec(
                *command,
                cwd=ROOT,
                env=env or child_environment(),
                stdin=asyncio.subprocess.PIPE
                if data is not None
                else asyncio.subprocess.DEVNULL,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            # Keep draining pipes during termination; cancelling communicate
            # first can leave a full audio pipe blocking process.wait().
            communication = asyncio.create_task(process.communicate(data))
            output, _ = await asyncio.shield(communication)
            if process.returncode != 0:
                raise ValueError()
            return output
    except asyncio.CancelledError:
        if process is not None:
            await stop_process(process)
        raise
    except Exception:
        if process is not None:
            await stop_process(process)
        raise RuntimeError(code) from None
    finally:
        if communication is not None:
            if not communication.done():
                communication.cancel()
            await asyncio.gather(communication, return_exceptions=True)


async def caller_audio(env, phrases, text):
    child_env = child_environment()
    child_env.update({key: env[key] for key in ("AZURE_SPEECH_KEY", "AZURE_REGION")})
    data = json.dumps(
        {"voice": phrases["voice"], "locale": phrases["locale"], "text": text}
    ).encode()
    return await process_bytes(
        [sys.executable, "-c", TTS_CODE],
        data=data,
        env=child_env,
        timeout=CALLER_TTS_TIMEOUT,
        code="probe_caller_tts_failed",
    )


async def read_owned_async(container, call_id, *, cleanup=False):
    command = owned_command(container, call_id, cleanup)
    raw = await process_bytes(
        command,
        timeout=CLEANUP_STEP_TIMEOUT if cleanup else 20,
        code="probe_ledger_read_failed",
    )
    try:
        return owned_items(raw)
    except (ValueError, TypeError):
        raise RuntimeError("probe_ledger_read_failed") from None


async def worker_credentials(container):
    if not isinstance(container, str) or not re.fullmatch(
        r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", container
    ):
        raise ValueError("probe_container_invalid")
    raw = await process_bytes(
        [sys.executable, "-c", CREDENTIAL_CODE, container],
        timeout=CREDENTIAL_TIMEOUT,
        code="probe_credentials_failed",
    )
    try:
        env = json.loads(raw)
        if not isinstance(env, dict) or not all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in env.items()
        ):
            raise ValueError()
        return env
    except (ValueError, TypeError):
        raise RuntimeError("probe_credentials_failed") from None


ESTONIAN_CALLER_DAYS = (
    "esimesel",
    "teisel",
    "kolmandal",
    "neljandal",
    "viiendal",
    "kuuendal",
    "seitsmendal",
    "kaheksandal",
    "üheksandal",
    "kümnendal",
    "üheteistkümnendal",
    "kaheteistkümnendal",
    "kolmeteistkümnendal",
    "neljateistkümnendal",
    "viieteistkümnendal",
    "kuueteistkümnendal",
    "seitsmeteistkümnendal",
    "kaheksateistkümnendal",
    "üheksateistkümnendal",
    "kahekümnendal",
    "kahekümne esimesel",
    "kahekümne teisel",
    "kahekümne kolmandal",
    "kahekümne neljandal",
    "kahekümne viiendal",
    "kahekümne kuuendal",
    "kahekümne seitsmendal",
    "kahekümne kaheksandal",
    "kahekümne üheksandal",
    "kolmekümnendal",
    "kolmekümne esimesel",
)


def scenario(language, day):
    if language not in ("et", "en", "ru"):
        raise ValueError("probe_language_invalid")
    # Speak one named calendar date, not a machine ISO sequence or a second
    # relative weekday. Keep the expected ledger date independently in run().
    date = restaurant_spoken_date(day.isoformat(), language).rsplit(", ", 1)[-1]
    if language == "et":
        date = date.replace(f"{day.day}.", ESTONIAN_CALLER_DAYS[day.day - 1], 1)
    phrases = {
        "et": {
            "voice": "et-EE-KertNeural",
            "locale": "et-EE",
            "request": f"Palun broneeri laud neljale inimesele {date} kell kuus õhtul.",
            "premature_yes": "Jah.",
            "conditional": "Jah, kui saame istuda akna ääres.",
            "consent": "Jah, olen nõus.",
            "decline": "Ei, ära kinnita broneeringut.",
            "cancel": "Jah, tühista.",
            "details": {
                "date": date,
                "time": "Kell 18:00.",
                "party": "Kokku 4 inimest.",
            },
        },
        "en": {
            "voice": "en-US-GuyNeural",
            "locale": "en-US",
            "request": f"Please reserve a table for 4 people on {date} at 18:00.",
            "premature_yes": "Yes.",
            "conditional": "Yes, if we can sit by the window.",
            "consent": "Yes, that works for me.",
            "decline": "No, do not confirm the booking.",
            "cancel": "Please cancel this test booking.",
            "details": {
                "date": date,
                "time": "At 18:00.",
                "party": "Four guests in total.",
            },
        },
        "ru": {
            "voice": "ru-RU-DmitryNeural",
            "locale": "ru-RU",
            "request": f"Пожалуйста, забронируйте столик на 4 человека {date} в 18:00.",
            "premature_yes": "Да.",
            "conditional": "Да, если мы можем сесть у окна.",
            "consent": "Да, подходит.",
            "decline": "Нет, не подтверждайте бронирование.",
            "cancel": "Да, отмените.",
            "details": {"date": date, "time": "В 18:00.", "party": "Всего 4 человека."},
        },
    }[language]
    return {
        **phrases,
        "party_size": 4,
        "expected_time": "18:00",
        "recap_marker": COPY[language]["recap"].split("{", 1)[0],
    }


def complete_recap(text, language):
    template = COPY[language]["recap"]
    return (
        isinstance(text, str)
        and text.strip().startswith(template.split("{", 1)[0])
        and text.strip().endswith(
            COPY[language]["confirmation_question"] + template.split("{question}", 1)[1]
        )
    )


def diagnostic_counts(inputs, replies):
    return {
        "final_input_turns": len(inputs),
        "spoken_replies": len(replies),
        "canonical_recaps": sum(
            any(complete_recap(reply, language) for language in ("et", "en", "ru"))
            for reply in replies
        ),
    }


def failure_message(error):
    codes = {
        "probe_scope_invalid",
        "probe_scope_missing",
        "probe_container_invalid",
        "probe_language_invalid",
        "probe_reply_incomplete",
        "probe_no_recap",
        "probe_detail_limit",
        "probe_premature_write",
        "probe_premature_yes_write",
        "probe_conditional_write",
        "probe_decline_write",
        "probe_confirm_unproven",
        "probe_cancel_unproven",
        "probe_ledger_read_failed",
        "probe_caller_tts_failed",
        "probe_credentials_failed",
        "probe_cleanup_failed",
    }
    code = "probe_deadline" if isinstance(error, TimeoutError) else str(error)
    return "FAIL restaurant native probe: " + (
        code if code in codes | {"probe_deadline"} else "probe_failed"
    )


async def exercise(speak, read, phrases, language, day):
    extra_turns = 0

    async def request_recap():
        nonlocal extra_turns
        reply = await speak(phrases["request"])
        while True:
            assert not await read(), "probe_premature_write"
            if complete_recap(reply, language):
                return
            field = next(
                (
                    key
                    for key in ("date", "date_ambiguous", "time", "party")
                    if COPY[language][key] in reply
                ),
                None,
            )
            assert field is not None, "probe_no_recap"
            if field == "date_ambiguous":
                field = "date"
            assert extra_turns < 3, "probe_detail_limit"
            extra_turns += 1
            reply = await speak(phrases["details"][field])

    await speak(phrases["premature_yes"])
    assert not await read(), "probe_premature_yes_write"
    await request_recap()
    await speak(phrases["conditional"])
    assert not await read(), "probe_conditional_write"
    await speak(phrases["decline"])
    assert not await read(), "probe_decline_write"
    await request_recap()
    await speak(phrases["consent"])
    items = await read()
    assert len(items) == 1, "probe_confirm_unproven"
    item = items[0]
    assert (
        item["start"] == day.isoformat() + "T" + phrases["expected_time"] + ":00"
        and item["party_size"] == 4
        and item["status"] == "confirmed"
    ), "probe_confirm_unproven"
    await speak(phrases["cancel"])
    cancelled = await read()
    assert (
        len(cancelled) == 1
        and cancelled[0]["id"] == item["id"]
        and cancelled[0]["status"] == "cancelled"
    ), "probe_cancel_unproven"
    return {
        "extra_detail_turns": extra_turns,
        "before_consent_empty": True,
        "premature_yes_no_write": True,
        "conditional_no_write": True,
        "decline_no_write": True,
        "ledger_booking_verified": True,
        "ledger_cancel_verified": True,
    }


async def wait_reply(replies, playback, previous, audio):
    try:
        async with asyncio.timeout(REPLY_TIMEOUT):
            while True:
                if (
                    len(replies) > previous
                    and playback["voiced_frames"] > audio + 20
                    and asyncio.get_running_loop().time()
                    - max(playback["last_audio"], playback["last_reply"])
                    > 1.5
                ):
                    return
                await asyncio.sleep(0.25)
    except TimeoutError:
        raise AssertionError("probe_reply_incomplete") from None


async def close_audio_source(source):
    close = getattr(source, "aclose", None)
    if close is not None:
        result = close()
        if inspect.isawaitable(result):
            await result


async def run(container, env, language="et"):
    from livekit import api, rtc

    day = datetime.now(ZoneInfo("Europe/Tallinn")).date() + timedelta(
        days=14 + ("et", "en", "ru").index(language)
    )
    phrases = scenario(language, day)
    name = "voicebot-restaurant-probe-" + uuid.uuid4().hex
    identity = name + "-caller"
    client = api.LiveKitAPI(
        url="http://127.0.0.1:7880",
        api_key=env["LIVEKIT_API_KEY"],
        api_secret=env["LIVEKIT_API_SECRET"],
    )
    room = rtc.Room()
    source, call_id, creation_attempted = None, None, False
    audio_cleanup_failed = False
    audio_tasks, replies, inputs = [], [], []
    playback = {"voiced_frames": 0, "last_audio": 0, "last_reply": 0}

    async def receive(track):
        nonlocal audio_cleanup_failed
        stream = rtc.AudioStream.from_track(
            track=track, sample_rate=16000, num_channels=1
        )
        try:
            async for event in stream:
                samples = array.array("h", bytes(event.frame.data))
                if sum(float(x) ** 2 for x in samples) / max(1, len(samples)) > 40000:
                    playback["voiced_frames"] += 1
                    playback["last_audio"] = asyncio.get_running_loop().time()
        finally:
            try:
                async with asyncio.timeout(CLEANUP_STEP_TIMEOUT):
                    await stream.aclose()
            except Exception:
                audio_cleanup_failed = True

    @room.on("track_subscribed")
    def subscribed(track, publication, participant):
        if track.kind == rtc.TrackKind.KIND_AUDIO and participant.identity != identity:
            audio_tasks.append(asyncio.create_task(receive(track)))

    @room.on("transcription_received")
    def transcribed(segments, participant, publication):
        for segment in segments:
            if segment.final:
                if participant and participant.identity == identity:
                    inputs.append(segment.text)
                else:
                    replies.append(segment.text)
                    playback["last_reply"] = asyncio.get_running_loop().time()

    async def speak(text):
        previous, audio = len(replies), playback["voiced_frames"]
        data = await caller_audio(env, phrases, text)
        with wave.open(io.BytesIO(data), "rb") as wav:
            if wav.getparams()[:3] != (1, 2, 24000):
                raise AssertionError("probe_reply_incomplete")
            while chunk := wav.readframes(480):
                await source.capture_frame(
                    rtc.AudioFrame(chunk, 24000, 1, len(chunk) // 2)
                )
        for _ in range(75):
            await source.capture_frame(rtc.AudioFrame(bytes(960), 24000, 1, 480))
        await source.wait_for_playout()
        await wait_reply(replies, playback, previous, audio)
        return " ".join(replies[previous:])

    async def read():
        return await read_owned_async(container, call_id)

    async def stop_audio():
        for task in audio_tasks:
            task.cancel()
        results = await asyncio.gather(*audio_tasks, return_exceptions=True)
        if audio_cleanup_failed or any(
            isinstance(result, BaseException)
            and not isinstance(result, asyncio.CancelledError)
            for result in results
        ):
            raise RuntimeError("probe_cleanup_failed")

    async def delete_room():
        if creation_attempted:
            try:
                await client.room.delete_room(api.DeleteRoomRequest(room=name))
            except api.TwirpError as error:
                if error.code != "not_found":
                    raise

    async def cleanup_ledger():
        if call_id:
            await read_owned_async(container, call_id, cleanup=True)

    try:
        async with asyncio.timeout(CONVERSATION_TIMEOUT):
            # The server may create the UUID room before a lost response or
            # cancellation. Attempted creation therefore always requires delete.
            creation_attempted = True
            await client.room.create_room(
                api.CreateRoomRequest(name=name, departure_timeout=5)
            )
            credential = (
                api.AccessToken(env["LIVEKIT_API_KEY"], env["LIVEKIT_API_SECRET"])
                .with_identity(identity)
                .with_grants(api.VideoGrants(room_join=True, room=name))
                .to_jwt()
            )
            await room.connect("ws://127.0.0.1:7880", credential)
            source = rtc.AudioSource(24000, 1, queue_size_ms=100)
            track = rtc.LocalAudioTrack.create_audio_track(
                "fictional-restaurant-caller", source
            )
            await room.local_participant.publish_track(
                track, rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_MICROPHONE)
            )
            await client.agent_dispatch.create_dispatch(
                api.CreateAgentDispatchRequest(
                    agent_name=env.get("VOICEBOT_AGENT_NAME", "voicebot"), room=name
                )
            )
            await wait_reply(replies, playback, 0, 0)
            scopes = {
                p.attributes.get("voicebot.call_id")
                for p in room.remote_participants.values()
                if p.attributes.get("voicebot.call_id")
            }
            assert len(scopes) == 1, "probe_scope_missing"
            call_id = scopes.pop()
            if not isinstance(call_id, str) or not re.fullmatch(
                r"[a-f0-9]{32}", call_id
            ):
                call_id = None
                raise ValueError("probe_scope_invalid")
            checks = await exercise(speak, read, phrases, language, day)
            return {
                "pass": True,
                "language": language,
                **checks,
                **diagnostic_counts(inputs, replies),
                "voiced_frames": playback["voiced_frames"],
                "physical_microphone_verified": False,
                "carrier_verified": False,
            }
    except BaseException:
        print(json.dumps({"diagnostics": diagnostic_counts(inputs, replies)}))
        raise
    finally:
        failed_steps = 0
        # Independent deadlines: one stalled close must not prevent deleting
        # this room or cancelling only strongly proven call-owned reservations.
        for close in (
            stop_audio,
            room.disconnect,
            lambda: close_audio_source(source),
            delete_room,
            cleanup_ledger,
            client.aclose,
        ):
            try:
                async with asyncio.timeout(CLEANUP_STEP_TIMEOUT):
                    await close()
            except (Exception, asyncio.CancelledError):
                failed_steps += 1
        if failed_steps:
            print(json.dumps({"cleanup_failed_steps": failed_steps}))
            raise RuntimeError("probe_cleanup_failed")


async def main(container, language):
    async with asyncio.timeout(300):
        env = await worker_credentials(container)
        result = await run(container, env, language)
    print(json.dumps(result))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-container", required=True)
    parser.add_argument("--language", choices=("et", "en", "ru"), default="et")
    args = parser.parse_args()
    failure = None
    try:
        asyncio.run(main(args.source_container, args.language))
    except (Exception, KeyboardInterrupt) as error:
        failure = failure_message(error)
        traceback.clear_frames(error.__traceback__)
    gc.collect()
    if failure:
        raise SystemExit(failure)
