#!/usr/bin/env python3
"""Næmnipróf með skattframtalsmiðgildi (TEK01001).

Endurgerir tölurnar sem verðlagsgreinin (Eggertsson 2026, Verðlagsgrein)
birtir fyrir framreikning íslenska SILC-miðgildisins með vexti miðgildis
ráðstöfunartekna af skattframtölum: framreiknað tekjugildi, tekjuleiðrétt
gildi á kvarða glæru 20, og spágildi aðhvarfsins fyrir Ísland með þessum
tekjunefnara. Les eingöngu fryst gögn úr ``hra/``; sækir ekkert af netinu.

Keyrsla:  python3 forrit/tek01001_naemniprof.py
Úttak:    nidurstodur/tek01001_naemniprof.csv
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
    """Les Eurostat JSON-stat skrá og skilar {geo: gildi} fyrir gefnar síur."""
    d = json.loads(path.read_text())
    dims = d["id"]
    sizes = d["size"]
    index = {dim: d["dimension"][dim]["category"]["index"] for dim in dims}
    strides = {}
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


def ols_loglog(pairs: list[tuple[float, float]]) -> tuple[float, float, float, float]:
    """OLS á ln(y) = a + b ln(x); skilar (a, b, R2, staðalvillu leifa)."""
    xs = [math.log(x) for x, _ in pairs]
    ys = [math.log(y) for _, y in pairs]
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    b = sxy / sxx
    a = my - b * mx
    resid = [y - (a + b * x) for x, y in zip(xs, ys)]
    sse = sum(r * r for r in resid)
    sst = sum((y - my) ** 2 for y in ys)
    r2 = 1 - sse / sst
    se_res = math.sqrt(sse / (n - 2))
    return a, b, r2, se_res


def main() -> None:
    # 1) Skattframtalsmiðgildið (Hagstofa TEK01001, fryst 14.7.2026)
    tek = json.loads((RAW / "hagstofa_tek01001_20260714.json").read_text())
    # Eining-kóði 2 er "Miðgildi allra framteljenda" (kóði 3 er miðgildi
    # þeirra sem hafa viðkomandi tekjur); greinin notar allra-framteljenda-röðina.
    med = {
        row["key"][4]: float(row["values"][0])
        for row in tek["data"]
        if row["key"][1] == "2"
    }
    factor = med["2024"] / med["2020"]

    # 2) Íslenska SILC-miðgildið 2020 í krónum (fryst Eurostat-skrá)
    silc_is_2020 = jsonstat_values(
        RAW / "eurostat_ilc_di03_is_2020.json", unit="NAC"
    )["IS"]

    # 3) Meðalgengi evru 2024: einfalt meðaltal daglegra skráninga SÍ
    quotes = []
    with open(RAW / "sedlabanki_eur_midgengi_2024.csv") as f:
        for line in f:
            parts = line.strip().split(";")
            if len(parts) >= 8 and parts[7]:
                quotes.append(float(parts[7]))
    fx = sum(quotes) / len(quotes)

    # 4) Framreikningur og kvarði glæru 20
    y_is = silc_is_2020 * factor / fx
    medians_2024 = jsonstat_values(RAW / "eurostat_ilc_di03_2024_eur.json")
    y_eu = medians_2024["EU27_2020"]
    ratio = y_is / y_eu

    pli = {
        cat: jsonstat_values(RAW / "eurostat_prc_ppp_ind_2024.json", ppp_cat=cat)
        for cat in ("A01", "E011")
    }
    m_a01 = pli["A01"]["IS"] / ratio
    m_e011 = pli["E011"]["IS"] / ratio

    rows = [
        ("TEK01001 miðgildi 2020", med["2020"], "þús. kr."),
        ("TEK01001 miðgildi 2024", med["2024"], "þús. kr."),
        ("Vaxtastuðull skattframtalsmiðgildis 2020-2024", factor, "hlutfall"),
        ("SILC-miðgildi Íslands, time=2020", silc_is_2020, "ISK"),
        ("Meðalgengi evru 2024", fx, "ISK/EUR"),
        ("Framreiknað miðgildi með vexti skattframtalsmiðgildis", y_is, "EUR"),
        ("Tekjuhlutfall Íslands og ESB", ratio, "hlutfall"),
        ("Tekjuleiðrétt gildi, A01 (glæra 20: 72)", m_a01, "vísitala"),
        ("Tekjuleiðrétt gildi, E011", m_e011, "vísitala"),
    ]

    # 5) Aðhvarfið með miðgildistekjum: ESB-27 í mati, Íslandi spáð utan mats
    for cat in ("E011", "A01"):
        pairs = [
            (medians_2024[g], pli[cat][g])
            for g in EU27
            if g in medians_2024 and g in pli[cat]
        ]
        a, b, r2, se_res = ols_loglog(pairs)
        pred = math.exp(a + b * math.log(y_is))
        actual = pli[cat]["IS"]
        dev = actual / pred - 1
        sv = math.log(actual / pred) / se_res
        rows += [
            (f"Aðhvarf {cat}: teygni", b, "hlutfall"),
            (f"Aðhvarf {cat}: R2", r2, "hlutfall"),
            (f"Aðhvarf {cat}: staðalvilla leifa", se_res, "log-einingar"),
            (f"Aðhvarf {cat}: spáð verðlag Íslands", pred, "vísitala"),
            (f"Aðhvarf {cat}: frávik Íslands", dev, "hlutfall"),
            (f"Aðhvarf {cat}: frávik í staðalvillum leifa", sv, "staðalvillur"),
        ]

    OUT.mkdir(exist_ok=True)
    with open(OUT / "tek01001_naemniprof.csv", "w", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["stærð", "gildi", "eining"])
        for name, val, unit in rows:
            w.writerow([name, f"{val:.6f}".rstrip("0").rstrip("."), unit])

    for name, val, unit in rows:
        print(f"{name}: {val:.4f} {unit}")


if __name__ == "__main__":
    main()
