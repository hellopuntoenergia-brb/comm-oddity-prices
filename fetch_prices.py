"""
fetch_prices.py — Aggiorna PUN e PSV su GitHub Gist
Versione semplice: valori hardcoded, aggiorna sempre, zero dipendenze esterne.
Aggiorna FALLBACK_PUN e FALLBACK_PSV una volta al mese con i valori ARERA ufficiali.
"""

import json, os, datetime
from urllib.request import urlopen, Request

# ═══════════════════════════════════════════════════════
#  AGGIORNA QUESTI DUE VALORI UNA VOLTA AL MESE
#  Fonte: https://energumeno.it/risorse/quotazioni-pun-psv
# ═══════════════════════════════════════════════════════
FALLBACK_PUN = 0.1210   # €/kWh — PUN medio aprile 2026
FALLBACK_PSV = 0.5780   # €/Smc — PSV medio aprile 2026
# ═══════════════════════════════════════════════════════

GIST_ID    = os.environ["GIST_ID"]
GIST_TOKEN = os.environ["GIST_TOKEN"]

def update_gist(pun, psv):
    today = datetime.date.today()
    
    contenuto = {
        "pun": pun,
        "psv": psv,
        "pun_medio_mese": pun,
        "psv_medio_mese": psv,
        "data_aggiornamento": today.isoformat(),
        "mese_riferimento": today.strftime("%Y-%m"),
        "fonte": "valori_mensili_ARERA",
        "note": "Aggiornato da GitHub Actions"
    }
    
    body = json.dumps({
        "files": {
            "prezzi_energia.json": {
                "content": json.dumps(contenuto, indent=2, ensure_ascii=False)
            }
        }
    }).encode("utf-8")
    
    req = Request(
        f"https://api.github.com/gists/{GIST_ID}",
        data=body,
        method="PATCH",
        headers={
            "Authorization": f"Bearer {GIST_TOKEN}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    )
    
    with urlopen(req, timeout=20) as resp:
        result = json.loads(resp.read())
        print(f"✅ Gist aggiornato!")
        print(f"   PUN: {pun} euro/kWh")
        print(f"   PSV: {psv} euro/Smc")
        print(f"   Data: {today}")

if __name__ == "__main__":
    print("=== Aggiornamento PUN/PSV ===")
    print(f"PUN: {FALLBACK_PUN} | PSV: {FALLBACK_PSV}")
    update_gist(FALLBACK_PUN, FALLBACK_PSV)
