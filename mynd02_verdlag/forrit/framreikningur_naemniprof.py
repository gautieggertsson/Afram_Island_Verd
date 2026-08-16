#!/usr/bin/env python3
"""Framreikningurinn: verðlag Íslands miðað við reynslu Finnlands og Svíþjóðar.

Metur sameiginlega veldishjöðnun á frávikaferlum Finnlands og Svíþjóðar
1995--2024 (skrifuðum af ``innganga_naemniprof.py``),

    d(t) = c + (d0 - c) * exp(-k t),

með sameiginlegu jafnvægi c og hraða k en eigin upphafsstöðu hvors
ríkis, og heimfærir ferlið á báða enda íslensku upphafsstöðunnar, 23,8
og 30,5 prósent yfir því sem launin skýra. Frávikaferillinn er þýddur í
verðlagsstig með því að halda launastöðu Íslands og meðaltali ESB
föstum: P(t) = P_spa * (1 + d(t)), þar sem P_spa er verðlagið sem
launin skýra og P(0) = 161,7. Ytra bandið bætir við óvissu um hraðann,
helmingunartíma á bilinu 6 til 14 ár úr frávikasafni viðauka C (sjá
``panel_naemniprof.py``).

Viðmiðunargildi greinarinnar sem forritið sannreynir: c = 6,1%,
k = 0,091 (helmingunartími 7,6 ár); verðlag eftir 10 ár 141 til 153
(lækkun 6 til 13%) og eftir 20 ár 134 til 147 (lækkun 9 til 17%).

Les eingöngu ``nidurstodur/innganga_fravik.csv``.

Keyrsla:  python3 forrit/framreikningur_naemniprof.py
Úttak:    nidurstodur/framreikningur_island.csv
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "nidurstodur"

P_IS = 161.7          # verðlag Íslands 2024, meðaltal ESB = 100
D0_LAG, D0_HA = 23.8, 30.5   # bil upphafsfráviksins, prósent
HL_LAG, HL_HA = 14.0, 6.0    # helmingunartímabil panelsins, ár
AR_FRAM = list(range(0, 31))
MERKI_AR = (5, 10, 15, 20, 25)


def les_fravik() -> dict[str, list[float]]:
    slod = OUT / "innganga_fravik.csv"
    assert slod.is_file(), "Keyrið fyrst innganga_naemniprof.py"
    ut: dict[str, list[float]] = {"FI": [], "SE": []}
    with slod.open() as f:
        for r in csv.DictReader(f, delimiter=";"):
            ut["FI"].append(100 * float(r["FI"]))
            ut["SE"].append(100 * float(r["SE"]))
    assert len(ut["FI"]) == 30
    return ut


def leys3(A: list[list[float]], b: list[float]) -> list[float]:
    """Gauss-eyðing fyrir 3x3 kerfi."""
    n = 3
    M = [rod[:] + [b[i]] for i, rod in enumerate(A)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(M[r][col]))
        M[col], M[piv] = M[piv], M[col]
        p = M[col][col]
        for r in range(n):
            if r == col:
                continue
            f = M[r][col] / p
            for c in range(col, n + 1):
                M[r][c] -= f * M[col][c]
    return [M[i][n] / M[i][i] for i in range(n)]


def sameiginlegt_ferli(fravik: dict[str, list[float]]) -> tuple[float, float]:
    """Metur c og k sameiginlega; upphafsstaða hvors ríkis er frjáls.

    Fyrir gefið k er líkanið línulegt: y_gt = c + A_g * exp(-k t), og
    (c, A_FI, A_SE) leyst með minnstu kvaðrötum; k er fundið með
    þéttri leit.
    """
    t = list(range(30))
    best = None
    k = 0.0005
    while k <= 0.5:
        # Normaljöfnur fyrir (c, A_FI, A_SE).
        X = []
        y = []
        for g, dalkur in (("FI", 0), ("SE", 1)):
            for i in t:
                e = math.exp(-k * i)
                rod = [1.0, 0.0, 0.0]
                rod[1 + dalkur] = e
                X.append(rod)
                y.append(fravik[g][i])
        XtX = [[sum(X[r][a] * X[r][b] for r in range(len(X)))
                for b in range(3)] for a in range(3)]
        Xty = [sum(X[r][a] * y[r] for r in range(len(X))) for a in range(3)]
        c, a_fi, a_se = leys3(XtX, Xty)
        sse = sum((y[r] - (X[r][0] * c + X[r][1] * a_fi + X[r][2] * a_se)) ** 2
                  for r in range(len(X)))
        if best is None or sse < best[0]:
            best = (sse, k, c)
        k += 0.0005
    _, k, c = best
    return c, k


def ferill(d0: float, c: float, k: float, t: float) -> float:
    return c + (d0 - c) * math.exp(-k * t)


def stig(d0: float, c: float, k: float, t: float) -> float:
    p_spa = P_IS / (1 + d0 / 100)
    return p_spa * (1 + ferill(d0, c, k, t) / 100)


def main() -> None:
    fravik = les_fravik()
    c, k = sameiginlegt_ferli(fravik)
    hl = math.log(2) / k

    # Viðmiðunargildi greinarinnar.
    assert abs(c - 6.1) < 0.1, c
    assert abs(k - 0.091) < 0.001, k
    assert abs(hl - 7.6) < 0.2, hl

    k_lag = math.log(2) / HL_LAG
    k_ha = math.log(2) / HL_HA

    rodir = []
    for t in AR_FRAM:
        gildi = [stig(d0, c, kk, t)
                 for d0 in (D0_LAG, D0_HA)
                 for kk in (k_lag, k, k_ha)]
        innri = [stig(d0, c, k, t) for d0 in (D0_LAG, D0_HA)]
        rodir.append({
            "t": t,
            "ytra_lag": min(gildi), "ytra_ha": max(gildi),
            "innra_lag": min(innri), "innra_ha": max(innri),
            "mid": sum(innri) / 2,
        })

    # Viðmiðunargildi myndarinnar og meginmálsins (heil stig og prósent).
    vidmid = {5: (148, 157, 3, 8), 10: (141, 153, 6, 13),
              15: (137, 150, 8, 15), 20: (134, 147, 9, 17),
              25: (133, 145, 10, 18)}
    for ar, (lag, ha, f_lag, f_ha) in vidmid.items():
        r = rodir[ar]
        assert round(r["ytra_lag"]) == lag, (ar, r["ytra_lag"])
        assert round(r["ytra_ha"]) == ha, (ar, r["ytra_ha"])
        assert round(100 * (1 - r["ytra_ha"] / P_IS)) == f_lag, ar
        assert round(100 * (1 - r["ytra_lag"] / P_IS)) == f_ha, ar

    # Miðmatið sem samantekt greinarinnar vitnar í: um 146 eftir tíu ár
    # (10% lækkun) og um 139 eftir tuttugu (14% lækkun).
    assert round(rodir[10]["mid"]) == 146, rodir[10]["mid"]
    assert round(rodir[20]["mid"]) == 139, rodir[20]["mid"]
    assert round(100 * (1 - rodir[10]["mid"] / P_IS)) == 10
    assert round(100 * (1 - rodir[20]["mid"] / P_IS)) == 14

    OUT.mkdir(exist_ok=True)
    with (OUT / "framreikningur_island.csv").open("w", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["t", "ytra_lag", "innra_lag", "mid", "innra_ha",
                    "ytra_ha"])
        for r in rodir:
            w.writerow([r["t"]] + [round(r[d], 2) for d in
                                   ("ytra_lag", "innra_lag", "mid",
                                    "innra_ha", "ytra_ha")])

    print(f"Sameiginlegt ferli FI+SE: c = {c:.2f}%, k = {k:.4f}, "
          f"helmingunartími {hl:.1f} ár.")
    print(f"{'ár':>4s}{'verðlag':>16s}{'lækkun':>16s}")
    for ar in MERKI_AR:
        r = rodir[ar]
        print(f"{ar:4d}{r['ytra_lag']:8.0f}-{r['ytra_ha']:.0f}"
              f"{100*(1-r['ytra_ha']/P_IS):10.0f}-"
              f"{100*(1-r['ytra_lag']/P_IS):.0f}%")
    print("Ferillinn nálgast verðlagið sem launin skýra en nær því ekki.")


if __name__ == "__main__":
    main()
