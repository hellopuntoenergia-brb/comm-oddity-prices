# PUN/PSV Auto-Updater per Comm.Oddity

Aggiorna automaticamente PUN e PSV su un GitHub Gist ogni giorno lavorativo alle 18:00.
L'app Comm.Oddity legge questo Gist all'avvio → prezzi sempre aggiornati, zero costo.

## Setup (5 minuti)

### 1. Crea un Gist vuoto
- Vai su https://gist.github.com
- Crea un file `prezzi_energia.json` con contenuto `{}`
- Copia l'**ID del Gist** dall'URL (es. `abc123def456`)

### 2. Crea un Personal Access Token
- GitHub → Settings → Developer settings → Personal access tokens → Fine-grained
- Oppure: classic token con scope **gist** (solo gist, nient'altro)
- Copia il token

### 3. Aggiungi i secrets al repo
- In questo repo: Settings → Secrets and variables → Actions
- Aggiungi `GIST_TOKEN` = il token copiato
- Aggiungi `GIST_ID` = l'ID del Gist

### 4. Configura Comm.Oddity
- In Admin → Prezzi automatici
- Incolla l'URL raw del Gist:
  `https://gist.githubusercontent.com/TUO_USERNAME/GIST_ID/raw/prezzi_energia.json`

### 5. Test
- In GitHub: Actions → "Aggiorna PUN e PSV" → Run workflow
- Verifica che il Gist sia stato aggiornato

## Formato JSON output

```json
{
  "pun": 0.1210,
  "psv": 0.5780,
  "pun_medio_mese": 0.1198,
  "psv_medio_mese": 0.5650,
  "data_aggiornamento": "2026-04-05",
  "mese_riferimento": "2026-04",
  "fonte": "GME - Gestore Mercati Energetici"
}
```

## Fonti dati
- **PUN**: File ZIP mensili pubblicati da GME su mercatoelettrico.org (dati ufficiali pubblici)
- **PSV**: File ZIP mensili del mercato M-GAS del GME (dati ufficiali pubblici)
- Fallback: energumeno.it (aggregatore dati GME)

## Costo
**Zero.** GitHub Actions è gratuito illimitato per repository pubblici.
Per repo privati: 2.000 minuti/mese gratuiti (questo workflow usa ~1 minuto/giorno = ~22 min/mese).
