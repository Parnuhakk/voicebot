# Restorani kliendiküsimused eesti, inglise ja vene keeles

Uurimus koostatud 4. oktoobril 2026 saidi `robot.arleserver.cfd` kõneabilise jaoks. Materjalis on **270 küsimuse mõistet, 810 küsimuse-vastuse paari ja 17 teemat**. Uurimus seob kliendiküsimused restorani kinnitatud faktide, puuduva info ja vestluse tegelike tegevustega.

Parandused avaldati [PR39 kaudu](https://github.com/Parnuhakk/voicebot/pull/39). Avaliku saidi tagasilugemine kinnitas uue küsimustetoe ja kõik neli laste võimalust. Veebi ning telefoniprotsessi väljalaskeraport näitas sama koodiversiooni; tegelik operaatorikõne on kontrollimata. Täpsed versioonid, kontrollide tulemused ja tagasilugemise aeg on [protokollis](VALIDATION.md).

Kõigi tulevaste küsimuste või sõnastuste täielikku nimekirja ei saa teha. Kogumik katab levinud külastusolukorrad, olulised erivajadused ja testimisel leitud vead. Kirjaliku küsimuse õige vastus ei tõesta selle mõistmist mürarikkas telefonikõnes.

## Materjalide avamine

| Materjal | Kasutus |
| --- | --- |
| [Otsitav kogumik](review.html) | Ava brauseris; filtreeri teemat, keelt ja info alust. Iga küsimuse juures saab vaadata ka kohaliku boti tegelikku vastust |
| [Exceli jaoks CSV](questions.csv) | 810 rida, üks keel ja küsimuse-vastuse paar rea kohta; UTF-8 BOM |
| [Struktureeritud kogumik](questions.json) | Küsimuste, vastuste, allikate ja kinnitamist vajavate väljade masinloetav andmestik |
| [Omaniku täpsustused](OWNER.md) | 14 prioriteetset andmerühma, mida tuleks enne täpsemate lubaduste andmist kinnitada |
| [Täidetavad andmeväljad](owner-fields.json) | 216 kinnitamata välja; `null` tähendab kinnitamata infot |
| [Vestlusolukorrad](SCENARIOS.md) | Kolmekeelsed näited broneerimise, kõrvalküsimuste, paranduste ja katkestuste jaoks |
| [Meetod](METHOD.md) ja [allikad](sources.json) | Faktide päritolu, teiste restoranide kasutamise piirid ja kontrollide ulatus |
| [Kohaliku boti vastused](observations.json) | 810 küsimuse tegelik vastus jagatud vestluskoodiga, ilma tegevuse käivitamiseta |
| [Algseisu vastused](observations-before.json) | Enne selle uurimuse teenindusküsimuste parandusi salvestatud 771 vastust |
| [Uurimuse vaheversioon](observations-pre-integration.json) | 810 vastust enne sama öö põhiaru uuemate paranduste ühendamist |
| [Kontrollide protokoll](VALIDATION.md) | Täpsed kontrollid ja nende piirid |

Kogumik on iseseisev HTML-fail, sisaldab oma andmeid ega vaja fontide või skriptide allalaadimist. Brauseri automatiseerimise vahend ei lubanud `file:` aadressi, seetõttu kontrolliti kogumikku kohaliku HTTP-serveri kaudu. Otse failina avamist ei käsitleta eraldi kontrollitud tulemusena.

## Kinnitatud vastus laste kohta

Omanik kinnitas neli võimalust: joonistamine, mänguasjad, mängunurk ja lastemenüü. Jagatud veebiboti ja telefoniboti kood kasutab neid eraldi profiiliandmetena. Veebisaidi avaliku liidese tagasilugemine kinnitas kõik neli väärtust ja kolm tõlget pärast PR32 avaldamist.

| Keel | Vastus |
| --- | --- |
| Eesti | Lastele on olemas joonistamisvõimalus, mänguasjad, mängunurk ja lastemenüü. |
| English | For children, we have drawing activities, toys, a play corner and a children's menu. |
| Русский | Для детей есть возможность порисовать, игрушки, игровой уголок и детское меню. |

Lastemenüü roogasid, hindu ega allergeene pole omanik veel kinnitanud. Samuti vajavad kinnitust järelevalve, vanusepiirid, tasuta kasutamine, mängunurga eraldi lahtiolekuajad ning mänguasjade ja joonistamisvahendite materjalid. Kogumik annab nende jaoks täpsed küsimused ja vastused kõigis kolmes keeles.

## Küsimuste ulatus

| Teema | Mõisteid | Näited käsitletud küsimustest |
| --- | ---: | --- |
| Lapsed ja pere | 31 | Joonistamine, mänguasjad, lastemenüü, mängunurga vanused ja järelevalve, lastetool, lapsevanker, mähkimine, lapse toit esimesena |
| Allergiad ja eridieedid | 28 | Lastemenüü allergeenid, koostisosad, gluteen, laktoos, pähklid, eraldi valmistamine, vegan, halal ja koššer, individuaalne toidusobivus |
| Menüü ja toidud | 27 | Tavamenüü, portsjonid, muudatused, valmimisviis, hinnad, hooajalisus, tänane saadavus |
| Maksmine | 22 | Kaart, sularaha, telefonimakse, arve jagamine, ettevõtte arve, kinkekaart, ettemaks, tundlikud kaardiandmed |
| Mugavused | 21 | Wi-Fi, garderoob, tualett, suitsetamine, muusika, koerad ja teised loomad, tarvikud |
| Üritused ja grupid | 18 | Sünnipäev, eraruum, suurem seltskond, tort, dekoratsioonid, piletid ja erimenüü |
| Teenindus | 18 | Toidutellimus, kaasamüük, kojuvedu, töötaja abi, kaebus, vale roog, leitud ese |
| Joogid | 12 | Joogivalik, lastetoidu juurde jook, alkoholivabad joogid, veinisoovitus ja saadavus |
| Ligipääs | 16 | Astmed, ukse laius, ratastool, ligipääsetav tualett, kuulmise ja nägemise abivahendid |
| Istekohad | 16 | Kindel laud, aknaalune koht, laud mängunurga lähedal, terrass, lauad kokku, pikem külastus |
| Asukoht ja saabumine | 15 | Aadress, telefon, e-post, parkimine, ühistransport, ametlik menüülink |
| Tavapärased lahtiolekuajad | 12 | Kõik nädalapäevad, tööpäevad, nädalavahetus ja köögi sulgemine |
| Broneerimine | 11 | Alustamine, külaliste koguarv, kestus, saadavus, ettebroneerimine, muutmine, tühistamine ja kinnitus |
| Privaatsus | 8 | Kõne salvestamine, andmete säilitamine ja kasutamine, kustutamine, vastutav kontakt |
| Kõne ja keel | 6 | Eesti/inglise/vene keel, ebaselge kuupäev või kellaaeg, halb kuuldavus, inimese abi |
| Eripäevade ajad | 5 | Pühad, aastavahetus, köögi eriajad ja viimane tellimus |
| Hädaolukorrad | 4 | Hingamisraskus, teadvuse kaotus, tulekahju ja vahetu oht |

Allergeenide teema sisaldab ka toidu kohandamise ja toitumise küsimusi. Kategooria nimetus ei tähenda, et näiteks halal oleks allergeen. Hädaolukordade vastus on 112 ja lähedal oleva töötaja abi; bot ei väida, et ta ise helistas või annab ravi.

## Vastuste alus ja puuduv info

| Alus | Mõisteid | Mida see tähendab |
| --- | ---: | --- |
| Omaniku kinnitus | 6 | Kuus küsimust kasutavad sama nelja kinnitatud perevõimalust |
| Demo profiil | 27 | Fiktiivse restorani seadistatud menüü, tööajad ja broneerimispiirid |
| Tegelik tegevusreegel | 16 | Mida demo saab teha, millal vajab kinnitust ja kelle broneeringut võib muuta |
| Kiire abi juhis | 5 | Neli hädaolukorda ja üks tugeva allergilise reaktsiooni küsimus |
| Töötaja kinnitus vajalik | 216 | Konkreetne puuduv info ja soovitatud vastus selle puudumise ajal |

Kõik andmestiku vastused on märgitud `research_proposal`. Kogumikus olev hea sõnastus ja töötava boti vastus on eraldi vaadatavad. Puuduva fakti puhul on mõlemad piiratud kinnitamata infoga, kuid sõnastus ja detailsus võivad erineda. Uurimuse JSON ega omaniku täitmisfail ei muuda töötava restorani profiili automaatselt.

Praegune Meretuule profiil on **fiktiivne demo**. Profiilis puudub aadress. Tavamenüüs on köögiviljasupp, küpsetatud lõhe ja seenerisoto, hinnad pole kinnitatud. Tavabroneering on 90 minutit, kuni kuuele inimesele, saadavuse otsing kuni 90 päeva ette. Need on demo seaded, mida päris restorani avamisel peab omanik uuendama.

## Uurimuses leitud ja parandatud käitumine

1. **Kassid said koerte vastuse.** Nüüd kinnitab koerte reegel koerte lubamist; kasside ja teiste loomade tingimused jäävad eraldi kinnitamata.
2. **Lastemenüü allergiaküsimus võis saada täiskasvanute menüü.** Nüüd küsib vastus lastemenüü koostise ja köögi kinnituse kohta. Täiskasvanute roogade allergeeniloendit ei esitata lastemenüü infona.
3. **Hädaolukord jäi tavavestlusse.** Tuvastatud kiire ohu korral tuleb 112 juhis enne broneerimise küsimusi ja valmis kokkuvõtet. Olemasolevat laua hoidmist ei esitata kinnitatud broneeringuna.
4. **Kindla laua küsimus võis tekitada broneerimise välju.** Teenindusküsimus saab eraldi vastuse; see ei loo laua ettepanekut.
5. **„Support” ja „супермаркет” võisid sobituda supiga.** Roogade lühinimed sobituvad nüüd sõnapiiridel, säilitades tavapärased käändevormid.
6. **Pere märgis ja tänane toidu saadavus vajasid eraldi vastust.** Perevõimalused ei tõenda ametlikku sertifikaati; menüü ei tõenda laoseisu. Mõlemad saavad täpse kinnitamata info vastuse.
7. **Mängunurga ajad ja mänguasjade allergiaküsimus olid liiga üldised.** Need saavad oma tingimuste vastuse. Restorani tööaega ei esitata mängunurga ajana ning mänguasjade küsimust ei suunata toidumenüüsse.
8. **Raseduse mainimine ei tähenda alati toiduküsimust.** Toidusobivuse vastus eeldab toidukonteksti. Raseda külalise küsimus laua asukoha kohta jääb istumiskoha küsimuseks.
9. **Täpsed teenindusküsimused said liiga üldise vastuse.** Lisatud on läbivaadatud kolmekeelsed vastused näiteks maksmise, kõne salvestamise, menüü vormide, toidumuudatuste, kontaktide ja pere eritingimuste kohta.

Uus moodul sisaldab 31 teenindusteemat. Need vastused kasutavad kontrollitud sõnastusi ja jagatud olekut; nende puhul ei lubata generatiivsel mudelil puuduvat restoraniinfot juurde mõelda. Terviklike läbivaadatud kõrvalküsimuste sõnastused säilitavad broneerimisväljad. Lõdva teemavastega segatud muudatus ei anna seda õigust. See ei anna garantiid kõigi tulevaste sõnastuste tuvastamisele. Selge tundmatu küsimuse puhul peab üldine teadmata info vastus säilima.

## Kohalike vastuste võrdlus

Algseisu 771 ja lõppseisu 810 küsimuse seas võrreldakse samu 771 küsimuse-keele paari. Hiljem lisati 36 tavapäraste lahtiolekuaegade küsimust ja kolm mänguasjade materjalide küsimust.

| Läbivaatuse märge | Algseis | Lõppseisu ühised 771 paari |
| --- | ---: | ---: |
| Kiire abi vastusest puudus 112 | 15 | 0 |
| Teiste loomade küsimus sai koerte loa | 3 | 0 |
| Laste allergeeniküsimus sai täiskasvanute menüü | 9 | 0 |
| Infoküsimus tekitas ootamatuid broneerimise välju | 1 | 0 |
| Üldine teadmata info vastus | 390 | 214 |

Lõppseisu kõigis 810 paaris ei tuvastatud neid nelja konkreetset märget ega uut broneeringu ettepanekut. **214 üldist teadmata info vastust jääb alles.** Osa küsimusi vajab omaniku fakte, osa uusi sõnastusreegleid. Need vastused on kogumikus nähtavad; nende puudumist ei peideta protsendilise „täpsuse” taha.

Algseis pärineb versioonist `6dbf78f`. Uurimuse paranduste vaheversioonis oli 224 üldist teadmata info vastust. Lõppversioon ühendab uurimuse ja sama öö põhiaru muudatused kuni versioonini `a7be09c`; kogu muutust ei omistata ainult selle uurimuse koodile. Ühendamise kontroll leidis ka käibemaksuküsimuse, mis sobitus sõnaga „sisaldavad” allergeenidesse. See saab nüüd maksude ja lisatasude kinnitamata info vastuse.

Märked on automaatse läbivaatuse abivahend, mitte tõend semantilisest või kõnetuvastuse täpsusest. Teemade sobivuse abikaarti laiendati töö käigus, seetõttu selle märke kadumist ei käsitleta sõltumatu kvaliteedimõõduna. Eraldi regressioonitestid kontrollivad oluliste paranduste vastuseid ja vestluse olekut.

## Broneerimine ja kõrvalküsimused

Teenindusküsimusele tuleb vastata ja seejärel küsida seni puuduv kuupäev, kellaaeg või inimeste koguarv. Küsimuse sees olev hind, vanus või roogade arv ei asenda külaliste arvu. Lapsed loetakse külaliste koguarvu sisse.

Valmis kokkuvõtte järel küsitud kõrvalküsimus ei anna nõusolekut. Hoidmise identifikaator ja aegumine säilivad, kuid kokkuvõtte kättetoimetamise ja kinnituse olek tuleb uuendada enne kinnitamist. „Jah, kas mängunurk on olemas?” on küsimus; seda ei tohi käsitleda broneerimise nõusolekuna.

Ebaselget AM/PM kellaaega või mitmetähenduslikku kuupäeva peab täpsustama. Varasemad kuupäeva ja kellaaja parandused toetavad vorme nagu „4th October”, „6 o clock”, vene käänded ja piiratud kirjavead nagu „oktobte”. Bot ei saa lubada kõigi vigade õiget äraarvamist. Kokkuvõte teeb valitud kuupäeva ja aja kliendile kontrollitavaks.

## Allikad ja nende kasutus

Perekülastuse küsimused lähtuvad [Visit Estonia lastega söögikohtade ülevaatest](https://visitestonia.com/en/what-to-do/best-places-to-eat-with-children-in-estonia), [Eesti Lasterikaste Perede Liidu märgise statuudist](https://www.peresobralik.ee/statuut-2/) ja [Tallinki enda perevõimaluste kirjeldusest](https://hotels.tallink.com/news/celebrate-the-final-month-of-summer-and-the-beginning-of-a-new-school-year-in-our-restaurants). Teiste ettevõtete võimalusi, märgiseid ega vanu kampaaniaid ei omistata sellele restoranile.

Koostise, allergeenide ja tõese toiduinfo käsitlus tugineb [Põllumajandus- ja Toiduameti juhisele](https://pta.agri.ee/ettevotjale-tootjale-ja-turustajale/toidu-tootmine/toidu-margistamine). Küsimus koostise kohta ei võrdu lubadusega, et valmistuskeskkond välistab kokkupuute allergeeniga. [Ühendkuningriigi toiduallergia juhis](https://www.gov.uk/food-allergies) on täiendav küsimuste allikas, selle riigi nõudeid ei esitata Eesti õigusena.

Ligipääsu konkreetsete tingimuste küsimused on kooskõlas [Visit Estonia ligipääsetava reisimise juhisega](https://visitestonia.com/en/where-to-go/travel-options-in-estonia-for-people-with-disabilities). Üks üldine jah-vastus ei asenda vajalikku infot sissepääsu, laua ja tualeti kohta.

Kiire abi vastus põhineb [Häirekeskuse 112 juhisel](https://www.112.ee/et/juhend/hadaabinumber-112). Bot suunab helistama ja töötajat kutsuma; see ei ole botipoolne kõne ega meditsiiniline hinnang.

Privaatsuse küsimuste koostamisel kasutati [Andmekaitse Inspektsiooni kõnesalvestamise käsitlust](https://aastaraamat.aki.ee/aastaraamat-2024/telefonikonede-salvestamine). Restorani tegelikku salvestamise ega säilitamise korda ei mõeldud selle põhjal välja. Kaebuste küsimuste tausta jaoks loeti [TTJA avalduse esitamise juhist](https://www.ttja.ee/avalduse-esitamine); runtime ei luba selle põhjal konkreetset hüvitist ega restorani vastamise tähtaega.

[Restorani enda avalik KKK](https://www.gordonramsayrestaurants.com/en/uk/street-burger/faqs) aitas laiendada küsimuste ringi broneerimise, grupikülastuse, kinkekaartide ja tellimuste teemadel. See on Ühendkuningriigi ettevõtte näide; selle hinnad, piirid ja teenused jäävad selle ettevõtte omaks.

Üks leitud Riigi Teataja tekst oli ajalooline ja praeguse järglasversiooni lugemine tagastas JavaScripti kesta. Neid ei kasutatud täpsete kehtivate õigusväidete aluseks. Lugemispiir on kirjas allikaregistris; kontrollitud PTA juhist kasutati praktilise vastuse piiri määramiseks.

## Telefonikõne ja tegeliku teenuse piirid

Veebi ja LiveKiti telefoniboti kood kasutab samu kontrollitud vastuseid. Kohalikud testid kontrollivad native vooru jagatud olekus. See **ei kinnita töötava telefoniprotsessi uut versiooni ega päris operaatorivõrgu kõnet**. Veebisaidi avaldamine ja telefoniprotsessi avaldamine on eri kontrollid.

Uurimuse alguses näitas avalik staatuse liides telefoniväljalaske olekuks `unverified`. Avaldamise järel näitas tagasilugemine `in_sync`, sama veebi ja telefoni sõrmejälge ning avaldatud versiooni `0bbffde`. Avalik ingress ja operaatorikõne olid endiselt kinnitamata. Täpne tagasilugemise aeg on [protokollis](VALIDATION.md). Sünkroonimise kõrval tuleb endiselt teha päris kõne kõigis kolmes keeles; olekuraport ei mõõda kõnetuvastuse kvaliteeti.

Ka toidutellimuse, makse, tagasikõne, kaebuse edastamise või inimesega ühendamise võimalus vajab tegelikku integratsiooni. Selle demo vastus ei tohi öelda, et neid tegevusi tehti. Omaniku järgmine sisuline töö on [puuduvate faktide kinnitamine](OWNER.md), alustades lastemenüü koostisest ja hindadest, perevõimaluste kasutustingimustest, kontaktidest ning köögi allergeeniprotsessist.
