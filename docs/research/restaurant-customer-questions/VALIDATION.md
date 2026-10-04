# Kontrollide protokoll

Kõik allpool nimetatud kohalikud kontrollid kasutavad sünteetilist restorani ja fixture'e. Tehtud päris HTTP-päringud ja brauseri sündmused on eristatud tegelikest väliste teenusepakkujate kõnedest.

## Valmis kontrollid enne põhiaru ühendamist

- 412 pereküsimuste, teenindusküsimuste, loomareeglite ja vestluse regressiooni läbisid kontrolli pärast konkreetsete suunamisvigade parandusi.
- 142 teenindusküsimuste regressiooni läbisid eraldi kontrolli: 30 teemat kolmes keeles, lastemenüü allergeenid, teised loomad, sõnapiirid, perevõimaluste sõnastused, hädaabi valmis kokkuvõtte ja puuduva või mitmetähendusliku aja puhul, HTTP vastused ja native vooru jagatud olek.
- 7 kogumiku kontrolli läbisid: determinism, 270/810 mõistete ja paaride arv, kolm täielikku keelt, CSV terviklikkus, 216 omaniku kinnitamata välja, vigaste lähteridade tõrjumine ja HTML-i põimitud andmete turvaline kodeerimine.
- 810 küsimuse kohaliku taasesituse kontroll ei käivitanud dispatch'i ega lubanud kirjutusi. Selle ainus läbivaatuse märge oli 224 üldist teadmata info vastust. [Algseis](observations-before.json) sisaldab 771 paari; lõppvõrdlus kasutab samu 771 paari.
- `flake8.cmd --select E4,E7,E9,F` läbis muudetud Python-moodulite, testide ja genereerimisskriptide kontrolli. See on nende valitud reeglite tulemus, mitte kõigi stiilireeglite kontroll.
- `basedpyright.cmd app/restaurant_family.py app/restaurant_service_questions.py`: **0 viga, 0 hoiatust**. See ei ole kogu hoidla tüübikontroll.
- `git diff --check` läbis tavapärase hoidla reavahetuse seadistusega. Reavahetuste normaliseerimise teated ei ole testi tulemus. Üks katse `core.autocrlf=false` ühekordse seadistusega käsitles olemasolevaid CRLF ridu tühikutena; lõppkontroll kasutab hoidla oma seadistust.

## Brauser

`tests/run_browser_checks.cjs` käivitas päris restorani rakenduse kohaliku HTTP-liidese ja Chrome'i kaudu. Tulemused:

- Kolm keelt, perevõimaluste vastused ja 18 lisatud teenindusküsimust läbisid.
- Broneerimise 12 kõrvalküsimust, kuupäeva ja kellaaja vormid, kokkuvõtte kviitung, kinnitamine, tühistamine ja lehe uuesti avamisel tulemuse näitamine läbisid.
- Mikrofonist saadeti PCM WAV, 16 kHz, üks kanal; see on sünteetiline sisend, mitte päris STT täpsuse kontroll.
- Töölaua ja mobiili vaated ning 320 px horisontaalse ülevoolu kontroll läbisid.
- **0 JavaScripti leheviga, 0 välist päringut**, Chrome 154.0.8037.97.

Uurimuse HTML kontrolliti eraldi kohaliku HTTP-serveri kaudu: kõik 270 kirjet, filtrid, omaniku kinnitatud kuus mõistet, kolme keele kuvamine, tühi otsingutulemus, täpitähtede suhtes paindlik otsing, töölaua ja 390 × 844 mobiilivaade. Teadlikult vigase JSON-iga brauserikatse näitas veateadet, null kirjet ja peidetud tulemuste laiendamise nuppu; pärast katset taastati korrektne leht. `file:` navigeerimine oli Playwright CLI poolt keelatud, seetõttu otse faili avamine ei ole eraldi kontrollitud.

## Avalik sait ja telefon

PR32 järel loeti avalikult saidilt nelja perevõimaluse `true` väärtused ja kõik kolm keeleversiooni tagasi. See tõendab veebiversiooni avaldamist ja avaliku profiili andmeid.

Native regressioon kasutab paigaldatud LiveKit SDK-d ning kutsub tegelikku `TelephoneAgent.on_user_turn_completed` meetodit jagatud kõneolekuga. Ei tehtud päris STT-, TTS-, mudeli- ega operaatorivõrgu kõnet.

Telefoniboti avalik väljalaske staatus oli uurimise alguses `unverified`; native sõrmejälg puudus. 4. oktoobril kell 06:17 UTC näitas avalik staatus `in_sync` ja veebiga sama sõrmejälge ning telefoniversiooni `ff11d69279d1b0e7f9fe59b4c1ce77b262dd1aa3`. See on avaliku sünkroonimisraporti tagasilugemine. Avalik ingress ja operaatorikõne olid jätkuvalt `false`; sünkroonimisraport ei kinnita päriskõne kvaliteeti.

## Lõppversioon

