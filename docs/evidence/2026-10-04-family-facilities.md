# Lastele mõeldud võimalused

## Kinnitatud info

Omanik kinnitas vestluses 4. oktoobril 2026, et olemas on joonistamisvõimalus, mänguasjad, mängunurk ja lastemenüü. Need neli fakti lisati restorani profiili ning jagatud veebi- ja telefonivestluse vastustesse.

- Eesti: „Lastele on olemas joonistamisvõimalus, mänguasjad, mängunurk ja lastemenüü.”
- English: “For children, we have drawing activities, toys, a play corner and a children's menu.”
- Русский: «Для детей есть возможность порисовать, игрушки, игровой уголок и детское меню.»

Lastemenüü koostist ja hindu, mängunurga vanusepiiranguid, tasuta kasutamist ega lapsehoidu ei ole kinnitatud. Nende küsimuste vastus palub üksikasju restorani töötajaga täpsustada. Üldine lasteküsimus ei kinnita lastetooli ega ligipääsetavust.

## Rakendus

`family_facilities` on valikuline, rangelt kontrollitud profiiliobjekt. Ainult väärtus `true` lubab võimalust olemasolevana nimetada. Puuduv väli, `null` ja teise profiili teadmata võimalused ei päri näidisrestorani kinnitusi. Muud tüübid ja tundmatud võtmed lükatakse tagasi.

Küsimuste valija eristab lastele mõeldud tegevusi, lastemenüüd, täpsustamist vajavaid tingimusi ja broneeringu inimeste arvu. Avalik profiili API tagastab sama vastuse kõigis kolmes keeles. Veebi vastuste faktikogum ja LiveKiti viimase kõnevooru käsitlus kasutavad jagatud vastust.

## Kohalik kontroll

- Restoranitestid, vene loomuliku kõne kontrollid ja inglise kuupäevade kontrollid: **8429 läbitud**.
- Chrome'i brauserikontroll: laste tegevuste ja lastemenüü küsimused kõigis kolmes keeles; lisaks broneerimine, kinnitus, tühistamine, mikrofoni fixture, mobiil ja töölaud. **0 lehe viga, 0 välist päringut**.
- `flake8.cmd --select E4,E7,E9,F`: läbitud.
- Uue mooduli `basedpyright.cmd`: **0 viga, 0 hoiatust**.
- Pärast põhiharu paralleelsete hääle- ja väljalaskemuudatuste liitmist: **466 läbitud, 1 vahele jäetud**; Chrome'i täielik restoranikontroll uuesti läbitud.

Kõne- ja brauserikontrollid kasutavad kohalikke teenusepakkujate fixturesid. Need ei tõesta tegeliku telefonikõne helituvastust, tasulise kõnesünteesi kvaliteeti ega tootmises töötava telefoniprotsessi versiooni. Näidisrestorani broneering ei ole päris restorani tellimus.
