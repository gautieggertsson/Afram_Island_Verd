#!/usr/bin/env python3
"""Kaupmáttur vinnustundar: endurgerð inntaksskrár kaupmáttarmyndarinnar.

Endurgerir ``nidurstodur/kaupmattur_vinnustundar.csv``, inntaksskrá
myndarinnar ``gera_mynd_kaupmattur.m`` (mynd 2 í greininni), beint úr
frystu hráskránum:

1. ``hra/eurostat_lc_lci_lev_20260714.json``: launakostnaður á
   vinnustund 2024 í evrum (Eurostat, lc_lci_lev, fryst 14.7.2026).
2. ``hra/eurostat_prc_ppp_ind_2024.json``: verðlagsvísitala
   einkaneysluútgjalda heimila (E011), ESB-27 = 100.

Verðleiðrétta gildið er launakostnaður deildur með E011-vísitölunni:
kaupmáttur vinnustundar á sambærilegu verðlagi. Lykiltölur greinarinnar:
Ísland 53,2 evrur á vinnustund (2. sæti), verðleiðrétt 32,9 (9. sæti);
óvegið meðaltal ESB-ríkjanna 27 er 27,7 og vegið ESB-meðaltal Eurostat
33,5 evrur.

Les eingöngu fryst gögn úr ``hra/``; sækir ekkert af netinu.

Keyrsla:  python3 forrit/kaupmattur_naemniprof.py
Úttak:    nidurstodur/kaupmattur_vinnustundar.csv
"""

from __future__ import annotations

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

# Íslensk landaheiti, sama vörpun og í neysla_naemniprof.py og
# nidurstodur/mynd02_haegri_A01.csv.
LOND = {
    "BE": "Belgía", "BG": "Búlgaría", "CZ": "Tékkland", "DK": "Danmörk",
    "DE": "Þýskaland", "EE": "Eistland", "IE": "Írland", "EL": "Grikkland",
    "ES": "Spánn", "FR": "Frakkland", "HR": "Króatía", "IT": "Ítalía",
    "CY": "Kýpur", "LV": "Lettland", "LT": "Litháen", "LU": "Lúxemborg",
    "HU": "Ungverjaland", "MT": "Malta", "NL": "Holland", "AT": "Austurríki",
    "PL": "Pólland", "PT": "Portúgal", "RO": "Rúmenía", "SI": "Slóvenía",
    "SK": "Slóvakía", "FI": "Finnland", "SE": "Svíþjóð", "IS": "Ísland",
}


def jsonstat_values(path: Path, **fix: str) -> dict[str, float]:
    """JSON-stat svar -> {geo: gildi} fyrir fastar víddir í ``fix``."""
    d = json.loads(path.read_text())
    dims = d["id"]
    sizes = d["size"]
    index = {dim: d["dimension"][dim]["category"]["index"] for dim in dims}
    strides: dict[str, int] = {}
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


def talnastrengur(v: float) -> str:
    """Töluformun eins og í frystu skránni: engin óþörf núll aftast."""
    s = repr(v)
    return s[:-2] if s.endswith(".0") else s


def main() -> None:
    wages_raw = json.loads(
        (RAW / "eurostat_lc_lci_lev_20260714.json").read_text()
    )
    wages = {g: v["2024"] for g, v in wages_raw.items() if "2024" in v}
    pli = jsonstat_values(RAW / "eurostat_prc_ppp_ind_2024.json", ppp_cat="E011")

    geos = EU27 + ["IS"]
    assert all(g in wages for g in geos), "Launakostnað vantar fyrir eitthvert land."
    assert all(g in pli for g in geos), "E011-vísitölu vantar fyrir eitthvert land."

    rows = []
    for g in geos:
        cost = float(wages[g])
        p = pli[g]
        rows.append((g, LOND[g], wages[g], p, round(cost / (p / 100.0), 4)))
    # Raðað eftir E011-vísitölunni, hæsta verðlag efst.
    rows.sort(key=lambda r: (-r[3], r[0]))

    # Viðmiðunartölur greinarinnar.
    verd = {g: v for g, _, _, _, v in rows}
    eu_agg = float(wages["EU27_2020"])
    mean_nominal = sum(float(wages[g]) for g in EU27) / len(EU27)
    mean_adjusted = sum(verd[g] for g in EU27) / len(EU27)
    assert abs(verd["IS"] - 32.9) < 0.1, "Verðleiðrétt gildi Íslands stenst ekki."
    assert abs(mean_adjusted - 27.7) < 0.1, "Óvegið meðaltal ESB-27 stenst ekki."
    assert abs(eu_agg - 33.5) < 0.1, "Vegið ESB-meðaltal Eurostat stenst ekki."
    assert abs(mean_nominal - 28.4) < 0.1, "Óvegið meðaltal launakostnaðar stenst ekki."

    saeti_kostnadur = sorted(rows, key=lambda r: (-float(r[2]), r[0]))
    saeti_kaupmattur = sorted(rows, key=lambda r: (-r[4], r[0]))
    s_kost = next(i for i, r in enumerate(saeti_kostnadur, 1) if r[0] == "IS")
    s_kaup = next(i for i, r in enumerate(saeti_kaupmattur, 1) if r[0] == "IS")
    assert (s_kost, s_kaup) == (2, 9), f"Vænt sæti 2 og 9; fékk {s_kost} og {s_kaup}."

    out_path = OUT / "kaupmattur_vinnustundar.csv"
    OUT.mkdir(parents=True, exist_ok=True)
    # CRLF-línulok eins og í frystu skránni.
    with out_path.open("w", encoding="utf-8", newline="") as f:
        f.write("geo;land;launakostnadur_eur;pli_E011;verdleidrett\r\n")
        for g, land, cost, p, v in rows:
            f.write(f"{g};{land};{talnastrengur(float(cost))};{p:.1f};"
                    f"{talnastrengur(v)}\r\n")

    print(f"Ísland: {wages['IS']} evrur á vinnustund ({s_kost}. sæti); "
          f"verðleiðrétt {verd['IS']:.1f} ({s_kaup}. sæti).")
    print(f"Óvegið meðaltal ESB-27: {mean_nominal:.1f} evrur; "
          f"verðleiðrétt {mean_adjusted:.1f}; vegið ESB-meðaltal {eu_agg}.")
    print(f"Skrifað: {out_path}")


if __name__ == "__main__":
    main()
