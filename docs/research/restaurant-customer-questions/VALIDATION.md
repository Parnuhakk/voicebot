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

Uurimuse HTML kontrolliti eraldi kohaliku HTTP-serveri kaudu: kõik 270 kirjet, filtrid, omaniku kinnitatud kuus mõistet, kolme keele kuvamine, tühi otsingutulemus, täpitähtede suhtes paindlik otsing, töölaua ja 390 × 844 mobiilivaade. `file:` navigeerimine oli Playwright CLI poolt keelatud, seetõttu otse faili avamine ei ole eraldi kontrollitud.

## Avalik sait ja telefon

PR32 järel loeti avalikult saidilt nelja perevõimaluse `true` väärtused ja kõik kolm keeleversiooni tagasi. See tõendab veebiversiooni avaldamist ja avaliku profiili andmeid.

Native regressioon kasutab paigaldatud LiveKit SDK-d ning kutsub tegelikku `TelephoneAgent.on_user_turn_completed` meetodit jagatud kõneolekuga. Ei tehtud päris STT-, TTS-, mudeli- ega operaatorivõrgu kõnet.

Telefoniboti avalik väljalaske staatus oli uurimise ajal `unverified`; native sõrmejälg puudus, avalik ingress ja operaatorikõne polnud kinnitatud. Veebiversiooni CI ja tagasilugemine ei asenda telefoniprotsessi identiteedi ja päriskõne kontrolli.

## Lõppversioon

Põhiaru `a7be09c` muudatused ühendati vestluse, meditsiinilise konteksti, erisoovide ja toidutellimuse tegevuspiire säilitades. Ühendamise järel läbisid **343 sihitud testi** ja restorani Chrome'i brauserikontroll. Täpne lõppseisu taasesitus sisaldab 810 paari, mille ainus läbivaatuse märge on **214 üldist teadmata info vastust**. Mõlemad uued tüübitud moodulid läbisid kontrolli 0 vea ja 0 hoiatusega.

Põhiaru ühendamise eelne viimane täiskomplekt: **11 741 läbis, 10 jäeti vahele, 36 subtesti läbis**, kestus 252,58 sekundit. Testikäigus esines üks Starlette'i `httpx` kasutamise aegumise hoiatus. Kuus lisatud HTTP teksti ja sünteetilise kõne stsenaariumi kontrollivad uusi teenindusküsimusi kõigi kolme puuduva broneerimisvälja juures.

Põhiaru ühendamise järgne kogu hoidla kontroll, CI ja avaliku saidi lõppversiooni tagasilugemine lisatakse siia pärast nende tegelikku lõpetamist. Eelnev täiskomplekti kontroll enne viimaste regressioonide lisamist andis 11 684 läbimist, kolm vana kassiküsimuse ootuse lahknevust ja kümme vahele jäetud kontrolli. Kasside ootused on parandatud eraldi kinnitamata tingimuste vastusele; see tulemus ei ole esitatud puhta lõppkontrollina.
