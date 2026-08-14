#!/usr/bin/env python3
"""Næmnipróf fyrir mælingu vinnustunda: frávik Íslands við leiðrétt vinnuár.

Íslenska tímakaupið, 53,2 evrur á vinnustund 2024, er launakostnaður
þjóðhagsreikninga deilt með áætlaðri vinnustundaröð Hagstofunnar
(fjölþætt tölfræðilegt mat úr staðgreiðslugögnum með áætluðum frádrætti
fjarvista). Sú röð telur íslenska vinnuárið eitt hið stysta í Evrópu,
1.451 stund á launþega, þótt samræmdu mælingarnar tvær sem til eru sýni
báðar langt vinnuár: vinnuvika Íslendinga er yfir meðaltali ESB í
vinnumarkaðskönnun Eurostat (35,6 stundir á móti 35,3) og vinnustundir
starfsfólks í fullu starfi þær flestu í Evrópu í launakönnun Eurostat
(1.854 á ári 2020, á móti 1.604 að meðaltali í ESB). Ríki með stutt
vinnuár í þjóðhagsreikningum (Danmörk, Noregur) hafa jafnframt stutta
vinnuviku; Ísland eitt parar langa vinnuviku við stutt vinnuár.

Prófið reiknar vinnuárið beint úr samræmdu vinnuvikunni: virkar vikur
hvers ríkis eru ársstundir þjóðhagsreikninga deilt með vinnuvikunni, og
vinnuár Íslands er vinnuvika þess margfölduð með meðalfjölda virkra
vikna í ESB. Tímakaupið lækkar að sama skapi og frávikið frá
aðhvarfslínunni stækkar. Skekkjan liggur öll í eina átt: engin mæliröð
styður færri stundir en opinbera talan, svo frávikið +24% í greininni
er gólf og bilið 24 til 28% besta matið.

Les eingöngu frystu skrárnar ``hra/eurostat_vinnustundir_2024.json`` og
``hra/eurostat_utanesb_adhvarf.json``.

Keyrsla:  python3 forrit/vinnustundir_naemniprof.py
Úttak:    nidurstodur/vinnustundir_naemniprof.csv
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


def geo_gildi(svar: dict, vidbotarskilyrdi: dict | None = None) -> dict[str, float]:
    """JSON-stat svar -> {geo: gildi}, valfrjálst síað eftir öðrum víddum."""
    dims = svar["id"]
    size = svar["size"]
    inv = {k: {i: c for c, i in svar["dimension"][k]["category"]["index"].items()}
           for k in dims}
    ut = {}
    for flat, v in svar["value"].items():
        flat = int(flat)
        idxs = []
        for n in reversed(size):
            idxs.append(flat % n)
            flat //= n
        idxs = list(reversed(idxs))
        rec = {k: inv[k][i] for k, i in zip(dims, idxs)}
        if vidbotarskilyrdi and any(rec.get(k) != v2 for k, v2 in vidbotarskilyrdi.items()):
            continue
        ut[rec["geo"]] = v
    return ut


def main() -> None:
    fryst = json.loads((RAW / "eurostat_vinnustundir_2024.json").read_text())
    vika = geo_gildi(fryst["vika_lfsa_ewhan2"])
    arsst = geo_gildi(fryst["arsstundir_thsw"])
    fjoldi = geo_gildi(fryst["launthegar_thsper"])
    lcs_st = geo_gildi(fryst["lcs_stundir_fullt_starf"],
                       {"indic_lc": "HW_SAL_Y"})
    lcs_n = geo_gildi(fryst["lcs_fjoldi_fullt_starf"])

    # Samræmdu mælingarnar tvær: vinnuvikan og LCS-stundir í fullu starfi.
    assert abs(vika["IS"] - 35.6) < 0.05, vika["IS"]
    assert abs(vika["EU27_2020"] - 35.3) < 0.05, vika["EU27_2020"]
    lcs_is = lcs_st["IS"] / lcs_n["IS"]
    lcs_eu = lcs_st["EU27_2020"] / lcs_n["EU27_2020"]
    assert abs(lcs_is - 1854) < 2, lcs_is
    assert abs(lcs_eu - 1604) < 2, lcs_eu

    # Vinnuár og virkar vikur.
    ar_is = arsst["IS"] / fjoldi["IS"]
    ar_eu = arsst["EU27_2020"] / fjoldi["EU27_2020"]
    vikur_is = ar_is / vika["IS"]
    vikur_eu = ar_eu / vika["EU27_2020"]
    assert abs(ar_is - 1451) < 2, ar_is
    assert abs(vikur_is - 40.8) < 0.1, vikur_is
    assert abs(vikur_eu - 43.8) < 0.1, vikur_eu

    # Leiðrétt vinnuár Íslands og tímakaup.
    ar_leidrett = vika["IS"] * vikur_eu
    assert abs(ar_leidrett - 1560) < 2, ar_leidrett

    # Aðhvarfslínan úr aðalmatinu (frysta skráin, árið 2024).
    g24 = json.loads((RAW / "eurostat_utanesb_adhvarf.json").read_text())["ar"]["2024"]
    P = g24["pli_E011"]
    W = g24["launakostnadur_eur"]
    xs = [math.log(W[g]) for g in EU27]
    ys = [math.log(P[g]) for g in EU27]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    a = my - b * mx
    assert abs(b - 0.4238) < 5e-4, b

    rows = []
    for heiti, ar in [("Opinberar stundir þjóðhagsreikninga", ar_is),
                      ("Vinnuvika Íslands x virkar vikur ESB", ar_leidrett)]:
        w_kaup = W["IS"] * ar_is / ar
        spad = math.exp(a + b * math.log(w_kaup))
        fravik = P["IS"] / spad - 1
        rows.append((heiti, round(ar, 1), round(w_kaup, 2),
                     round(spad, 1), round(fravik, 4)))

    assert abs(100 * rows[0][4] - 23.8) < 0.15, rows[0]
    assert abs(100 * rows[1][4] - 27.6) < 0.15, rows[1]

    OUT.mkdir(exist_ok=True)
    with (OUT / "vinnustundir_naemniprof.csv").open("w", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["adferd", "vinnuar_klst", "timakaup_eur", "spad_verdlag",
                    "fravik"])
        w.writerows(rows)

    print("Vinnuvika 2024 (Eurostat, launþegar 20-64): "
          f"Ísland {vika['IS']}, ESB {vika['EU27_2020']}")
    print(f"Vinnuár þjóðhagsreikninga: Ísland {ar_is:,.0f}, ESB {ar_eu:,.0f}"
          f"  (virkar vikur: {vikur_is:.1f} á móti {vikur_eu:.1f})")
    print("Launakönnun Eurostat 2020, unnar stundir í fullu starfi: "
          f"Ísland {lcs_is:,.0f} (flestar í Evrópu), ESB {lcs_eu:,.0f}")
    for heiti, ar, w_kaup, spad, fravik in rows:
        print(f"  {heiti:38s} {ar:8,.1f} klst.  {w_kaup:5.2f} evrur  "
              f"spáð {spad:5.1f}  frávik {100*fravik:+5.1f}%")
    print("Aðrar leiðréttingarleiðir (greiddar stundir launarannsóknar að")
    print("frádregnu orlofi og helgidögum; eigin launakönnunarskil Íslands)")
    print("gefa +28 til +31%. Bil greinarinnar: 24 til 28%.")


if __name__ == "__main__":
    main()
