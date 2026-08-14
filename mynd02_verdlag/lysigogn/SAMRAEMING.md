# Mynd 2: samræming við frumglæru og aðferðarmat

## Frumglæran

Vinstri hlið Myndar 2 byggist á glæru 20 í `stadreyndir-esb-island-juli-2026-2.pdf`.
Glæran nefnir „verðlag í hlutfalli við miðgildi ráðstöfunartekna á mann 2024*“
og birtir sex verðflokka. Nákvæmu gagnasafnskóðarnir koma ekki fram á
glærunni. Nákvæm endurgerð birtu talnanna sýnir að eftirfarandi kóðar
endurgera þær.

Verðgögnin eru úr Eurostat-gagnasafninu `prc_ppp_ind`, með síunum
`freq=A`, `na_item=PLI_EU27_2020` og `time=2024`. Flokkarnir eru:

| Kóði | Heiti |
|---|---|
| `A01` | Einstaklingsbundin neysla |
| `A0101` | Matur og óáfengir drykkir |
| `A0103` | Föt og skór |
| `A010405` | Rafmagn, gas og annað eldsneyti |
| `A010703` | Flutningaþjónusta |
| `A0111` | Veitingastaðir og hótel |

„Almennt verðlag“ á glærunni er því `A01`, ekki `E011`. „Flutningar“ eru
flutningaþjónusta, ekki allur neysluflokkurinn `A0107`.

Tekjugögnin eru úr Eurostat-gagnasafninu `ilc_di03`, með síunum `freq=A`,
`age=TOTAL`, `sex=T`, `statinfo=MED_EI`, `unit=EUR` og `time=2024`.
Heiti `MED_EI` hjá Eurostat er *Median equivalised income*. Hér er stærðin
kölluð miðgildi jafngildra ráðstöfunartekna, það er ráðstöfunartekna heimilis
sem hafa verið leiðréttar fyrir stærð og samsetningu heimilis. Áfram Ísland
nefnir hana miðgildi ráðstöfunartekna á mann. ESB-27-gildið er 21.582 evrur í
frystu gagnaútgáfunni.

Í frosnu tekjugögnunum merkir Eurostat gildi Króatíu `b`, rof í tímaröð, og
gildi Litháens `p`, bráðabirgðagildi. Stöðufánarnir eru varðveittir í
vinnubókinni.

## Endurgerð reikningsins

Látum \(P_{c,k}\) tákna verðlagsvísi lands \(c\) í flokki \(k\), þar sem
ESB-27 er 100. Látum \(Y_c\) tákna miðgildi jafngildra ráðstöfunartekna í
evrum. Kvarði glærunnar er:

\[
M_{c,k}=\frac{P_{c,k}}{Y_c/Y_{ESB}}
       =P_{c,k}\frac{Y_{ESB}}{Y_c}.
\]

Kvarðinn fæst með því að deila verðlagsvísinum með hlutfallslegum tekjum.
Stærðin er því ekki verðlagsvísir í hefðbundnum skilningi. Tekjuhá lönd færast sjálfkrafa niður
og tekjulág lönd upp, jafnvel þótt verðlagið sjálft breytist ekki.

Frumglæran segir að tekjutala Íslands sé framreiknuð frá 2020 með
ráðstöfunartekjum í þjóðhagsreikningum, en birtir ekki formúlu, gagnaútgáfu
eða gengisaðferð. Birtu íslensku gildin endurgerast nákvæmlega með eftirfarandi
framreikningi:

1. `ilc_di03`, `geo=IS`, `time=2020`, `statinfo=MED_EI`, `unit=NAC`:
   4.933.016 krónur.
2. Röðin „Ráðstöfunartekjur (tekjur - gjöld)“ fyrir geira S.14 í
   bráðabirgðauppgjöri Hagstofunnar frá 4. apríl 2025: 1.544.765,940 m.kr.
   árið 2020 og 2.425.484,373 m.kr. árið 2024. Vaxtastuðullinn er
   1,570130665.
3. Einfalt meðaltal 249 daglegra skráninga ársins 2024 úr röð 4064,
   „Evra, skráð miðgengi“, hjá Seðlabanka Íslands: 149,310321 krónur á evru.

Framreiknaða talan er því:

\[
Y_{IS}^{*}=
\frac{4.933.016\times(2.425.484{,}373/1.544.765{,}940)}{149{,}310321}
=51.875{,}05\text{ evrur}.
\]

Hlutfallið \(Y_{IS}^{*}/Y_{ESB}\) er 2,403625. Þar með verður íslenska
`A01`-gildið \(172,7/2,403625=71,8498\), sem er birt sem 72 á
frumglærunni. Sama aðferð endurgerir öll sex íslensku gildin eftir námundun:
72, 60, 60, 27, 71 og 70.

## Gagnaútgáfa og frávik

Af 114 birtum reitum á frumglærunni endurgera núverandi frosnu
Eurostat-gögnin 108 nákvæmlega eftir námundun. Sex frávik eru öll fyrir
Ungverjaland. Núverandi tekjugildi er 8.488 evrur. Sameiginlegt bil
tekjugilda sem endurgerir alla sex reitina er 8.800,30--8.829,56 evrur.
Lokaendurgerðin notar 8.815 evrur, námundaðan miðpunkt bilsins, og endurgerir
því alla 114 reitina eftir námundun.

Þar sem Áfram Ísland birtir ekki gagnaafrit er 8.815 ekki sett fram sem
endurheimt frumgagn. Það er gagnsætt afleitt endurgerðargildi sem sex birtu
reitirnir afmarka. Vinnubókin varðveitir bæði núverandi Eurostat-gildið og
afleidda gildið og sýnir niðurstöðu beggja útreikninga.

