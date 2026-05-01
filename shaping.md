---
shaping: true
---

# Wi-Fi QRCode Maker — Shaping

## Source

> # ACACIA WIKI QRCODE Maker
>
> Questo progetto racchiude un semplice che script che, dati una serie di parametri di una connessione wiki, realizza l'immagine ONG di un qrcode che permette di accedere ad un rete wifi quando un utente lo inquadra.
>
> Lo script è tutto da fare.
>
> I dati in ingresso sono:
>
> * Identificativo utile a contruire il nome del file, tipo un codice a tre cifre (AMA) - il file finale dovrà chiamarsi AMA-wifi.png
> * L'SSID del router
> * La password
>
> Il concetto deve essere simile al servizio offerto da https://qifi.org/ solo senza una UI.
>
> Dei dati di esempio ponnon essere:
>
> * Code: PRI
> * ssid: <SSID>
> * pwd: <password>

---

## Problem

Acacia ha bisogno di stampare cartelli con QR code Wi-Fi per le proprie strutture. Oggi servizi come qifi.org risolvono il problema ma richiedono l'uso di una UI web — operazione manuale, non riproducibile, poco adatta a generare in batch più cartelli o a tenere traccia delle reti.

## Outcome

Da un terminale, dato un codice struttura + SSID + password, ottenere in pochi secondi il file `qrcodes/<CODE>-wifi.png` pronto per la stampa, leggibile da iOS e Android.

---

## Requirements (R)

| ID | Requirement | Status |
|----|-------------|--------|
| R0 | Da `code` + `ssid` + `password` produrre un PNG che, scansionato, fa fare il join automatico alla rete Wi-Fi | Core goal |
| R1 | Funzionamento da CLI, senza UI | Must-have |
| R2 | File salvato come `qrcodes/<CODE>-wifi.png` | Must-have |
| R3 | QR riconosciuto sia da iOS che da Android (payload `WIFI:T:...;S:...;P:...;;` con escape corretto dei caratteri speciali) | Must-have |
| 🟡 R4 | Tipo di sicurezza: default WPA, parametro opzionale per WEP/nopass | Must-have |
| 🟡 R5 | Formato del `code`: esattamente 3 lettere maiuscole `[A-Z]{3}`, validato | Must-have |
| 🟡 R6 | Se `qrcodes/<CODE>-wifi.png` esiste già: overwrite silenzioso | Must-have |
| 🟡 R7 | Supporto reti nascoste | Out |
| 🟡 R8 | Stack: Python 3 con libreria `qrcode` (che porta dietro `Pillow`) | Must-have |
| 🟡 R9 | Caption sotto al QR: nome esteso (positional CLI, es. `Primula`) su riga 1, suffisso fisso `Wi-Fi by Acacia` su riga 2 | Must-have |
| 🟡 R10 | Icona Wi-Fi al centro del QR, da asset PNG locale `assets/wifi.png` (download una tantum) | Must-have |
| 🟡 R11 | Error correction H (~30%) per garantire scansione anche con il logo che oscura ~18% dei moduli centrali | Must-have |
| 🟡 R12 | Font caption: usa font di sistema rilevato (Arial/DejaVu), fallback al default PIL — da rifinire in iterazione successiva | Nice-to-have |

---

## A: Script Python single-file con `qrcode` + `Pillow`

| Part | Mechanism | Flag |
|------|-----------|:----:|
| **A1** | **Parsing argomenti CLI** — `argparse` con 4 positional (`code`, `name`, `ssid`, `password`) e flag opzionale `--security {WPA,WEP,nopass}` (default `WPA`) | |
| **A2** | **Validazione `code`** — regex `^[A-Z]{3}$`, errore con `sys.exit(2)` e messaggio chiaro se non matcha | |
| **A3** | **Costruzione payload Wi-Fi** — funzione `build_payload(ssid, password, security)` che produce `WIFI:T:<sec>;S:<ssid_esc>;P:<pwd_esc>;;` con escape di `\ ; , : "` secondo lo standard | |
| 🟡 **A4** | **Generazione QR** — `qrcode.QRCode(error_correction=H, box_size=20)`; output ~800–900 px per stampa | |
| 🟡 **A5** | **Overlay icona** — apre `assets/wifi.png`, ridimensiona a ~18% della larghezza del QR, aggiunge un padding bianco intorno per leggibilità, paste al centro | |
| 🟡 **A6** | **Caption** — estende il canvas verso il basso; disegna `<NAME>` (bold, ~qw/14) e `Wi-Fi by Acacia` (regular, ~qw/22) centrati; trova il TTF con lookup di candidati (Arial/DejaVu) e fallback al default PIL | |
| 🟡 **A7** | **Asset Wi-Fi** — `assets/wifi.png` scaricato dal repo Material Design Icons di Google (Apache 2.0), committato in repo | |
| **A8** | **Output path** — `qrcodes/<CODE>-wifi.png` rispetto alla cwd; overwrite implicito | |

---

## Fit Check

| Req | Requirement | Status | A |
|-----|-------------|--------|:-:|
| R0 | Da `code` + `ssid` + `password` produrre un PNG che, scansionato, fa fare il join automatico alla rete Wi-Fi | Core goal | ✅ |
| R1 | Funzionamento da CLI, senza UI | Must-have | ✅ |
| R2 | File salvato come `qrcodes/<CODE>-wifi.png` | Must-have | ✅ |
| R3 | QR riconosciuto sia da iOS che da Android (payload standard con escape) | Must-have | ✅ |
| R4 | Tipo di sicurezza default WPA, parametro per WEP/nopass | Must-have | ✅ |
| R5 | Formato `code` `[A-Z]{3}` validato | Must-have | ✅ |
| R6 | Overwrite silenzioso se file esiste | Must-have | ✅ |
| R8 | Stack Python 3 con `qrcode` | Must-have | ✅ |
| 🟡 R9 | Caption `<NAME>` + `Wi-Fi by Acacia` sotto al QR | Must-have | ✅ |
| 🟡 R10 | Icona Wi-Fi al centro da asset PNG locale | Must-have | ✅ |
| 🟡 R11 | Error correction H per scansione con logo | Must-have | ✅ |
| 🟡 R12 | Font caption (sistema con fallback) | Nice-to-have | ✅ |

Nessuna parte ⚠️. Font (R12) marcato come Nice-to-have perché soggetto a iterazione visiva — partiamo con quello che troviamo sul sistema.
