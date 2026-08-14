#!/usr/bin/env python3
"""Róbustnesspróf grunnmatsins: Ísland innan úrtaks og án Lúxemborgar/Írlands.

Endurgerir grunnmat verðlagsgreinarinnar (ln P á ln W, ESB-27, verðlagsvísitala
E011 og launakostnaður á vinnustund 2024) og bætir við tveimur prófum:

1. Ísland innan úrtaksins (28 lönd í mati í stað 27).
2. ESB-27 án Lúxemborgar og Írlands (25 lönd í mati, Íslandi spáð utan mats).

Les eingöngu fryst gögn úr ``hra/``; sækir ekkert af netinu.

Keyrsla:  python3 forrit/adhvarf_naemniprof.py
Úttak:    nidurstodur/adhvarf_naemniprof.csv
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
    strides = {}
    acc = 1
    for dim, size in zip(reversed(dims), reversed(sizes)):
        strides[dim] = acc
        acc *= size
    base = sum(index[dim][val] * strides[dim] for dim, val in fix.items())
    out = {}
    for geo, gi in index["geo"].items():
        val = d["value"].get(str(base + gi * strides["geo"]))
        if val is not None:
            out[geo] = float(val)
    return out


def ols_loglog(pairs):
    xs = [math.log(x) for x, _ in pairs]
    ys = [math.log(y) for _, y in pairs]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    b = sxy / sxx
    a = my - b * mx
    resid = [y - (a + b * x) for x, y in zip(xs, ys)]
    sse = sum(r * r for r in resid)
    sst = sum((y - my) ** 2 for y in ys)
    se_res = math.sqrt(sse / (n - 2))
    se_b = se_res / math.sqrt(sxx)
    return a, b, 1 - sse / sst, se_res, se_b


def main() -> None:
    wages = json.loads((RAW / "eurostat_lc_lci_lev_20260714.json").read_text())
    w = {g: float(v["2024"]) for g, v in wages.items() if "2024" in v}
    pli = jsonstat_values(RAW / "eurostat_prc_ppp_ind_2024.json", ppp_cat="E011")
    w_is, p_is = w["IS"], pli["IS"]

    rows = []

    def fit(tag, sample, iceland_in_sample):
        pairs = [(w[g], pli[g]) for g in sample]
        if iceland_in_sample:
            pairs.append((w_is, p_is))
        a, b, r2, se_res, se_b = ols_loglog(pairs)
        pred = math.exp(a + b * math.log(w_is))
        dev = p_is / pred - 1
        sv = math.log(p_is / pred) / se_res
        rows.extend([
            (f"{tag}: fjöldi landa í mati", len(pairs), "lönd"),
            (f"{tag}: halli (teygni)", b, "hlutfall"),
            (f"{tag}: staðalfrávik hallamats", se_b, "hlutfall"),
            (f"{tag}: R2", r2, "hlutfall"),
            (f"{tag}: staðalfrávik frá matslínunni", se_res, "log-einingar"),
            (f"{tag}: spáð/metið verðlag Íslands", pred, "vísitala"),
            (f"{tag}: frávik Íslands", dev, "hlutfall"),
            (f"{tag}: frávik í staðalfrávikum", sv, "staðalfrávik"),
        ])
        return b, r2, pred, dev, sv

    fit("Grunnmat (ESB-27, Ísland utan mats)", EU27, False)
    fit("Ísland innan úrtaks (28 lönd)", EU27, True)
    fit("Án Lúxemborgar og Írlands (25 lönd, Ísland utan mats)",
        [g for g in EU27 if g not in ("LU", "IE")], False)

    OUT.mkdir(exist_ok=True)
    with open(OUT / "adhvarf_naemniprof.csv", "w", newline="") as f:
        wcsv = csv.writer(f, delimiter=";")
        wcsv.writerow(["stærð", "gildi", "eining"])
        for name, val, unit in rows:
            wcsv.writerow([name, f"{val:.6f}".rstrip("0").rstrip("."), unit])

    for name, val, unit in rows:
        print(f"{name}: {val:.4f} {unit}")


if __name__ == "__main__":
    main()
