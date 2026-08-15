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

Munurinn á efsta sæti og fjórða sæti er verðálagið.

Les eingöngu frystu skrána ``hra/eurostat_neysla_2024.json``.

Keyrsla:  python3 forrit/neysla_naemniprof.py
Úttak:    nidurstodur/neysla_saeti.csv
"""

from __future__ import annotations

import csv
import json
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

    for cat, heiti, nu, s_nu, leidrett, s_leidrett in rows:
        print(f"{heiti}: Ísland {nu} ({s_nu}. sæti) -> "
              f"{leidrett} ({s_leidrett}. sæti) félli verðlagið að"
              " spágildinu.")
    print("Munurinn á efsta sæti og fjórða sæti er verðálagið.")


if __name__ == "__main__":
    main()
