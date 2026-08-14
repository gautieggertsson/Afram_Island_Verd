#!/usr/bin/env python3
"""Næmnipróf með landsframleiðslu á mann (VLF-lína töflu 2).

Endurgerir VLF-línu næmniprófstöflu verðlagsgreinarinnar: aðhvarf
ln(E011-verðlags) á ln(landsframleiðslu á mann í evrum, nama_10_pc, röð
CP_EUR_HAB) fyrir ESB-ríkin 27 árið 2024, Ísland utan mats og spáð fyrir
það. Les eingöngu fryst gögn úr ``hra/``; sækir ekkert af netinu.

Viðmiðunargildi greinarinnar: teygni 0,41 og frávik Íslands +23%.

Keyrsla:  python3 forrit/vlf_naemniprof.py
Úttak:    nidurstodur/vlf_naemniprof.csv
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


def jsonstat_values(path: Path, **fix: str) -> dict[str, float]:
    d = json.loads(path.read_text())
    dims = d["id"]
    sizes = d["size"]
    index = {dim: d["dimension"][dim]["category"]["index"] for dim in dims}
    strides: dict[str, int] = {}
    acc = 1
    for dim, size in zip(reversed(dims), reversed(sizes)):
        strides[dim] = acc
        acc *= size
    base = 0
    for dim, value in fix.items():
        base += index[dim][value] * strides[dim]
    out = {}
    for geo, gi in index["geo"].items():
        flat = base + gi * strides["geo"]
        val = d["value"].get(str(flat))
        if val is not None:
            out[geo] = float(val)
    return out


def main() -> None:
    pli = jsonstat_values(
        RAW / "eurostat_prc_ppp_ind_2024.json", ppp_cat="E011"
    )
    vlf = jsonstat_values(
        RAW / "eurostat_nama_10_pc_2024.json",
        unit="CP_EUR_HAB", na_item="B1GQ",
    )

    xs = [math.log(vlf[g]) for g in EU27]
    ys = [math.log(pli[g]) for g in EU27]
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    b = sxy / sxx
    a = my - b * mx
    res = [y - (a + b * x) for x, y in zip(xs, ys)]
    sse = sum(r * r for r in res)
    sst = sum((y - my) ** 2 for y in ys)
    r2 = 1 - sse / sst
    s = math.sqrt(sse / (n - 2))

    pred = math.exp(a + b * math.log(vlf["IS"]))
    frav = pli["IS"] / pred - 1
    sd_units = (math.log(pli["IS"]) - (a + b * math.log(vlf["IS"]))) / s

    assert abs(b - 0.411268) < 5e-4, b
    assert abs(r2 - 0.863860) < 5e-4, r2
    assert abs(pred - 131.516) < 5e-2, pred
    assert abs(frav - 0.229506) < 5e-4, frav

    rows = [
        ("Teygni verðlags gagnvart VLF á mann", round(b, 6), "hlutfall"),
        ("R2", round(r2, 6), "hlutfall"),
        ("Staðalvilla leifa", round(s, 6), "log-einingar"),
        ("VLF Íslands á mann", vlf["IS"], "EUR"),
        ("Spáð verðlag Íslands", round(pred, 6), "vísitala"),
        ("Frávik Íslands", round(frav, 6), "hlutfall"),
        ("Frávik í staðalvillum leifa", round(sd_units, 6), "staðalvillur"),
    ]
    OUT.mkdir(exist_ok=True)
    with (OUT / "vlf_naemniprof.csv").open("w", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["stærð", "gildi", "eining"])
        w.writerows(rows)
    for name, val, unit in rows:
        print(f"{name}: {val} {unit}")


if __name__ == "__main__":
    main()
