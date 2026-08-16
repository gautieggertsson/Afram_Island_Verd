#!/usr/bin/env python3
"""Neysla á mann: sæti Íslands nú og félli verðlag að spágildinu.

Les frystar magnvísitölur Eurostat um neyslu á mann (ESB = 100, 2024),
bæði einstaklingsbundna neyslu (AIC, sem telur opinbera þjónustu við
heimilin) og einkaneysluútgjöld heimila, og reiknar tvennt:

1. Sæti Íslands í neyslu á mann meðal ESB-ríkjanna 27 og Íslands við
   núverandi verðlag: 4. sæti á báðum vísitölum.
2. Sæti Íslands héldust neysluútgjöld í evrum óbreytt en hlutfallslegt
   verðlag einkaneyslu félli úr 161,7 í spágildi aðhvarfsins, 130,6:
   raunneysla margfaldast þá með 161,7/130,6 og Ísland fer í efsta
   sæti, jafnfætis eða upp fyrir Lúxemborg. Þetta er reikningur á
   kaupmætti óbreyttra útgjalda, ekki spá.

Fyrir mynd 7 er reikningurinn gerður á körfu myndarinnar sjálfrar:
aðhvarf ln(verðlagsvísitölu einstaklingsbundinnar neyslu, A01) á
ln(launakostnaðar á vinnustund) yfir ESB-ríkin 27, Ísland utan mats.
Verðlag Íslands á körfunni er 172,7 en launin skýra um 137 við opinbera
tímakaupið, 53,2 evrur, og um 129 við tímakaupið sem launakönnun
Eurostat gefur, 46,75 evrur (sjá ``vinnustundir_naemniprof.py``).
Félli verðlag körfunnar að spágildinu ykist magnvísitalan um 25,7 til
34,2 prósent, úr 116 í 145,9 til 155,6, og Ísland færi úr fjórða sæti
í það efsta, upp fyrir Lúxemborg (141).

Munurinn á efsta sæti og fjórða sæti er verðálagið.

Les eingöngu frystu skrárnar ``hra/eurostat_neysla_2024.json``,
``hra/eurostat_prc_ppp_ind_2024.json`` og
``hra/eurostat_lc_lci_lev_20260714.json``.

Keyrsla:  python3 forrit/neysla_naemniprof.py
Úttak:    nidurstodur/neysla_saeti.csv
          nidurstodur/neysla_mynd.csv  (gögn fyrir mynd 7)
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "hra"
OUT = ROOT / "nidurstodur"

EU27 = [
    "BE", "BG", "CZ", "DK", "DE", "EE", "IE", "EL", "ES", "FR",
    "HR", "IT", "CY", "LV", "LT", "LU", "HU", "MT", "NL", "AT",
    "PL", "PT", "RO", "SI", "SK", "FI", "SE",
]

P_IS = 161.7      # hlutfallslegt verðlag einkaneyslu heimila 2024
P_SPAD = 130.64   # spágildi aðhvarfsins (sjá adhvarf_naemniprof.py)

W_IS = 53.2       # launakostnaður á vinnustund 2024, evrur (sama frysta
                  # skrá og adhvarf_naemniprof.py les)
W_LEIDRETT = 46.75  # tímakaup við vinnuár launakönnunar Eurostat 2020,
                    # efri mörk leiðréttingarinnar (rétt eins og í
                    # vinnustundir_naemniprof.py, "Launakönnun Eurostat,
                    # óbreytt stig")

# Íslensk landaheiti, sama vörpun og í nidurstodur/mynd02_haegri_A01.csv.
LOND = {
    "BE": "Belgía", "BG": "Búlgaría", "CZ": "Tékkland", "DK": "Danmörk",
    "DE": "Þýskaland", "EE": "Eistland", "IE": "Írland", "EL": "Grikkland",
    "ES": "Spánn", "FR": "Frakkland", "HR": "Króatía", "IT": "Ítalía",
    "CY": "Kýpur", "LV": "Lettland", "LT": "Litháen", "LU": "Lúxemborg",
    "HU": "Ungverjaland", "MT": "Malta", "NL": "Holland", "AT": "Austurríki",
    "PL": "Pólland", "PT": "Portúgal", "RO": "Rúmenía", "SI": "Slóvenía",
    "SK": "Slóvakía", "FI": "Finnland", "SE": "Svíþjóð", "IS": "Ísland",
}


def flokkagildi(svar: dict) -> dict[str, dict[str, float]]:
    """JSON-stat svar -> {ppp_cat: {geo: gildi}}."""
    dims = svar["id"]
    size = svar["size"]
    inv = {k: {i: c for c, i in svar["dimension"][k]["category"]["index"].items()}
           for k in dims}
    ut: dict[str, dict[str, float]] = {}
    for flat, v in svar["value"].items():
        flat = int(flat)
        idxs = []
        for n in reversed(size):
            idxs.append(flat % n)
            flat //= n
        idxs = list(reversed(idxs))
        rec = {k: inv[k][i] for k, i in zip(dims, idxs)}
        ut.setdefault(rec["ppp_cat"], {})[rec["geo"]] = v
    return ut


def saeti(gildi: dict[str, float], gildi_is: float) -> int:
    rod = sorted([(g, gildi_is if g == "IS" else gildi[g])
                  for g in EU27 + ["IS"] if g in gildi],
                 key=lambda x: -x[1])
    return [i for i, (g, _) in enumerate(rod, 1) if g == "IS"][0]


def main() -> None:
    fryst = json.loads((RAW / "eurostat_neysla_2024.json").read_text())
    gildi = flokkagildi(fryst["magnvisitolur"])

    rows = []
    for cat, heiti in (("A01", "Einstaklingsbundin neysla (AIC)"),
                       ("E011", "Einkaneysluútgjöld heimila")):
        g = gildi[cat]
        nu = g["IS"]
        s_nu = saeti(g, nu)
        leidrett = nu * P_IS / P_SPAD
        s_leidrett = saeti(g, leidrett)
        rows.append((cat, heiti, nu, s_nu, round(leidrett, 1), s_leidrett))

    # Viðmiðunargildi greinarinnar: 4. sæti nú, efsta sæti leiðrétt.
    assert rows[0][2] == 116 and rows[0][3] == 4, rows[0]
    assert rows[1][2] == 114 and rows[1][3] == 4, rows[1]
    assert rows[0][5] == 1 and rows[1][5] == 1, (rows[0], rows[1])

    OUT.mkdir(exist_ok=True)
    with (OUT / "neysla_saeti.csv").open("w", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["flokkur", "heiti", "IS_nu", "saeti_nu",
                    "IS_leidrett", "saeti_leidrett"])
        w.writerows(rows)

    # Reikningur á körfu myndarinnar sjálfrar: aðhvarf ln(verðlags-
    # vísitölu A01) á ln(launakostnaðar á vinnustund) yfir ESB-ríkin 27,
    # Ísland utan mats. Verðhjöðnun körfunnar að spágildinu margfaldar
    # magnvísitöluna með 172,7/spágildi.
    a01 = gildi["A01"]
    ppp = json.loads((RAW / "eurostat_prc_ppp_ind_2024.json").read_text())
    pli_a01 = flokkagildi(ppp)["A01"]
    wages = json.loads((RAW / "eurostat_lc_lci_lev_20260714.json").read_text())
    laun = {g: float(v["2024"]) for g, v in wages.items() if "2024" in v}
    assert abs(pli_a01["IS"] - 172.7) < 0.05, pli_a01["IS"]
    assert abs(laun["IS"] - W_IS) < 0.05, laun["IS"]

    xs = [math.log(laun[g]) for g in EU27]
    ys = [math.log(pli_a01[g]) for g in EU27]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    halli = (sum((x - mx) * (y - my) for x, y in zip(xs, ys))
             / sum((x - mx) ** 2 for x in xs))
    skurdur = my - halli * mx

    spagildi = {}
    avinningur = {}
    magn = {}
    for merki, w_klst in (("lag", W_IS), ("ha", W_LEIDRETT)):
        spagildi[merki] = math.exp(skurdur + halli * math.log(w_klst))
        avinningur[merki] = pli_a01["IS"] / spagildi[merki] - 1
        magn[merki] = round(a01["IS"] * (1 + avinningur[merki]), 1)

    # Viðmiðunargildi greinarinnar: ávinningur 25,7 til 34,2 prósent og
    # efsta sæti á báðum endum bilsins, upp fyrir Lúxemborg (141).
    assert abs(avinningur["lag"] - 0.257) < 0.01, avinningur["lag"]
    assert abs(avinningur["ha"] - 0.342) < 0.01, avinningur["ha"]
    assert a01["LU"] == 141, a01["LU"]
    assert saeti(a01, magn["lag"]) == 1, magn["lag"]
    assert saeti(a01, magn["ha"]) == 1, magn["ha"]

    # Gögn fyrir mynd 7: A01-magnvísitalan fyrir öll ESB-ríkin 27 og
    # Ísland, raðað lækkandi, ásamt neðri og efri mörkum leiðrétta
    # gildisins félli verðlag körfunnar að spágildi aðhvarfsins.
    mynd_rod = sorted([(g, LOND[g], a01[g]) for g in EU27 + ["IS"]],
                      key=lambda x: -x[2])
    with (OUT / "neysla_mynd.csv").open("w", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["geo", "land", "a01"])
        w.writerows(mynd_rod)
        w.writerow(["IS_leidrett_lag", "Ísland við spágildi (neðri mörk)",
                    magn["lag"]])
        w.writerow(["IS_leidrett_ha", "Ísland við spágildi (efri mörk)",
                    magn["ha"]])

    for cat, heiti, nu, s_nu, leidrett, s_leidrett in rows:
        print(f"{heiti}: Ísland {nu} ({s_nu}. sæti) -> "
              f"{leidrett} ({s_leidrett}. sæti) félli verðlagið að"
              " spágildinu.")
    print("Karfa myndar 7 (A01): verðlag Íslands 172,7; launin skýra "
          f"{spagildi['lag']:.1f} við {W_IS} evrur og "
          f"{spagildi['ha']:.1f} við {W_LEIDRETT} evrur.")
    print("Félli verðlag körfunnar að spágildinu ykist magnvísitalan um "
          f"{100 * avinningur['lag']:.1f} til {100 * avinningur['ha']:.1f}"
          f" prósent, úr {a01['IS']:.0f} í {magn['lag']} til {magn['ha']},"
          " og Ísland færi úr fjórða sæti í það efsta (Lúxemborg: 141).")
    print("Munurinn á efsta sæti og fjórða sæti er verðálagið.")


if __name__ == "__main__":
    main()
