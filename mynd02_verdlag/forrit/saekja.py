#!/usr/bin/env python3
"""Frystir frumgögn fyrir lokaútgáfu Myndar 2.

Sjálfgefið er að varðveita fyrirliggjandi frystingu. Nota þarf ``--refresh``
til að sækja nýja gagnaútgáfu. Myndagerðin sjálf sækir aldrei gögn af netinu.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import ssl
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import certifi


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "hra"
META = ROOT / "lysigogn"
EUROSTAT = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"
SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())

EU27 = [
    "BE", "BG", "CZ", "DK", "DE", "EE", "IE", "EL", "ES", "FR",
    "HR", "IT", "CY", "LV", "LT", "LU", "HU", "MT", "NL", "AT",
    "PL", "PT", "RO", "SI", "SK", "FI", "SE",
]

# A01 og undirflokkarnir endurgera glæru 20. E011 er notaður hægra megin
# sem hefðbundinn verðlagsvísir einkaneyslu heimila og samræmist eldri
# útgáfu greinarinnar.
PRICE_CATEGORIES = ["A01", "A0101", "A0103", "A010405", "A010703", "A0111", "E011"]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def eurostat_url(dataset: str, selectors: dict[str, object]) -> str:
    params: list[tuple[str, str]] = [("format", "JSON"), ("lang", "EN")]
    for key, value in selectors.items():
        if isinstance(value, list):
            params.extend((key, str(item)) for item in value)
        else:
            params.append((key, str(value)))
    return f"{EUROSTAT}/{dataset}?{urllib.parse.urlencode(params)}"


def get(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Kontext-grein-reproducibility/1.0"},
    )
    with urllib.request.urlopen(request, timeout=180, context=SSL_CONTEXT) as response:
        return response.read()


def post_json(url: str, payload: dict[str, Any]) -> bytes:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Kontext-grein-reproducibility/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=180, context=SSL_CONTEXT) as response:
        return response.read()


def source_pdf_metadata(prior: dict[str, Any] | None = None) -> dict[str, object]:
    # Greiningarskjalið sjálft fylgir ekki pakkanum (höfundarréttur). Sé það
    # til á vélinni má vísa á það með umhverfisbreytunni GREINING_PDF; annars
    # standa frystu lýsigögnin (SHA-256 og stærð) óbreytt í manifest-skránni.
    pdf = Path(os.environ.get("GREINING_PDF", RAW / "stadreyndir-esb-island-juli-2026-2.pdf"))
    out: dict[str, object] = {
        "file_name": pdf.name,
        "slide": 20,
        "title": (
            "Verðlag á Íslandi er hátt en hvað ef við snúum kaupmáttarhugtakinu "
            "við og horfum á verðlagið í hlutfalli við ráðstöfunartekjur? Þá er "
            "Ísland ódýrt"
        ),
        "pdf_creation_time": "2026-07-08T16:17:15Z",
    }
    if pdf.exists():
        data = pdf.read_bytes()
        out.update({"sha256": sha256(data), "bytes": len(data)})
    else:
        if prior:
            out = {**prior, **out}
        out["local_file_not_found"] = True
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="skipta fyrirliggjandi frystingu út fyrir ný svör",
    )
    args = parser.parse_args()

    RAW.mkdir(parents=True, exist_ok=True)
    META.mkdir(parents=True, exist_ok=True)
    checked_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    manifest_path = META / "manifest.json"
    old_manifest: dict[str, Any] = {}
    if manifest_path.exists():
        old_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    old_entries = {
        str(entry["file"]): entry for entry in old_manifest.get("files", [])
    }

    geos = EU27 + ["IS", "NO", "EU27_2020"]
    get_specs: list[dict[str, Any]] = [
        {
            "file": "eurostat_prc_ppp_ind_2024.json",
            "source": "Eurostat",
            "dataset": "prc_ppp_ind",
            "selectors": {
                "freq": "A",
                "na_item": "PLI_EU27_2020",
                "ppp_cat": PRICE_CATEGORIES,
                "geo": geos,
                "time": "2024",
            },
        },
        {
            "file": "eurostat_ilc_di03_2024_eur.json",
            "source": "Eurostat",
            "dataset": "ilc_di03",
            "selectors": {
                "freq": "A",
                "age": "TOTAL",
                "sex": "T",
                "statinfo": "MED_EI",
                "unit": "EUR",
                "geo": geos,
                "time": "2024",
            },
        },
        {
            "file": "eurostat_ilc_di03_is_2020.json",
            "source": "Eurostat",
            "dataset": "ilc_di03",
            "selectors": {
                "freq": "A",
                "age": "TOTAL",
                "sex": "T",
                "statinfo": "MED_EI",
                "unit": ["EUR", "NAC", "PPS"],
                "geo": "IS",
                "time": "2020",
            },
        },
        {
            "file": "eurostat_demo_pjan_is.json",
            "source": "Eurostat",
            "dataset": "demo_pjan",
            "selectors": {
                "freq": "A",
                "unit": "NR",
                "age": "TOTAL",
                "sex": "T",
                "geo": "IS",
                "time": ["2019", "2020", "2021", "2023", "2024", "2025"],
            },
        },
    ]

    entries: list[dict[str, Any]] = []
    for spec in get_specs:
        url = eurostat_url(spec["dataset"], spec["selectors"])
        path = RAW / spec["file"]
        data = _obtain(path, args.refresh, lambda url=url: get(url))
        payload = json.loads(data)
        if "error" in payload:
            raise RuntimeError(f"Eurostat-villa í {path.name}: {payload['error']}")
        entries.append(
            _entry(
                path,
                data,
                old_entries,
                checked_at,
                source=spec["source"],
                dataset=spec["dataset"],
                method="GET",
                url=url,
                selectors=spec["selectors"],
                response_updated=payload.get("updated"),
                allow_changed=args.refresh,
            )
        )

    px_url = (
        "https://px.hagstofa.is/pxis/api/v1/is/Efnahagur/"
        "thjodhagsreikningar/tekjuskipting/tekjuskipting/THJ06020.px"
    )
    px_payload = {
        "query": [
            {"code": "Skipting", "selection": {"filter": "item", "values": ["7"]}},
            {
                "code": "Ár",
                "selection": {
                    "filter": "item",
                    "values": [str(year) for year in range(2000, 2025)],
                },
            },
            {"code": "Geiri", "selection": {"filter": "item", "values": ["S.14"]}},
        ],
        "response": {"format": "json"},
    }
    px_path = RAW / "hagstofa_thj06020_nuverandi_B6N.json"
    px_data = _obtain(px_path, args.refresh, lambda: post_json(px_url, px_payload))
    entries.append(
        _entry(
            px_path,
            px_data,
            old_entries,
            checked_at,
            source="Hagstofa Íslands",
            dataset="THJ06020",
            method="POST",
            url=px_url,
            selectors=px_payload,
            allow_changed=args.refresh,
        )
    )

    # Glæra 20 endurgerist nákvæmlega með bráðabirgðavintage Hagstofunnar
    # frá 4. apríl 2025, ekki með síðar endurskoðuðu THJ06020-tölunum.
    vintage_url = "https://datawrapper.dwcdn.net/PrrvG/1/dataset.csv"
    vintage_path = RAW / "hagstofa_frett_vintage_2025-04-04_PrrvG.csv"
    vintage_data = _obtain(vintage_path, args.refresh, lambda: get(vintage_url))
    entries.append(
        _entry(
            vintage_path,
            vintage_data,
            old_entries,
            checked_at,
            source="Hagstofa Íslands, frétt 4. apríl 2025",
            dataset="Datawrapper PrrvG/1",
            method="GET",
            url=vintage_url,
            selectors={
                "source_page": (
                    "https://hagstofa.is/utgafur/frettasafn/thjodhagsreikningar/"
                    "tekjuskiptingaruppgjor-2024-heimilisgeirinn-aaetlun/"
                ),
                "series_used": "Ráðstöfunartekjur (tekjur - gjöld)",
                "years": ["2020", "2024"],
                "status": "bráðabirgðavintage birt 2025-04-04",
            },
            allow_changed=args.refresh,
        )
    )

    meta_path = RAW / "hagstofa_thj06020_lysigogn.json"
    meta_data = _obtain(meta_path, args.refresh, lambda: get(px_url))
    entries.append(
        _entry(
            meta_path,
            meta_data,
            old_entries,
            checked_at,
            source="Hagstofa Íslands",
            dataset="THJ06020 metadata",
            method="GET",
            url=px_url,
            allow_changed=args.refresh,
        )
    )

    cbi_url = (
        "https://www.sedlabanki.is/xmltimeseries/Default.aspx?"
        "DagsFra=2024-01-01&DagsTil=2024-12-31&TimeSeriesID=4064&Type=csv"
    )
    cbi_path = RAW / "sedlabanki_eur_midgengi_2024.csv"
    cbi_data = _obtain(cbi_path, args.refresh, lambda: get(cbi_url))
    entries.append(
        _entry(
            cbi_path,
            cbi_data,
            old_entries,
            checked_at,
            source="Seðlabanki Íslands",
            dataset="XML-timeseries 4064",
            method="GET",
            url=cbi_url,
            selectors={
                "TimeSeriesID": 4064,
                "currency": "EUR",
                "measure": "skráð miðgengi",
                "frequency": "D",
                "period": "2024-01-01/2024-12-31",
            },
            allow_changed=args.refresh,
        )
    )

    manifest: dict[str, Any] = {
        "schema_version": 1,
        "purpose": "Frosin frumgögn fyrir Mynd 2: tekjuleiðréttur kvarði og verðlag",
        "manifest_written_at_utc": checked_at,
        "source_slide": source_pdf_metadata(old_manifest.get("source_slide")),
        "files": entries,
    }
    if not args.refresh and "validation" in old_manifest:
        manifest["validation"] = old_manifest["validation"]
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Lýsigögn skrifuð: {manifest_path}")
    return 0


def _obtain(path: Path, refresh: bool, fetcher: Any) -> bytes:
    if path.exists() and not refresh:
        data = path.read_bytes()
        print(f"varðveitt: {path.name} ({len(data)} bæti)")
        return data
    data = fetcher()
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)
    print(f"fryst: {path.name} ({len(data)} bæti)")
    return data


def _entry(
    path: Path,
    data: bytes,
    old_entries: dict[str, Any],
    checked_at: str,
    allow_changed: bool = False,
    **details: Any,
) -> dict[str, Any]:
    relative = str(path.relative_to(ROOT))
    prior = old_entries.get(relative, {})
    digest = sha256(data)
    expected = prior.get("sha256")
    if expected and digest != expected and not allow_changed:
        raise RuntimeError(
            f"Frosna skráin {relative} hefur breyst án --refresh: "
            f"vænt {expected}, fékk {digest}"
        )
    return {
        "file": relative,
        **details,
        "retrieved_at_utc": prior.get("retrieved_at_utc", checked_at),
        "last_verified_at_utc": checked_at,
        "sha256": digest,
        "bytes": len(data),
    }


if __name__ == "__main__":
    sys.exit(main())
