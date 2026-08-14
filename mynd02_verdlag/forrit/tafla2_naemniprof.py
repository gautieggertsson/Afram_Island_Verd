#!/usr/bin/env python3
"""Endurgerir SILC-línur næmniprófstöflu verðlagsgreinarinnar (tafla 2).

Taflan metur aðhvarfið ln(verðlag) = a + b·ln(tekjur) á ESB-ríkjunum 27,
þar sem tekjurnar eru mælt miðgildi jafngildra ráðstöfunartekna 2024 í
evrum, og spáir fyrir Ísland utan mats. Íslenska tekjugildið er
framreikningur, reiknaður hér frá grunni á þrjá vegu úr frystu gögnunum:

1. framreikningur greiningarinnar: vöxtur heildarráðstöfunartekna
   heimilageirans 2020--2024 (51.875,05 evrur);
2. vöxtur ráðstöfunartekna á mann úr sömu gagnaútgáfu (47.760,92 evrur);
3. vöxtur miðgildis ráðstöfunartekna allra framteljenda af skattframtölum,
   TEK01001, Eining 2 (46.727,40 evrur).

Hver framreikningur er látinn mæta báðum verðlagsvísitölum, E011 og A01;
út koma sex línur töflunnar. Grunnmat greinarinnar (launakostnaður) er í
forritinu adhvarf_naemniprof.py og VLF-línan í vlf_naemniprof.py.

Keyrsla:  python3 forrit/tafla2_naemniprof.py
Úttak:    nidurstodur/tafla2_naemniprof.csv
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


def hagstofulina(heiti: str) -> tuple[float, float]:
    """Skilar gildum áranna 2020 og 2024 úr frystu bráðabirgðatölunum."""
    for line in (RAW / "hagstofa_frett_vintage_2025-04-04_PrrvG.csv").read_text().splitlines():
        cells = line.split("\t")
        if cells[0].strip() == heiti:
            return (float(cells[1].replace(",", ".")),
                    float(cells[5].replace(",", ".")))
    raise KeyError(heiti)


def medalgengi_evru() -> float:
    gengi = []
    for line in (RAW / "sedlabanki_eur_midgengi_2024.csv").read_text().splitlines():
        cells = line.split(";")
        if len(cells) >= 8 and cells[4] == "Evra":
            gengi.append(float(cells[7]))
    return sum(gengi) / len(gengi)


def tek_midgildi() -> tuple[float, float]:
    """TEK01001, Eining 2 (miðgildi allra framteljenda), 2020 og 2024."""
    tek = json.loads((RAW / "hagstofa_tek01001_20260714.json").read_text())
    med = {
        row["key"][4]: float(row["values"][0])
        for row in tek["data"]
        if row["key"][1] == "2"
    }
    return med["2020"], med["2024"]


def ols(xs: list[float], ys: list[float]) -> tuple[float, float, float, float]:
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - b * mx
    res = [y - (a + b * x) for x, y in zip(xs, ys)]
    sse = sum(r * r for r in res)
    r2 = 1 - sse / sum((y - my) ** 2 for y in ys)
    s = math.sqrt(sse / (n - 2))
    return a, b, r2, s


def main() -> None:
    silc_is_2020 = jsonstat_values(
        RAW / "eurostat_ilc_di03_is_2020.json", unit="NAC"
    )["IS"]
    gengi = medalgengi_evru()

    heild_2020, heild_2024 = hagstofulina("Ráðstöfunartekjur (tekjur - gjöld)")
    amann_2020, amann_2024 = hagstofulina("Ráðstöfunartekjur á mann (í þús. kr.)")
    tek_2020, tek_2024 = tek_midgildi()

    framreikningar = [
        ("framreikningur greiningarinnar", heild_2024 / heild_2020, 51875.05),
        ("vöxtur á mann", amann_2024 / amann_2020, 47760.92),
        ("skattframtalsmiðgildi (Eining 2)", tek_2024 / tek_2020, 46727.40),
    ]

    tekjur = jsonstat_values(RAW / "eurostat_ilc_di03_2024_eur.json")
    vidmid = {
        "E011": (146.4, 141.5, 140.2),
        "A01": (158.2, 151.9, 150.2),
    }

    rows = []
    for visitala in ("E011", "A01"):
        pli = jsonstat_values(RAW / "eurostat_prc_ppp_ind_2024.json", ppp_cat=visitala)
        xs = [math.log(tekjur[g]) for g in EU27]
        ys = [math.log(pli[g]) for g in EU27]
        a, b, r2, s = ols(xs, ys)
        for k, (heiti, voxtur, vidm) in enumerate(framreikningar):
            tekjugildi = silc_is_2020 * voxtur / gengi
            assert abs(tekjugildi - vidm) < 0.01, (heiti, tekjugildi)
            spa = math.exp(a + b * math.log(tekjugildi))
            frav = pli["IS"] / spa - 1
            sd = (math.log(pli["IS"]) - (a + b * math.log(tekjugildi))) / s
            assert abs(spa - vidmid[visitala][k]) < 0.05, (visitala, heiti, spa)
            rows.append((
                visitala, heiti,
                round(b, 6), round(r2, 6),
                round(tekjugildi, 2), round(spa, 6),
                round(frav, 6), round(sd, 6),
            ))

    OUT.mkdir(exist_ok=True)
    with (OUT / "tafla2_naemniprof.csv").open("w", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow([
            "visitala", "framreikningur", "teygni", "R2",
            "tekjugildi_eur", "spad_verdlag", "fravik", "fravik_stadalvillur",
        ])
        w.writerows(rows)

    for r in rows:
        print(
            f"{r[0]:5s} {r[1]:35s} teygni {r[2]:.3f}  spáð {r[5]:7.2f}  "
            f"frávik {100*r[6]:+5.1f}%  ({r[7]:.2f} staðalvillur)"
        )


if __name__ == "__main__":
    main()
