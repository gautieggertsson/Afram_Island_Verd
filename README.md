# Áfram_Island_Verd — gagna- og endurgerðarpakki verðlagsgreinarinnar

Gagnapakki greinarinnar **„Ísland er mjög dýrt land"** (Gauti B.
Eggertsson, 2026). Greinin mælir hve mikið af verðlagi á Íslandi launin
skýra, ber niðurstöðuna saman við reynslu ríkjanna sem gengu í ESB árið
1995 og metur fullyrðingu Áfram Íslands um að verðlag hér sé 28% undir
meðaltali ESB, sem sett er fram á síðu 20 í greiningu Kontext ehf. fyrir
RSE og Áfram Ísland frá júlí 2026.

Pakkinn geymir frosin hráafrit allra gagna sem greinin notar, forritin
sem endurgera kjarnaniðurstöður greinarinnar (sjá `lysigogn/` um
umfang), og niðurstöðuskrárnar sem út koma. Ekkert forrit sækir gögn af netinu; allt les úr frystu
skránum í `mynd02_verdlag/hra/`. Hvert forrit ber lykiltölur saman við
birtu gildin í greininni og stöðvast með villu ef eitthvað ber á milli.

## Helstu tölur greinarinnar sem pakkinn endurgerir

- Verðlag Íslands 2024: 161,7 (einkaneysluútgjöld heimila) og 172,7
  (einstaklingsbundin neysla), meðaltal ESB = 100.
- Aðhvarf verðlags á laun á klukkustund, metið á ESB-ríkjunum 27:
  halli 0,42, R² 0,87; spáð verðlag Íslands 131, frávik +23,8%.
- Bil matsins, 24 til 31%, eftir því hvernig vinnustundir eru mældar;
  mælikvarði án vinnustunda (laun á hvern launþega) gefur +20,9%.
- Endurgerð 28%-tölunnar: 0,72 á kvarða greiningarinnar, ásamt
  næmniprófum á framreikningi teknanna (20 til 22% í stað 28).
- Inngöngusamanburðurinn: frávik Finnlands, Svíþjóðar og Austurríkis
  frá metnu sambandi hvert ár 1995 til 2024 (Finnland +18,7% við
  inngöngu, +9,9% árið 2024; Austurríki við línuna allan tímann);
  leitni myndarinnar er Hodrick-Prescott-sía með lambda = 100.
- Framreikningurinn (mynd 4): sameiginlegt hjöðnunarferli Finnlands og
  Svíþjóðar (jafnvægi 6,1%, helmingunartími 7,6 ár) heimfært á stöðu
  Íslands; verðlag færi úr 161,7 í 141 til 153 eftir tíu ár (lækkun 6
  til 13%) og 134 til 147 eftir tuttugu ár (lækkun 9 til 17%); miðmatið
  er um 146 eftir tíu ár (10% lækkun) og um 139 eftir tuttugu (14%).
- Frávikasafn viðauka C: 33 ríki 1995 til 2024; helmingunartími frávika
  6 til 14 ár í breiðu úrtökunum; frávik Íslands +24,9% árið 2024 og
  +15,9% að meðaltali frá 1995, án leitni að línunni.
- Verðlag matvöruflokka 2024: kjöt +72,5%, mjólkurvörur og egg +71,7%,
  fiskur +10,1%.
- Sæti Íslands í neyslu á mann: 4. sæti nú, efsta sæti félli
  hlutfallslegt verðlag að spágildinu.
- Frávik Íslands öll ár launakönnunarinnar: +17 til +29% hvert einasta
  ár frá 2016; niðurstaðan veltur ekki á gengisstöðu eins árs.

## Uppbygging

```
figs/                        myndir greinarinnar (PDF)
mynd02_verdlag/
  hra/                       frosin hráafrit frumgagna
  gogn/                      fryst gagnavinnubók myndakóðans
  forrit/                    öll endurgerðarforrit
  nidurstodur/               niðurstöðuskrár (CSV)
  mynd/                      myndirnar eins og forritin skila þeim
  lysigogn/                  manifest, samræmingarskjal og hjálpargögn
```

## Frumgögn í `hra/`

Öll 17 hráafritin eru skráð í `lysigogn/manifest.json` með stærð í
bætum, SHA-256-hashi, lýsingu og heimild eða fyrirspurnarlýsingu.

