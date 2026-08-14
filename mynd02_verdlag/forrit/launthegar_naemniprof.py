#!/usr/bin/env python3
"""Næmnipróf án vinnustunda: launakostnaður á hvern launþega.

Metur aðhvarf verðlags (E011) á launakostnað á hvern launþega í evrum,
mælikvarða sem notar engar vinnustundir: heildarlaunakostnaður
þjóðhagsreikninga (D1) deilt með fjölda launþega (SAL_DC). Línan er metin
á ESB-ríkjunum 27 og Íslandi spáð utan mats, eins og í aðalmatinu.

Þar sem engar vinnustundir koma við sögu svarar prófið athugasemdum um
mælingu vinnustunda á Íslandi; niðurstaðan er hin sama og í aðalmatinu.

Les eingöngu frystu skrárnar ``hra/eurostat_laun_a_launthega_2024.json``
(D1 og SAL_DC) og ``hra/eurostat_utanesb_adhvarf.json`` (verðlag 2024).

Keyrsla:  python3 forrit/launthegar_naemniprof.py
Úttak:    nidurstodur/launthegar_naemniprof.csv
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


def geo_gildi(svar: dict) -> dict[str, float]:
    """JSON-stat svar með eina vídd breytilega (geo) -> {geo: gildi}."""
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
        ut[rec["geo"]] = v
    return ut


def main() -> None:
    fryst = json.loads((RAW / "eurostat_laun_a_launthega_2024.json").read_text())
    d1 = geo_gildi(fryst["d1_cp_meur"])
    launthegar = geo_gildi(fryst["launthegar_ths"])
    P = json.loads((RAW / "eurostat_utanesb_adhvarf.json").read_text())["ar"]["2024"]["pli_E011"]

    W = {g: d1[g] * 1e6 / (launthegar[g] * 1000)
         for g in EU27 + ["IS"] if g in d1 and g in launthegar}

    xs = [math.log(W[g]) for g in EU27]
    ys = [math.log(P[g]) for g in EU27]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    a = my - b * mx
    s = math.sqrt(sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys)) / (n - 2))
    r2 = 1 - sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys)) / sum((y - my) ** 2 for y in ys)

    spad = math.exp(a + b * math.log(W["IS"]))
    fravik = P["IS"] / spad - 1
    sd = (math.log(P["IS"]) - (a + b * math.log(W["IS"]))) / s

    # Viðmiðunargildi greinarinnar.
    assert abs(b - 0.4825) < 5e-4, b
    assert abs(r2 - 0.879) < 5e-3, r2
    assert abs(W["IS"] - 77254) < 5, W["IS"]
    assert abs(spad - 133.7) < 0.1, spad
    assert abs(100 * fravik - 20.9) < 0.15, fravik
    assert abs(sd - 2.36) < 0.02, sd

    OUT.mkdir(exist_ok=True)
    with (OUT / "launthegar_naemniprof.csv").open("w", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["geo", "laun_a_launthega_eur", "pli_E011", "hlutverk"])
        for g in EU27:
            w.writerow([g, round(W[g], 1), P[g], "mat"])
        w.writerow(["IS", round(W["IS"], 1), P["IS"], "utan"])

    print(f"Halli {b:.4f}, R² {r2:.3f}. Ísland: {W['IS']:,.0f} evrur á launþega,")
    print(f"spáð verðlag {spad:.1f}, raunverðlag {P['IS']}, frávik {100*fravik:+.1f}% ({sd:.2f} sf).")
    print("Engar vinnustundir í mælikvarðanum; niðurstaðan er hin sama og í aðalmatinu.")


if __name__ == "__main__":
    main()