Põhiaru `a7be09c` muudatused ühendati vestluse, meditsiinilise konteksti, erisoovide ja toidutellimuse tegevuspiire säilitades. Ühendamise järel läbisid **343 sihitud testi** ja restorani Chrome'i brauserikontroll. Täpne lõppseisu taasesitus sisaldab 810 paari, mille ainus läbivaatuse märge on **214 üldist teadmata info vastust**. Mõlemad uued tüübitud moodulid läbisid kontrolli 0 vea ja 0 hoiatusega.

Järgmine täielik ühendatud kontroll tõi välja kaheksa vana vastuse või tundmatu küsimuse ootust ning Windowsi testikeskkonna piirid. Kaheksa ootust uuendati, säilitades tundmatu küsimuse oleku aegumise kontrolli päriselt tundmatu luuleõhtute küsimusega. Windowsi native alamprotsessi minimaalne keskkond säilitab nüüd `SYSTEMROOT` ja `WINDIR`, UTF-8 lähtefail loetakse selge kodeeringuga ning ainult POSIX õigusbittide kontroll jäetakse Windowsis vahele. Õigusbittide kontroll käib endiselt Linux CI-s. Kõiki neid muudatusi kattev komplekt: **440 läbis, 3 jäeti vahele**. Siin ei väideta, et Windowsi õigusbittide kontroll läbis.

Lisaks ühendati uusim põhiaru kõnetuvastuse muudatus `ff11d69`. Lõpliku täiskomplekti kontroll käivitati selle ühendatud versiooni jaoks.

Põhiaru ühendamise eelne viimane täiskomplekt: **11 741 läbis, 10 jäeti vahele, 36 subtesti läbis**, kestus 252,58 sekundit. Testikäigus esines üks Starlette'i `httpx` kasutamise aegumise hoiatus. Kuus lisatud HTTP teksti ja sünteetilise kõne stsenaariumi kontrollivad uusi teenindusküsimusi kõigi kolme puuduva broneerimisvälja juures.

Täielik kohalik ühendatud komplekt: **12 756 läbis, 17 jäeti vahele, 36 subtesti läbis**, kestus 397,46 sekundit. Selle käivitamise järel piirati veel toidukonteksti sõnapiiri, et „support” ei muudaks raseda külalise laua valimise küsimust toiduküsimuseks. Viimane parandus ja fixture'ite importide lintimise korrastus läbisid **165 sihitud kontrolli**, Flake8 valitud reeglid ja BasedPyrighti 0 vea ning 0 hoiatusega. Kõik muudetud Python-moodulid, testid ja genereerimisskriptid läbisid valitud Flake8 reeglid.

GitHubi ühendatud versiooni kontroll enne viimast sõnapiiri parandust: **12 439 läbis, 86 jäeti vahele, 36 subtesti läbis**; lisaks Linuxi hosti/Compose'i kontrollis 216 läbimist ja 5 vahelejätmist. Mõlemad tegelikud konteinerid ehitati; ühised identiteedid kattusid ning native töötaja ja Twilio silla import läbis võrgu ja päris volitusteta konteineris. Windowsis paigaldatud meedia-SDK-ga testitakse rohkem native juhtumeid kui Linuxi põhipakettidega CI-s, seetõttu on arvud erinevad.

Lõplik kontrollitud commit `0be0f2bdbf0c847985fd55c3b8bf0533a339ee00`: [GitHubi kontroll](https://github.com/Parnuhakk/voicebot/actions/runs/37182707750) läbis mõlemad tööd. Linuxi põhipakettidega **12 440 läbis, 86 jäeti vahele, 36 subtesti läbis**; hosti ja Compose'i kontrollis 216 läbimist, 5 vahelejätmist. Konteinerite ehitamine, identiteetide võrdlus ning native töötaja ja silla import läbisid. Lõplik kohalik külalise vestluse, teenindusküsimuste ja kogumiku kontroll: **433 läbis**.

[PR39](https://github.com/Parnuhakk/voicebot/pull/39) ühendati 4. oktoobril kell 06:27:43 UTC, avaldatud koodi commit `0bbffde9d84b52272270adb4439a12b35253acc6`. Avaliku veebisaidi tagasilugemine kell **06:33:06 UTC** kinnitas:

- `/api/public/restaurant`: `customer_questions_version` on `reviewed-service-v1`; kõik neli perevõimalust on `true` ja kõik kolm keeleversiooni olemas.
- `/api/status`: telefoniprotsessi väljalase on `in_sync`, versioon `0bbffde9d84b52272270adb4439a12b35253acc6`; veeb ja telefon näitavad sama sõrmejälge `b3153e3e98b396d1c2719776e66a1e02442ca12f6de0086704ea1bbbd94a599c`.
- `public_ingress_verified` ja `carrier_call_verified` on endiselt `false`. Päris operaatorikõnet ei tehtud; staatuseraport ei tõenda akustilist kvaliteeti.

Eelnev ebaõnnestunud CI leiti ja parandati; seda ei esitata edukana. Varasem 11 684 läbimise ja kolme kassiküsimuse vana ootuse lahknevusega kontroll oli vahetulemus, mille lahknevused parandati enne ülaltoodud edukat kontrolli.
