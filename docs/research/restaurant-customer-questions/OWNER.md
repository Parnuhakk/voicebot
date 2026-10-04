# Restorani info täpsustamine

Joonistamisvõimalus, mänguasjad, mängunurk ja lastemenüü on kinnitatud. Järgmised täpsustused võimaldavad anda rohkem sisulisi vastuseid. Küsimused on soovituslik tööjärjekord; praegune kõneabiline peab teadmata info puhul küsima töötajalt täpsustamist.

## Kõigepealt täpsustatav info

| Teema | Vajalik kinnitus | Vastuse piir kuni kinnituseni |
| --- | --- | --- |
| Lastemenüü | Roogade nimetused kolmes keeles, koostis, allergeenid, hinnad, portsjonid | Lastemenüü olemasolu võib kinnitada; üldmenüü roogi ei tohi lastemenüüks nimetada |
| Allergiad | Kes kinnitab köögis koostist, muudatusi ja ristsaastumise tingimusi | Bot ei garanteeri allergiaohutust |
| Mängunurk | Vanused, järelevalve, kasutusaeg, tasu, koristamine | Olemasolu võib kinnitada; lapsehoidu ja tasuta kasutamist ei tohi eeldada |
| Pere mugavused | Lastetoolid, istmekõrgendused, lapsevankri koht, mähkimislaud, beebitoidu soojendamine | Iga võimalus vajab eraldi kinnitust |
| Ligipääs | Astmed, kaldtee, ukse laius, laua kõrgus ja vaba ruum, tualett, abivõimalus | Üldine „ligipääsetav” ei asenda konkreetsete tingimuste kirjeldust |
| Kontakt | Päris aadress, avalik telefon, e-post, ametlik menüü ja kaart | Praegune profiil on fiktiivne ja aadress puudub |
| Maksmine | Kaardid, sularaha, telefonimakse, arve jagamine, ettevõtte arve, teenindustasu | Bot ei kogu pangakaardi andmeid ega kinnita makset |
| Broneerimise erandid | Hilinemise tähtaeg, pikem külastus, kindel laud, suuremad grupid, ootenimekiri | Saadavust ja erisoovi täitmist tuleb kontrollida |
| Eripäevad | Kuupäevad, sulgemised, köögi ajad, erimenüüd ja piletid | Tavaline nädalagraafik ei kinnita ürituse korraldust |
| Lemmikloomad | Koerte lisatingimused ja teiste loomade lubamine | Koerte luba ei tähenda kasside või teiste loomade luba |
| Tellimused | Kaasamüük, kojuvedu, hinnad, piirkond ja tellimuse vastuvõtmise kanal | Demo bot ei võta toidutellimusi vastu |
| Kaebused | Vastuvõtja, kontakt, lahenduse protsess, leitud esemete tagastamine | Bot ei luba hüvitist ega ütle, et avaldus on edastatud |
| Privaatsus | Tegelik salvestamine, andmete kasutus ja säilitamine, õiguste kontakt, alternatiivne kanal | Bot ei mõtle tingimusi ise välja |
| Telefon | Töötava protsessi versioon, väljalaske sünkroonimine, päris kõne proov | Kohalik SDK kontroll ei kinnita operaatorivõrgu kõnet |

## Andmete kinnitamine

Failis `owner-fields.json` on 216 täpsustamist vajavat andmevälja koos küsimustega eesti, inglise ja vene keeles. Väärtus `null` tähendab „kinnitamata”. See ei tähenda „puudub”. Fail on täitmise ja ülevaatuse materjal; töötav bot seda automaatselt ei lae.

Kinnitusega tuleb säilitada vastutav inimene, kuupäev ja tõend või viide. Tingimusliku teenuse puhul tuleb salvestada ka tingimus: näiteks millal mängunurk on kasutatav, kas lastetooli peab ette küsima või millise dieedi puhul on köögi kontroll vajalik. Allergia, ligipääsu ja maksmise teave vajab eriti täpset sõnastust.

Menüü uus versioon peab uuendama roogade nimetused, koostise, allergeenid ja hinnad koos. Puuduva allergeeni märge ei kinnita aine täielikku puudumist valmistuskeskkonnast. Ürituse erimenüü, lastemenüü ja tavamenüü tuleb kirjeldada eraldi.

## Üks täpne kinnitus mitme oletuse asemel

„Mängunurk on olemas” kinnitab mängunurga olemasolu. See ei kinnita lapsehoidjat, teatud vanusele sobivust, koristusgraafikut ega tasuta kasutamist. „Koeraga võib tulla” kinnitab koerte lubamist; teiste loomade reegel vajab oma kinnitust. „Taimetoit” ja „vegan” ei anna allergiaohutuse kinnitust.

Bot saab säilitada erisoovi vestluse kontekstis. Ta ei tohi öelda, et erisoov on köögile edastatud või restorani poolt heaks kiidetud, kui puudub tegelik edastamise tegevus ja kinnitus.
