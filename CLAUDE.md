# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Cosa fa il progetto

Script CLI Python che genera un PNG di QR code per il join automatico a una rete Wi‑Fi, con icona Wi‑Fi al centro e didascalia sotto (`<NAME>` + "Wi-Fi by Acacia"). Pensato per stampare cartelli nelle strutture Acacia.

Tutta la logica vive in `make_wifi_qr.py`. Lo shaping completo è in `shaping.md`; il pitch originale in `pitch.md`. L'asset Wi‑Fi è in `assets/wifi.png` (Material Design Icons di Google, Apache 2.0).

## Comandi

Setup ambiente (una volta):
```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Generazione di un QR (output → `qrcodes/<CODE>-wifi.png`):
```
.venv/bin/python make_wifi_qr.py <CODE> <NAME> <SSID> <PASSWORD> [--security WPA|WEP|nopass]
```

Esempio:
```
.venv/bin/python make_wifi_qr.py PRI Primula 'MyNetwork-XXXX' 'super-secret-password'
```

Non c'è suite di test; le verifiche si fanno importando `build_payload` da REPL e/o ispezionando il PNG generato.

## Pipeline di rendering

`main()` compone tre passi in sequenza, ciascuno isolato in una funzione:

1. **`make_qr(payload)`** — crea il QR con `error_correction=H` e `box_size=20` (~800–900 px). H è non negoziabile: serve a coprire la perdita di moduli causata dal logo overlay.
2. **`overlay_logo(qr, assets/wifi.png)`** — ridimensiona l'icona al ~18% della larghezza del QR e la incolla al centro su un riquadro bianco con padding, in modo da non spezzare la lettura.
3. **`add_caption(qr, name)`** — estende il canvas verso il basso e disegna `<NAME>` (bold, ~qw/14) e `Wi-Fi by Acacia` (regular, ~qw/22) centrati. Il font è cercato fra Arial / DejaVu di sistema; se non trovato, fallback al default PIL (bitmap, brutto in stampa).

## Vincoli tecnici non ovvi

- **Formato del payload Wi‑Fi.** Il QR deve contenere esattamente `WIFI:T:<sec>;S:<ssid>;P:<pwd>;;` (la `P:` viene omessa quando `--security nopass`). I caratteri `\ ; , " :` dentro SSID e password vanno backslash-escapati, altrimenti iOS/Android non parsano il QR. La logica è in `escape_value` e `build_payload`.
- **Code vincolato a `[A-Z]{3}`.** Tre lettere maiuscole, validazione fatale con exit 2 se non matcha. Coerente con gli esempi del pitch (`AMA`, `PRI`) e con il filename `<CODE>-wifi.png`.
- **Error correction H + ratio logo 18%.** Cambiare uno dei due valori senza l'altro può rendere il QR non scansionabile. Il margine disponibile a livello H copre fino a ~30% di moduli oscurati; teniamo un buffer.
- **Overwrite silenzioso.** Se `qrcodes/<CODE>-wifi.png` esiste già viene sovrascritto senza prompt.
- **Reti nascoste fuori scope.** Il flag `H:true` del payload non è supportato (R7 in `shaping.md`).
- **Font.** Il lookup parte da `/System/Library/Fonts/Supplemental/Arial*.ttf` (macOS) e DejaVu (Linux). Se serve qualità tipografica controllata, committare un TTF in `assets/` e aggiungerlo come primo candidato.

## Quando modificare cosa

- Aggiunte/modifiche di requirement o di shape → aggiornare `shaping.md` (è il documento di shaping vivo, con `shaping: true` in frontmatter).
- Nuovi vincoli sul payload o sulla CLI → aggiornare anche questo file nella sezione "Vincoli tecnici non ovvi".
