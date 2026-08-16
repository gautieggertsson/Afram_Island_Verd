#!/usr/bin/env python3
"""Inngöngusamanburðurinn: Finnland, Svíþjóð og Austurríki 1995--2024.

Fyrir hvert ár 1995--2024 er samband verðlags og launa metið á
upprunalegu aðildarríkjunum ellefu (Bretland vantar í
þjóðhagsreikningaraðir Eurostat) og frávik ríkjanna þriggja sem gengu í
sambandið 1995 reiknuð utan mats: hlutfallslegt verðlag hvers þeirra
deilt með spágildinu af línunni. Tekjustærðin er laun á hvern launþega
(heildarlaunakostnaður deilt með fjölda launþega), eina launastærðin sem
mæld er alla leið aftur til 1995; launakostnaður á klukkustund nær
aðeins til 2008.

Leitni myndarinnar er Hodrick-Prescott-sía með lambda = 100, sem
hreinsar burt sveiflur sem standa skemur en um áratug, einkum
gengissveiflur (sjá Ravn og Uhlig 2002 um val á lambda fyrir árleg
gögn; hefðbundna hagsveiflugildið 6,25 skilur gengissveiflurnar eftir).
Fimm ára miðjusett meðaltal fyrri útgáfu er reiknað áfram til
samanburðar og skrifað í sömu skrá.

Les eingöngu frystu skrána ``hra/eurostat_innganga_1995_2024.json``.

Keyrsla:  python3 forrit/innganga_naemniprof.py
Úttak:    nidurstodur/innganga_fravik.csv
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "hra"
OUT = ROOT / "nidurstodur"

ESB11 = ["BE", "DE", "DK", "EL", "ES", "FR", "IE", "IT", "LU", "NL", "PT"]
NY1995 = ["FI", "SE", "AT"]
AR = [str(a) for a in range(1995, 2025)]
LAMBDA_HP = 100.0


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


def leitni5(rod: list[float]) -> list[float]:
    """Fimm ára miðjusett meðaltal, styttri gluggi við endana."""
    n = len(rod)
    ut = []
    for i in range(n):
        lo, hi = max(0, i - 2), min(n, i + 3)
        ut.append(sum(rod[lo:hi]) / (hi - lo))
    return ut


def hp_sia(rod: list[float], lam: float = LAMBDA_HP) -> list[float]:
    """Hodrick-Prescott-leitni: leysir (I + lam*D'D) tau = y.

    Hrein Python-útfærsla með Gauss-eyðingu; kerfið er aðeins 30x30 svo
    engin þörf er á tölfræðipökkum.
    """
    n = len(rod)
    # A = I + lam * D'D, þar sem D er (n-2)xn fylki annarrar mismununar.
    A = [[0.0] * n for _ in range(n)]
    for i in range(n):
        A[i][i] = 1.0
    for i in range(n - 2):
        d = [0.0] * n
        d[i], d[i + 1], d[i + 2] = 1.0, -2.0, 1.0
        for a in range(i, i + 3):
            for b in range(i, i + 3):
                A[a][b] += lam * d[a] * d[b]
    y = list(rod)
    # Gauss-eyðing með vali á stærsta stuðli í dálki.
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(A[r][col]))
        A[col], A[piv] = A[piv], A[col]
        y[col], y[piv] = y[piv], y[col]
        p = A[col][col]
        for r in range(col + 1, n):
            f = A[r][col] / p
            if f == 0.0:
                continue
            for c in range(col, n):
                A[r][c] -= f * A[col][c]
            y[r] -= f * y[col]
    tau = [0.0] * n
    for r in range(n - 1, -1, -1):
        s = y[r] - sum(A[r][c] * tau[c] for c in range(r + 1, n))
        tau[r] = s / A[r][r]
    return tau


def lowess(rod: list[float], hlutfall: float = 0.55) -> list[float]:
    """Staðbundin línuleg aðhvarfssléttun (LOWESS) með þríteningsvogum.

    Notuð í næmniprófi neðanmálsgreinar greinarinnar um val sléttunar:
    endapunktar hennar mega ekki víkja meira en hálfu stigi frá
    HP-leitninni.
    """
    n = len(rod)
    gluggi = max(3, int(round(hlutfall * n)))
    ut = []
    for i in range(n):
        fjarl = sorted(range(n), key=lambda j: abs(j - i))[:gluggi]
        h = max(abs(j - i) for j in fjarl) or 1
        vigt = {j: (1 - (abs(j - i) / h) ** 3) ** 3 for j in fjarl}
        sw = sum(vigt.values())
        sx = sum(vigt[j] * j for j in fjarl)
        sy = sum(vigt[j] * rod[j] for j in fjarl)
        sxx = sum(vigt[j] * j * j for j in fjarl)
        sxy = sum(vigt[j] * j * rod[j] for j in fjarl)
        nefnari = sw * sxx - sx * sx
        if abs(nefnari) < 1e-12:
            ut.append(sy / sw)
            continue
        b = (sw * sxy - sx * sy) / nefnari
        a = (sy - b * sx) / sw
        ut.append(a + b * i)
    return ut


def main() -> None:
    fryst = json.loads((RAW / "eurostat_innganga_1995_2024.json").read_text())
    pli = gildi(fryst["pli_e011"])
    d1 = gildi(fryst["d1_cp_meur"])
    sal = gildi(fryst["launthegar_ths"])

    fravik = {g: [] for g in NY1995}
    hallar = []
    for ar in AR:
        xs, ys = [], []
        for g in ESB11:
            w = d1[(g, ar)] * 1e6 / (sal[(g, ar)] * 1000)
            xs.append(math.log(w))
            ys.append(math.log(pli[(g, ar)]))
        n = len(xs)
        assert n == 11, (ar, n)
        mx, my = sum(xs) / n, sum(ys) / n
        b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) \
            / sum((x - mx) ** 2 for x in xs)
        a = my - b * mx
        hallar.append(b)
        for g in NY1995:
            w = d1[(g, ar)] * 1e6 / (sal[(g, ar)] * 1000)
            spad = math.exp(a + b * math.log(w))
            fravik[g].append(pli[(g, ar)] / spad - 1)

    # Viðmiðunargildi: innganga 1995, brúarárið 2008 og 2024.
    assert abs(100 * fravik["FI"][0] - 18.8) < 0.2, fravik["FI"][0]
    assert abs(100 * fravik["SE"][0] - 17.6) < 0.2, fravik["SE"][0]
    assert abs(100 * fravik["AT"][0] - (-0.1)) < 0.2, fravik["AT"][0]
    assert abs(100 * fravik["FI"][AR.index("2008")] - 7.8) < 0.2
    assert abs(100 * fravik["FI"][-1] - 9.9) < 0.2
    assert 0.30 < min(hallar) and max(hallar) < 0.45

    trend = {g: leitni5(fravik[g]) for g in NY1995}
    hp = {g: hp_sia(fravik[g]) for g in NY1995}

    # Viðmiðunargildi HP-leitninnar (mynd 3): endapunktar beggja átta.
    assert abs(100 * hp["FI"][0] - 18.2) < 0.2, hp["FI"][0]
    assert abs(100 * hp["FI"][-1] - 8.9) < 0.2, hp["FI"][-1]
    assert abs(100 * hp["SE"][0] - 20.5) < 0.2, hp["SE"][0]
    assert abs(100 * hp["SE"][-1] - 4.6) < 0.2, hp["SE"][-1]
    assert abs(100 * hp["AT"][-1] - (-5.3)) < 0.2, hp["AT"][-1]

    # Næmnipróf sléttunarvalsins: LOWESS-endapunktar innan hálfs stigs
    # frá HP-leitninni (sbr. neðanmálsgrein greinarinnar).
    for g in NY1995:
        lw = lowess(fravik[g])
        assert abs(100 * (lw[0] - hp[g][0])) < 0.5, (g, lw[0], hp[g][0])
        assert abs(100 * (lw[-1] - hp[g][-1])) < 0.5, (g, lw[-1], hp[g][-1])

    OUT.mkdir(exist_ok=True)
    with (OUT / "innganga_fravik.csv").open("w", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["ar", "FI", "SE", "AT", "FI_leitni", "SE_leitni",
                    "AT_leitni", "FI_hp", "SE_hp", "AT_hp", "halli"])
        for i, ar in enumerate(AR):
            w.writerow([ar] + [round(fravik[g][i], 4) for g in NY1995]
                       + [round(trend[g][i], 4) for g in NY1995]
                       + [round(hp[g][i], 4) for g in NY1995]
                       + [round(hallar[i], 4)])

    print("Frávik frá metna sambandinu (leitni = HP-sía, lambda = 100):")
    print(f"{'ár':6s}{'FI':>8s}{'SE':>8s}{'AT':>8s}")
    for i, ar in enumerate(AR):
        if ar in ("1995", "2000", "2005", "2010", "2015", "2020", "2024"):
            print(f"{ar:6s}" + "".join(f"{100*hp[g][i]:+7.1f}%"
                                       for g in NY1995))
    print("Finnland og Svíþjóð sigu að línunni; Austurríki hélst við hana.")


if __name__ == "__main__":
    main()
