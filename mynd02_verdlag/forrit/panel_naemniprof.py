#!/usr/bin/env python3
"""Frávikasafnið í viðauka C: leitar frávikið frá metna sambandinu til baka?

Notar nákvæmlega sömu forskrift og ``innganga_naemniprof.py``: fyrir
hvert ár 1995--2024 er samband ln(verðlags) og ln(launa á hvern
launþega) metið á upprunalegu aðildarríkjunum ellefu og frávik allra
ríkja sem gögn ná til reiknuð utan mats, 33 ríki alls. Á safninu er
síðan metið villuleiðréttingarsamband,

    d(t+k) - d(t) = alfa + beta * d(t),

fyrir k = 1, 5 og 10 ár, eftir úrtökum (öll ríki; án matsríkjanna
ellefu; aðildarríki á hverjum tíma; ríki utan ESB; Ísland, Noregur og
Sviss), með staðalvillum sem leyfa fylgni innan ríkja. Einnig er
reiknuð hóptaflan (frávik við inngöngu og 2024) og ferill Íslands.

Viðmiðunargildi viðauka C sem forritið sannreynir: helmingunartímabil
6 til 14 ár í úrtakinu án matsríkjanna; aðdráttarpunktur Íslands,
Noregs og Sviss +14 til +15%; frávik Íslands 2024 +24,9% og meðaltal
+15,9% frá 1995.

Þarf numpy. Les eingöngu ``hra/eurostat_innganga_1995_2024.json``.

Keyrsla:  python3 forrit/panel_naemniprof.py
Úttak:    nidurstodur/panel_fravik.csv, panel_villuleidretting.csv,
          panel_hopar.csv
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "hra"
OUT = ROOT / "nidurstodur"

ESB11 = ["BE", "DE", "DK", "EL", "ES", "FR", "IE", "IT", "LU", "NL", "PT"]
AR_TALA = list(range(1995, 2025))
AR = [str(a) for a in AR_TALA]

SAFNTOLUR = {"EA", "EA11", "EA12", "EA13", "EA15", "EA16", "EA17", "EA18",
             "EA19", "EA20", "EA21", "EU15", "EU25", "EU27_2007",
             "EU27_2020", "EU28", "CPC1"}

INNGANGA = {"FI": 1995, "SE": 1995, "AT": 1995,
            "CZ": 2004, "EE": 2004, "CY": 2004, "LV": 2004, "LT": 2004,
            "HU": 2004, "MT": 2004, "PL": 2004, "SI": 2004, "SK": 2004,
            "BG": 2007, "RO": 2007, "HR": 2013}
HOPROD = ["FI", "SE", "AT",
          "CZ", "EE", "CY", "LV", "LT", "HU", "MT", "PL", "SI", "SK",
          "BG", "RO", "HR"]
UTAN = ["IS", "NO", "CH"]


def gildi(svar: dict) -> dict[tuple[str, str], float]:
    """JSON-stat svar -> {(geo, ár): gildi}."""
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
        ut[(rec["geo"], rec["time"])] = v
    return ut


def er_adili(g: str, ar: int) -> bool:
    return g in ESB11 or INNGANGA.get(g, 9999) <= ar


def ols_thyrpad(y: np.ndarray, X: np.ndarray, thyrpingar: np.ndarray):
    """OLS með þyrptum (CR1) staðalvillum eftir ríkjum."""
    n, p = X.shape
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ (X.T @ y)
    u = y - X @ beta
    rike = np.unique(thyrpingar)
    G = len(rike)
    kjot = np.zeros((p, p))
    for g in rike:
        m = thyrpingar == g
        s = X[m].T @ u[m]
        kjot += np.outer(s, s)
    dof = (G / (G - 1)) * ((n - 1) / (n - p))
    V = dof * XtX_inv @ kjot @ XtX_inv
    se = np.sqrt(np.diag(V))
    r2 = 1 - float(u @ u) / float(((y - y.mean()) ** 2).sum())
    return beta, se, r2, n, G


def main() -> None:
    fryst = json.loads((RAW / "eurostat_innganga_1995_2024.json").read_text())
    pli = gildi(fryst["pli_e011"])
    d1 = gildi(fryst["d1_cp_meur"])
    sal = gildi(fryst["launthegar_ths"])

    rike = sorted(({g for g, _ in pli} & {g for g, _ in d1}
                   & {g for g, _ in sal}) - SAFNTOLUR)

    fravik: dict[str, dict[int, float]] = {g: {} for g in rike}
    hallar = []
    for artala, ar in zip(AR_TALA, AR):
        xs, ys = [], []
        for g in ESB11:
            w = d1[(g, ar)] * 1e6 / (sal[(g, ar)] * 1000)
            xs.append(math.log(w))
            ys.append(math.log(pli[(g, ar)]))
        assert len(xs) == 11, ar
        mx, my = sum(xs) / 11, sum(ys) / 11
        b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) \
            / sum((x - mx) ** 2 for x in xs)
        a = my - b * mx
        hallar.append(b)
        for g in rike:
            lyklar = (g, ar)
            if lyklar not in pli or lyklar not in d1 or lyklar not in sal:
                continue
            if any(v is None for v in (pli[lyklar], d1[lyklar], sal[lyklar])):
                continue
            if d1[lyklar] <= 0 or sal[lyklar] <= 0 or pli[lyklar] <= 0:
                continue
            w = d1[lyklar] * 1e6 / (sal[lyklar] * 1000)
            fravik[g][artala] = pli[lyklar] / math.exp(a + b * math.log(w)) - 1

    # Akkeri inngöngusamanburðarins verða að endurgerast nákvæmlega.
    assert abs(100 * fravik["FI"][1995] - 18.8) < 0.2
    assert abs(100 * fravik["SE"][1995] - 17.6) < 0.2
    assert abs(100 * fravik["AT"][1995] - (-0.1)) < 0.2
    assert abs(100 * fravik["FI"][2008] - 7.8) < 0.2
    assert abs(100 * fravik["FI"][2024] - 9.9) < 0.2
    assert 0.30 < min(hallar) and max(hallar) < 0.45
    assert len(rike) == 33, len(rike)

    OUT.mkdir(exist_ok=True)
    with (OUT / "panel_fravik.csv").open("w", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["geo", "ar", "fravik", "adili"])
        for g in rike:
            for artala in AR_TALA:
                if artala in fravik[g]:
                    w.writerow([g, artala, round(fravik[g][artala], 6),
                                int(er_adili(g, artala))])

    # --- Villuleiðréttingarmatið ---
    def urtak(k: int, hvad: str):
        rod = []
        for g in rike:
            for artala in AR_TALA:
                if artala in fravik[g] and (artala + k) in fravik[g]:
                    if hvad == "oll":
                        med = True
                    elif hvad == "an11":
                        med = g not in ESB11
                    elif hvad == "adilar":
                        med = er_adili(g, artala)
                    elif hvad == "utan":
                        med = not er_adili(g, artala)
                    else:
                        med = g in UTAN
                    if med:
                        rod.append((g, fravik[g][artala],
                                    fravik[g][artala + k] - fravik[g][artala]))
        return rod

    ec = []
    for hvad, heiti in [("oll", "Öll ríki"),
                        ("an11", "Án matsríkjanna ellefu"),
                        ("adilar", "Aðildarríki ESB"),
                        ("utan", "Ríki utan ESB"),
                        ("efta", "Ísland, Noregur og Sviss")]:
        for k in (1, 5, 10):
            rod = urtak(k, hvad)
            g = np.array([r[0] for r in rod])
            x = np.array([r[1] for r in rod])
            y = np.array([r[2] for r in rod])
            X = np.column_stack([np.ones_like(x), x])
            (alfa, beta), (se_a, se_b), r2, n, G = ols_thyrpad(y, X, g)
            if -1 < beta < 0:
                hl = k * math.log(0.5) / math.log(1 + beta)
            else:
                hl = float("nan")
            mu = -alfa / beta
            ec.append([heiti, k, n, G, beta, se_b, hl, r2, mu])

    with (OUT / "panel_villuleidretting.csv").open("w", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["urtak", "k", "n", "riki", "beta", "se_beta",
                    "helmingunartimi_ar", "r2", "adrattarpunktur_mu"])
        for rod in ec:
            w.writerow(rod[:4] + [round(v, 5) if v == v else ""
                                  for v in rod[4:]])

    # Viðmiðunargildi viðauka C (tafla C.1).
    lita = {(rod[0], rod[1]): rod for rod in ec}
    assert abs(lita[("Öll ríki", 1)][4] - (-0.0834)) < 0.003
    assert abs(lita[("Án matsríkjanna ellefu", 1)][4] - (-0.1008)) < 0.003
    assert abs(lita[("Aðildarríki ESB", 1)][4] - (-0.0336)) < 0.003
    assert abs(lita[("Ísland, Noregur og Sviss", 1)][4] - (-0.197)) < 0.005
    hl_an11 = [lita[("Án matsríkjanna ellefu", k)][6] for k in (1, 5, 10)]
    assert 6.0 < min(hl_an11) and max(hl_an11) < 14.0, hl_an11
    mu_efta = [lita[("Ísland, Noregur og Sviss", k)][8] for k in (1, 5, 10)]
    assert all(0.14 < m < 0.15 for m in mu_efta), mu_efta

    # --- Hóptaflan ---
    hopur = []
    for g in HOPROD:
        inn = INNGANGA[g]
        hopur.append([g, inn, fravik[g][inn], fravik[g][2024]])
    for g in UTAN:
        hopur.append([g, "utan ESB", fravik[g][1995], fravik[g][2024]])

    with (OUT / "panel_hopar.csv").open("w", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["geo", "innganga", "fravik_vid_inngongu", "fravik_2024"])
        for rod in hopur:
            w.writerow(rod[:2] + [round(v, 4) for v in rod[2:]])

    # Viðmiðunargildi töflu C.2 og krosshallinn.
    h = {rod[0]: rod for rod in hopur}
    assert abs(100 * h["FI"][2] - 18.7) < 0.15 and abs(100 * h["FI"][3] - 9.9) < 0.15
    assert abs(100 * h["RO"][3] - (-19.1)) < 0.15
    assert abs(100 * h["IS"][3] - 24.9) < 0.15
    assert abs(100 * h["NO"][3] - 1.0) < 0.15
    x = np.array([rod[2] for rod in hopur[:16]])
    y = np.array([rod[3] for rod in hopur[:16]])
    X = np.column_stack([np.ones_like(x), x])
    (a16, b16), (_, se16), *_ = ols_thyrpad(y, X, np.array([r[0] for r in hopur[:16]]))
    # Einföld OLS-staðalvilla (eitt ár á ríki, engin þyrping).
    u = y - (a16 + b16 * x)
    se_ols = math.sqrt((u @ u / (len(x) - 2))
                       * np.linalg.inv(X.T @ X)[1, 1])
    assert abs(b16 - 0.285) < 0.02, b16
    assert abs(se_ols - 0.204) < 0.02, se_ols

    # --- Ferill Íslands ---
    ar_is = sorted(fravik["IS"])
    d_is = np.array([fravik["IS"][a] for a in ar_is])
    t = np.array(ar_is, float) - 1995.0
    Xt = np.column_stack([np.ones_like(t), t])
    halli_t = np.linalg.lstsq(Xt, d_is, rcond=None)[0][1]
    assert abs(100 * fravik["IS"][2024] - 24.9) < 0.15
    assert abs(100 * d_is.mean() - 15.9) < 0.15
    assert abs(100 * d_is.std(ddof=1) - 8.8) < 0.15
    assert abs(100 * halli_t - 0.39) < 0.05

    print(f"Frávikasafnið: {len(rike)} ríki, 1995 til 2024.")
    print("Villuleiðrétting (beta, k=1): "
          + "; ".join(f"{rod[0]} {rod[4]:+.3f}" for rod in ec if rod[1] == 1))
    print(f"Helmingunartímabil án matsríkjanna: "
          f"{min(hl_an11):.1f} til {max(hl_an11):.1f} ár.")
    print(f"Aðdráttarpunktur Íslands, Noregs og Sviss: "
          f"{100*min(mu_efta):.1f} til {100*max(mu_efta):.1f}%.")
    print(f"Ísland: 2024 {100*fravik['IS'][2024]:+.1f}%, meðaltal "
          f"{100*d_is.mean():+.1f}%, leitni {100*halli_t:+.2f} prósentustig á ári.")
    print("Ekkert ríki sem gekk inn með stórt jákvætt frávik hélt því.")


if __name__ == "__main__":
    main()
