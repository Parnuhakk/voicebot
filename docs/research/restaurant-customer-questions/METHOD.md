# Restorani kliendiküsimuste uurimise meetod

Materjal aitab otsustada, millele kõneabiline saab praegu vastata, millised andmed tuleb omanikult koguda ja milliseid tegevusi saab süsteem tegelikult teha. Igal küsimuse mõistel on eraldi eesti, inglise ja vene versioon ning vastus. Kogumik ei tõesta kõigi võimalike sõnastuste või kõigi päris kõnede mõistmist.

## Faktide päritolu

Restorani vastuse aluseks on omaniku kinnitus, kontrollitud profiil või tegeliku rakenduse tegevusreegel. Teiste restoranide veebilehed annavad küsimuste ideid. Nende menüü, hinnad ja võimalused ei muutu selle restorani faktideks. Avalike asutuste juhiseid kasutatakse teabe täpsuse, allergeenide, hädaolukordade ja andmekaitse vastuste piiride määramiseks. Allikate register on failis `sources.json`.

Praegune restoraniprofiil on fiktiivne demo. Sellest saadud menüü ja lahtiolekuajad on demo andmed. Joonistamisvõimaluse, mänguasjade, mängunurga ja lastemenüü olemasolu kinnitas kasutaja selles vestluses 4. oktoobril 2026. Lastemenüü koostist, hindu, lapsehoidu ja vanusepiiranguid ta ei kinnitanud.

## Vastuste koostamine

Vastus peab esmalt käsitlema küsitud asja. Teadmata küsimuse puhul nimetab see täpse puuduva info ja palub restorani töötajaga täpsustada. Teadmata asja ei esitata puuduva teenusena. Erisoovi võimalikkust ei esitata kokkulepituna. Bot ei ütle, et tegi tellimuse, edastas kaebuse, kutsus kiirabi või ühendas töötajaga, kui sellist tegevust ei toimunud.

Kuupäeva, kellaaja ja inimeste arvu kogumine tuleb eristada üldisest infoküsimusest. Laste menüü, lapse vanuse või mängunurga kohta käiva küsimuse numbrid ei tohi muuta broneeringu inimeste arvu. Küsimus keset broneerimist peab säilitama seni kogutud andmed ja jätkama õige puuduva välja küsimist. Valmis kokkuvõtte järel vajatakse endiselt selle lugemist või kuulamist ja hilisemat selget kinnitust.

## Kontrollide ulatus

Kirjalikud päringud mängitakse läbi jagatud vestluskoodiga, kohaliku SQLite'i ja sünteetiliste andmetega. Vastuste sisu võrreldakse eraldi koostatud kontrollitud vastustega. Suunamise kontroll ei ole kõnetuvastuse kvaliteedimõõt. Brauserikontroll kasutab päris lehte ja HTTP liidest, kuid teenusepakkujate fixturesid. LiveKiti vooru kontroll kasutab paigaldatud SDK-d ja sama jagatud kõneolekut; see ei ole päris operaatorivõrgu telefonikõne.

Omaniku täpsustamist vajavad andmed jäävad kogumikus nähtavaks. Puuduvat aadressi, kontaktisikut, telefoniprotsessi versiooni või allergiaohutuse kinnitust ei asendata oletusega. Päris kõnede kontroll nõuab eraldi töötava telefoniprotsessi ja tegeliku kõnesignaali kontrollimist.
