"""
fetch_prices.py — Aggiorna PUN e PSV su GitHub Gist
Versione semplificata e robusta — funziona sempre anche se le fonti primarie sono bloccate.
"""

import json, os, re, datetime
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

GIST_ID    = os.environ["GIST_ID"]
GIST_TOKEN = os.environ["GIST_TOKEN"]

# ── VALORI DI FALLBACK (aggiornati manualmente ogni mese se necessario) ──────
# Fonte: ARERA / GME — aggiornare a inizio mese con i valori ufficiali
FALLBACK_PUN = 0.1210   # €/kWh — PUN medio aprile 2026
FALLBACK_PSV = 0.5780   # €/Smc — PSV medio aprile 2026

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/json,/',
    'Accept-Language': 'it-IT,it;q=0.9',
}

def fetch_from_selectra():
    """Selectra pubblica PUN e PSV aggiornati — fonte affidabile."""
    try:
        url = "https://luce-gas.it/guida/mercato/andamento-prezzo/energia-elettrica"
        req = Request(url, headers=HEADERS)
        with urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='replace')
        
        # Cerca pattern PSV nella pagina
        psv_match = re.search(
            r'PSV[^\d]{0,20}([\d][,.][\d]{3,6})\s*[€]?[/\s]*[Ss]mc',
            html, re.I
        )
        # Cerca PUN
        pun_match = re.search(
            r'PUN[^\d]{0,30}(0[,.][\d]{3,6})\s*[€]?[/\s]*kWh',
            html, re.I
        )
        
        pun = float(pun_match.group(1).replace(',','.')) if pun_match else None
        psv = float(psv_match.group(1).replace(',','.')) if psv_match else None
        
        # Sanity check
        if pun and 0.05 < pun < 0.50: 
            print(f"  [Selectra] PUN: {pun}")
        else:
            pun = None
        if psv and 0.10 < psv < 3.0:
            print(f"  [Selectra] PSV: {psv}")
        else:
            psv = None
            
        return pun, psv
    except Exception as e:
        print(f"  [Selectra] Fallito: {e}")
        return None, None

def fetch_from_abbassalebollette():
    """Fonte alternativa italiana per PUN."""
    try:
        url = "https://www.abbassalebollette.it/glossario/pun-prezzo-unico-nazionale/"
        req = Request(url, headers=HEADERS)
        with urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='replace')
        
        pun_match = re.search(
            r'PUN[^<]{0,100}(0[,.][\d]{3,6})\s*€/kWh',
            html, re.I
        )
        if pun_match:
            pun = float(pun_match.group(1).replace(',','.'))
            if 0.05 < pun < 0.50:
                print(f"  [abbassalebollette] PUN: {pun}")
                return pun, None
    except Exception as e:
        print(f"  [abbassalebollette] Fallito: {e}")
    return None, None

def update_gist(pun, psv, fonte):
    """Aggiorna il Gist con i valori trovati."""
    today = datetime.date.today()
    mese = today.strftime('%Y-%m')
    
    payload = {
        "pun": round(pun, 6),
        "psv": round(psv, 6),
        "pun_medio_mese": round(pun, 6),
        "psv_medio_mese": round(psv, 6),
        "data_aggiornamento": today.isoformat(),
        "mese_riferimento": mese,
        "fonte": fonte,
        "aggiornato_da": "GitHub Actions — automatico"
    }
    
    body = json.dumps({
        "files": {
            "prezzi_energia.json": {
                "content": json.dumps(payload, ensure_ascii=False, indent=2)
            }
        }
    }).encode('utf-8')
    
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
        raw_url = result["files"]["prezzi_energia.json"]["raw_url"]
        print(f"\n✅ Gist aggiornato!")
        print(f"   PUN: {pun} €/kWh")
        print(f"   PSV: {psv} €/Smc")
        print(f"   Data: {today}")
        print(f"   Fonte: {fonte}")
        return True

if _name_ == "_main_":
    print("=== Fetch PUN/PSV ===")
    
    pun, psv = None, None
    fonte = "fallback"
    
    # Prova fonte 1
    print("\nTento Selectra...")
    pun, psv = fetch_from_selectra()
    if pun: fonte = "selectra.it"
    
    # Prova fonte 2 se PUN mancante
    if not pun:
        print("\nTento abbassalebollette...")
        pun2, _ = fetch_from_abbassalebollette()
        if pun2: pun = pun2; fonte = "abbassalebollette.it"
    
    # Fallback ai valori del mese corrente
    if not pun:
        print(f"\n⚠️  Fonti web non raggiungibili — uso valori fallback del mese")
        pun = FALLBACK_PUN
        fonte = "fallback_manuale"
    
    if not psv:
        psv = FALLBACK_PSV
    
    print(f"\nValori finali: PUN={pun}, PSV={psv}, fonte={fonte}")
    
    # Aggiorna sempre il Gist (anche con fallback)
    update_gist(pun, psv, fonte)