Frumglæran sýnir valin ríki, þar á meðal Noreg. Lokamynd greinarinnar sýnir
hins vegar öll 27 ESB-ríkin og Ísland. Noregur er varðveittur í hráum gögnum
til sannprófunar, en er ekki í lokaröðuninni.

## Aðferðafræðilegt frávik í framreikningi Íslands

Sá framreikningur sem endurgerir glæruna margfaldar miðgildi jafngildra
ráðstöfunartekna með vexti heildarráðstöfunartekna alls heimilisgeirans.
Heildartekjur hækka bæði þegar tekjur á mann aukast og þegar íbúum fjölgar.
Því eru þessar tvær stærðir ekki sambærilegar.

Í sömu gagnaútgáfu Hagstofunnar heitir samanburðarröðin „Ráðstöfunartekjur á
mann (í þús. kr.)“. Vaxtastuðull hennar er 1,445606 frá 2020 til 2024, en
vaxtastuðull heildartekna er 1,570131. Notkun heildartekna hækkar
framreiknuðu tekjutöluna um 8,6% vegna fólksfjölgunar. Með vexti á mann yrði
tekjuleiðrétt `A01`-gildi Íslands 78,04 í stað 71,85.

Þetta er næmnipróf sem fjarlægir mannfjöldaáhrif, ekki fullkomin leiðrétting.
Meðaltal ráðstöfunartekna á mann í þjóðhagsreikningum er annað tekjuhugtak en
miðgildi jafngildra ráðstöfunartekna í EU-SILC.

Að auki er `time=2024` í EU-SILC könnunarár. Tekjuviðmiðunartímabilið er
almennt árið á undan. Sama gildir um `time=2020`. Framreikningur 2020 til
2024 í þjóðhagsreikningum fellur því ekki nákvæmlega að tekjuárum SILC.

## Val á hægri hlið lokamyndar

Hægri hliðin sýnir `E011`, hefðbundinn verðlagsvísi einkaneyslu heimila,
án tekjudeilingar. Þetta er röðin sem fyrri útgáfa greinarinnar notar og
gildi Íslands er 161,7. Ísland er hæst í samanburðarhópnum, sem samanstendur
af 27 ESB-ríkjum og Íslandi.

`A01` og `E011` eru efnislega ólík. Einstaklingsbundin neysla (`A01`)
nær einnig yfir einstaklingsbundna þjónustu sem hið opinbera og
félagasamtök greiða, en einkaneysluútgjöld heimila (`E011`) ná til útgjalda
heimilanna sjálfra. Því má ekki segja að aðeins tekjunefnarinn breytist milli
myndhlutanna.

Ísland er í 27. sæti af 28 á kvarða Áfram Íslands og í 1. sæti á
`E011`-kvarðanum. Örin merkir samanburð þessara tveggja skilgreindu
mælikvarða, ekki tímabreytingu. `A01 = 172,7` án tekjudeilingar er varðveitt
í vinnubókinni sem næmnipróf; Ísland er einnig í 1. sæti á þeirri röð.

## Næmnipróf með skattframtalsmiðgildi (viðbót 8. ágúst 2026)

Verðlagsgreinin (stutta greinin um glæru 20) bætir við þriðja
framreikningskostinum: vexti miðgildis ráðstöfunartekna allra framteljenda
16 ára og eldri af skattframtölum (Hagstofa Íslands, TEK01001; heildartekjur
að frádregnum sköttum og greiðslum í lífeyrissjóð). Fryst afrit frá
14. júlí 2026 er í `hra/hagstofa_tek01001_20260714.json`. Svar Hagstofunnar
geymir tvær miðgildisraðir; hér er notuð röðin „Miðgildi allra
framteljenda“ (Eining 2, 4.482 og 6.339 þús. kr.), eins og greinin lýsir.
Hin röðin, „Miðgildi framteljenda sem hafa viðkomandi tekjur/skatta“
(Eining 3, 4.484 og 6.341 þús. kr.), breytir tölunum nær engu.
Vaxtastuðullinn 2020–2024 er 1,414324, á móti 1,570131 fyrir heildartekjur
geirans og 1,445606 á mann. Forritið `forrit/tek01001_naemniprof.py` les
eingöngu frystu skrárnar og endurgerir allar birtar tölur: framreiknað
tekjugildi 46.727,40 evrur, tekjuleiðrétt gildi 79,77 (A01), og
aðhvarfsspár Íslands 140,2 (E011, frávik +15,3%, 1,79 staðalvillur leifa)
og 150,2 (A01, frávik +15,0%, 1,86 staðalvillur). Úttak í
`nidurstodur/tek01001_naemniprof.csv`.

## Róbustnesspróf grunnmatsins (viðbót 10. ágúst 2026)

Forritið `forrit/adhvarf_naemniprof.py` endurgerir grunnmat verðlagsgreinarinnar
úr frystum gögnum (`hra/eurostat_lc_lci_lev_20260714.json`, launakostnaður á
vinnustund 2024, fryst 14.7.2026, og `hra/eurostat_prc_ppp_ind_2024.json`,
E011) og bætir við tveimur úrtaksprófum. Grunnmat: halli 0,424 (staðalfrávik
0,033), R² 0,871, spáð verðlag Íslands 130,6, frávik +23,8% (2,57
staðalfrávik). Ísland innan úrtaks (28 lönd): halli 0,446, R² 0,868, metið
gildi 133,7, frávik +20,9% (2,10 staðalfrávik). Án Lúxemborgar og Írlands (25
lönd, Ísland utan mats): halli 0,408, R² 0,862, spáð 128,2, frávik +26,2%
(2,91 staðalfrávik). Úttak í `nidurstodur/adhvarf_naemniprof.csv`.
