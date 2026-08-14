#!/usr/bin/env python3
"""Endurgerð aðhvarfsmyndar verðlagsgreinarinnar (mynd 3) úr frosnum gögnum.

Teiknar punktarit ESB-ríkjanna 27: launakostnaður á vinnustund 2024 á
lárétta ásnum (log-kvarði) og E011-verðlagsvísitala á þeim lóðrétta
(log-kvarði). Aðhvarfslínan er metin á ríkjunum 27, Ísland er utan mats og
sýnt sérstaklega. Skyggða beltið er FAST belti: metið log-verðlag ±2
staðalvillur leifa; það er hvorki öryggis- né spábil.

Myndin er efnisleg endurgerð birtu myndarinnar (figs/m12_adhvarf.pdf), gerð
til að endurgerðarpakkinn teikni hverja mynd úr frosnum gögnum; útlit er
einfaldað en allir punktar, línan, beltið og frávik Íslands eru eins.

Keyrsla:  python3 forrit/gera_mynd_adhvarf.py
Úttak:    mynd/m12_adhvarf_endurgerd.pdf og .png
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "hra"
OUT = ROOT / "mynd"

EU27 = [
    "BE", "BG", "CZ", "DK", "DE", "EE", "IE", "EL", "ES", "FR",
    "HR", "IT", "CY", "LV", "LT", "LU", "HU", "MT", "NL", "AT",
    "PL", "PT", "RO", "SI", "SK", "FI", "SE",
]

GRAY = "#6b6b6b"
BLUE = "#2a78d6"
RED = "#c0392b"
INK = "#1a1a1a"


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
    pli = jsonstat_values(RAW / "eurostat_prc_ppp_ind_2024.json", ppp_cat="E011")
    wages = json.loads((RAW / "eurostat_lc_lci_lev_20260714.json").read_text())
    w = {g: float(wages[g]["2024"]) for g in EU27 + ["IS"]}

    xs = [math.log(w[g]) for g in EU27]
    ys = [math.log(pli[g]) for g in EU27]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - b * mx
    res = [y - (a + b * x) for x, y in zip(xs, ys)]
    s = math.sqrt(sum(r * r for r in res) / (n - 2))

    pred_is = math.exp(a + b * math.log(w["IS"]))
    assert abs(b - 0.423789) < 5e-4
    assert abs(pred_is - 130.638) < 5e-2

    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    grid = [math.log(v) for v in (9, 60)]
    lx = [grid[0] + i * (grid[1] - grid[0]) / 200 for i in range(201)]
    line = [a + b * x for x in lx]
    ax.fill_between(
        [math.exp(x) for x in lx],
        [math.exp(v - 2 * s) for v in line],
        [math.exp(v + 2 * s) for v in line],
        color=BLUE, alpha=0.12, linewidth=0,
        label="Fast belti: lína ±2 staðalvillur leifa",
    )
    ax.plot([math.exp(x) for x in lx], [math.exp(v) for v in line],
            color=BLUE, lw=1.6, label="Metið aðhvarf (ESB-27)")
    ax.scatter([w[g] for g in EU27], [pli[g] for g in EU27],
               s=28, color=GRAY, zorder=3, label="ESB-ríkin 27")
    ax.scatter([w["IS"]], [pli["IS"]], s=60, color=RED, zorder=4,
               label="Ísland (utan mats)")
    ax.annotate("Ísland: 161,7\nspáð: 131", (w["IS"], pli["IS"]),
                textcoords="offset points", xytext=(10, -6),
                color=RED, fontsize=9, fontweight="bold")
    ax.plot([w["IS"], w["IS"]], [pred_is, pli["IS"]],
            color=RED, lw=1.1, ls=":", zorder=2)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks([10, 15, 20, 30, 40, 55])
    ax.set_yticks([60, 80, 100, 120, 140, 160])
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.get_xaxis().set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.get_yaxis().set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_xlabel("Launakostnaður á vinnustund 2024, evrur (log-kvarði)")
    ax.set_ylabel("Verðlagsvísitala E011, ESB=100 (log-kvarði)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout()

    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / "m12_adhvarf_endurgerd.pdf")
    fig.savefig(OUT / "m12_adhvarf_endurgerd.png", dpi=200)
    print("Skrifað:", OUT / "m12_adhvarf_endurgerd.pdf")


if __name__ == "__main__":
    main()
