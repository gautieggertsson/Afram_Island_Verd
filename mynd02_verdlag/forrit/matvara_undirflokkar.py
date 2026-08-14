#!/usr/bin/env python3
"""Verðlag matvöru á Íslandi 2024 eftir vöruflokkum (mynd 4 í greininni).

Les frysta Eurostat-svarið ``hra/eurostat_prc_ppp_ind_matvara_2024.json``
(gagnasettið prc_ppp_ind, PLI_EU27_2020, árið 2024, Ísland) og skrifar
verðlagsvísitölur matvöruflokkanna í niðurstöðuskrá. Meðaltal ESB er 100.

Flokkarnir fylgja alþjóðlegu neysluflokkuninni sem Eurostat notar:
kjöt og mjólkurvörur bera íslenska verðtolla og magntolla, fiskur ber
enga innflutningstolla. Myndin í greininni sýnir fimm flokka; hér eru
allir sjö varðveittir.

Keyrsla:  python3 forrit/matvara_undirflokkar.py
Úttak:    nidurstodur/matvara_undirflokkar.csv
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "hra"
OUT = ROOT / "nidurstodur"

HEITI = {
    "A0101": "Mat- og drykkjarvörur alls",
    "A01010101": "Brauð og kornvörur",
    "A01010102": "Kjöt",
    "A01010103": "Fiskur",
    "A01010104": "Mjólkurvörur og egg",
    "A01010105": "Olíur og feiti",
    "A01010106": "Ávextir, grænmeti og kartöflur",
}

# Viðmiðunargildi greinarinnar; keyrslan stöðvast ef frysta skráin ber
# önnur gildi.
VIDMID = {
    "A0101": 143.9,
    "A01010101": 150.8,
    "A01010102": 172.5,
    "A01010103": 110.1,
    "A01010104": 171.7,
    "A01010105": 122.4,
    "A01010106": 136.1,
}


def main() -> None:
    d = json.loads((RAW / "eurostat_prc_ppp_ind_matvara_2024.json").read_text())
    idx = d["dimension"]["ppp_cat"]["category"]["index"]
    vals = d["value"]

    rows = []
    for code, i in sorted(idx.items(), key=lambda x: x[1]):
        v = vals[str(i)]
        assert abs(v - VIDMID[code]) < 1e-9, (code, v)
        rows.append((code, HEITI[code], v))

    assert len(rows) == 7, "Vænt sjö vöruflokka."

    OUT.mkdir(exist_ok=True)
    with (OUT / "matvara_undirflokkar.csv").open("w", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["flokkur", "heiti", "pli_2024"])
        w.writerows(rows)

    for code, heiti, v in sorted(rows, key=lambda r: -r[2]):
        print(f"{code:12s} {heiti:32s} {v:6.1f}  ({v-100:+.1f}%)")


if __name__ == "__main__":
    main()