| Skrá | Efni |
|---|---|
| `eurostat_prc_ppp_ind_2024.json` | Verðlagsvísitölur 2024 (A01, E011 og undirflokkar), ESB = 100 |
| `eurostat_prc_ppp_ind_matvara_2024.json` | Verðlagsvísitölur matvöruflokka 2024 (kjöt, mjólkurvörur, fiskur o.fl.) |
| `eurostat_utanesb_adhvarf.json` | Verðlag og launakostnaður öll ár launakönnunarinnar 2012–2024, fyrir aðhvarfið og frávik Íslands öll ár (skráin geymir einnig gögn um Noreg og Sviss fyrir aukagreiningu sem birtist ekki í greininni) |
| `eurostat_lc_lci_lev_20260714.json` | Launakostnaður á vinnustund, fryst 14.7.2026 |
| `eurostat_laun_a_launthega_2024.json` | Heildarlaunakostnaður (D1) og fjöldi launþega 2024, fyrir mælikvarðann án vinnustunda |
| `eurostat_vinnustundir_2024.json` | Vinnuvika (LFS), vinnuár þjóðhagsreikninga, stundir launakönnunar Eurostat og vinnumarkaðsrannsóknartöflur Hagstofunnar (VIN00941, VIN00931), fyrir næmnipróf vinnustunda |
| `eurostat_innganga_1995_2024.json` | Verðlag og laun á hvern launþega 1995–2024, fyrir inngöngusamanburðinn (mynd 3) |
| `eurostat_neysla_2024.json` | Magnvísitölur neyslu á mann 2024 (AIC og einkaneysla), fyrir sætisreikninginn |
| `eurostat_ilc_di03_2024_eur.json` | Miðgildi jafngildra ráðstöfunartekna 2024, evrur |
| `eurostat_ilc_di03_is_2020.json` | Sama stærð fyrir Ísland 2020, krónur (síðasta mælda gildið) |
| `eurostat_nama_10_pc_2024.json` | Landsframleiðsla á mann 2024, evrur |
| `eurostat_demo_pjan_is.json` | Mannfjöldi Íslands |
| `hagstofa_frett_vintage_2025-04-04_PrrvG.csv` | Bráðabirgðatölur Hagstofunnar um ráðstöfunartekjur heimilageirans, útgáfa 4.4.2025 |
| `hagstofa_tek01001_20260714.json` | Miðgildi ráðstöfunartekna af skattframtölum (TEK01001), fryst 14.7.2026 |
| `hagstofa_thj06020_*.json` | Núverandi útgáfa þjóðhagsreikninga til samanburðar |
| `sedlabanki_eur_midgengi_2024.csv` | Skráð miðgengi evru 2024, allar dagsetningar |

## Forritin og keyrsluröð

Python-forritin þurfa Python 3.10 eða nýrri ásamt pökkunum `openpyxl`
(les vinnubókina í sannprófunarforritinu), `numpy` (frávikasafns- og
framreikningsforritin) og `matplotlib` (endurgerð aðhvarfsmyndarinnar).
Myndir greinarinnar eru teiknaðar í MATLAB R2024b. Keyrsluröðin:

```
python3 forrit/sannreyna_vinnubok.py      # ber vinnubókina saman við frumgögnin
python3 forrit/adhvarf_naemniprof.py      # aðalmatið (0,42; +23,8%) og úrtakspróf
python3 forrit/vinnustundir_naemniprof.py # bil matsins 24–31% (vinnustundir)
python3 forrit/launthegar_naemniprof.py   # mælikvarðinn án vinnustunda (+20,9%)
python3 forrit/innganga_naemniprof.py     # Finnland, Svíþjóð og Austurríki 1995–2024
python3 forrit/framreikningur_naemniprof.py # framreikningurinn fyrir Ísland (mynd 4)
python3 forrit/panel_naemniprof.py        # frávikasafn viðauka C (þarf numpy)
python3 forrit/neysla_naemniprof.py       # sæti Íslands í neyslu á mann
python3 forrit/matvara_undirflokkar.py    # verðlag matvöruflokka
python3 forrit/utanesb_naemniprof.py      # frávik Íslands öll ár (NO/CH-hlutinn er aukagreining utan greinar)
python3 forrit/tafla2_naemniprof.py       # SILC-línur næmniprófanna
python3 forrit/tek01001_naemniprof.py     # skattframtalsframreikningurinn
python3 forrit/vlf_naemniprof.py          # VLF-næmniprófið
python3 forrit/kaupmattur_naemniprof.py   # inntak kaupmáttarmyndarinnar (53,2 -> 32,9)
python3 forrit/gera_mynd_adhvarf.py       # endurgerð aðhvarfsmyndarinnar í Python
```

Öll forritin eru keyrð úr `mynd02_verdlag/`. Hvert þeirra prentar
niðurstöður sínar og skrifar CSV-skrá í `nidurstodur/`.

Myndir greinarinnar eru teiknaðar í MATLAB (R2024b). Keyrt úr rót
pakkans:

```
matlab -batch "run('mynd02_verdlag/forrit/gera_mynd3_adhvarf.m')"      # aðhvarfsmyndin
matlab -batch "run('mynd02_verdlag/forrit/gera_mynd_kaupmattur.m')"    # kaupmáttur vinnustundar
matlab -batch "run('mynd02_verdlag/forrit/gera_mynd5_innganga.m')"     # inngöngumyndin
matlab -batch "run('mynd02_verdlag/forrit/gera_mynd6_spa.m')"          # framreikningsmyndin
matlab -batch "run('mynd02_verdlag/forrit/gera_mynd02_samisvisir.m')"  # deiling og verðlag hlið við hlið
matlab -batch "run('mynd02_verdlag/forrit/gera_mynd4_matvara.m')"      # matvöruflokkarnir
matlab -batch "run('mynd02_verdlag/forrit/gera_mynd7_neysla.m')"     # neyslumyndin (mynd 6 í grein; skráarheiti sögulegt)
```

Forritið `gera_mynd02.m` teiknar eldri útgáfu samanburðarmyndarinnar og
er varðveitt til samanburðar. Forritið `saekja.py` sótti frumgögnin á
sínum tíma og skrifaði manifest-skrána; það þarf ekki að keyra, enda eru
hráafritin fryst.

## Skjalfest frávik og fyrirvarar

- **Ungverjaland.** Tekjutalan sem endurgerir alla birta reiti
  greiningarinnar (um 8.815 evrur) er ályktuð af reitunum sjálfum; sótta
  Eurostat-gildið í frysta svarinu er 8.488 evrur. Bæði gildin eru
  varðveitt og merkt í vinnubókinni og í `lysigogn/SAMRAEMING.md`.
- **TEK01001.** Svar Hagstofunnar geymir tvær miðgildisraðir. Hér er
  notuð röðin „Miðgildi allra framteljenda" (Eining 2), eins og greinin
  lýsir; hin röðin breytir tölunum nær engu.
- **Tímaviðmið SILC.** `time=2024` í EU-SILC vísar almennt til tekjuárs
  á undan könnunarári; framreikningur 2020–2024 í þjóðhagsreikningum
  fellur ekki nákvæmlega að tekjuárum SILC. Sjá `lysigogn/SAMRAEMING.md`.
- **Inngöngusamanburðurinn** er metinn á upprunalegu aðildarríkjunum
  ellefu, því bresk gögn liggja ekki fyrir í þjóðhagsreikningaröðum
  Eurostat; tekjustærðin fyrir 1995 er laun á hvern launþega, ekki laun
  á klukkustund, sem ekki eru mæld svo langt aftur.
- **Sætisreikningur neyslunnar** er reikningur á kaupmætti óbreyttra
  útgjalda við lægra verðlag, ekki spá um hegðun.
- **Beltið á aðhvarfsmyndinni** er fast: metið log-verðlag ±2
  staðalvillur leifa. Það er hvorki öryggis- né spábil.

## Viðmiðunarútgáfur greinarinnar

Endurgerð skal miða við tiltekna útgáfu greinarinnar, auðkennda með
SHA-256-hash PDF-skjalsins, ekki við skráarheiti eitt og sér. Fimmta
útgáfan, frá 17. ágúst 2026 (39 bls., eftir óháða úttekt: körfusamræmt
neyslumat á mynd 7, framreikningsnæmni, uppfærð ytri gjöld og
frávikasafn án EFTA-ríkja), hefur hashið
`7b0551e766799b15a01efdf7e8bfb60698fe0687583e5cb4dbc0f175ddac79a1`.
Þriðja útgáfan, fyrr sama dag (39 bls., með samantektarsíðu,
framreikningnum á mynd 4 og frávikasafni viðauka C), hefur hashið
`579862c4c8a5933273bfc50e55e3fb63a0e82fa1485e876cef0fc4999c7c7556`.
Útgáfan frá 15. ágúst 2026 (34 bls., með inngöngusamanburðinum og
bilinu 24–31%) hafði hashið
`c592eff2e889c7272eda7d6ea6ef54a3ce84507106ca0e7258fc62862ebafd69`.
Eldri útgáfa, `Verdlagsgrein-7.pdf` (27 bls.), hafði hashið
`a4079c56547a06ce643d01996543c0aacf18163edbe94270832de24720904a23`;
lykiltölur aðalmatsins eru óbreyttar milli útgáfna.

## Heimildir gagna

Eurostat (`prc_ppp_ind`, `ilc_di03`, `lc_lci_lev`, `lc_nnum1_r2`,
`lfsa_ewhan2`, `nama_10_pc`, `nama_10_gdp`, `nama_10_a10`,
`nama_10_a10_e`, `demo_pjan`), Hagstofa Íslands (þjóðhagsreikningar,
TEK01001, vinnumarkaðsrannsókn VIN00941 og VIN00931) og Seðlabanki
Íslands (gengisskráning). Um endurnot gagnanna gilda skilmálar hverrar
stofnunar.
