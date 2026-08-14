# Áfram_Island_Verd — gagna- og endurgerðarpakki verðlagsgreinarinnar

Gagnapakki greinarinnar **„Ísland er mjög dýrt land“** (Gauti B. Eggertsson,
2026), sem metur fullyrðingu Áfram Íslands um að Ísland sé „ódýrt“ þegar
verðlagi er deilt með tekjum. Fullyrðingin er sett fram á síðu 20 í
greiningu Kontext ehf. fyrir RSE og Áfram Ísland frá júlí 2026.

Pakkinn geymir frosin hráafrit allra gagna sem greinin notar, forritin sem
endurgera hverja birta tölu og hverja mynd, og niðurstöðuskrárnar sem út
koma. Ekkert forrit sækir gögn af netinu; allt les úr frystu skránum í
`mynd02_verdlag/hra/`.

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

| Skrá | Efni |
|---|---|
| `eurostat_prc_ppp_ind_2024.json` | Verðlagsvísitölur 2024 (A01, E011 og undirflokkar), ESB = 100 |
| `eurostat_prc_ppp_ind_matvara_2024.json` | Verðlagsvísitölur matvöruflokka 2024 (kjöt, mjólkurvörur, fiskur o.fl.), ESB = 100 |
| `eurostat_laun_a_launthega_2024.json` | Heildarlaunakostnaður (D1) og fjöldi launþega 2024, fyrir mælikvarðann án vinnustunda |
| `eurostat_vinnustundir_2024.json` | Vinnuvika (LFS), vinnuár þjóðhagsreikninga og stundir launakönnunar Eurostat, fyrir næmnipróf vinnustunda |
| `eurostat_ilc_di03_2024_eur.json` | Miðgildi jafngildra ráðstöfunartekna 2024, evrur |
| `eurostat_ilc_di03_is_2020.json` | Sama stærð fyrir Ísland 2020, krónur (síðasta mælda gildið) |
| `eurostat_lc_lci_lev_20260714.json` | Launakostnaður á vinnustund, fryst 14.7.2026 |
| `eurostat_nama_10_pc_2024.json` | Landsframleiðsla á mann 2024, evrur |
| `eurostat_demo_pjan_is.json` | Mannfjöldi Íslands |
| `hagstofa_frett_vintage_2025-04-04_PrrvG.csv` | Bráðabirgðatölur Hagstofunnar um ráðstöfunartekjur heimilageirans, útgáfa 4.4.2025 |
| `hagstofa_tek01001_20260714.json` | Miðgildi ráðstöfunartekna af skattframtölum (TEK01001), fryst 14.7.2026 |
| `hagstofa_thj06020_*.json` | Núverandi útgáfa þjóðhagsreikninga til samanburðar |
| `sedlabanki_eur_midgengi_2024.csv` | Skráð miðgengi evru 2024, allar dagsetningar |

## Forritin og keyrsluröð

Python-forritin (þarf Python 3.10 eða nýrri; `openpyxl` fyrir
sannprófunarforritið og `matplotlib` fyrir aðhvarfsmyndina):

```
python3 forrit/sannreyna_vinnubok.py    # ber vinnubókina saman við frumgögnin
python3 forrit/adhvarf_naemniprof.py    # grunnmatið og úrtakspróf
python3 forrit/tafla2_naemniprof.py     # SILC-línur næmniprófstöflunnar
python3 forrit/tek01001_naemniprof.py   # skattframtalsframreikningurinn
python3 forrit/vlf_naemniprof.py        # VLF-lína næmniprófstöflunnar
python3 forrit/utanesb_naemniprof.py    # samanburðurinn við Noreg og Sviss
python3 forrit/matvara_undirflokkar.py  # verðlag matvöruflokka (mynd 4)
python3 forrit/launthegar_naemniprof.py # næmnipróf án vinnustunda (laun á launþega)
python3 forrit/vinnustundir_naemniprof.py # næmnipróf fyrir mælingu vinnustunda
python3 forrit/gera_mynd_adhvarf.py     # endurgerð aðhvarfsmyndarinnar í Python
```

Öll forritin eru keyrð úr `mynd02_verdlag/`. Hvert þeirra prentar
niðurstöður sínar og skrifar CSV-skrá í `nidurstodur/`; forritin bera
lykiltölur saman við birtu gildin í greininni og stöðvast með villu ef
eitthvað ber á milli.

Myndir 1--4 eru teiknaðar í MATLAB (R2024b). Keyrt úr rót pakkans:

```
matlab -batch "run('mynd02_verdlag/forrit/gera_mynd02_samisvisir.m')"
matlab -batch "run('mynd02_verdlag/forrit/gera_mynd_kaupmattur.m')"
matlab -batch "run('mynd02_verdlag/forrit/gera_mynd3_adhvarf.m')"
matlab -batch "run('mynd02_verdlag/forrit/gera_mynd4_matvara.m')"
```

Forritið `gera_mynd02.m` teiknar eldri útgáfu samanburðarmyndarinnar
(A01 vinstra megin, E011 hægra megin) og er varðveitt til samanburðar.
Forritið `saekja.py` sótti frumgögnin á sínum tíma og skrifaði
manifest-skrána; það þarf ekki að keyra, enda eru hráafritin fryst.

## Skjalfest frávik og fyrirvarar

- **Ungverjaland.** Tekjutalan sem endurgerir alla birta reiti
  greiningarinnar (um 8.815 evrur) er ályktuð af reitunum sjálfum; sótta
  Eurostat-gildið í frysta svarinu er 8.488 evrur. Bæði gildin eru varðveitt
  og merkt í vinnubókinni og í `lysigogn/SAMRAEMING.md`.
- **TEK01001.** Svar Hagstofunnar geymir tvær miðgildisraðir. Hér er notuð
  röðin „Miðgildi allra framteljenda“ (Eining 2), eins og greinin lýsir;
  hin röðin breytir tölunum nær engu.
- **Tímaviðmið SILC.** `time=2024` í EU-SILC vísar almennt til tekjuárs á
  undan könnunarári; framreikningur 2020–2024 í þjóðhagsreikningum fellur
  ekki nákvæmlega að tekjuárum SILC. Sjá `lysigogn/SAMRAEMING.md`.
- **Beltið á aðhvarfsmyndinni** er fast: metið log-verðlag ±2 staðalvillur
  leifa. Það er hvorki öryggis- né spábil.

## Viðmiðunarútgáfur greinarinnar

Endurgerð skal miða við tiltekna útgáfu greinarinnar, auðkennda með
SHA-256-hash PDF-skjalsins, ekki við skráarheiti eitt og sér. Útgáfan
`Verdlagsgrein-7.pdf` (27 bls.) hefur hashið
`a4079c56547a06ce643d01996543c0aacf18163edbe94270832de24720904a23`;
síðari útgáfur bera annan hash en lykiltölur greinarinnar eru óbreyttar.

## Heimildir gagna

Eurostat (`prc_ppp_ind`, `ilc_di03`, `lc_lci_lev`, `nama_10_pc`,
`demo_pjan`), Hagstofa Íslands (þjóðhagsreikningar, TEK01001) og
Seðlabanki Íslands (gengisskráning). Um endurnot gagnanna gilda skilmálar
hverrar stofnunar.
