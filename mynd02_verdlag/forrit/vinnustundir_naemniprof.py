#!/usr/bin/env python3
"""Næmnipróf fyrir mælingu vinnustunda: frávik Íslands við leiðréttar stundir.

Íslenska tímakaupið, 53,2 evrur á vinnustund 2024, hvílir á vinnustundum
þjóðhagsreikninga, sem eru að hluta áætlaðar. Samantekt á fjórum óháðum
mæliröðum Hagstofunnar (vinnustundir þjóðhagsreikninga; raunverulegar og
venjulegar stundir vinnumarkaðsrannsóknar; greiddar stundir
launarannsóknar, sbr. töflur nama_10_a10_e hjá Eurostat og VIN00941 og
VIN02002 hjá Hagstofu) bendir til þess að opinberu stundirnar séu fremur
van- en oftaldar; besta matið er um 2,5% fleiri stundir árið 2024 en
þjóðhagsreikningar telja. Fleiri stundir þýða lægra tímakaup og stærra
frávik frá aðhvarfslínunni.

Þetta forrit endurmetur frávik Íslands þegar vinnustundir eru leiðréttar
um 0 til 10%: tímakaupið verður 53,2/(1+x) og spáin færist eftir línunni
sem metin er á ESB-ríkjunum 27. Skekkjan liggur öll í eina átt: hver
leiðrétting stækkar frávikið, svo talan +24% í greininni er gólf.

Les eingöngu frystu skrána ``hra/eurostat_utanesb_adhvarf.json``.

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

# Leiðrétting vinnustunda: 0 = opinberar tölur; 0,025 = besta mat
# samantektarinnar; hærri gildi til fróðleiks.
LEIDRETTINGAR = [0.0, 0.025, 0.05, 0.10]


def main() -> None:
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
    for x in LEIDRETTINGAR:
        w_leidrett = W["IS"] / (1 + x)
        spad = math.exp(a + b * math.log(w_leidrett))
        fravik = P["IS"] / spad - 1
        rows.append((x, round(w_leidrett, 2), round(spad, 1), round(fravik, 4)))

    assert abs(100 * rows[0][3] - 23.8) < 0.15, rows[0]
    assert abs(100 * rows[1][3] - 25.1) < 0.15, rows[1]
    assert abs(100 * rows[3][3] - 28.9) < 0.15, rows[3]

    OUT.mkdir(exist_ok=True)
    with (OUT / "vinnustundir_naemniprof.csv").open("w", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["leidretting_stunda", "timakaup_eur", "spad_verdlag", "fravik"])
        w.writerows(rows)

    print("Leiðrétting stunda  Tímakaup  Spáð verðlag  Frávik Íslands")
    for x, wl, sp, fr in rows:
        merki = "  <- besta mat samantektarinnar" if abs(x - 0.025) < 1e-9 else ""
        print(f"{100*x:16.1f}%  {wl:8.2f}  {sp:12.1f}  {100*fr:+12.1f}%{merki}")
    print("Hver leiðrétting stækkar frávikið; +24% í greininni er því gólf.")


if __name__ == "__main__":
    main()
