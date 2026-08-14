#!/usr/bin/env python3
"""Ríkin utan ESB og aðhvarfslínan: Ísland, Noregur og Sviss 2012--2024.

Metur aðhvarf verðlags á launakostnað á ESB-ríkjunum 27 fyrir árin 2012,
2016 og 2024 og reiknar frávik ríkjanna þriggja utan ESB frá línu hvers
árs. Les eingöngu frystu skrána ``hra/eurostat_utanesb_adhvarf.json``.

Launakostnaður Sviss er ekki í Eurostat-gögnum; hann er reiknaður úr
gögnum svissnesku hagstofunnar (BFS) eins og lýst er í frystu skránni og
er því aðeins til fyrir 2024.

Keyrsla:  python3 forrit/utanesb_naemniprof.py
Úttak:    nidurstodur/utanesb_naemniprof.csv og adhvarf_utanesb.csv
          (gagnaskrá myndarinnar)
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

LOND = {
    "IS": "Ísland", "NO": "Noregur", "CH": "Sviss",
}

VIDMID = {
    "2012": {"NO": 15.7, "IS": 10.5, "CH": 14.3},
    "2016": {"NO": 9.3, "IS": 29.4, "CH": 14.6},
    "2024": {"NO": -5.5, "IS": 23.8, "CH": 19.1},
}


def ols(xs: list[float], ys: list[float]) -> tuple[float, float, float]:
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - b * mx
    s = math.sqrt(sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys)) / (n - 2))
    return a, b, s


def main() -> None:
    d = json.loads((RAW / "eurostat_utanesb_adhvarf.json").read_text())
    w_ch = d["ch_launakostnadur_2024_eur"]

    rows = []
    for yr, gogn in sorted(d["ar"].items()):
        P = gogn["pli_E011"]
        W = dict(gogn["launakostnadur_eur"])
        if yr == "2024":
            W["CH"] = w_ch
        xs = [math.log(W[g]) for g in EU27]
        ys = [math.log(P[g]) for g in EU27]
        a, b, s = ols(xs, ys)
        for g in ("IS", "NO", "CH"):
            if g not in W or g not in P:
                continue
            pred = math.exp(a + b * math.log(W[g]))
            frav = P[g] / pred - 1
            sd = (math.log(P[g]) - (a + b * math.log(W[g]))) / s
            assert abs(100 * frav - VIDMID[yr][g]) < 0.15, (yr, g, frav)
            rows.append((yr, g, LOND[g], W[g], P[g],
                         round(pred, 1), round(frav, 4), round(sd, 2),
                         round(b, 3)))

    OUT.mkdir(exist_ok=True)
    with (OUT / "utanesb_naemniprof.csv").open("w", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["ar", "geo", "land", "launakostnadur_eur", "pli_E011",
                    "spad", "fravik", "fravik_sd", "teygni_ars"])
        w.writerows(rows)

    # Gagnaskrá aðhvarfsmyndarinnar: ESB-27 árið 2024 auk Íslands, Noregs
    # og Sviss.
    g24 = d["ar"]["2024"]
    with (OUT / "adhvarf_utanesb.csv").open("w", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["geo", "launakostnadur_eur", "pli_E011", "hlutverk"])
        for g in EU27:
            w.writerow([g, g24["launakostnadur_eur"][g], g24["pli_E011"][g],
                        "mat"])
        w.writerow(["IS", g24["launakostnadur_eur"]["IS"],
                    g24["pli_E011"]["IS"], "utan"])
        w.writerow(["NO", g24["launakostnadur_eur"]["NO"],
                    g24["pli_E011"]["NO"], "utan"])
        w.writerow(["CH", w_ch, g24["pli_E011"]["CH"], "utan"])

    # Meðaltal áranna þriggja jafnar út gengissveiflur einstakra ára.
    medal = {}
    for g in ("IS", "NO", "CH"):
        frav = [r[6] for r in rows if r[1] == g]
        if frav:
            medal[g] = sum(frav) / len(frav)
    assert abs(100 * medal["IS"] - 21.2) < 0.2, medal["IS"]
    assert abs(100 * medal["NO"] - 6.5) < 0.2, medal["NO"]
    assert abs(100 * medal["CH"] - 16.0) < 0.2, medal["CH"]

    for r in rows:
        print(f"{r[0]}  {r[2]:8s} W={r[3]:6.2f}  P={r[4]:6.1f}  "
              f"spáð {r[5]:6.1f}  frávik {100*r[6]:+5.1f}%  ({r[7]:+.2f} sf)")
    print("Meðalfrávik áranna 2012, 2016 og 2024:")
    for g, m in medal.items():
        arafjoldi = len([r for r in rows if r[1] == g])
        print(f"  {LOND[g]:8s} {100*m:+5.1f}%  ({arafjoldi} ár)")


if __name__ == "__main__":
    main()
