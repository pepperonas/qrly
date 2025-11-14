# celox.io Google Review QR Code - ANLEITUNG

## Problem
Die URL `https://www.google.com/maps/place/celox.io/@52.4813276,13.4275323...` enthält **nur eine CID**, keine echte Place ID.

**CID vs Place ID:**
- ❌ CID: `0x47bd7b12516c75ff:0xf1cbcad05d451d78` - funktioniert NICHT für Review Links
- ✅ Place ID: `ChIJ...` - funktioniert für direkte Review Links

## Lösung: Offizielles Google Tool (OHNE API!)

### Methode 1: Google Place ID Finder (Einfachste Methode)

**1. Tool öffnen:**
```
https://developers.google.com/maps/documentation/places/web-service/place-id
```

**2. Nach unten scrollen bis zum "Place ID Finder" Widget**

**3. Im Suchfeld eingeben:**
```
celox.io Berlin
```
oder
```
celox.io Ritterstraße
```

**4. celox.io aus den Vorschlägen auswählen**

**5. Place ID kopieren** (sieht aus wie: `ChIJ...`)

**6. Mit Qrly verwenden:**

```bash
# Mit Place ID:
./venv-gui/bin/python -m qrly \
    --place-id "ChIJ_KOPIERTE_PLACE_ID" \
    --mode rectangle-text \
    --text "CELOX.IO" \
    --name celox-review

# ODER in der GUI:
# 1. Starten: ./venv-gui/bin/python -m qrly.app
# 2. Place ID einfügen
# 3. "Generate Google Review Link" aktivieren
# 4. Text: "CELOX.IO"
# 5. Mode: Rectangle + Text
# 6. Generate!
```

**7. Verifizieren:**

Testen Sie die Place ID im Browser:
```
https://search.google.com/local/writereview?placeid=ChIJ_IHRE_PLACE_ID
```

✅ Sollte direkt zum celox.io Review-Formular führen!

---

### Methode 2: Browser Inspector (Alternative)

Falls das Tool nicht funktioniert:

**1. Google Suche öffnen:**
```
https://www.google.com/search?q=celox.io+Berlin
```

**2. Rechtsklick auf "Rezension schreiben" Button** (Knowledge Panel rechts)

**3. "Element untersuchen" / "Inspect" wählen**

**4. In Developer Tools: Ctrl+F (oder Cmd+F auf Mac)**

**5. Suchen nach: `data-pid`**

**6. Wert kopieren** (nach `data-pid="..."`)

Beispiel HTML:
```html
<button data-pid="ChIJxxx..." ...>Rezension schreiben</button>
                    ^^^^^^^^^
                    Das ist die Place ID!
```

---

### Methode 3: Google My Business Dashboard

**1. Login:**
```
https://business.google.com/
```

**2. celox.io Business auswählen**

**3. Navigation:**
```
Info → Advanced Information → Place ID
```

**4. Place ID kopieren**

---

## Warum PlusCode NICHT funktioniert

PlusCode (z.B. `9F4FFRJ7+G8`) ist nur eine **geografische Koordinate**, keine Business-Identifikation.

- ✅ PlusCode: Gut für Standort-Sharing
- ❌ PlusCode: Enthält KEINE Place ID
- ❌ PlusCode: Kann nicht zu Business-Reviews führen

**Beispiel celox.io:**
- PlusCode: `9F4FFRJ7+G8` (nur Koordinaten)
- CID: `0x47bd7b12516c75ff:0xf1cbcad05d451d78` (funktioniert nicht für Reviews)
- Place ID: `ChIJ...` ← DAS brauchen wir!

---

## Erfolgs-Checkliste

- [ ] Google Place ID Finder geöffnet
- [ ] "celox.io Berlin" gesucht
- [ ] celox.io aus Vorschlägen ausgewählt
- [ ] Place ID kopiert (beginnt mit ChIJ)
- [ ] Im Browser getestet: `https://search.google.com/local/writereview?placeid=...`
- [ ] Review-Formular öffnet sich direkt ✅
- [ ] QR-Code mit Qrly generiert
- [ ] QR-Code mit Handy getestet
- [ ] QR-Code führt direkt zum Review-Formular ✅

---

## Falls nichts funktioniert

**Fallback-Option:**

Der QR-Code führt zur Google Maps Seite (nicht direkt zum Review-Formular).
User muss dann manuell auf "Rezension schreiben" klicken.

```bash
# Funktioniert immer (ohne Place ID):
./venv-gui/bin/python -m qrly \
    "https://www.google.com/maps/place/celox.io/@52.4813276,13.4275323,17z/data=..." \
    --mode rectangle-text \
    --text "CELOX.IO" \
    --name celox-maps
```

✅ QR-Code wird erstellt
⚠️ Führt zur Maps-Seite (nicht direkt zum Review-Formular)
ℹ️ User klickt dann auf "Rezension schreiben"

---

## Zusammenfassung

**Beste Methode:** Google Place ID Finder Tool
- Keine API benötigt
- Offizielle Google-Lösung
- Funktioniert zuverlässig

**URL:** https://developers.google.com/maps/documentation/places/web-service/place-id

**Suche:** "celox.io Berlin"

**Ergebnis:** Echte Place ID (ChIJ...) → Direkte Review Links ✅
